# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A faceted leaf written outside the core, presented as SCAD.

`MeshScad` takes the other faceted path the leaf contract declares: it
produces no STL of its own, declares no `materialize`, and presents its
render as SCAD through `as_scad`, which OpenSCAD turns into the STL. It
is what a node package for a SCAD-producing technology looks like, and
it is described by the core exactly as the core's own `Solid2Node` is
(the `backend-switch` change).
"""

from solid2 import cube

from machinome.node.leaf import LeafNode


class MeshScad(LeafNode):
    """A 2 mm cube presented to OpenSCAD as SCAD."""

    leaf_contract = 1

    def render(self):
        return cube(2)

    def as_scad(self, rendered):
        return rendered
