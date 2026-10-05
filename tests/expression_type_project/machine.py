# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The fixture of `tests/expression_type_golden.py` (OpenSpec change
`expression-type`).

One assembly whose operations carry animation time and one driver through
`machinome.math`, with a subexpression shared between them -- so the
compact closed text of an operation carries a `let` -- and one flexible
leaf whose port is fed from the same values, so a flexible parameter
carries an expression. What it pins is the text and publication of
symbolic values, not geometry: the rigid leaves are cubes.
"""

from molejo import Circle, Helix, P, Shape
from solid2 import cube

import machinome.math as m
from machinome.motion.ports import TranslationalPort
from machinome.node.assembly import AssemblyNode
from machinome.node.molejo import MolejoNode
from machinome.node.solid2 import Solid2Node
from machinome.simulation import Driver


class Block(Solid2Node):
    """A cube. The geometry is not the point."""

    def render(self):
        return cube(2, center=True)


class Coil(MolejoNode):
    """A short helix whose height is the one thing the machine moves."""

    height = TranslationalPort(unit='mm')

    def render(self):
        return Shape(
            profile=Circle(radius=1.0),
            path=[Helix(radius=6.0, turns=3, height=P.height)],
            path_samples=48,
            profile_samples=8,
        )


class SharedMotion(AssemblyNode):
    """Time and a driver, composed once and read in four places."""

    drive = Driver(default=0, range=(0, 90), unit='deg')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arm = Block()
        self.slider = Block()
        self.coil = Coil()

    def render(self):
        return [self.arm, self.slider, self.coil]

    def simulate(self):
        phase = m.sin(self.time * 360 + self.drive)
        swing = m.clamp(phase * phase, 0, 1)
        self.arm.rotate(swing * 45 + phase, [0, 0, 1])
        self.slider.translate([m.cos(self.drive) * swing, swing + 1, 0])
        self.connect(20 + 5 * swing, self.coil.height)
