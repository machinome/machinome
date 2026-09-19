# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The PAWL fixture: cycle 1's counter with an anti-reversal pawl.

The originating project is `projects/Calculators/Curta-Type-I-3x`, whose
booklet says of the crank that "it is always locked against backward
turns". Its project spike measured what cycle 1 does without that lock:
dragging the crank backwards through `floor(crank / 360)` with an
additive law commits a SECOND addition, 9 to 18. The pawl is the
declaration that stops it, and it is a `Bound` on a joint and nothing
else (OpenSpec change ``a-bound-stops-the-request``, design section 12).

`Counter` is imported unchanged, and so are its level and its law: the
ONLY difference between `Pawl` and `Counter` is the ranged `crank_dial`,
so a test asserting the two apart is asserting the pawl and nothing
else.

`Stroke` sits beside it for the other shape the Curta's interlocks take
-- `blocked_crank_lift`, a plain numeric `range=(0, 9)` on a lift that
simply stops at 9 mm. Every expected value in the tests is computed BY
HAND; the bounds below are never called to produce one.
"""

from machinome.math import floor
from machinome.motion.joints import Prismatic, Revolute
from machinome.node import AssemblyNode
from machinome.simulation import Driver, State

from .counter import DIGIT, advance, strokes
from .parts import Dial, Plate


#: The pawl's tooth pitch, in degrees of the crank dial. Exactly
#: representable, so a test can name a seated tooth as a float.
PITCH = 6.0

#: The crank lift's whole stroke, in millimetres.
STROKE = 9.0


class Pawl(AssemblyNode):
    """`Counter` with one addition: a crank dial whose declared range is
    the last seated tooth, and nothing above it.

    The bound is the one-argument shape ADR-109 gave a ratchet -- read at
    the value the coordinate HELD when the request started, which is what
    makes the tooth the tooth the request began on rather than one the
    bound follows down.
    """

    crank = Driver(default=0, unit='deg')
    units = State(default=0, range=(0, 9), dtype=int)
    tens = State(default=0, range=(0, 9), dtype=int)

    units_dial = Dial()
    tens_dial = Dial()
    crank_dial = Dial(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(lambda turn: PITCH * floor(turn / PITCH), None)))

    (crank & units & tens).commits((units, tens), at=strokes, law=advance)

    units.drives(units_dial.turn, ratio=DIGIT)
    tens.drives(tens_dial.turn, ratio=DIGIT)
    crank.drives(crank_dial.turn)


class Stroke(AssemblyNode):
    """A plain numeric range on a lift the crank drives: the Curta's
    `blocked_crank_lift`, which stops at 9 mm and does not refuse the
    stroke that reached it."""

    crank = Driver(default=0, unit='deg')
    lift = Driver(default=0.0, unit='mm')
    units = State(default=0, range=(0, 9), dtype=int)
    tens = State(default=0, range=(0, 9), dtype=int)

    units_dial = Dial()
    tens_dial = Dial()
    plate = Plate(lift=Prismatic(axis=(0, 0, 1), unit='mm',
                                 range=(0, STROKE)))

    (crank & units & tens).commits((units, tens), at=strokes, law=advance)

    units.drives(units_dial.turn, ratio=DIGIT)
    tens.drives(tens_dial.turn, ratio=DIGIT)
    lift.drives(plate.lift)


class ScaledStroke(AssemblyNode):
    """`Stroke` whose lift driver carries a SCALE: a request states its
    travel in design units, the bank holds native units, and `admitted`
    speaks the units `by=` speaks."""

    crank = Driver(default=0, unit='deg')
    lift = Driver(default=0.0, unit='mm', scale=0.5)
    units = State(default=0, range=(0, 9), dtype=int)
    tens = State(default=0, range=(0, 9), dtype=int)

    units_dial = Dial()
    tens_dial = Dial()
    plate = Plate(lift=Prismatic(axis=(0, 0, 1), unit='mm',
                                 range=(0, STROKE)))

    (crank & units & tens).commits((units, tens), at=strokes, law=advance)

    units.drives(units_dial.turn, ratio=DIGIT)
    tens.drives(tens_dial.turn, ratio=DIGIT)
    lift.drives(plate.lift)


class TwoStops(AssemblyNode):
    """Two bounded coordinates one driver reaches, whose stops land on
    the SAME float: several constraints met at one landing are several
    entries of ONE stop."""

    crank = Driver(default=0, unit='deg')
    lift = Driver(default=0.0, unit='mm')
    units = State(default=0, range=(0, 9), dtype=int)
    tens = State(default=0, range=(0, 9), dtype=int)

    units_dial = Dial()
    tens_dial = Dial()
    front = Plate(lift=Prismatic(axis=(0, 0, 1), unit='mm',
                                 range=(0, STROKE)))
    back = Plate(lift=Prismatic(axis=(0, 0, 1), unit='mm',
                                range=(0, STROKE)))

    (crank & units & tens).commits((units, tens), at=strokes, law=advance)

    units.drives(units_dial.turn, ratio=DIGIT)
    tens.drives(tens_dial.turn, ratio=DIGIT)
    lift.drives(front.lift)
    lift.drives(back.lift)
