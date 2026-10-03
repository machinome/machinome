# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD engine seam, `machinome.scad_engine` (OpenSpec change
`expression-type`, capability `scad-engine-dependency`).

The core names the OpenSCAD engine in one place and resolves it on first
use, of the exact engine seam's shape: `scad_engine()` answers the provider
or None, once per process, and refuses a provider declaring another contract
version. In this cycle the core asks it for one thing, the adoption of a
value SolidPython built as an expression graph; no path requires it, so an
absent engine means only that such a value is not an expression.

Every test here that substitutes a provider does so through `sys.modules`
under `patch.dict` or a `sys.meta_path` finder, and clears the seam's
one-per-process cache before and after, so the real engine is resolved
afresh by whatever runs next. The tests of an absent engine run in a
subprocess under `tests/exact_engine_absent.py`'s finder.
"""

import importlib
import importlib.abc
import importlib.machinery
import json
import sys
import types
from unittest import TestCase
from unittest.mock import patch

from tests.exact_engine_absent import run_python

PROVIDER = 'machinome.openscad.engine'


def _seam():
    return importlib.import_module('machinome.scad_engine')


class _SeamCacheCleared(TestCase):

    def setUp(self):
        self.seam = _seam()
        self.seam.scad_engine.cache_clear()
        self.addCleanup(self.seam.scad_engine.cache_clear)


class DeclarationTest(TestCase):

    def test_the_seam_declares_its_contract_and_its_one_provider(self):
        seam = _seam()
        self.assertEqual(seam.CONTRACT, 1)
        self.assertEqual(seam.PROVIDER, PROVIDER)

    def test_importing_the_seam_imports_neither_the_provider_nor_solid2(self):
        run = run_python(
            'import sys, json\n'
            'import machinome.scad_engine\n'
            'print(json.dumps(sorted(name for name in sys.modules if '
            'name.startswith(("machinome.openscad", "solid2")))))',
            blocked=False)
        self.assertEqual(run.returncode, 0, run.output)
        self.assertEqual(json.loads(run.stdout.strip().splitlines()[-1]), [])


class ProviderTest(_SeamCacheCleared):

    def test_the_provider_resolves_once_and_speaks_the_core_contract(self):
        with patch.object(self.seam.importlib, 'import_module',
                          wraps=importlib.import_module) as imported:
            first = self.seam.scad_engine()
            second = self.seam.scad_engine()

        self.assertEqual(first.__name__, PROVIDER)
        self.assertIs(first, second)
        self.assertEqual(first.CONTRACT, self.seam.CONTRACT)
        self.assertEqual(imported.call_count, 1)


#: Ask the seam for the engine and print what it answered.
ASK = '''
import machinome.scad_engine as seam
print(repr(seam.scad_engine()))
'''


class AbsentEngineTest(_SeamCacheCleared):

    def test_the_provider_absent_answers_none(self):
        with patch.dict(sys.modules, {PROVIDER: None}):
            self.assertIsNone(self.seam.scad_engine())

    def test_the_engine_package_absent_answers_none(self):
        run = run_python(ASK, absent=('machinome.openscad',))
        self.assertEqual(run.returncode, 0, run.output)
        self.assertEqual(run.stdout.strip().splitlines()[-1], 'None')

    def test_solidpython_absent_answers_none(self):
        run = run_python(ASK, absent=('solid2',))
        self.assertEqual(run.returncode, 0, run.output)
        self.assertEqual(run.stdout.strip().splitlines()[-1], 'None')


class _BrokenProviderFinder(importlib.abc.MetaPathFinder,
                            importlib.abc.Loader):
    """Finds the provider, then fails to import it from inside with
    `error`, as a provider whose own imports cannot load would."""

    def __init__(self, error):
        self.error = error

    def find_spec(self, name, path=None, target=None):
        if name == PROVIDER:
            return importlib.machinery.ModuleSpec(name, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        raise self.error


class BrokenEngineTest(_SeamCacheCleared):

    def assert_propagates(self, error):
        finder = _BrokenProviderFinder(error)
        package = importlib.import_module('machinome.openscad')
        saved = getattr(package, 'engine', None)
        sys.meta_path.insert(0, finder)
        try:
            with patch.dict(sys.modules):
                sys.modules.pop(PROVIDER, None)
                with self.assertRaises(type(error)) as raised:
                    self.seam.scad_engine()
                self.assertIs(raised.exception, error)
        finally:
            sys.meta_path.remove(finder)
            if saved is not None:
                package.engine = saved

    def test_an_import_error_from_inside_the_provider_propagates(self):
        self.assert_propagates(ImportError('broken provider'))

    def test_another_missing_module_propagates(self):
        self.assert_propagates(
            ModuleNotFoundError("No module named 'lark'", name='lark'))


def _stub(**attributes):
    module = types.ModuleType(PROVIDER)
    for name, value in attributes.items():
        setattr(module, name, value)
    return module


class ContractMismatchTest(_SeamCacheCleared):

    def assert_refused(self, provider, declared):
        for _ in range(2):
            with patch.dict(sys.modules, {PROVIDER: provider}):
                with self.assertRaises(
                        self.seam.ScadEngineIncompatible) as raised:
                    self.seam.scad_engine()
            message = str(raised.exception)
            self.assertIn(PROVIDER, message)
            self.assertIn(declared, message)
            self.assertIn(str(self.seam.CONTRACT), message)

    def test_a_provider_declaring_another_version_is_refused(self):
        self.assert_refused(_stub(CONTRACT=2), '2')

    def test_a_provider_declaring_no_version_is_refused(self):
        self.assert_refused(_stub(), 'declares none')

    def test_a_refusal_is_not_cached(self):
        with patch.dict(sys.modules, {PROVIDER: _stub(CONTRACT=2)}):
            with self.assertRaises(self.seam.ScadEngineIncompatible):
                self.seam.scad_engine()
        self.assertIsNotNone(self.seam.scad_engine())


#: Run the expression golden's comparison in this interpreter.
GOLDEN_CHECK = '''
import runpy, sys
sys.argv = ['tests/expression_type_golden.py', '--check']
runpy.run_path('tests/expression_type_golden.py', run_name='__main__')
'''

#: The numeric face, the law and the seam, with a SolidPython value.
SOLIDPYTHON_VALUE = '''
import machinome.scad_engine as seam
from solid2.core.object_base import scad_inline
import machinome.math as m
print('ENGINE', repr(seam.scad_engine()))
try:
    m.sin(scad_inline('$t'))
except Exception as error:
    print('SIN', type(error).__name__, error)
from machinome.simulation import Sim
from tests.expression_type_project.running import LegacyTime
try:
    Sim(LegacyTime(), 0.1)
except Exception as error:
    print('LAW', type(error).__name__, error)
'''


class WithoutTheEngineTest(TestCase):
    """The engine blocked in every process of the run: native values need
    nothing of it, and a SolidPython value is simply not an expression."""

    ENGINE = (PROVIDER,)

    def test_native_values_compose_and_publish_the_golden(self):
        run = run_python(GOLDEN_CHECK, absent=self.ENGINE)
        self.assertEqual(run.returncode, 0, run.output)
        self.assertIn('golden comparison: 17 values, 0 differences',
                      run.stdout)

    def test_a_solidpython_value_meets_the_existing_refusals(self):
        run = run_python(SOLIDPYTHON_VALUE, absent=self.ENGINE)
        self.assertEqual(run.returncode, 0, run.output)
        lines = run.stdout.splitlines()
        self.assertIn('ENGINE None', lines)
        sin = next(line for line in lines if line.startswith('SIN '))
        self.assertTrue(sin.startswith('SIN TypeError must be real number'),
                        sin)
        law = next(line for line in lines if line.startswith('LAW '))
        self.assertTrue(law.startswith('LAW UnsupportedLaw'), law)
        self.assertIn('which is neither a number nor an expression over '
                      'its sources.', law)


class NumbersNeverConsultTheEngineTest(TestCase):

    def test_a_plain_number_never_consults_the_seam(self):
        import machinome.math as m
        from machinome.expression_graph import as_node, symbolic
        from tests.expression_type_project.machine import SharedMotion
        seam = _seam()
        real = seam.scad_engine
        t = SharedMotion().time
        with patch.object(seam, 'scad_engine', wraps=real) as asked:
            m.sin(1.0), m.cos(30), m.atan2(1, 2), m.min(1, 2)
            m.max(1.5, 2), m.clamp01(0.5), m.piecewise(0.5, [(0, 0), (1, 1)])
            t + 1, 2 * t, t ** 2, t / 3.0, t < 1, m.sin(t), m.min(t, 1)
            as_node(3), as_node(2.5), symbolic(1), symbolic(0.5)
            self.assertEqual(asked.call_count, 0)
            # The stub is wired: anything else does consult it.
            symbolic('not a number')
            self.assertEqual(asked.call_count, 1)
