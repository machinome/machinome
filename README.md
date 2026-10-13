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
| [`machinome-node-openscad`](packages/machinome-node-openscad/) | The OpenSCAD node family, `machinome.node.openscad`, with its SCAD writer; installed by `machinome[openscad]`. |
| [`machinome-node-solid2`](packages/machinome-node-solid2/) | The SolidPython node type, `machinome.node.solid2`; installed by `machinome[solid2]`. |
| [`machinome-node-jscad`](packages/machinome-node-jscad/) | The JSCAD node type, `machinome.node.jscad`; installed by `machinome[jscad]`. |
| [`machinome-node-stl`](packages/machinome-node-stl/) | The STL node type, `machinome.node.stl`; installed by `machinome[stl]`. |
| [`machinome-node-freecad`](packages/machinome-node-freecad/) | The FreeCAD node type, `machinome.node.freecad`, a native FreeCAD assembly read by FreeCAD; installed by `machinome[freecad]`. |
| [`machinome-mechanics`](packages/machinome-mechanics/) | The mechanics helpers, `machinome.mechanics`: gear, screw, crank, cam, delta, linkage, rolling and belt formulas for numeric poses and symbolic motion; installed by `machinome[mechanics]`. |
| [`machinome-viewer`](packages/machinome-viewer/) | The browser viewer, `machinome.viewer.web`: the embeddable widget, the development server and the headless capture; installed by `machinome[viewer]`. |
| [`machinome-viewer-openscad`](packages/machinome-viewer-openscad/) | The OpenSCAD viewer, `machinome.viewer.openscad`: a still drawn by the `openscad` executable; installed by `machinome[viewer-openscad]`, `machinome[openscad]` and `machinome[solid2]`. |
| [`machinome-movie`](packages/machinome-movie/) | The films, `machinome.movie` and the command `machinome movie`: a narrated film of a machine declared in Python or written as an episode, checked, voiced, previewed, rendered and served through the browser viewer; installed by `machinome[movie]`. |
| [`machinome-studio`](packages/machinome-studio/) | The studio, `machinome.studio`: the project hub and workspace where a team of agents builds a project with its maker, and the command `machinome studio`; installed by `machinome[studio]`. |
| [`machinome-skills`](packages/machinome-skills/) | The machinome skills for assistants that read Agent Skills, `machinome` and `machinome-simulate`, and the command `machinome skills` that installs them; installed by `machinome[skills]`. |

## Licence

Every package in this repository is licensed GPL-2.0-or-later or
CERN-OHL-S-2.0-or-later, at the recipient's choice; see
[LICENSE](LICENSE) and the texts in [LICENSES](LICENSES/). The Machinome
name and marks are not part of it; [TRADEMARKS.md](TRADEMARKS.md) says how
anyone may use them.
[CONTRIBUTING.rst](CONTRIBUTING.rst) says how to work on them and
[AI-USE.md](AI-USE.md) how AI is used in their development.
