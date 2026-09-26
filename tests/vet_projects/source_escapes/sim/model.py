# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.node import AssemblyNode
from machinome.node import OpenScadNode, StlNode


class Outside(OpenScadNode):
    scad_source = '../../../outside.scad'


class Linked(StlNode):
    stl_source = 'link/gear.stl'


class Nothing(StlNode):
    stl_source = None


class Machine(AssemblyNode):
    pass
