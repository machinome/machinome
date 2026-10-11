# machinome-node-freecad

The FreeCAD node type of [Machinome](https://github.com/machinome/machinome):
the package `machinome.node.freecad`, whose `FreeCADAssemblyNode` is a whole
native [FreeCAD](https://www.freecad.org) assembly, read by FreeCAD itself in
a separate process with its fixed and revolute joints and their enabled
limits, and whose `FreeCADJoint` names one of its revolutes for a driver.
FreeCAD is installed apart and found through `MACHINOME_FREECAD_ROOT`.

## Install

    pip install "machinome[freecad]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
