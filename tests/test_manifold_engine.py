# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The manifold mesh engine, `machinome.manifold.engine` (OpenSpec change
`mesh-engine`, capability `manifold-engine`).

A fresh interpreter imports the engine and runs every contract operation
on boxes written out as numpy arrays, so what the engine imports is
measured on its own: manifold3d and numpy, never trimesh, never the OCCT
binding and never a CAD front end.
"""

import ast
import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
ENGINE_SOURCE = ROOT / 'machinome' / 'manifold' / 'engine.py'

PROBE = r'''
import json, sys
import numpy as np

import machinome.manifold
from machinome.manifold import engine

UNIT = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                 [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]], np.float64)
#: Two triangles per face, wound outward.
TRIANGLES = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
                      [0, 1, 5], [0, 5, 4], [3, 7, 6], [3, 6, 2],
                      [0, 4, 7], [0, 7, 3], [1, 2, 6], [1, 6, 5]], np.int64)


def translation(x, y, z):
    matrix = np.eye(4)
    matrix[:3, 3] = (x, y, z)
    return matrix


def cube(size):
    return engine.solid_from_mesh(UNIT * size, TRIANGLES)


def rows(vertices):
    vertices = np.asarray(vertices, np.float64)
    return vertices[np.lexsort(vertices.T[::-1])].tolist()


def bounds(solid):
    vertices, _ = engine.mesh_arrays(solid)
    return [np.min(vertices, axis=0).tolist(),
            np.max(vertices, axis=0).tolist()]


results = {}
closed = cube(2.0)
results['fault_closed'] = engine.fault(closed)
results['fault_open'] = engine.fault(
    engine.solid_from_mesh(UNIT * 2.0, TRIANGLES[:-1]))

vertices, faces = engine.mesh_arrays(closed)
results['mesh_arrays'] = [list(np.shape(vertices)), list(np.shape(faces))]

moved = engine.placed_solid(closed, translation(3, -2, 5))
results['placed'] = [rows(engine.mesh_arrays(moved)[0]),
                     rows(np.asarray(vertices, np.float64) + (3, -2, 5))]

# The flush-contact probe of the design: two 2 mm boxes laid out as
# trimesh.creation.box lays one out, the second 2 mm along X. Whether
# manifold3d reports an exact face contact empty depends on how the shared
# face is triangulated -- two boxes of the layout above, sharing a face at
# x = 2, come back empty -- and the engine reports what manifold3d reports.
BOX = np.array([[-1, -1, -1], [-1, -1, 1], [-1, 1, -1], [-1, 1, 1],
                [1, -1, -1], [1, -1, 1], [1, 1, -1], [1, 1, 1]], np.float64)
BOX_TRIANGLES = np.array([[1, 3, 0], [4, 1, 0], [0, 3, 2], [2, 4, 0],
                          [1, 7, 3], [5, 1, 4], [5, 7, 1], [3, 7, 2],
                          [6, 4, 2], [2, 7, 6], [6, 5, 4], [7, 5, 6]],
                         np.int64)
flush = engine.intersect_solids(
    engine.solid_from_mesh(BOX, BOX_TRIANGLES),
    engine.placed_solid(engine.solid_from_mesh(BOX, BOX_TRIANGLES),
                        translation(2, 0, 0)))
results['flush'] = [engine.is_empty(flush), engine.volume(flush)]

overlap = engine.intersect_solids(
    closed, engine.placed_solid(cube(2.0), translation(1, 0, 0)))
results['overlap'] = [engine.is_empty(overlap), engine.volume(overlap)]

apart = engine.intersect_solids(
    closed, engine.placed_solid(cube(2.0), translation(10, 0, 0)))
results['apart'] = [engine.is_empty(apart), engine.volume(apart)]

second = engine.placed_solid(cube(2.0), translation(1, 0, 0))
third = engine.placed_solid(cube(2.0), translation(0, 1, 0))
united = engine.unite_solids([closed, second, third])
folded = engine.unite_solids([engine.unite_solids([closed, second]), third])
united_vertices, united_faces = engine.mesh_arrays(united)
folded_vertices, folded_faces = engine.mesh_arrays(folded)
results['unite_three'] = [
    united_vertices.tobytes() == folded_vertices.tobytes(),
    united_faces.tobytes() == folded_faces.tobytes(),
    engine.volume(united)]
results['unite_one'] = engine.unite_solids([closed]) is closed

box = engine.centred_box((2, 4, 6))
results['centred_box'] = [engine.volume(box), bounds(box)]

results['identity'] = list(engine.identity())
results['package_has_solid_from_mesh'] = hasattr(machinome.manifold,
                                                 'solid_from_mesh')
results['loaded'] = sorted(name for name in ('trimesh', 'OCP', 'cadquery',
                                             'build123d')
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

    def test_the_engine_judges_what_it_built(self):
        self.assertIsNone(self.results['fault_closed'])
        self.assertEqual(self.results['fault_open'], 'NotManifold')

    def test_a_solid_meshes_back_with_three_vertex_columns(self):
        vertex_shape, face_shape = self.results['mesh_arrays']
        self.assertEqual(vertex_shape, [8, 3])
        self.assertEqual(face_shape, [12, 3])

    def test_placement_moves_by_exactly_the_translation(self):
        placed, expected = self.results['placed']
        self.assertEqual(placed, expected)

    def test_a_flush_contact_stays_non_empty_at_zero_volume(self):
        self.assertEqual(self.results['flush'], [False, 0.0])

    def test_an_overlap_measures_its_volume(self):
        is_empty, volume = self.results['overlap']
        self.assertFalse(is_empty)
        self.assertAlmostEqual(volume, 4.0, delta=1e-5)
        self.assertEqual(self.results['apart'], [True, 0.0])

    def test_a_union_is_the_left_fold(self):
        same_vertices, same_faces, volume = self.results['unite_three']
        self.assertTrue(same_vertices)
        self.assertTrue(same_faces)
        self.assertAlmostEqual(volume, 16.0, delta=1e-5)
        self.assertIs(self.results['unite_one'], True)

    def test_the_centred_box(self):
        volume, (low, high) = self.results['centred_box']
        self.assertAlmostEqual(volume, 48.0, delta=1e-9)
        self.assertEqual(low, [-1.0, -2.0, -3.0])
        self.assertEqual(high, [1.0, 2.0, 3.0])

    def test_the_engine_names_the_installed_kernel(self):
        self.assertEqual(self.results['identity'],
                         ['manifold3d',
                          importlib.metadata.version('manifold3d')])

    def test_the_package_exports_no_operation(self):
        self.assertIs(self.results['package_has_solid_from_mesh'], False)

    def test_the_engine_imports_no_mesh_library_and_no_exact_stack(self):
        self.assertEqual(self.results['loaded'], [])


class ContractDeclarationTest(TestCase):

    def test_the_contract_is_an_integer_literal_of_one(self):
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
        self.assertEqual(value.value, 1)
