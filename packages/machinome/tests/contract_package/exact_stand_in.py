# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""An exact leaf written outside the core: machinome-freecad's shape.

`NativeSolid` reads BREP bytes into a bare `TopoDS_Shape` with
`BRepTools.Read_s`, exactly as machinome-freecad reads the BREP its
FreeCAD worker transferred, and returns it as it is: the exact engine's
currency, with no CAD front end imported and no `namespace` declared.

Which bytes it reads is decided by `RECIPE`, the stand-in for the
adapter's native recipe -- a digest of what FreeCAD made of the document,
which can change while no tracked file does. The node states it through
`source_recipe`, the declared member, so the core folds it into the
currency of every artifact the node publishes.
"""

import io

from OCP.BRep import BRep_Builder
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

from machinome.node.brep_leaf import BrepLeafNode


def _pin_brep(radius):
    """A pin of `radius` from z = -5 to z = 15, as BREP bytes: what a
    native transfer hands an adapter."""
    stream = io.BytesIO()
    BRepTools.Write_s(BRepPrimAPI_MakeCylinder(
        gp_Ax2(gp_Pnt(0, 0, -5), gp_Dir(0, 0, 1)), radius, 20).Shape(),
        stream)
    return stream.getvalue()


#: The native transfers this stand-in can be handed, by recipe.
NATIVE_BREPS = {
    'native-v1': _pin_brep(3),
    'native-v2': _pin_brep(4),
}

#: What decides the native geometry beyond the tracked files. Changed
#: in memory by the tests, never on disk, so no tracked file moves.
RECIPE = 'native-v1'


class NativeSolid(BrepLeafNode):
    """A solid whose geometry a native tool produced."""

    leaf_contract = 3

    @property
    def source_recipe(self):
        return RECIPE

    def render(self):
        shape = TopoDS_Shape()
        BRepTools.Read_s(shape, io.BytesIO(NATIVE_BREPS[RECIPE]),
                         BRep_Builder())
        return shape


class IntSolid(NativeSolid):
    """A broken native transfer: something the engine does not admit."""

    def render(self):
        return 5
