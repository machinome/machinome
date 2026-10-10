# machinome-node-step

The STEP node types of [Machinome](https://github.com/machinome/machinome):
the module `machinome.node.step`, whose `StepNode` is one part read from a
STEP document, B-rep geometry on the framework's B-rep engine, and whose
`StepAssembly` reads the document's products and their placements, both
through CadQuery's reader. `machinome import-step` uses it to write a
project's source from a document.

## Install

    pip install "machinome[step]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
