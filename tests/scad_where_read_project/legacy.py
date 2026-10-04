# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A project leaf overriding `as_scad`, the legacy SCAD-only seam: its
STL is rendered by OpenSCAD from the SCAD it returns, so its materialization
asks the OpenSCAD engine for SCAD text."""

from solid2 import cube

from machinome.node import AssemblyNode
from machinome.node.leaf import LeafNode

from .native import Block


class Bracket(LeafNode):
    namespace = 'solid2'

    def render(self):
        return cube([3, 5, 7])

    def as_scad(self, rendered):
        return rendered


class LegacyBench(AssemblyNode):
    def render(self):
        return [Block(), Bracket(name='bracket').translate([20, 0, 0])]
