# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Characterization baseline for the exact-engine change.

Builds seven exact fixtures in a temporary build directory and records,
for each, the SHA-256 of its `.brep` and `.stl`, its volume and solid
count, its optimal bounding box and the SHA-256 of its per-face box
array. Run on the unmodified tree it wrote `tests/data/
exact_engine_golden.json`; run on the rewritten tree with `--check` it
compares every digest and measurement against that file.

    python tests/exact_engine_golden.py [--out PATH] [--check]

Not collected by pytest (its name does not start with `test_`): it is a
script, green before and after the change by design. Its fixture classes
are imported by `tests/test_exact_currency.py`; importing this module
builds nothing and sets no environment.
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
GOLDEN = os.path.join(BASEDIR, 'data', 'exact_engine_golden.json')

if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)

import build123d as b3d  # noqa: E402
import cadquery as cq  # noqa: E402
from OCP.BRepTools import BRepTools  # noqa: E402

from machinome.node import (Build123dNode, Build123dSheetNode,  # noqa: E402
                            CadQueryNode, FusionNode)
from machinome.occt import engine  # noqa: E402
from machinome import exact_cache  # noqa: E402


class CadQueryBoredBlock(CadQueryNode):
    """A box less a through bore."""

    def render(self):
        return (cq.Workplane('XY').box(20, 20, 10)
                .faces('>Z').workplane().hole(8))


class Build123dBoredBlock(Build123dNode):
    """The same part in build123d."""

    def render(self):
        return b3d.Box(20, 20, 10) - b3d.Cylinder(4, 10)


class Panel(Build123dSheetNode):
    """A sheet panel with a round hole."""

    thickness = 3

    def profile(self):
        return (b3d.Rectangle(40, 30)
                - b3d.Pos(8, 0) * b3d.Circle(5))


class Collar(CadQueryNode):
    """A ring whose bore the shaft fills exactly."""

    def render(self):
        return cq.Workplane('XY').circle(6).circle(3).extrude(8)


class Shaft(CadQueryNode):
    """A shaft of the collar's bore diameter."""

    def render(self):
        return cq.Workplane('XY').circle(3).extrude(20)


class ShaftInBore(FusionNode):
    """An exact fusion of a shaft into a bore of equal diameter."""

    def __init__(self):
        self.collar = Collar()
        self.shaft = Shaft()
        super().__init__()

    def render(self):
        return [self.collar, self.shaft]


class Peg(Build123dNode):
    """A build123d peg standing on the CadQuery block."""

    def render(self):
        return b3d.Pos(0, 0, 8) * b3d.Cylinder(2, 12)


class MixedFusion(FusionNode):
    """A fusion mixing a CadQuery and a build123d child."""

    def __init__(self):
        self.block = CadQueryBoredBlock()
        self.peg = Peg()
        super().__init__()

    def render(self):
        return [self.block, self.peg]


def _sha256(path):
    with open(path, 'rb') as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _measure(shape):
    bounds = exact_cache.cached_bounding_box(shape)
    boxes = exact_cache.cached_face_boxes(shape)
    return {
        'volume': repr(float(engine.solid_volume(shape))),
        'solid_count': int(engine.solid_count(shape)),
        'bounding_box': [repr(float(value))
                         for corner in bounds for value in corner],
        'face_boxes_sha256': hashlib.sha256(boxes.tobytes()).hexdigest(),
        'face_boxes_shape': list(boxes.shape),
    }


def _built(node):
    node.assemble()
    if isinstance(node, FusionNode):
        node.generate_stl()
    entry = {'brep_sha256': _sha256(node.brep_file),
             'stl_sha256': _sha256(node.stl_file)}
    entry.update(_measure(node.shape()))
    return entry


def _step_product():
    from tests.step_project import parts
    from tests.test_step_node import (WRAPPED_SINGLE_PART_STEP,
                                      build_wrapped_single_part)
    build_wrapped_single_part(WRAPPED_SINGLE_PART_STEP)
    return _built(parts.WrappedSinglePart())


def _molejo_spring():
    from tests.flexible_project import spring
    node = spring.Valvetrain()
    node.set_state(lift=4.0)
    node.assemble()
    shape = node.spring.shape()
    path = os.path.join(os.environ['SOLID_BUILD_DIR'], 'spring.brep')
    BRepTools.Write_s(engine.as_shape(shape), path)
    entry = {'brep_sha256': _sha256(path),
             'stl_sha256': _sha256(node.spring.snapshot_stl_file(
                     node.spring.bound_values()))}
    entry.update(_measure(shape))
    return entry


def measurements():
    """Every fixture's measurements, built under `SOLID_BUILD_DIR`."""
    return {
        'cadquery_bored_block': _built(CadQueryBoredBlock()),
        'build123d_bored_block': _built(Build123dBoredBlock()),
        'build123d_sheet_panel': _built(Panel()),
        'step_product': _step_product(),
        'exact_fusion_shaft_in_bore': _built(ShaftInBore()),
        'mixed_backend_fusion': _built(MixedFusion()),
        'molejo_spring': _molejo_spring(),
    }


def _bench_commit():
    return subprocess.run(['git', '-C', REPO_DIR, 'rev-parse', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=GOLDEN)
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='exact-engine-golden-') as build:
        os.environ['SOLID_BUILD_DIR'] = build
        measured = measurements()
    if arguments.check:
        with open(GOLDEN) as handle:
            golden = json.load(handle)['fixtures']
        differences = [
            (fixture, field, golden[fixture][field], value)
            for fixture, entry in measured.items()
            for field, value in entry.items()
            if golden[fixture][field] != value]
        for difference in differences:
            print('DIFFERS: %s.%s golden=%r now=%r' % difference)
        print('golden comparison: %d fixtures, %d differences'
              % (len(measured), len(differences)))
        return 1 if differences else 0
    with open(arguments.out, 'w') as handle:
        json.dump({'bench_commit': _bench_commit(), 'fixtures': measured},
                  handle, indent=2, sort_keys=True)
        handle.write('\n')
    print(f'wrote {arguments.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
