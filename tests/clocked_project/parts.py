# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Leaves for the clocked fixtures: one dial, and nothing else.

A dial is a cylinder with one revolute joint, which is the whole of the
geometry either fixture needs -- a state poses a part, and a part that
turns is enough to read that pose off. No fixture here builds a mesh.
"""

from solid2 import cylinder

from solid_node.motion.joints import Revolute
from solid_node.node import Solid2Node


class Dial(Solid2Node):
    """A numbered wheel: one revolute joint on a LEAF."""

    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cylinder(r=10, h=3)
