# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Characterization baseline for the lean-install change's markings seam.

The `Svg` artwork reducer leaves `machinome.node.markings` for
`machinome.node.build123d`, behind a seam; the marking bytes must not move.
This builds, in a temporary build directory, the marking fixtures of
`tests/test_markings.py`: the exact `Dial` (a `Wrapped` marking of
`label.svg`, whose first region carries a hole), the faceted `Plate` (the
mixin's `Flat` badge and its own `Wrapped` band), and `ScaledPlate`, the
`Plate` again carrying one more marking: a `Flat` marking of `label.svg`
with `scale`. For every marking artifact it records the SHA-256 of its
bytes; for every artwork, its closed-region count (read off the reducer's
own INFO line, which names it) and the triangle count and a SHA-256 of the
flat triangles the reduction yields. Run on the unmodified tree it wrote
`tests/data/markings_golden.json`; run with `--check` it compares
everything against that file.

    python tests/markings_golden.py [--out PATH] [--check]

Not collected by pytest (its name does not start with `test_`): green
before and after the change by design. `ScaledPlate` is declared here
rather than in the fixture package so the package the suite reads is
unchanged; a marking artifact's bytes depend on its artwork, its placement
and the tolerance, never on the module that declares it.
"""

import argparse
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import tempfile

BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)
GOLDEN = os.path.join(BASEDIR, 'data', 'markings_golden.json')

if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

#: The tolerance every artwork is reduced at here: the framework's default
#: deflection, which the faceted fixture's markings are meshed at.
_TOLERANCE = 0.1


def _sha256(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _scaled_plate():
    from machinome.node.markings import Flat, Marking, Svg
    from tests.markings_project.plate import Plate

    class ScaledPlate(Plate):
        """The plate, carrying one more marking: `label.svg` at half
        size, flat on its top face."""

        stl_source = 'markings_project/plate.stl'

        stamp = Marking(
            Svg('markings_project/label.svg', scale=0.5),
            Flat(at=(0.0, 0.0, 2.0), normal=(0, 0, 1), x_axis=(1, 0, 0)),
            color='#000000',
        )

    return ScaledPlate


def _markings(node):
    node.assemble()
    return {name: _sha256(node.marking_file(name))
            for name in node.declared_markings()}


class _Regions(logging.Handler):
    """The reducer's INFO line: '<path>: N open path(s) ignored, M closed
    region(s) read'."""

    def __init__(self):
        super().__init__(logging.INFO)
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


def _artwork(relative, scale=None):
    from machinome.node.markings import Svg
    from tests.markings_project.dial import Dial
    import numpy as np

    art = Svg(relative, scale=scale)
    art.resolve(BASEDIR, Dial, 'digits')
    handler = _Regions()
    logger = logging.getLogger('node.markings')
    level = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    try:
        vertices, triangles = art.tessellate(_TOLERANCE)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(level)
    counts = [re.search(r'(\d+) closed region', line)
              for line in handler.lines]
    digest = hashlib.sha256(
        np.ascontiguousarray(vertices, dtype=np.float64).tobytes()
        + np.ascontiguousarray(triangles, dtype=np.int64).tobytes()
    ).hexdigest()
    return {
        'regions': [int(match.group(1)) for match in counts if match],
        'triangles': int(len(triangles)),
        'vertices': int(len(vertices)),
        'triangles_sha256': digest,
    }


def measurements():
    """Every fixture's records, built under `SOLID_BUILD_DIR`."""
    from tests.markings_project.dial import Dial
    from tests.markings_project.plate import Plate
    return {
        'markings': {
            'exact_dial': _markings(Dial()),
            'faceted_plate': _markings(Plate()),
            'scaled_plate': _markings(_scaled_plate()()),
        },
        'artworks': {
            'label': _artwork('markings_project/label.svg'),
            'label_scaled': _artwork('markings_project/label.svg',
                                     scale=0.5),
            'badge': _artwork('markings_project/decals/badge.svg'),
        },
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=GOLDEN)
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='markings-golden-') as build:
        os.environ['SOLID_BUILD_DIR'] = build
        measured = measurements()
    if arguments.check:
        with open(GOLDEN) as handle:
            golden = dict(_flatten(json.load(handle)['fixtures']))
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
        json.dump({'bench_commit': _bench_commit(), 'fixtures': measured},
                  handle, indent=2, sort_keys=True)
        handle.write('\n')
    print(f'wrote {arguments.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
