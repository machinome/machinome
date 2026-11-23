# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`Layered`: a clocked machine whose parts declare layers.

`case` is on no layer; `circuit` is on `ELECTRICAL` and holds `wire`
(declaring nothing) and `lamp` (adding `MECHANICAL`); `lever` is on
`MECHANICAL`; `key` is on both; `cover` is a fusion declaring nothing
whose fused child declares `ELECTRICAL`; `spare` is omitted and is the only
part on `SPARE`. `Layered` declares its own app; `Bare` is the same machine without one.
"""

from solid2 import cube

from machinome.node.assembly import AssemblyNode
from machinome.node.fusion import FusionNode
from machinome.node.solid2 import Solid2Node
from machinome.simulation import Driver, Instruction, State

from .layers import ELECTRICAL, MECHANICAL, SPARE


class Case(Solid2Node):
    def render(self):
        return cube([12, 12, 2], center=True)


class Wire(Solid2Node):
    def render(self):
        return cube([1, 1, 8], center=True)


class Lamp(Solid2Node):
    layers = MECHANICAL

    def render(self):
        return cube([3, 3, 3], center=True)


class Circuit(AssemblyNode):
    layers = ELECTRICAL

    wire = Wire()
    lamp = Lamp()

    def simulate(self):
        self.lamp.translate((6, 0, 0))


class Lever(Solid2Node):
    layers = MECHANICAL

    def render(self):
        return cube([2, 8, 2], center=True)


class Key(Solid2Node):
    layers = (ELECTRICAL, MECHANICAL)

    def render(self):
        return cube([4, 4, 4], center=True)


class Inner(Solid2Node):
    layers = ELECTRICAL

    def render(self):
        return cube([2, 2, 2], center=True)


class Cover(FusionNode):
    inner = Inner()


class Spare(Solid2Node):
    layers = SPARE

    def render(self):
        return cube([1, 1, 1], center=True)


class Bare(AssemblyNode):
    """The machine without its app: what a producer that bundles nothing
    publishes."""

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


class Layered(Bare):
    """The machine, declaring its own app."""

    app = 'app/index.tsx'
