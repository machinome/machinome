# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Characterization baseline for the scad-presentation change.

Builds `tests/scad_presentation_project/tools/bench.py`'s `Bench` -- a root
in package `tools` placing, across packages, a coloured single-child
assembly, an empty assembly, an `optimize = False` assembly inlining
authored geometry, a `Solid2Node` declaring `fn`, an `StlNode`, an exact
leaf on a symbolic rotation, a faceted `FusionNode`, a numerically bound
flexible leaf, an `OpenScadNode` and a project leaf overriding `as_scad` --
in a temporary build directory: assembled, every STL job run, then
assembled once more with every artifact current, as
`tests/test_scad_import_paths.py` builds its fixtures. `Loose`, whose one
part imports a file of the project's own by a relative path, is assembled
beside it and never built to STL. It records the SHA-256 and length of:

- every node's `scad_code`, by its path of names in the tree;
- every `.scad` file under the build directory after that last
  `assemble()`, by its path relative to the build directory, each marked
  with whether the node that writes it is SCAD-authored (a `Solid2Node`, an
  `OpenScadNode`, or a leaf overriding `as_scad`).

Run on the unmodified tree it wrote `tests/data/scad_presentation_golden.json`;
run with `--check` it compares against that file. Every `scad_code` and
every SCAD-authored leaf's file must be present and byte-identical. A file
of a node that is not SCAD-authored must be byte-identical when present;
absent, it is reported as expected, because after the change nothing
writes it (design.md, Decision 3). A `.scad` the golden does not record is
a difference.

    python tests/scad_presentation_golden.py [--out PATH] [--check]

Not collected by pytest (its name does not start with `test_`): green
before and after the change by design. Importing this module builds
nothing and sets no environment.
"""

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
import tempfile

BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)
GOLDEN = os.path.join(BASEDIR, 'data', 'scad_presentation_golden.json')

if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)


def _digest(text):
    data = text.encode('utf-8') if isinstance(text, str) else text
    return {'sha256': hashlib.sha256(data).hexdigest(), 'length': len(data)}


def _forget_assembly(node):
    node._assembled = False
    for child in node.children:
        _forget_assembly(child)


def _build_stl(node):
    from machinome.node import StlRenderStart
    for _ in range(20):
        try:
            node.trigger_stl()
        except StlRenderStart as job:
            job.wait()
        else:
            return
    raise AssertionError(f'{node} never finished triggering STL jobs')


def _walk(node, prefix=''):
    path = f'{prefix}/{node.name}' if prefix else node.name
    yield path, node
    for child in node.children:
        yield from _walk(child, path)


def scad_code(node):
    """A node's SCAD text: a family leaf's own (`OpenScadNode` composes it
    with its source), any other node's through the OpenSCAD writer
    (`openscad-out`, task 6.5)."""
    from machinome.node.openscad import writer
    from machinome.node.openscad.leaf import ScadLeafNode
    if isinstance(node, ScadLeafNode):
        return node.scad_code
    return writer.scad_code(node)


def scad_authored(node):
    """Whether the node's geometry is authored in SCAD, read without the
    change's own predicate so the golden answers the same before it."""
    from machinome.node.openscad import OpenScadNode
    from machinome.node.solid2 import Solid2Node
    if isinstance(node, (Solid2Node, OpenScadNode)):
        return True
    legacy = getattr(node, '_uses_legacy_scad_materialization', None)
    return bool(legacy and not node.children and legacy())


def measurements(build_dir):
    """Every value this golden pins, built under `build_dir`."""
    from tests.scad_presentation_project.tools.bench import Bench, Loose
    bench = Bench()
    bench.assemble()
    _build_stl(bench)
    _forget_assembly(bench)
    bench.assemble()
    loose = Loose()
    loose.assemble()

    nodes = dict(_walk(bench))
    nodes.update(_walk(loose))
    authored = {}
    for node in nodes.values():
        from machinome.node.openscad import writer
        relative = os.path.relpath(writer.scad_file(node), build_dir)
        authored[relative] = authored.get(relative, False) or scad_authored(
            node)

    files = {}
    for path in sorted(glob.glob(os.path.join(build_dir, '**', '*.scad'),
                                 recursive=True)):
        relative = os.path.relpath(path, build_dir)
        with open(path, 'rb') as handle:
            entry = _digest(handle.read())
        entry['scad_authored'] = authored.get(relative, False)
        files[relative] = entry

    scad = {path: _digest(scad_code(node)) for path, node in nodes.items()}
    return {'scad_code': scad, 'files': files}


def _bench_commit():
    return subprocess.run(['git', '-C', REPO_DIR, 'rev-parse', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()


def compare(golden, now):
    """`(differences, expected_absent)`: every difference as a line, and
    the recorded presentation files now absent as Decision 3 expects."""
    differences, absent = [], []
    for path in sorted(set(golden['scad_code']) | set(now['scad_code'])):
        if golden['scad_code'].get(path) != now['scad_code'].get(path):
            differences.append(
                f'scad_code {path}: golden={golden["scad_code"].get(path)!r} '
                f'now={now["scad_code"].get(path)!r}')
    for path in sorted(set(golden['files']) | set(now['files'])):
        recorded, present = golden['files'].get(path), now['files'].get(path)
        if recorded is None:
            differences.append(f'file {path}: not recorded, now {present!r}')
        elif present is None:
            if recorded['scad_authored']:
                differences.append(
                    f'file {path}: SCAD-authored, recorded, now absent')
            else:
                absent.append(path)
        elif present != recorded:
            differences.append(
                f'file {path}: golden={recorded!r} now={present!r}')
    return differences, absent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=GOLDEN)
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='scad-presentation-golden-') as build:
        os.environ['SOLID_BUILD_DIR'] = build
        measured = measurements(build)
    if arguments.check:
        with open(GOLDEN) as handle:
            golden = json.load(handle)['fixture']
        differences, absent = compare(golden, measured)
        for difference in differences:
            print(f'DIFFERS: {difference}')
        for path in absent:
            print(f'ABSENT (expected, not SCAD-authored): {path}')
        values = len(measured['scad_code']) + len(golden['files'])
        print('golden comparison: %d values, %d differences, '
              '%d presentation files absent as expected'
              % (values, len(differences), len(absent)))
        return 1 if differences else 0
    with open(arguments.out, 'w') as handle:
        json.dump({'bench_commit': _bench_commit(), 'fixture': measured},
                  handle, indent=2, sort_keys=True)
        handle.write('\n')
    print(f'wrote {arguments.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
