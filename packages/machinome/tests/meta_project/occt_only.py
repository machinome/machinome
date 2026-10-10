# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A project whose exact leaves render the kernel's own shape.

The stand-in for the originating caller of the `exact-engine` change:
machinome-freecad's exact leaf reads a FreeCAD BREP into a bare
`TopoDS_Shape` with `BRepTools.Read_s` and, before this change, had to
import cadquery only to cast it. Here `Pin` reads its BREP bytes exactly
that way, and the blocks are made with `BRepPrimAPI_MakeBox`; every leaf
declares `namespace = 'OCP'` and returns the bare shape, with no override
of the framework's conversion. Nothing in this project imports a CAD
front end.
"""

import io

from OCP.BRep import BRep_Builder
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

from machinome.node.assembly import AssemblyNode
from machinome.node.fusion import FusionNode
from machinome.node.brep_leaf import BrepLeafNode


def _brep_bytes(shape):
    stream = io.BytesIO()
    BRepTools.Write_s(shape, stream)
    return stream.getvalue()


#: A pin of radius 3 from z = -5 to z = 15, as BREP bytes: what a native
#: transfer hands an adapter.
PIN_BREP = _brep_bytes(BRepPrimAPI_MakeCylinder(
    gp_Ax2(gp_Pnt(0, 0, -5), gp_Dir(0, 0, 1)), 3, 20).Shape())


def _box(corner, size):
    return BRepPrimAPI_MakeBox(gp_Pnt(*corner), *size).Shape()


class Block(BrepLeafNode):

    namespace = 'OCP'

    def render(self):
        return _box((-10, -10, 0), (20, 20, 10))


class Pin(BrepLeafNode):

    namespace = 'OCP'

    def render(self):
        shape = TopoDS_Shape()
        BRepTools.Read_s(shape, io.BytesIO(PIN_BREP), BRep_Builder())
        return shape


class PinnedBlock(FusionNode):

    def __init__(self):
        self.block = Block()
        self.pin = Pin()
        super().__init__()

    def render(self):
        return [self.block, self.pin]


class Probe(BrepLeafNode):
    """Overlaps the block on a 5 mm cube: 125 mm^3."""

    namespace = 'OCP'

    def render(self):
        return _box((5, 5, 5), (10, 10, 10))


class Far(BrepLeafNode):
    """Clear of everything."""

    namespace = 'OCP'

    def render(self):
        return _box((40, 0, 0), (5, 5, 5))


class OcctOnly(AssemblyNode):

    def __init__(self):
        self.pinned_block = PinnedBlock()
        self.probe = Probe()
        self.far = Far()
        super().__init__()

    def render(self):
        return [self.pinned_block, self.probe, self.far]
