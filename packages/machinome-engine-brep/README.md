# machinome-engine-brep

The B-rep engine of [Machinome](https://github.com/machinome/machinome): the
module `machinome.engine.brep`, which reads, places, fuses, intersects,
measures and writes boundary-representation shapes on the OCCT kernel,
through its Python binding OCP. The framework resolves it when a part has
B-rep geometry.

## Install

    pip install "machinome[brep]"

The extras of the node types built on OCCT (`cadquery`, `build123d`, `step`
and `molejo`) install it too.

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
