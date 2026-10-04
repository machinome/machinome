# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Parts that need neither SolidPython nor the OpenSCAD engine (OpenSpec
change `scad-presentation`): an imported STL, a second one, an exact
part, and the all-STL and all-exact assemblies a build without the engine
publishes. This module imports no SolidPython, so it loads where SolidPython
is absent."""

import cadquery

from machinome.node import AssemblyNode, CadQueryNode, StlNode


class Bracket(StlNode):
    stl_source = 'bracket.stl'


class Tab(StlNode):
    stl_source = 'tab.stl'


class Block(CadQueryNode):
    def render(self):
        return cadquery.Workplane('XY').box(8, 8, 8)


class Plinth(CadQueryNode):
    def render(self):
        return cadquery.Workplane('XY').box(12, 12, 2)


class StlBench(AssemblyNode):
    """Every part an imported STL."""

    def render(self):
        return [Bracket(), Tab().translate([30, 0, 0])]


class ExactBench(AssemblyNode):
    """Every part exact."""

    def render(self):
        return [Block(), Plinth().translate([0, 0, -6])]
