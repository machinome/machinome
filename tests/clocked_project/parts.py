# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Leaves for the clocked fixtures: one dial, and nothing else.

A dial is a cylinder with one revolute joint, which is the whole of the
geometry either fixture needs -- a state poses a part, and a part that
turns is enough to read that pose off. No fixture here builds a mesh.
"""

from solid2 import cube, cylinder

from machinome.motion.joints import Prismatic, Revolute
from machinome.node import Solid2Node


class Dial(Solid2Node):
    """A numbered wheel: one revolute joint on a LEAF."""

    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cylinder(r=10, h=3)


class Slide(Solid2Node):
    """A body travelling along one line: one prismatic joint on a LEAF.

    The shape every bounded coordinate of the interlock fixtures has --
    the Curta's own selector knob is a slide, and its stop is a `Bound`
    on this joint (OpenSpec change ``a-bound-stops-the-request``).
    """

    travel = Prismatic(axis=(1, 0, 0), unit='mm')

    def render(self):
        return cube([20, 6, 6], center=True)


class Plate(Solid2Node):
    """A plate rising in its guide: the same joint under the name a
    LIFT answers to, so a fixture can read one and travel the other."""

    lift = Prismatic(axis=(0, 0, 1), unit='mm')

    def render(self):
        return cube([12, 12, 3], center=True)
