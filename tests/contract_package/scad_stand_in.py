# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A faceted leaf written outside the core, presented as SCAD.

`MeshScad` takes the path a SCAD-producing leaf takes since `openscad-out`:
it subclasses the OpenSCAD node family's `Solid2Node`, produces no STL of its
own, and lets the family write its render as SCAD, which OpenSCAD turns into
the STL. It is what a project leaf that once overrode `as_scad` looks like
now, and the core describes it exactly as it describes `Solid2Node`.
"""

from solid2 import cube

from machinome.node.solid2 import Solid2Node


class MeshScad(Solid2Node):
    """A 2 mm cube presented to OpenSCAD as SCAD."""

    leaf_contract = 2

    def render(self):
        return cube(2)
