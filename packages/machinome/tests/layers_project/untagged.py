# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`machine.py`'s tree with no declaration and no app: the byte pin.

Its root is named `Layered` too, so that its document and the tagged
one differ in nothing but what layers add.
"""

from solid2 import cube

from machinome.node.assembly import AssemblyNode
from machinome.node.fusion import FusionNode
from machinome.node.solid2 import Solid2Node
from machinome.simulation import Driver, Instruction, State


class Case(Solid2Node):
    def render(self):
        return cube([12, 12, 2], center=True)


class Wire(Solid2Node):
    def render(self):
        return cube([1, 1, 8], center=True)


class Lamp(Solid2Node):
    def render(self):
        return cube([3, 3, 3], center=True)


class Circuit(AssemblyNode):
    wire = Wire()
    lamp = Lamp()

    def simulate(self):
        self.lamp.translate((6, 0, 0))


class Lever(Solid2Node):
    def render(self):
        return cube([2, 8, 2], center=True)


class Key(Solid2Node):
    def render(self):
        return cube([4, 4, 4], center=True)


class Inner(Solid2Node):
    def render(self):
        return cube([2, 2, 2], center=True)


class Cover(FusionNode):
    inner = Inner()


class Spare(Solid2Node):
    def render(self):
        return cube([1, 1, 1], center=True)


class Layered(AssemblyNode):
    powered = Driver(default=0., range=(0., 1.))
    count = State(default=0, dtype=int)
    (powered & count).commits(
        count,
        at=lambda sources, targets: lambda powered, count: powered > .5,
        law=lambda sources, targets: lambda powered, count: count + 1)

    instructions = {'Power': Instruction({'powered': 1.}, duration=.5)}

    case = Case()
    circuit = Circuit()
    lever = Lever()
    key = Key()
    cover = Cover()
    spare = Spare()

    def simulate(self):
        self.lever.translate((0, 12, 0))
        self.key.translate((-12, 0, 0))
        self.cover.translate((0, -12, 0))

    def render(self):
        self.spare.omit()
