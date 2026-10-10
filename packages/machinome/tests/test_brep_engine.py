# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OCCT exact engine, `machinome.engine.brep` (OpenSpec change
`exact-engine`, capability `occt-engine`).

A fresh interpreter imports the engine and runs every contract operation
on a box and a cylinder made with `BRepPrimAPI`, so what the engine
imports is measured on its own: OCP and numpy, never a CAD front end and
never trimesh.
"""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
ENGINE_SOURCE = ROOT / 'machinome' / 'engine' / 'brep.py'

PROBE = r'''
import json, math, os, sys, tempfile
import numpy as np
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.TopoDS import TopoDS_Shape
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

import machinome.engine
from machinome.engine import brep as engine

results = {}
box = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 10, 10, 10).Shape()
cylinder = BRepPrimAPI_MakeCylinder(
    gp_Ax2(gp_Pnt(5, 5, -5), gp_Dir(0, 0, 1)), 2, 20).Shape()
inner = BRepPrimAPI_MakeBox(gp_Pnt(4, 4, 4), 2, 2, 2).Shape()
far = BRepPrimAPI_MakeBox(gp_Pnt(50, 0, 0), 1, 1, 1).Shape()


def kind(value):
    return 'shape' if isinstance(value, TopoDS_Shape) else type(value).__name__


directory = tempfile.mkdtemp()
brep = os.path.join(directory, 'box.brep')
stl = os.path.join(directory, 'box.stl')
engine.write_brep(box, brep)
read = engine.read_brep(brep)
results['read_brep'] = [kind(read), engine.solid_volume(read)]
engine.write_stl(box, stl, 0.1, 0.1)
results['write_stl'] = os.path.getsize(stl) > 84

matrix = np.eye(4)
matrix[:3, 3] = (10, 0, 0)
placed = engine.placed_shape(box, matrix)
results['placed_shape'] = [kind(placed), engine.bounds(placed),
                           engine.bounds(box)]

fused = engine.fuse_shapes(box, cylinder, 'Box', 'Cylinder')
results['fuse_shapes'] = [kind(fused), engine.solid_count(fused),
                          engine.solid_volume(fused)]
common = engine.intersect_shapes(box, cylinder, 'Box', 'Cylinder')
results['intersect_overlap'] = [kind(common), engine.solid_count(common),
                                engine.solid_volume(common)]
empty = engine.intersect_shapes(box, far, 'Box', 'Far')
results['intersect_disjoint'] = [kind(empty), engine.solid_count(empty)]
results['solid_count'] = engine.solid_count(box)
results['solid_volume'] = engine.solid_volume(box)
results['bounds'] = engine.bounds(box)
faces = engine.face_bounds(box)
results['face_bounds'] = [type(faces).__name__, str(faces.dtype),
                          list(faces.shape)]
results['mutually_outside_disjoint'] = engine.mutually_outside(box, far)
results['mutually_outside_contained'] = [
    engine.mutually_outside(box, inner), engine.mutually_outside(inner, box)]
compound = engine.compound([box, far])
results['compound'] = [kind(compound), engine.solid_count(compound)]
results['as_shape_bare'] = engine.as_shape(box) is box


class Carrier:
    def __init__(self, wrapped):
        self.wrapped = wrapped


results['as_shape_wrapped'] = engine.as_shape(Carrier(box)) is box
try:
    engine.as_shape(7)
except TypeError as error:
    results['as_shape_int'] = str(error)
results['package_has_intersect'] = hasattr(machinome.engine,
                                           'intersect_shapes')
results['front_ends'] = sorted(name for name in ('cadquery', 'build123d',
                                                 'trimesh')
                               if name in sys.modules)
print('RESULTS ' + json.dumps(results))
'''


def run_probe():
    completed = subprocess.run(
        [sys.executable, '-c', PROBE], cwd=ROOT,
        env=dict(os.environ, PYTHONPATH=str(ROOT)),
        capture_output=True, text=True, timeout=300)
    for line in completed.stdout.splitlines():
        if line.startswith('RESULTS '):
            return json.loads(line[len('RESULTS '):])
    raise AssertionError(f'probe failed:\n{completed.stdout}\n'
                         f'{completed.stderr}')


class EngineOperationsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.results = run_probe()

    def test_a_brep_round_trips(self):
        kind, volume = self.results['read_brep']
        self.assertEqual(kind, 'shape')
        self.assertAlmostEqual(volume, 1000.0)
        self.assertTrue(self.results['write_stl'])

    def test_placement_returns_a_new_placed_shape(self):
        kind, placed, original = self.results['placed_shape']
        self.assertEqual(kind, 'shape')
        self.assertAlmostEqual(placed[0][0], 10.0, places=5)
        self.assertAlmostEqual(placed[1][0], 20.0, places=5)
        self.assertAlmostEqual(original[0][0], 0.0, places=5)
        self.assertAlmostEqual(original[1][0], 10.0, places=5)

    def test_booleans_return_the_currency(self):
        kind, count, volume = self.results['fuse_shapes']
        self.assertEqual((kind, count), ('shape', 1))
        self.assertGreater(volume, 1000.0)
        kind, count, volume = self.results['intersect_overlap']
        self.assertEqual((kind, count), ('shape', 1))
        self.assertAlmostEqual(volume, 40 * 3.141592653589793, places=4)
        self.assertEqual(self.results['intersect_disjoint'], ['shape', 0])

    def test_measurements_are_numbers(self):
        self.assertEqual(self.results['solid_count'], 1)
        self.assertAlmostEqual(self.results['solid_volume'], 1000.0)
        low, high = self.results['bounds']
        for value, expected in zip(low + high, (0, 0, 0, 10, 10, 10)):
            self.assertAlmostEqual(value, expected, places=5)
        self.assertEqual(self.results['face_bounds'],
                         ['ndarray', 'float64', [6, 2, 3]])

    def test_the_containment_guard(self):
        self.assertIs(self.results['mutually_outside_disjoint'], True)
        self.assertEqual(self.results['mutually_outside_contained'],
                         [False, False])

    def test_currency_composition_and_admission(self):
        self.assertEqual(self.results['compound'], ['shape', 2])
        self.assertIs(self.results['as_shape_bare'], True)
        self.assertIs(self.results['as_shape_wrapped'], True)
        self.assertIn('int', self.results['as_shape_int'])

    def test_the_engine_imports_no_front_end_and_no_trimesh(self):
        self.assertEqual(self.results['front_ends'], [])

    def test_the_package_exports_no_operation(self):
        self.assertIs(self.results['package_has_intersect'], False)


class ContractDeclarationTest(TestCase):

    def test_the_contract_is_an_integer_literal_of_two(self):
        tree = ast.parse(ENGINE_SOURCE.read_text())
        assignments = [
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == 'CONTRACT'
                    for target in node.targets)]

        self.assertEqual(len(assignments), 1)
        value = assignments[0].value
        self.assertIsInstance(value, ast.Constant)
        self.assertIs(type(value.value), int)
        self.assertEqual(value.value, 2)
