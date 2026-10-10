# Machinome

[![Build status](https://github.com/machinome/machinome/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/machinome/machinome/actions/workflows/python-app.yml)

Source code for machines. This repository holds the Machinome packages,
each in its own directory under `packages/`, named as the distribution
it builds.

| Package | What it is |
|---|---|
| [`machinome`](packages/machinome/) | The framework: a whole machine described in Python source, its parts, dimensions, joints, relations, inputs and tests. Manual: <https://machinome.readthedocs.io>. |
| [`machinome-engine-brep`](packages/machinome-engine-brep/) | The B-rep engine, `machinome.engine.brep`, on OCCT; installed by `machinome[brep]`. |
| [`machinome-engine-mesh`](packages/machinome-engine-mesh/) | The mesh engine, `machinome.engine.mesh`, on manifold3d; installed by `machinome[mesh]`. |
| [`machinome-node-cadquery`](packages/machinome-node-cadquery/) | The CadQuery node type, `machinome.node.cadquery`; installed by `machinome[cadquery]`. |
| [`machinome-node-build123d`](packages/machinome-node-build123d/) | The build123d node types and the reducer of SVG artwork, `machinome.node.build123d`; installed by `machinome[build123d]`. |
| [`machinome-node-step`](packages/machinome-node-step/) | The STEP node types, `machinome.node.step`; installed by `machinome[step]`. |
| [`machinome-node-molejo`](packages/machinome-node-molejo/) | The molejo node type, `machinome.node.molejo`; installed by `machinome[molejo]`. |
| [`machinome-node-openscad`](packages/machinome-node-openscad/) | The OpenSCAD node family, `machinome.node.openscad`, with its SCAD writer and the OpenSCAD snapshot renderer; installed by `machinome[openscad]`. |
| [`machinome-node-solid2`](packages/machinome-node-solid2/) | The SolidPython node type, `machinome.node.solid2`; installed by `machinome[solid2]`. |
| [`machinome-node-jscad`](packages/machinome-node-jscad/) | The JSCAD node type, `machinome.node.jscad`; installed by `machinome[jscad]`. |
| [`machinome-node-stl`](packages/machinome-node-stl/) | The STL node type, `machinome.node.stl`; installed by `machinome[stl]`. |

## Licence

Every package in this repository is licensed GPL-2.0-or-later or
CERN-OHL-S-2.0-or-later, at the recipient's choice; see
[LICENSE](LICENSE) and the texts in [LICENSES](LICENSES/).
[CONTRIBUTING.rst](CONTRIBUTING.rst) says how to work on them and
[AI-USE.md](AI-USE.md) how AI is used in their development.
