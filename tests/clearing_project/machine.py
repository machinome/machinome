# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The Curta's clearing interface, reduced to what the run is answerable
for.

The originating project is `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation`, checkpoint `b285393`, and the requirement is recorded
whole in `workflow/docs/curta-retained-angle-clearing.md`. Clearing
sweeps a ring carrying two nine-tooth racks past the register dials: one
row over the counter, one over the result, on opposite halves of the
ring. A rack turns a dial only while its teeth reach it AND the dial is
not already standing at its missing-tooth zero -- nine teeth, one gap,
and the gap is what lets the ring go on sweeping past a dial that has
finished while it still clears the dials beyond it.

The numbers are the project's own, source-backed: the racks start at
`9.75` and `10.5` ring degrees, their pitches are `degrees(3.75 / 52)`
and `degrees(3.75 / 49.55)` ring degrees per tooth, a tooth turns a dial
`36` wheel degrees, and the stations are `(130 if counter else 0) -
20 * place`. The ring angle is the middle 80 % of the clearing control,
which is a `clamp01` window -- so the law's SKELETON is NOT affine, and
every self-read crossing of this shape falls to the sampled search
rather than to a solve. That is what makes this fixture the price list
the migration reads (design.md section 11).

What the fixture does NOT copy is the clearance: the band's half-width
here is STATED, and the migration substitutes the measured one.
"""

import math

from solid_node.math import clamp01, floor
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode
from solid_node.parameters import Angle
from solid_node.simulation import Driver

from ..running_project.parts import Arbor

#: Where the ring stands at the start of a sweep, and how far it
#: travels, in ring degrees: enough to carry every station's nine teeth
#: past its dial.
ORIGIN = -40.0
SWEEP = 240.0

#: Where each rack's first tooth stands, in ring degrees.
RESULT_START = 10.5
COUNTER_START = 9.75

#: Ring degrees per tooth of each rack.
RESULT_PITCH = math.degrees(3.75 / 49.55)
COUNTER_PITCH = math.degrees(3.75 / 52)

#: Wheel degrees a tooth turns a dial, and the teeth a rack carries.
TOOTH = 36.0
TEETH = 9

#: The clearing gear's stated clearance: the dial is disengaged over a
#: BAND of this half-width about every multiple of 360, entered from
#: either side.
GAP = 0.5

#: The places each row carries, digits first.
PLACES = 3


def station(place, counter):
    """Where along the ring this dial's rack reaches it, in ring
    degrees -- the project's own table."""
    return (130.0 if counter else 0.0) - 20.0 * place


def ring_angle(control):
    """The ring's angle over the MIDDLE 80 % of the clearing control:
    the `clamp01` window that makes this law's skeleton non-affine."""
    return ORIGIN + SWEEP * clamp01((control - 0.1) / 0.8)


def clearing_rack(place, counter):
    """One dial's clearing law: a rack term continuous in the control,
    multiplied by an engagement gate over the dial's OWN retained
    angle."""
    start = (COUNTER_START if counter else RESULT_START) + station(place,
                                                                  counter)
    pitch = COUNTER_PITCH if counter else RESULT_PITCH

    def make(sources, target):
        def law(control, wheel):
            reach = ring_angle(control) - start
            meshed = (reach >= 0.0) * (reach <= TEETH * pitch)
            shifted = wheel + GAP
            free = shifted - 360.0 * floor(shifted / 360.0) >= 2 * GAP
            return (TOOTH / pitch) * reach * meshed * free

        return law

    return make


class CurtaInterface(AssemblyNode):
    """Six register dials cleared by one ring, two rows of three.

    Each dial is its own relation with its own self-read and its own
    walk: one dial's disengagement cuts only its own path. A `.repeat()`
    would be the natural shape for a row, but a repeated child's joint
    coordinate has no qualified id the run can bank it under, which the
    running root already refuses -- so the places are named one by one.
    """

    time = Time.running()

    #: What the FIRST dial rests at, so a test can stand it a hair short
    #: of its gap; the other five keep the fixture's own digits.
    digit = Angle(TOOTH)

    clearing = Driver(default=0.0, unit=None)

    result0 = Arbor()
    result1 = Arbor()
    result2 = Arbor()
    counter0 = Arbor()
    counter1 = Arbor()
    counter2 = Arbor()

    (clearing & result0.turn).drives(result0.turn,
                                     law=clearing_rack(0, False))
    (clearing & result1.turn).drives(result1.turn,
                                     law=clearing_rack(1, False))
    (clearing & result2.turn).drives(result2.turn,
                                     law=clearing_rack(2, False))
    (clearing & counter0.turn).drives(counter0.turn,
                                      law=clearing_rack(0, True))
    (clearing & counter1.turn).drives(counter1.turn,
                                      law=clearing_rack(1, True))
    (clearing & counter2.turn).drives(counter2.turn,
                                      law=clearing_rack(2, True))

    def render(self):
        for index, dial in enumerate(self.dials()):
            dial.translate([25.0 * index, 0.0, 0.0])

    def dials(self):
        return (self.result0, self.result1, self.result2,
                self.counter0, self.counter1, self.counter2)

    def simulate(self):
        for index, dial in enumerate(self.dials()):
            if dial.turn.value is None:
                dial.turn = self.digit if index == 0 else TOOTH * (index + 1)
