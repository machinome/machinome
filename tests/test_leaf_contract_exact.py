# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""An exact leaf written outside the core (OpenSpec change `leaf-contract`,
capabilities `leaf-contract`, `exact-geometry` and `node-model`).

`tests/contract_package/exact_stand_in.py` stands in for machinome-freecad's
exact leaf as it is after its validation migration: a bare `TopoDS_Shape`
read from BREP bytes, no `namespace`, no cadquery, a `source_recipe` in
place of overriding the core's private currency, and `leaf_contract = 2`.
It is built, fused with a CadQuery leaf and compared by exact assertions
in a fresh interpreter, the way a project would use it.
"""

import glob
import json
import os
import shutil
import tempfile
from unittest import TestCase

from .exact_engine_absent import run_machinome, run_python


class ExactStandInTest(TestCase):

    def setUp(self):
        self.build_dir = tempfile.mkdtemp(prefix='leaf-contract-exact-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)

    def artifacts(self, pattern):
        return glob.glob(os.path.join(self.build_dir, '**', pattern),
                         recursive=True)

    def test_the_stand_in_module_imports_no_cad_front_end(self):
        run = run_python(
            'import tests.contract_package.exact_stand_in',
            blocked=False, build_dir=self.build_dir)

        self.assertEqual(run.returncode, 0, run.output)
        self.assertEqual(run.exact_stack & {'cadquery', 'build123d'}, set())

    def test_a_project_of_the_stand_in_builds_fuses_and_tests_exactly(self):
        run = run_machinome('test', 'tests/contract_package/exact_project.py',
                            blocked=False, build_dir=self.build_dir)

        self.assertIn('3 passed, 0 failed', run.stdout, run.output)
        self.assertEqual(run.returncode, 0, run.output)
        for node in ('NativeSolid', 'PinnedBlock', 'Probe', 'Clamp'):
            for suffix in ('.brep', '.stl'):
                with self.subTest(node=node, suffix=suffix):
                    self.assertEqual(len(self.artifacts(
                        f'*-{node}-*{suffix}')), 1)

    def test_changing_the_recipe_alone_makes_both_artifacts_stale(self):
        run = run_python('''
import json
from machinome import currency
import tests.contract_package.exact_stand_in as stand_in

first = stand_in.NativeSolid()
first.assemble()
built = {'brep': currency.recorded_digest(first.brep_file),
         'stl': currency.recorded_digest(first.stl_file),
         'current': [first._up_to_date(first.brep_file),
                     first._up_to_date(first.stl_file)]}
stand_in.RECIPE = 'native-v2'
second = stand_in.NativeSolid()
stale = [second._up_to_date(second.brep_file),
         second._up_to_date(second.stl_file)]
second.assemble()
rebuilt = {'brep': currency.recorded_digest(second.brep_file),
           'stl': currency.recorded_digest(second.stl_file),
           'digest': second.source_digest,
           'current': [second._up_to_date(second.brep_file),
                       second._up_to_date(second.stl_file)]}
print('RESULT', json.dumps({'built': built, 'stale': stale,
                            'rebuilt': rebuilt,
                            'same_paths': first.brep_file == second.brep_file}))
''', blocked=False, build_dir=self.build_dir)

        self.assertEqual(run.returncode, 0, run.output)
        result = json.loads(run.stdout.split('RESULT ', 1)[1])
        self.assertEqual(result['built']['current'], [True, True])
        self.assertTrue(result['same_paths'])
        self.assertEqual(result['stale'], [False, False])
        self.assertEqual(result['rebuilt']['current'], [True, True])
        self.assertEqual(result['rebuilt']['brep'], result['rebuilt']['digest'])
        self.assertEqual(result['rebuilt']['stl'], result['rebuilt']['digest'])
        self.assertNotEqual(result['rebuilt']['brep'], result['built']['brep'])

    def test_an_unconvertible_render_is_refused_naming_the_node(self):
        run = run_python('''
import tests.contract_package.exact_stand_in as stand_in
try:
    stand_in.IntSolid().assemble()
except TypeError as error:
    print('REFUSED', error)
''', blocked=False, build_dir=self.build_dir)

        self.assertEqual(run.returncode, 0, run.output)
        self.assertIn('REFUSED', run.stdout, run.output)
        message = run.stdout.split('REFUSED ', 1)[1]
        self.assertIn('IntSolid', message)
        self.assertIn('int', message)
        self.assertEqual(self.artifacts('*-IntSolid-*.brep'), [])
        self.assertEqual(self.artifacts('*-IntSolid-*.stl'), [])


class StandInDistinctnessTest(TestCase):
    """The `node-model` scenario: an adapter written outside the core is
    its own type."""

    def test_the_stand_in_is_neither_core_exact_adapter(self):
        from unittest.mock import patch

        from machinome.node import Build123dNode, CadQueryNode
        from tests.contract_package.exact_project import Block
        from tests.contract_package.exact_stand_in import NativeSolid

        build_dir = tempfile.mkdtemp(prefix='leaf-contract-types-')
        self.addCleanup(shutil.rmtree, build_dir, ignore_errors=True)
        with patch.dict(os.environ, {'SOLID_BUILD_DIR': build_dir}):
            stand_in, block = NativeSolid(), Block()
        for adapter in (CadQueryNode, Build123dNode):
            with self.subTest(adapter=adapter.__name__):
                self.assertNotIsInstance(stand_in, adapter)
                self.assertFalse(issubclass(adapter, NativeSolid))
        self.assertNotIsInstance(block, NativeSolid)
