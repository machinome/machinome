# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""One part per faceted leaf kind the leaf-contract golden pins."""

from solid2 import cube, cylinder

from machinome.node import JScadNode, OpenScadNode, Solid2Node


class Washer(Solid2Node):
    """A solid2 part: a square washer with a round bore."""

    def render(self):
        return cube([12, 12, 2], center=True) - cylinder(r=3, h=4,
                                                         center=True)


class Block(OpenScadNode):
    """A part whose geometry is an OpenSCAD module."""

    scad_source = 'block.scad'


class JsBlock(JScadNode):
    """A part whose geometry is a JSCAD script."""

    jscad_source = 'block.js'
