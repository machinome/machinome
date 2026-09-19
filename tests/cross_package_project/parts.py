# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Leaves for the cross-package import-anchoring tests
(`tests/test_scad_import_paths.py`): one per artifact-emitting leaf kind,
a leaf that imports a file of the PROJECT's own by a relative path, and a
rigid leaf that declines the STL-import optimization.

Modelled on
`openspec/changes/import-the-artifact-by-path/evidence/probe_cross_package.py`,
which already builds this shape with the real `machinome build` and measures
the bug (`evidence.md`).
"""

import cadquery
from molejo import Circle, Helix, P, Shape
from solid2 import cube, cylinder, import_stl

from machinome.node import CadQueryNode, MolejoNode, Solid2Node
from machinome.motion.ports import TranslationalPort


class RigidLeaf(Solid2Node):
    def render(self):
        return cube(10, 10, 10)


class ExactLeaf(CadQueryNode):
    def render(self):
        return cadquery.Workplane('XY').box(8, 8, 8)


class FlexLeaf(MolejoNode):
    height = TranslationalPort(unit='mm')

    def render(self):
        return Shape(
            profile=Circle(radius=1.0),
            path=[Helix(radius=5.0, turns=3.0, height=P.height)],
            path_samples=60,
            profile_samples=8,
        )


class OwnImportLeaf(Solid2Node):
    """A leaf whose render() imports a file of the PROJECT's own, by a
    relative path of its own meaning. Re-anchoring this would corrupt
    it -- the guard on the re-anchoring pass (design.md, "Telling a
    framework import from a project's")."""

    def render(self):
        return import_stl('vendor/external.stl')


class UnoptimizedLeaf(Solid2Node):
    """A rigid leaf that declines the STL-import optimization: no
    import is ever emitted for it, whole geometry inlined instead."""

    optimize = False

    def render(self):
        return cylinder(r=4, h=12)
