# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A self-contained project of imported meshes, for the `mesh-engine`
change.

Written into a directory a caller owns, never into the repository, which
carries no binary meshes: a manifest, a package `mfixture` whose module
`parts.py` declares `StlNode` parts over three meshes generated here with
trimesh, and the meshes themselves. Every part is an `StlNode`, so the
project builds with no renderer and no CAD kernel, and every fusion of its
parts is faceted, decided by the mesh engine:

- `Shelf`, an assembly of two parts and no fusion: a build that never needs
  the mesh engine;
- `Fused`, a fusion of three parts, two overlapping and one turned about Z:
  the faceted fusion whose STL the golden pins;
- `HoleyFused`, a fusion whose second child is a box missing one triangle,
  admitted by its node (`require_watertight = False`) and refused by the
  mesh engine.

Used by `tests/mesh_engine_golden.py` and `tests/test_mesh_engine_dependency.py`.
"""

import os

import trimesh

#: The modification time every source of the project is given.
SOURCE_TIME = 1_700_000_000

MANIFEST = '''\
[tool.machinome]
model = "mfixture.parts:Shelf"
'''

PARTS = '''\
from machinome.node import AssemblyNode, FusionNode, StlNode


class Block(StlNode):
    """A 10 x 6 x 4 mm block."""

    stl_source = 'block.stl'


class Bar(StlNode):
    """A 16 x 2 x 2 mm bar."""

    stl_source = 'bar.stl'


class Holey(StlNode):
    """A 4 mm box missing one triangle: open, admitted knowingly."""

    stl_source = 'holey.stl'
    require_watertight = False


class Shelf(AssemblyNode):
    """Two parts, apart, and no fusion."""

    def __init__(self):
        self.block = Block()
        self.bar = Bar()
        super().__init__()
        self.bar.translate([0, 0, 10])

    def render(self):
        return [self.block, self.bar]


class Fused(FusionNode):
    """A block, a bar overlapping it, and a second bar turned 30 degrees
    about Z overlapping both."""

    def __init__(self):
        self.block = Block()
        self.bar = Bar()
        self.cross = Bar()
        super().__init__()
        self.bar.translate([3, 0, 1])
        self.cross.rotate(30, [0, 0, 1])
        self.cross.translate([-2, 1, 0.5])

    def render(self):
        return [self.block, self.bar, self.cross]


class HoleyFused(FusionNode):
    """A block and an open box overlapping it."""

    def __init__(self):
        self.block = Block()
        self.holey = Holey()
        super().__init__()
        self.holey.translate([2, 0, 0])

    def render(self):
        return [self.block, self.holey]
'''


def holey_box(size=4.0):
    """A box missing its last triangle: not a closed solid, to anyone."""
    mesh = trimesh.creation.box((size, size, size))
    mesh.faces = mesh.faces[:-1]
    return mesh


def write_fixture(project):
    """Write the project into the existing directory `project`; return the
    path of its `parts.py`."""
    package = os.path.join(project, 'mfixture')
    os.makedirs(package)
    with open(os.path.join(project, 'pyproject.toml'), 'w') as handle:
        handle.write(MANIFEST)
    open(os.path.join(package, '__init__.py'), 'w').close()
    parts = os.path.join(package, 'parts.py')
    with open(parts, 'w') as handle:
        handle.write(PARTS)
    trimesh.creation.box((10, 6, 4)).export(
        os.path.join(package, 'block.stl'))
    trimesh.creation.box((16, 2, 2)).export(
        os.path.join(package, 'bar.stl'))
    holey_box().export(os.path.join(package, 'holey.stl'))
    # Sources dated in the past, as a checked-out project's are. A build of
    # sources written within the last moments restarts its generation
    # without end (`machinome build` printing START every second; the wart
    # of 3 October 2026, "a `machinome build` hanging three hours in a fresh
    # project worktree"), which is not what these fixtures exercise.
    for folder, _, names in os.walk(project):
        for name in names:
            os.utime(os.path.join(folder, name), (SOURCE_TIME, SOURCE_TIME))
    return parts
