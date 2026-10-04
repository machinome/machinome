# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The parts of the SCAD presentation golden (`tests/scad_presentation_golden.py`,
OpenSpec change `scad-presentation`): one per construct the SCAD
presentation carries that the expression golden does not -- a colour on a
leaf, `fn`, inlined authored geometry, an imported STL, an exact leaf, a
faceted fusion's fused artifact, a numerically bound flexible leaf, an
OpenSCAD module, a project leaf overriding `as_scad` and a project's own
`import_stl` -- and the small assemblies that place them, declared in this
package so that the root, in `tools/`, places them across packages.
"""

import cadquery
from molejo import Circle, Helix, P, Shape
from solid2 import cube, cylinder, import_stl, sphere

from machinome.motion.ports import TranslationalPort
from machinome.node import (AssemblyNode, CadQueryNode, FusionNode,
                            MolejoNode, OpenScadNode, Solid2Node, StlNode)
from machinome.node.leaf import LeafNode


class ColouredCube(Solid2Node):
    """A coloured leaf: the colour wraps its import in the parent."""

    color = '#ff8000'

    def render(self):
        return cube(6, center=True)


class FineCylinder(Solid2Node):
    """A leaf declaring `fn`: its own `.scad` begins with `$fn`."""

    fn = 24

    def render(self):
        return cylinder(r=3, h=8)


class InlineCylinder(Solid2Node):
    """A leaf that declines the STL import: its authored geometry is
    inlined, coloured, wherever it is presented."""

    optimize = False
    color = '#00a0ff'

    def render(self):
        return cylinder(r=2, h=5)


class OwnImport(Solid2Node):
    """A leaf whose render imports a file of the project's own by a
    relative path, which no presentation may re-anchor."""

    def render(self):
        return cube(1) + import_stl('vendor/external.stl')


class Bracket(StlNode):
    """An imported STL part."""

    stl_source = 'bracket.stl'


class Block(CadQueryNode):
    """An exact part."""

    def render(self):
        return cadquery.Workplane('XY').box(8, 8, 8)


class Lug(Solid2Node):
    def render(self):
        return cube([4, 4, 4])


class Boss(Solid2Node):
    def render(self):
        return sphere(r=3)


class Fused(FusionNode):
    """A faceted fusion of two SCAD-authored parts, presented by the
    import of its fused artifact once that is current."""

    def render(self):
        return [Lug(), Boss().translate([2, 2, 2])]


class Coil(MolejoNode):
    """A flexible part, numerically bound by its parent."""

    height = TranslationalPort(unit='mm')

    def render(self):
        return Shape(
            profile=Circle(radius=0.5),
            path=[Helix(radius=3.0, turns=2.0, height=P.height)],
            path_samples=40,
            profile_samples=6,
        )


class Plate(OpenScadNode):
    """A part whose geometry is an OpenSCAD module."""

    scad_source = 'plate.scad'


class Legacy(LeafNode):
    """A project leaf overriding `as_scad`: the legacy SCAD-only seam,
    whose STL OpenSCAD renders from the SCAD it returns."""

    namespace = 'solid2'

    def render(self):
        return cube([3, 5, 7])

    def as_scad(self, rendered):
        return rendered


class Single(AssemblyNode):
    """A coloured assembly of one child."""

    color = '#3366cc'

    def render(self):
        return [ColouredCube()]


class Empty(AssemblyNode):
    """A non-rigid assembly with no present part."""

    def render(self):
        return []


class Unoptimized(AssemblyNode):
    """An assembly declining optimization, inlining authored geometry."""

    optimize = False

    def render(self):
        return [InlineCylinder().translate([0, 0, 3])]
