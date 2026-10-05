# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node.assembly import AssemblyNode
from machinome.node.openscad import OpenScadNode
from machinome.node.stl import StlNode


class Outside(OpenScadNode):
    scad_source = '../../../outside.scad'


class Linked(StlNode):
    stl_source = 'link/gear.stl'


class Nothing(StlNode):
    stl_source = None


class Machine(AssemblyNode):
    pass
