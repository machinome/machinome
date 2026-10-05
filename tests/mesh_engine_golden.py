# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Characterization baseline for the mesh-engine change.

The change moves every manifold3d call of the core behind the mesh engine
seam and promises that nothing it computes changes: every verdict, every
refusal's status word, every fused byte. This script records, on the
unmodified tree, what the faceted path computes, and compares a later tree
with that record.

- **Verdicts.** Every companion test of `tests/meta_project/` is run with
  `machinome test --no-verdict-store`, once on the faceted kernel and once
  on the exact one, into one temporary `SOLID_BUILD_DIR` per invocation,
  under a probe that wraps `machinome.test._memoized`, `_virtual_floor`,
  `_interface_contacts` and `_body_count`. It records each run's exit
  status, summary, per-test outcome and the first line of every exception
  it printed; every verdict the shared helper returned, in order, as
  `(path, is_empty, volume.hex())`; the SHA-256 of every virtual floor's
  vertices and faces and of every contact list, in order; and every body
  count `assertJoined` read.
- **Admission.** The refusal of a box missing one triangle, as a compared
  part and as a faceted fusion's child (`tests/mesh_engine_fixture.py`).
- **Fusion.** The SHA-256 and length of the faceted STL of the fixture's
  `Fused`, three `StlNode` children, one turned and two overlapping.
- **The `.mesh` fallback.** `(is_empty, volume.hex())` of the helper for
  pairs of `tests/test_assertions.py`'s `FakeNode`, which expose only
  `.mesh`.

    python tests/mesh_engine_golden.py --record [--out PATH]
    python tests/mesh_engine_golden.py --check

`--check` reports two differences as expected, design.md Decision 4: a
compared part's refusal saying "cannot build a solid" where it said
"cannot build a Manifold", and the fusion's saying "manifold3d reported
NotManifold" where it said "manifold3d reported Error.NotManifold".
Anything else is a difference, and the exit status is 1.

The OpenSpec change `brep-mesh` renamed the engines' words without
re-recording the data: the runs are now made with `--mesh` and `--brep`
and kept under those keys, and `--check` reads the record's former keys
and words through `BREP_MESH_EXPECTED` (the verdict path words, the mesh
run's summary note and the mesh fusion's refusal), counting each value so
read as renamed rather than different.

Not collected by pytest (its name does not start with `test_`).
"""

import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)
GOLDEN = os.path.join(BASEDIR, 'data', 'mesh_engine_golden.json')
META = os.path.join(BASEDIR, 'meta_project')

if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

#: The probe each `machinome test` child runs: the same code on both trees,
#: reading only names both trees define.
PROBE = r'''
import hashlib, json, os, sys

import numpy as np

import machinome.test as _framework

_log = open(os.environ['MESH_ENGINE_GOLDEN_LOG'], 'w')


def _write(kind, value):
    _log.write(json.dumps([kind, value]) + '\n')
    _log.flush()


def _digest(*arrays):
    digest = hashlib.sha256()
    for array in arrays:
        digest.update(np.ascontiguousarray(array).tobytes())
    return digest.hexdigest()


_memoized = _framework._memoized


def _verdict(key, compute):
    stats = _memoized(key, compute)
    _write('verdict', [None if key is None else key[2],
                       bool(stats.is_empty), float(stats.volume).hex()])
    return stats


_virtual_floor = _framework._virtual_floor


def _floor(*arguments, **keywords):
    record = _virtual_floor(*arguments, **keywords)
    mesh = _framework._placed_mesh(record[1])
    _write('floor', _digest(np.asarray(mesh.vertices, np.float64),
                            np.asarray(mesh.faces, np.int64)))
    return record


_interface_contacts = _framework._interface_contacts


def _contacts(*arguments, **keywords):
    found = list(_interface_contacts(*arguments, **keywords))
    _write('contacts', [len(found), _digest(*(
        np.asarray(value, np.float64) for pair in found for value in pair))])
    return found


_body_count = _framework._body_count


def _bodies(mesh):
    count = _body_count(mesh)
    _write('bodies', count)
    return count


_framework._memoized = _verdict
_framework._virtual_floor = _floor
_framework._interface_contacts = _contacts
_framework._body_count = _bodies

from machinome.cli import manage
manage()
'''

ANSI = re.compile(r'\x1b\[[0-9;]*m')
RESULT = re.compile(r'^Running \S+?\.(?P<name>test_\w+)')
SUMMARY = re.compile(r'Ran (\d+) tests in [\d.]+ seconds: (.*)$')
EXCEPTION = re.compile(r'^[A-Za-z_][\w.]*(Error|Exception|Unavailable|'
                       r'Incompatible): ')

#: Decision 4's two changes of wording, old to new.
EXPECTED = (('cannot build a Manifold', 'cannot build a solid'),
            ('manifold3d reported Error.', 'manifold3d reported '))

#: The `brep-mesh` change's renamed words, old to new: the verdict path
#: words, the mesh run's summary note and the mesh fusion's refusal. The
#: record's run keys `faceted` and `exact` are read as `mesh` and `brep`.
BREP_MESH_EXPECTED = (('"fac' 'eted"', '"mesh"'), ('"ex' 'act"', '"brep"'),
                      ('fac' 'eted kernel, volume epsilon',
                       'mesh engine, volume epsilon'),
                      ('fac' 'eted fusion', 'mesh fusion'))

#: The record's run keys, read as the change names them.
BREP_MESH_KEYS = {'fac' 'eted': 'mesh', 'ex' 'act': 'brep'}


def _normalize(text, build):
    return text.replace(build, '<build>').replace(REPO_DIR, '<repo>')


def _fixtures():
    for path in sorted(glob.glob(os.path.join(META, 'test_*.py'))):
        name = os.path.basename(path)[len('test_'):-len('.py')]
        if os.path.exists(os.path.join(META, f'{name}.py')):
            yield name


def _run_fixture(name, engine, build):
    with tempfile.TemporaryDirectory(prefix='mesh-engine-golden-log-') as tmp:
        log = os.path.join(tmp, 'probe.log')
        env = dict(os.environ, SOLID_BUILD_DIR=build, PYTHONPATH=REPO_DIR,
                   MESH_ENGINE_GOLDEN_LOG=log)
        env.pop('SOLID_TEST_ENGINE', None)
        completed = subprocess.run(
            [sys.executable, '-c', PROBE, 'test', f'--{engine}',
             '--no-verdict-store', f'tests/meta_project/{name}.py'],
            cwd=REPO_DIR, env=env, capture_output=True, text=True,
            timeout=900)
        events = []
        if os.path.exists(log):
            with open(log) as handle:
                events = [json.loads(line) for line in handle]
    stdout = ANSI.sub('', completed.stdout)
    entry = {'returncode': completed.returncode,
             'summary': None, 'results': {}, 'exceptions': [],
             'verdicts': [], 'floors': [], 'contacts': [], 'bodies': []}
    for line in stdout.splitlines():
        match = RESULT.match(line)
        if match:
            entry['results'][match.group('name')] = (
                'failed' if 'FAIL!' in line else 'passed')
        match = SUMMARY.search(line)
        if match:
            entry['summary'] = f'Ran {match.group(1)} tests: {match.group(2)}'
        if EXCEPTION.match(line):
            entry['exceptions'].append(_normalize(line, build))
    for line in completed.stderr.splitlines():
        if line.startswith('Error') or EXCEPTION.match(line):
            entry['exceptions'].append(_normalize(line, build))
    for kind, value in events:
        entry[{'verdict': 'verdicts', 'floor': 'floors',
               'contacts': 'contacts', 'bodies': 'bodies'}[kind]].append(value)
    return entry


def verdicts(build):
    """Every meta fixture's runs on both engines, into `build`."""
    return {engine: {name: _run_fixture(name, engine, build)
                     for name in _fixtures()}
            for engine in ('mesh', 'brep')}


class _MeshPart:
    """A topmost faceted part read through its STL alone."""

    rigid = True
    flexible = False
    brep = False
    children = ()

    def __init__(self, name, stl_file, offset=(0.0, 0.0, 0.0)):
        from machinome.node.operations import Translation
        self.name = name
        self.stl_file = stl_file
        self._parent = None
        self.operations = []
        if any(offset):
            self.operations.append(Translation(list(offset), self))

    def as_number(self, value):
        return float(value)


def _sha256(path):
    with open(path, 'rb') as handle:
        data = handle.read()
    return hashlib.sha256(data).hexdigest(), len(data)


def in_process(scratch):
    """Admission, fusion and the `.mesh` fallback, in this process."""
    os.environ['SOLID_BUILD_DIR'] = os.path.join(scratch, 'build')
    os.environ['SOLID_TEST_VERDICT_STORE'] = 'off'
    import machinome.test as framework
    from machinome.node.operations import Rotation, Translation
    from tests.mesh_engine_fixture import holey_box, write_fixture
    from tests.test_assertions import FakeNode, FarAway

    measured = {}

    holey_path = os.path.join(scratch, 'holey.stl')
    holey_box(2.0).export(holey_path)
    import trimesh
    box_path = os.path.join(scratch, 'box.stl')
    trimesh.creation.box((2, 2, 2)).export(box_path)
    try:
        framework._intersection_stats(
            _MeshPart('Holey', holey_path),
            _MeshPart('Against', box_path, (0.5, 0.0, 0.0)))
    except ValueError as error:
        measured['admission_compared'] = str(error).replace(scratch,
                                                            '<scratch>')
    else:
        measured['admission_compared'] = None

    project = os.path.join(scratch, 'project')
    os.makedirs(project)
    write_fixture(project)
    sys.path.insert(0, project)
    from mfixture import parts

    fused = parts.Fused()
    fused.assemble()
    fused.build_stls()
    digest, length = _sha256(fused.stl_file)
    measured['fusion_stl_sha256'] = digest
    measured['fusion_stl_length'] = length

    try:
        holey_fused = parts.HoleyFused()
        holey_fused.assemble()
        holey_fused.build_stls()
    except ValueError as error:
        measured['admission_fusion_child'] = str(error)
    else:
        measured['admission_fusion_child'] = None

    def translated(name, offset):
        node = FakeNode(name)
        node.operations.append(Translation(offset, node))
        return node

    def turned(name, angle):
        node = FakeNode(name)
        node.operations.append(Rotation(angle, [0, 0, 1], node))
        return node

    pairs = {
        'overlapping': (FakeNode('A'), translated('B', [0.5, 0, 0])),
        'flush': (FakeNode('A'), translated('B', [1.0, 0, 0])),
        'far': (FakeNode('A'), FarAway()),
        'turned': (FakeNode('A', size=1.5), turned('B', 45)),
        'nested': (FakeNode('A', size=3.0), translated('B', [0.25, 0, 0])),
    }
    measured['mesh_fallback'] = {}
    for label, (first, second) in pairs.items():
        stats = framework._intersection_stats(first, second)
        measured['mesh_fallback'][label] = [bool(stats.is_empty),
                                            float(stats.volume).hex()]
    return measured


def measurements():
    with tempfile.TemporaryDirectory(prefix='mesh-engine-golden-') as scratch:
        build = os.path.join(scratch, 'meta-build')
        os.makedirs(build)
        measured = in_process(scratch)
        measured['verdicts'] = verdicts(build)
    return measured


def _leaves(value, path=()):
    if isinstance(value, dict):
        for key in sorted(value):
            yield from _leaves(value[key], path + (str(key),))
    elif isinstance(value, list) and any(
            isinstance(item, (dict, list)) for item in value):
        for index, item in enumerate(value):
            yield from _leaves(item, path + (str(index),))
        yield path + ('#',), len(value)
    else:
        yield path, value


def _expected(old, new, table=EXPECTED):
    if not (isinstance(old, (str, list)) and isinstance(new, type(old))):
        return False
    text = json.dumps(old)
    for before, after in table:
        text = text.replace(before, after)
    return text == json.dumps(new)


def _renamed_path(path):
    """A recorded path with its run key read as `brep-mesh` names it."""
    if len(path) > 1 and path[0] == 'verdicts':
        return (path[0], BREP_MESH_KEYS.get(path[1], path[1])) + path[2:]
    return path


def compare(golden, measured):
    old = {_renamed_path(path): value
           for path, value in _leaves(golden)}
    new = dict(_leaves(measured))
    differences, expected, renamed = [], [], []
    for path in sorted(set(old) | set(new)):
        before, after = old.get(path, '<absent>'), new.get(path, '<absent>')
        if before == after:
            continue
        if _expected(before, after):
            expected.append((path, before, after))
        elif _expected(before, after, BREP_MESH_EXPECTED):
            renamed.append((path, before, after))
        elif _expected(before, after, EXPECTED + BREP_MESH_EXPECTED):
            expected.append((path, before, after))
        else:
            differences.append((path, before, after))
    return len(set(old) | set(new)), differences, expected, renamed


def _bench_commit():
    return subprocess.run(['git', '-C', REPO_DIR, 'rev-parse', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--record', action='store_true')
    action.add_argument('--check', action='store_true')
    parser.add_argument('--out', default=GOLDEN)
    arguments = parser.parse_args()
    measured = measurements()
    if arguments.check:
        with open(GOLDEN) as handle:
            golden = json.load(handle)['values']
        count, differences, expected, renamed = compare(golden, measured)
        for path, before, after in expected:
            print('EXPECTED: %s golden=%r now=%r'
                  % ('.'.join(path), before, after))
        for path, before, after in differences:
            print('DIFFERS: %s golden=%r now=%r'
                  % ('.'.join(path), before, after))
        print('golden comparison: %d values, %d differences, %d expected '
              '(design.md Decision 4), %d renamed (brep-mesh)'
              % (count, len(differences), len(expected), len(renamed)))
        return 1 if differences else 0
    with open(arguments.out, 'w') as handle:
        json.dump({'bench_commit': _bench_commit(), 'values': measured},
                  handle, indent=1, sort_keys=True)
        handle.write('\n')
    count = len(dict(_leaves(measured)))
    print(f'wrote {arguments.out}: {count} values')
    return 0


if __name__ == '__main__':
    sys.exit(main())
