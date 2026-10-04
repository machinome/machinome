# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD engine seam, `machinome.scad_engine` (OpenSpec changes
`expression-type` and `scad-presentation`, capability
`scad-engine-dependency`).

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
        self.assertEqual(seam.CONTRACT, 2)
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
        self.assert_refused(_stub(CONTRACT=1), '1')

    def test_a_provider_declaring_no_version_is_refused(self):
        self.assert_refused(_stub(), 'declares none')

    def test_a_refusal_is_not_cached(self):
        with patch.dict(sys.modules, {PROVIDER: _stub(CONTRACT=1)}):
            with self.assertRaises(self.seam.ScadEngineIncompatible):
                self.seam.scad_engine()
        self.assertIsNotNone(self.seam.scad_engine())


#: The expression golden's operations and published document, compared in
#: this interpreter; and its SCAD text, which since `scad-presentation`
#: only the engine writes, refused. Its `Solid2Node` parts are built first
#: with the engine (`BUILT`): materializing one asks the engine for its SCAD.
GOLDEN_CHECK = '''
import json, os, sys
sys.path.insert(0, 'tests')
import expression_type_golden as golden
from machinome.core.serializer import symbolic_document
from machinome.scad_engine import ScadEngineUnavailable
recorded = json.load(open(golden.GOLDEN))['fixture']
node = golden._machine()
operations = {}
with symbolic_document(node):
    for each in (node, node.arm, node.slider, node.coil):
        operations[each.name] = [
            golden._digest(json.dumps(operation.serialized))
            for operation in each.operations]
    try:
        node.scad_code
        print('SCAD answered')
    except ScadEngineUnavailable as error:
        print('SCAD refused', error)
print('OPERATIONS', operations == recorded['operations'])
print('PUBLISHED', golden._document() == recorded['published'])
'''

#: The expression golden's parts built with the engine installed.
BUILT = '''
import sys
sys.path.insert(0, 'tests')
import expression_type_golden as golden
golden._machine().build_stls()
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
        """The golden's operations and document byte for byte; its SCAD
        text, which only the engine writes (`scad-presentation`), refused
        naming the engine. Its `Solid2Node` parts are built first with the
        engine, since materializing one is a path that requires it."""
        import shutil
        import tempfile
        build_dir = tempfile.mkdtemp(prefix='expression-golden-')
        self.addCleanup(shutil.rmtree, build_dir, ignore_errors=True)
        built = run_python(BUILT, blocked=False, build_dir=build_dir)
        self.assertEqual(built.returncode, 0, built.output)
        run = run_python(GOLDEN_CHECK, absent=self.ENGINE,
                         build_dir=build_dir)
        self.assertEqual(run.returncode, 0, run.output)
        lines = run.stdout.splitlines()
        self.assertIn('OPERATIONS True', lines)
        self.assertIn('PUBLISHED True', lines)
        refused = next(line for line in lines if line.startswith('SCAD '))
        self.assertTrue(refused.startswith('SCAD refused node SharedMotion '
                                           '(SharedMotion)'), refused)
        self.assertIn(PROVIDER, refused)

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


class RequireTest(_SeamCacheCleared):
    """(`scad-presentation`) The paths that need SCAD text require the
    engine through the seam, and the binary's refusal is the seam's."""

    def test_require_scad_engine_returns_the_provider(self):
        engine = self.seam.require_scad_engine('node part (Part)', 'reasons')
        self.assertEqual(engine.__name__, PROVIDER)
        self.assertIs(engine, self.seam.scad_engine())

    def test_the_provider_absent_is_refused_naming_it(self):
        with patch.dict(sys.modules, {PROVIDER: None}):
            with self.assertRaises(self.seam.ScadEngineUnavailable) as raised:
                self.seam.require_scad_engine(
                    'the OpenSCAD snapshot renderer', 'it draws SCAD',
                    'use --renderer web')
        message = str(raised.exception)
        for words in ('the OpenSCAD snapshot renderer', 'it draws SCAD',
                      PROVIDER, 'reinstall machinome', '--renderer web'):
            self.assertIn(words, message)
        self.assertNotIn('machinome[', message)

    def test_the_binarys_refusal_is_the_seams_with_its_message_unchanged(self):
        from machinome.openscad.binary import OpenScadUnavailable
        self.assertTrue(issubclass(OpenScadUnavailable,
                                   self.seam.ScadEngineUnavailable))
        error = OpenScadUnavailable('node housing (FacetedBox)',
                                    'its STL is rendered from SCAD by '
                                    'OpenSCAD', 'use --renderer web')
        self.assertEqual(
            str(error),
            'node housing (FacetedBox) requires the OpenSCAD binary because '
            'its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and '
            "ensure 'openscad' is on PATH, or use --renderer web")


class CountingProviderTest(_SeamCacheCleared):
    """A stub provider counting what the core asks of it: SCAD text once per
    stale SCAD-authored leaf a build materializes and never for
    `assemble()`; the binary for a stale `Solid2Node`'s STL and for the
    snapshot renderer."""

    def setUp(self):
        super().setUp()
        import os
        import shutil
        import tempfile
        real = importlib.import_module(PROVIDER)
        self.texts, self.binaries = [], []

        def scad_text(description, fn=None):
            self.texts.append(description)
            return real.scad_text(description, fn=fn)

        def require_binary(needed_by, reason, alternative=None):
            self.binaries.append(needed_by)
            return real.require_binary(needed_by, reason, alternative)

        stub = _stub(CONTRACT=2, adopt=real.adopt, scad_text=scad_text,
                     require_binary=require_binary)
        # Only the provider's entry is replaced and restored: restoring the
        # whole of sys.modules would drop the modules this test imports
        # (OCP's among them), which cannot be imported twice.
        sys.modules[PROVIDER] = stub
        self.addCleanup(sys.modules.__setitem__, PROVIDER, real)
        self.build_dir = tempfile.mkdtemp(prefix='scad-counting-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)
        environment = patch.dict(os.environ,
                                 {'SOLID_BUILD_DIR': self.build_dir})
        environment.start()
        self.addCleanup(environment.stop)

    def machine(self):
        from tests.scad_where_read_project.machine import Machine
        node = Machine()
        node._prepare()
        fine = next(child for child in node.children
                    if type(child).__name__ == 'FineCylinder')
        return node, fine

    def test_scad_text_once_per_stale_scad_authored_leaf_never_by_assemble(self):
        node, _ = self.machine()
        self.assertEqual(len(self.texts), 1)
        node.assemble()
        self.assertEqual(len(self.texts), 1)

    def test_the_binary_for_a_stale_solid2nodes_stl_and_the_renderer(self):
        import os
        from types import SimpleNamespace
        from unittest.mock import MagicMock
        from machinome.node import StlRenderStart
        from machinome.viewers.openscad import OpenScadRenderer
        node, fine = self.machine()
        with patch('machinome.node.base.Popen',
                   return_value=MagicMock(pid=os.getpid())):
            with self.assertRaises(StlRenderStart) as started:
                fine.generate_stl()
        started.exception._discard()
        self.assertEqual(self.binaries,
                         ['node FineCylinder (FineCylinder)'])

        args = SimpleNamespace(camera=None, autocenter=False, viewall=False,
                               imgsize='64x48', projection=None,
                               colorscheme=None, preview=False, view=None)
        runner = MagicMock(return_value=SimpleNamespace(stdout='',
                                                        stderr=''))
        OpenScadRenderer().render(node, args, 'out.png', runner)
        runner.assert_called_once()
        self.assertEqual(self.binaries[-1], 'the OpenSCAD snapshot renderer')
