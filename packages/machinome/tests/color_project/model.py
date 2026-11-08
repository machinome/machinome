# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Standard authored rigid fixtures, with independent native palette expectations."""
from solid2 import cube
from machinome.color import color_when
from machinome.expression_graph import symbolic
from machinome.math import sqrt
from machinome.motion.ports import Time
from machinome.node.assembly import AssemblyNode
from machinome.node.solid2 import Solid2Node
from machinome.simulation import Driver, State

OFF = '#e5dfce'
ON = '#ffd978'

class Glass(Solid2Node):
    color = OFF
    def render(self):
        return cube([12, 12, 6], center=True)

class Posed(AssemblyNode):
    powered = Driver(default=0., range=(0., 1.))
    independent = Driver(default=0., range=(0., 5.))
    glass = Glass()
    def simulate(self):
        self.glass.color = color_when(self.powered > .5, on=ON, off=OFF)
        self.glass.translate((self.independent, 0, 0))

class Powered(Posed):
    powered = Driver(default=1., range=(0., 1.))

class Running(Posed):
    time = Time.running()

class Clocked(Posed):
    count = State(default=0, dtype=int)
    (Posed.powered & count).commits(count,
        at=lambda sources, targets: lambda powered, count: powered > .5,
        law=lambda sources, targets: lambda powered, count: count + 1)

class InvalidClocked(Clocked):
    later = Glass()
    def simulate(self):
        super().simulate()
        self.later.color = color_when(sqrt(2 - self.powered), on=ON, off=OFF)
        self.later.translate((20, 0, 0))

class FailingPublication(Posed):
    def simulate(self):
        super().simulate()
        if symbolic(self.powered) is not None:
            raise RuntimeError('deliberate publication failure after color assignment')

# Relation-fed presentation: the output is settled by the normal whole-tree
# fixpoint, and color is read afterwards by the standard presentation walk.
from machinome.motion.ports import SignalPort

class ObservationSource(AssemblyNode):
    def render(self):
        return []
    request = SignalPort()
    observed = SignalPort(out=True)
    def simulate(self):
        self.observed = self.request.value > .5

class ObservedGlass(Glass):
    @property
    def color(self):
        return color_when(self.condition_port.value, on=ON, off=OFF)

class ObservedLampBank(AssemblyNode):
    observation = SignalPort()
    bulbs = [ObservedGlass()]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bulbs[0].condition_port = self.observation

class PropertyPosed(AssemblyNode):
    powered = Driver(default=0., range=(0., 1.))
    source = ObservationSource()
    lamps = ObservedLampBank()
    powered.drives(source.request)
    source.observed.drives(lamps.observation)

class Shared(Posed):
    second = Glass()
    def simulate(self):
        super().simulate()
        same = self.powered > .5
        self.second.color = color_when(same, on=ON, off=OFF)
        self.second.translate((same * 20, 0, 0))

class Nested(AssemblyNode):
    unit = Posed()

class NumericChoice(Posed):
    def simulate(self):
        self.glass.color = color_when(True, on=ON, off=OFF)

class ClockedStateColor(Clocked):
    def simulate(self):
        super().simulate()
        self.glass.color = color_when(self.count > 0, on=ON, off=OFF)

from machinome.parameters import Flag

class PublicationChoice(Clocked):
    unsafe = Flag(False)
    def simulate(self):
        super().simulate()
        condition = sqrt(2 - self.powered) if self.unsafe else self.powered > .5
        self.glass.color = color_when(condition, on=ON, off=OFF)
