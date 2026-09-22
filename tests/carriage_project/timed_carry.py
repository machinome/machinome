# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Curta's timing loss, without its geometry or project-specific constants.

The carry stops at one. A later station can add a selector crossing to the
same union graph, but has no active influence on the earlier carry at shift 0.
"""

from machinome.math import clamp01, floor
from machinome.motion.ports import Time
from machinome.motion.joints import Bound, Revolute
from machinome.node import AssemblyNode
from machinome.simulation import Driver

from ..running_project.parts import Arbor, Carriage


def timed_carry(*, later=False, nonuniform=False, bound=None, contact=False):
    class TimedCarry(AssemblyNode):
        time = Time.running()
        crank = Driver(default=0.0, unit='deg')
        shift = Driver(default=0.0, unit=None)
        lower = Arbor()
        higher = Arbor(turn=Revolute(axis=(0, 0, 1), unit='deg',
                                    range=(None, bound)))
        carry = Carriage()
        if contact:
            higher.turn.constrain(range=(None, Bound(
                lambda own, latch: 100+latch, reads=(carry.travel,))))

        crank.drives(lower.turn, law=lambda sources, target:
                     lambda crank: crank * crank if nonuniform == 'curved'
                     else clamp01(2 * crank) if nonuniform else crank)
        (crank & shift & carry.travel).drives(
            higher.turn, law=lambda sources, target:
            lambda crank, shift, latch:
            crank * (shift < .5) * (latch >= .5) + crank * (shift >= .5))
        if later:
            station = Arbor()
            (higher.turn & crank).drives(
                station.turn, law=lambda sources, target:
                lambda higher, crank: higher * (crank < 1) + crank * (crank >= 1))
            (lower.turn & higher.turn & shift & carry.travel & station.turn).drives(
                carry.travel, law=lambda sources, target:
                lambda lower, higher, shift, own, station:
                (lower * (shift < .5) + higher * (shift >= .5)
                 + station * (shift >= 2)) * (own < 1))
        else:
            (lower.turn & higher.turn & shift & carry.travel).drives(
                carry.travel, law=lambda sources, target:
                lambda lower, higher, shift, own:
                (lower * (shift < .5) + higher * (shift >= .5)) * (own < 1))

        def simulate(self):
            for part in (self.higher,):
                if part.turn.value is None:
                    part.turn = 0.0
            if self.carry.travel.value is None:
                self.carry.travel = 0.0
            if later and self.station.turn.value is None:
                self.station.turn = 0.0

    return TimedCarry


class InheritedCrossings(AssemblyNode):
    """Three surfaces split across harmless inherited kink boundaries."""
    time = Time.running()
    crank = Driver(default=0.0, unit='deg')
    lower = Arbor()
    higher = Arbor()
    observer = Arbor()
    crank.drives(lower.turn, law=lambda sources, target: lambda crank:
                 clamp01(crank) + clamp01(crank-1) + clamp01(crank-2)
                 + clamp01(crank-3))
    (crank & lower.turn).drives(higher.turn,
        law=lambda sources, target: lambda crank, lower: crank * floor(lower))
    higher.turn.drives(observer.turn)
