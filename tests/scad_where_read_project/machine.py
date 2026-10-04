# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Where SCAD is read (OpenSpec change `scad-presentation`, design.md
Decision 3): an assembly placing a sub-assembly of an exact part, a faceted
fusion of two imported STLs, a numerically bound flexible part and one
`Solid2Node`, the only part whose SCAD a build writes. The `Solid2Node` is
the presentation golden's `FineCylinder`, declared the same, so its `.scad`
is that golden's bytes; it turns with time, so two snapshot poses differ."""

from molejo import Circle, Helix, P, Shape
from solid2 import cylinder

from machinome.motion.ports import TranslationalPort
from machinome.node import AssemblyNode, FusionNode, MolejoNode, Solid2Node

from .native import Block, Bracket, Plinth, Tab


class FineCylinder(Solid2Node):
    fn = 24

    def render(self):
        return cylinder(r=3, h=8)


class Fused(FusionNode):
    def render(self):
        return [Bracket(), Tab().translate([2, 0, 0])]


class Spring(MolejoNode):
    height = TranslationalPort(unit='mm')

    def render(self):
        return Shape(
            profile=Circle(radius=0.5),
            path=[Helix(radius=3.0, turns=2.0, height=P.height)],
            path_samples=40,
            profile_samples=6,
        )


class Group(AssemblyNode):
    def render(self):
        return [Block()]


class Machine(AssemblyNode):
    def render(self):
        spring = Spring()
        spring.height = 12.0
        return [
            Group(),
            Fused().translate([-40, 0, 0]),
            spring.translate([0, -15, 0]),
            FineCylinder().rotate(self.time * 360, [0, 0, 1]),
        ]


class Mixed(AssemblyNode):
    """One `Solid2Node` among exact parts, for the develop builder."""

    def render(self):
        return [FineCylinder(), Block().translate([20, 0, 0]),
                Plinth().translate([0, 0, -6])]
