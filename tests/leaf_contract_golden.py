# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Characterization baseline for the leaf-contract change.

Builds one leaf of every kind whose publication the change touches, in a
temporary build directory: an `StlNode` carrying two markings, a
`CadQueryNode` carrying one (the exact leaf with a marking), a
`Build123dSheetNode` panel (its `.dxf`), a `MolejoNode` snapshot at one
binding, a `Solid2Node`, an `OpenScadNode` and, when `jscad` is on the
PATH, a `JScadNode`. For every artifact a node owns it records the SHA-256
of its bytes, the digest and record version of its source record, whether
the recorded fingerprint equals the node's own source fingerprint in the
same run, and whether the stamp equals the node's `mtime_ns`; for every
node its `uniq_id`. A `.dxf` is the one artifact whose bytes are not
reproducible -- ezdxf writes the clock, fresh GUIDs and a hash-ordered
OBJECTS section into every file -- so its digest is `entities_sha256`,
over the ENTITIES section that holds the cut geometry (`_dxf_entities`). Run on the unmodified tree it wrote
`tests/data/leaf_contract_golden.json`; run with `--check` it compares
everything against that file, reading the fields a later change was
expected to move through its table (`ROOT_CLEANUP_EXPECTED`) and counting
each such value as expected rather than different.

    python tests/leaf_contract_golden.py [--out PATH] [--check]

Not collected by pytest (its name does not start with `test_`): green
before and after the change by design. Its fixtures live in project
packages, never in this file, so the digests do not depend on this
script's bytes; importing this module builds nothing and sets no
environment.
"""

import argparse
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)
GOLDEN = os.path.join(BASEDIR, 'data', 'leaf_contract_golden.json')

if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

from machinome import currency  # noqa: E402

#: Files beside an artifact that are not artifacts of their own.
_NOT_ARTIFACTS = (currency.SIDECAR_SUFFIX, '.lock', '.tmp')

#: The fields OpenSpec change `root-cleanup` expects to differ (design.md
#: Decision 9): the `digest` of every artifact's source record. Each
#: fixture's package imported its node classes from the node root, and the
#: import line is part of the digested source, so repointing it to the
#: module moves the digest and nothing else -- no artifact byte
#: (`sha256`, `entities_sha256`), record version, `uniq_id` or match flag.
#: A value read through this table must be a digest before and after.
ROOT_CLEANUP_EXPECTED = ('digest',)


def _sha256(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _dxf_entities(path):
    """The SHA-256 of a DXF's ENTITIES section, the geometry it cuts.

    A DXF is a sequence of (group code, value) line pairs. Outside the
    ENTITIES section ezdxf writes the clock ($TDCREATE, $TDUPDATE, its
    `<version> @ <UTC time>` stamps), two fresh GUIDs, and an OBJECTS
    section whose order follows Python's hash seed, so the file's bytes
    differ on every write; the section holding the cut geometry does
    not, and it is digested exactly as written.
    """
    with open(path, encoding='utf-8', errors='surrogateescape') as handle:
        lines = handle.read().splitlines()
    pairs = [(lines[index].strip(), lines[index + 1].strip())
             for index in range(0, len(lines) - 1, 2)]
    start = pairs.index(('2', 'ENTITIES'))
    end = pairs.index(('0', 'ENDSEC'), start)
    return hashlib.sha256('\n'.join(
        f'{code}\n{value}' for code, value in pairs[start:end]).encode(
            'utf-8', 'surrogateescape')).hexdigest()


def _record(path):
    """The artifact's source record: `(version, digest, fingerprint)`."""
    try:
        with open(currency.sidecar(path)) as handle:
            content = handle.read().strip()
    except OSError:
        return None, None, None
    if not content.startswith('{'):
        return 'legacy', content, None
    record = json.loads(content)
    return record.get('version'), record.get('digest'), record.get(
        'fingerprint')


def _sources_of(node, path):
    """The tracked set an artifact of `node` is recorded over."""
    for name, marking in node.declared_markings().items():
        if node.marking_file(name) == path:
            return node.marking_sources(marking)
    return node.files


def _artifacts(node):
    """Every artifact file `node` owns in the build directory."""
    return sorted(
        path for path in glob.glob(f'{glob.escape(node.basepath)}*')
        if not path.endswith(_NOT_ARTIFACTS)
        and not os.path.basename(path).startswith('.'))


def _entry(node):
    artifacts = {}
    for path in _artifacts(node):
        sources = _sources_of(node, path)
        version, digest, fingerprint = _record(path)
        digest_field = ('entities_sha256', _dxf_entities) \
            if path.endswith('.dxf') else ('sha256', _sha256)
        artifacts[path[len(node.basepath):]] = {
            digest_field[0]: digest_field[1](path),
            'record_version': version,
            'digest': digest,
            'fingerprint_matches':
                fingerprint == node._tracked_fingerprint(sources),
            'stamp_matches':
                os.stat(path).st_mtime_ns == node._tracked_mtime_ns(sources),
        }
    return {'uniq_id': node.uniq_id, 'artifacts': artifacts}


def _assembled(node):
    node.assemble()
    return _entry(node)


def _built(node):
    node.assemble()
    node.build_stls()
    return _entry(node)


def _stl_with_markings():
    from tests.markings_project.plate import Plate
    return _assembled(Plate())


def _exact_with_marking():
    from tests.markings_project.dial import Dial
    return _assembled(Dial())


def _sheet_panel():
    from tests.sheet_project.frame_panel import FramePanel
    return _assembled(FramePanel())


def _molejo_snapshot():
    from tests.flexible_project.spring import Valvetrain
    machine = Valvetrain()
    machine.set_state(lift=4.0)
    machine.assemble()
    return _entry(machine.spring)


def _solid2():
    from tests.leaf_contract_project.parts import Washer
    return _built(Washer())


def _openscad():
    from tests.leaf_contract_project.parts import Block
    return _built(Block())


def _jscad():
    if shutil.which('jscad') is None:
        return {'skipped': 'jscad is not on the PATH'}
    from tests.leaf_contract_project.parts import JsBlock
    return _assembled(JsBlock())


def measurements():
    """Every fixture's records, built under `SOLID_BUILD_DIR`."""
    return {
        'stl_node_with_markings': _stl_with_markings(),
        'exact_leaf_with_marking': _exact_with_marking(),
        'build123d_sheet_panel': _sheet_panel(),
        'molejo_snapshot': _molejo_snapshot(),
        'solid2_node': _solid2(),
        'openscad_node': _openscad(),
        'jscad_node': _jscad(),
    }


def _bench_commit():
    return subprocess.run(['git', '-C', REPO_DIR, 'rev-parse', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()


def _flatten(value, prefix=''):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _flatten(item, f'{prefix}.{key}' if prefix else key)
    else:
        yield prefix, value


def _expected(key, before, after):
    """Whether a difference at flattened `key` is one `root-cleanup`
    expects: a source record's digest, a digest on both sides."""
    return (key.rpartition('.')[2] in ROOT_CLEANUP_EXPECTED
            and isinstance(before, str) and isinstance(after, str))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=GOLDEN)
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='leaf-contract-golden-') as build:
        os.environ['SOLID_BUILD_DIR'] = build
        measured = measurements()
    if arguments.check:
        with open(GOLDEN) as handle:
            golden = dict(_flatten(json.load(handle)['fixtures']))
        now = dict(_flatten(measured))
        changed = [(key, golden.get(key), now.get(key))
                   for key in sorted(set(golden) | set(now))
                   if golden.get(key) != now.get(key)]
        expected = [change for change in changed if _expected(*change)]
        differences = [change for change in changed
                       if not _expected(*change)]
        for change in expected:
            print('EXPECTED: %s golden=%r now=%r' % change)
        for difference in differences:
            print('DIFFERS: %s golden=%r now=%r' % difference)
        print('golden comparison: %d fixtures, %d values, %d differences, '
              '%d expected (root-cleanup: source digests)'
              % (len(measured), len(now), len(differences), len(expected)))
        return 1 if differences else 0
    with open(arguments.out, 'w') as handle:
        json.dump({'bench_commit': _bench_commit(), 'fixtures': measured},
                  handle, indent=2, sort_keys=True)
        handle.write('\n')
    print(f'wrote {arguments.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
