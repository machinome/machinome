# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Export the control fixtures the browser viewer reads.

The framework owns the `controls` table and the viewer owns the gesture;
between them sits a document, and a viewer-only fixture would let the
two drift without either repository noticing. So the documents the
viewer's reader and pointer tests read are PRODUCED HERE, by the
framework's own export, from the same machines `tests/test_controls.py`
and `tests/test_running_document.py` hold the producer to. Nothing in
this repository consumes them and nothing in the viewer regenerates
them: the handoff is the exported directory plus the framework content
commit it came from, recorded in the consumer's own evidence.

Five machines, chosen so every shape the `direct-part-motion` change
states is exported once:

  * `columns` -- the LEGACY shape: two inferred rotational turns and two
    buttons, no `operation_span` anywhere. A viewer that has learnt to
    read spans must still read this one exactly as it did before.
  * `selector` -- one prismatic joint: a `Slide`, and a `Button` on the
    same sliding part. Both carry a span, because a translation moves
    the point a gesture is measured from.
  * `crank` -- ONE body, two freedoms: a `Turn` and a `Button` on an
    off-centre rotational joint and a `Slide` on the prismatic one that
    carries it, each naming the coordinate it means. The two spans are
    different blocks of one node's operations.
  * `tilted` -- two NON-PARALLEL joints on one body, under an ancestor
    that places it: the case a frame taken from the whole body's world
    matrix gets wrong, because the inner rotation would turn the outer
    joint's line.
  * `register` -- a knob under a jointed child of a carriage, whose
    `Slide` selects the CARRIAGE's travel: a coordinate no walk up the
    tree would ever reach, since a nearer joint stands between.

Run from the framework worktree root, with the workspace environment::

    PYTHONPATH="$PWD" python tools/generate_control_fixtures.py \\
        --output <directory>

Each machine gets `<directory>/<name>/`, holding `manifest.json` and a
`models/` tree. The geometry is the test fixtures' own cubes and
cylinders, which is all a pick and a world matrix need.
"""

import argparse
import json
import os
import sys


# The machines, by the name their fixture directory takes. Imported
# lazily inside `main`, because importing the test package pulls the
# whole CAD stack and `--help` should not.
FIXTURES = (
    ('columns', 'Columns'),
    ('selector', 'Selector'),
    ('crank', 'Crank'),
    ('tilted', 'Tilted'),
    ('register', 'Register'),
)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split('\n\n')[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--output', required=True,
        help='directory to write one subdirectory per fixture into')
    arguments = parser.parse_args(argv)

    from machinome.core.export import export_node
    from machinome.simulation.enumeration import bind_declared_defaults
    from tests.running_project import machine

    os.makedirs(arguments.output, exist_ok=True)
    for name, class_name in FIXTURES:
        node = getattr(machine, class_name)()
        bind_declared_defaults(node)
        target = os.path.join(arguments.output, name)
        export_node(node, target, widget=False)
        with open(os.path.join(target, 'manifest.json')) as handle:
            document = json.load(handle)
        controls = document.get('controls', {})
        spans = sum(1 for entry in controls.values()
                    if 'operation_span' in entry)
        print(f'{name}: {class_name}, version {document["version"]}, '
              f'{len(controls)} controls, {spans} with a span -> {target}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
