# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Characterization baseline for the expression-type change.

Builds `tests/expression_type_project/machine.py`'s `SharedMotion` -- an
assembly whose operations carry animation time and one driver through
`machinome.math`, with a subexpression shared between them so the compact
closed text carries a `let`, and one flexible leaf whose port is fed from
the same values -- in a temporary build directory, and records the SHA-256
and length of:

- every operation's standalone `Operation.serialized` text, per node, read
  in symbolic driver mode (`symbolic_document`), where time and the driver
  are both symbolic;
- `scad_code` of the assembly and of each child, in the same mode;
- the published document `export_node` writes (`manifest.json`), as JSON
  with sorted keys, without the two fields that name the checkout rather
  than the model -- every node's `mtime` and the document's `source` --
  and, beside it, its `bindings` table and its `version`.

Run on the unmodified tree it wrote `tests/data/expression_type_golden.json`;
run with `--check` it compares everything against that file. The SCAD text
and the published document are what must not move when the symbolic value
becomes the core's own type (OpenSpec change `expression-type`).

    python tests/expression_type_golden.py [--out PATH] [--check]

Not collected by pytest (its name does not start with `test_`): green
before and after the change by design. Its fixture lives in a project
package, never in this file; importing this module builds nothing and sets
no environment.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile

BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)
GOLDEN = os.path.join(BASEDIR, 'data', 'expression_type_golden.json')

if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

#: Document fields that name the checkout or the file system, not the model.
_CHECKOUT_FIELDS = ('mtime', 'source')


def _digest(text):
    data = text.encode('utf-8')
    return {'sha256': hashlib.sha256(data).hexdigest(), 'length': len(data)}


def _without_checkout(value):
    if isinstance(value, dict):
        return {key: _without_checkout(item) for key, item in value.items()
                if key not in _CHECKOUT_FIELDS}
    if isinstance(value, list):
        return [_without_checkout(item) for item in value]
    return value


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def _machine():
    from machinome.simulation.enumeration import bind_declared_defaults
    from tests.expression_type_project.machine import SharedMotion
    node = SharedMotion()
    bind_declared_defaults(node)
    return node


def scad_code(node):
    """A node's SCAD text: a family leaf's own, any other node's through
    the OpenSCAD writer (`openscad-out`, task 6.5)."""
    from machinome.node.openscad import writer
    from machinome.node.openscad.leaf import ScadLeafNode
    if isinstance(node, ScadLeafNode):
        return node.scad_code
    return writer.scad_code(node)


def _symbolic():
    """Each node's operation texts and SCAD, in symbolic driver mode."""
    from machinome.core.serializer import symbolic_document
    node = _machine()
    operations, scad = {}, {}
    with symbolic_document(node):
        for each in (node, node.arm, node.slider, node.coil):
            operations[each.name] = [
                _digest(json.dumps(operation.serialized))
                for operation in each.operations]
            scad[each.name] = _digest(scad_code(each))
    return operations, scad


def _document():
    from machinome.core.export import export_node
    with tempfile.TemporaryDirectory(prefix='expression-type-export-') as out:
        export_node(_machine(), out, widget=False)
        with open(os.path.join(out, 'manifest.json')) as handle:
            document = json.load(handle)
    return {
        'document': _digest(_canonical(_without_checkout(document))),
        'bindings': _digest(_canonical(document['bindings'])),
        'version': document['version'],
    }


def measurements():
    """Every value this golden pins, built under `SOLID_BUILD_DIR`."""
    operations, scad = _symbolic()
    return {'operations': operations, 'scad_code': scad,
            'published': _document()}


def _bench_commit():
    return subprocess.run(['git', '-C', REPO_DIR, 'rev-parse', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()


def _flatten(value, prefix=''):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _flatten(item, f'{prefix}.{key}' if prefix else key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _flatten(item, f'{prefix}[{index}]')
    else:
        yield prefix, value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=GOLDEN)
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='expression-type-golden-') as build:
        os.environ['SOLID_BUILD_DIR'] = build
        measured = measurements()
    if arguments.check:
        with open(GOLDEN) as handle:
            golden = dict(_flatten(json.load(handle)['fixture']))
        now = dict(_flatten(measured))
        differences = [(key, golden.get(key), now.get(key))
                       for key in sorted(set(golden) | set(now))
                       if golden.get(key) != now.get(key)]
        for difference in differences:
            print('DIFFERS: %s golden=%r now=%r' % difference)
        print('golden comparison: %d values, %d differences'
              % (len(now), len(differences)))
        return 1 if differences else 0
    with open(arguments.out, 'w') as handle:
        json.dump({'bench_commit': _bench_commit(), 'fixture': measured},
                  handle, indent=2, sort_keys=True)
        handle.write('\n')
    print(f'wrote {arguments.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
