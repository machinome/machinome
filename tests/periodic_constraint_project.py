# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Curta's periodic closing surface, without the expensive printed geometry."""

from machinome.math import floor
from machinome.motion.joints import Bound
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver
from .running_project.parts import Arbor


def closing(own, drum):
    return -360 * floor((-drum - 10.8) / 360) - 125.22


class PeriodicStop(AssemblyNode):
    time = Time.running()
    crank = Driver(default=120)
    motor = Driver(default=0)
    drum = Arbor()
    bell = Arbor()
    free = Arbor()
    crank.drives(drum.turn, ratio=-1)
    crank.drives(bell.turn, ratio=-1)
    motor.drives(free.turn)
    bell.turn.constrain(range=(Bound(closing, reads=(drum.turn,)), None))


class FixedStop(AssemblyNode):
    time = Time.running()
    crank = Driver(default=120)
    bell = Arbor()
    crank.drives(bell.turn, ratio=-1)
    bell.turn.constrain(range=(-125.22, None))


class UpperPeriodicStop(AssemblyNode):
    time = Time.running()
    crank = Driver(default=120)
    drum = Arbor()
    bell = Arbor()
    crank.drives(drum.turn)
    crank.drives(bell.turn)
    bell.turn.constrain(range=(None, Bound(
        lambda own, drum: 360 * floor((drum - 10.8) / 360) + 125.22,
        reads=(drum.turn,))))


class RelievingStop(AssemblyNode):
    time = Time.running()
    crank = Driver(default=120)
    release = Driver(default=0)
    drum = Arbor()
    bell = Arbor()
    crank.drives(drum.turn, ratio=-1)
    crank.drives(bell.turn, ratio=-1)
    bell.turn.constrain(range=(Bound(
        lambda own, drum, release: closing(own, drum) - release,
        reads=(drum.turn, release)), None))


class TimePeriodicStop(AssemblyNode):
    time = Time.running()
    drum = Arbor()
    bell = Arbor()
    free = Arbor()
    time.drives(drum.turn, law=lambda source, target: lambda t: -120 - 7200*t)
    drum.turn.drives(bell.turn)
    time.drives(free.turn, ratio=10)
    bell.turn.constrain(range=(Bound(closing, reads=(drum.turn,)), None))


class SimultaneousStop(PeriodicStop):
    second = Arbor()
    PeriodicStop.crank.drives(second.turn, ratio=-1)
    second.turn.constrain(range=(Bound(
        closing, reads=(PeriodicStop.drum.turn,)), None))


class DisengagedStop(AssemblyNode):
    time = Time.running()
    crank = Driver(default=120)
    idle = Driver(default=0)
    engaged = Driver(default=0)
    drum = Arbor()
    bell = Arbor()
    (crank & idle & engaged).drives(drum.turn, law=lambda owners, target:
        lambda crank, idle, engaged: -crank - idle*(engaged > .5))
    drum.turn.drives(bell.turn)
    bell.turn.constrain(range=(Bound(closing, reads=(drum.turn,)), None))


class CompoundOnlyStop(AssemblyNode):
    time = Time.running()
    first = Driver(default=0)
    second = Driver(default=0)
    bell = Arbor()
    bell.turn.constrain(range=(Bound(lambda own, a, b: a*b - .1,
                                    reads=(first, second)), None))

    def simulate(self):
        if self.bell.turn.value is None:
            self.bell.turn = 0
