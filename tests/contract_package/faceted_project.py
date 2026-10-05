# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A project of the faceted stand-in: two cubes, apart."""

from machinome.node.assembly import AssemblyNode

from .faceted_stand_in import MeshPart


class Cube(MeshPart):
    """A 10 mm cube centred on the origin."""

    mesh_source = 'cube.stl'


class FacetedProject(AssemblyNode):

    def __init__(self):
        self.near = Cube()
        self.far = Cube()
        super().__init__()

    def render(self):
        self.far.translate([30, 0, 0])
        return [self.near, self.far]
