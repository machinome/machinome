# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Optional native FreeCAD assembly adapter. Native loading is point-of-use."""
__all__ = ['FreeCADAssemblyNode', 'FreeCADJoint']

def __getattr__(name):
    if name in __all__:
        from .adapter import FreeCADAssemblyNode, FreeCADJoint
        globals().update(FreeCADAssemblyNode=FreeCADAssemblyNode,
                         FreeCADJoint=FreeCADJoint)
        return globals()[name]
    raise AttributeError(name)
