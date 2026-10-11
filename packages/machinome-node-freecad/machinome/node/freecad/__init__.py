# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The FreeCAD node type: `FreeCADAssemblyNode`, a whole native FreeCAD
assembly read by FreeCAD itself, and `FreeCADJoint`, one of its revolutes.

- `machinome.node.freecad.adapter`: the two classes, which compile the native
  assembly into ordinary nodes, joints and B-rep leaves;
- `machinome.node.freecad.runtime`: the FreeCAD runtime named by
  `MACHINOME_FREECAD_ROOT`, its worker process and the snapshot cache;
- `machinome.node.freecad.worker`: the script FreeCAD's own Python runs,
  which reads the document through FreeCAD's API.

Importing this package or declaring a class opens no document and needs no
FreeCAD runtime; constructing an instance does. The occurrences' solids are
read through `OCP`, whose absence is refused here with the line that
installs it (OpenSpec change `join-freecad`, capabilities
`native-freecad-assembly` and `kernel-extras`).
"""

from machinome.extras import require_extra

require_extra('freecad',
              'machinome.node.freecad (FreeCADAssemblyNode, FreeCADJoint)',
              'OCP')

__all__ = ['FreeCADAssemblyNode', 'FreeCADJoint']


def __getattr__(name):
    if name in __all__:
        from .adapter import FreeCADAssemblyNode, FreeCADJoint
        globals().update(FreeCADAssemblyNode=FreeCADAssemblyNode,
                         FreeCADJoint=FreeCADJoint)
        return globals()[name]
    raise AttributeError(name)
