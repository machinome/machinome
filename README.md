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

## Licence

Every package in this repository is licensed GPL-2.0-or-later or
CERN-OHL-S-2.0-or-later, at the recipient's choice; see
[LICENSE](LICENSE) and the texts in [LICENSES](LICENSES/).
[CONTRIBUTING.rst](CONTRIBUTING.rst) says how to work on them and
[AI-USE.md](AI-USE.md) how AI is used in their development.
