# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.node import AssemblyNode
import cadquery as cq


def write():
    cq.Workplane('XY').box(1, 1, 1).export('out.stl')


class Machine(AssemblyNode):
    pass
