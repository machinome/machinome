# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The mesh engine seam, `machinome.mesh_engine` (OpenSpec change
`mesh-engine`, capability `mesh-engine-dependency`).

The core names its mesh engine in one place and resolves it on first use,
in the shape of the exact engine's seam: `mesh_engine()` answers the
provider or None, `require_mesh_engine()` the provider or one actionable
refusal naming the extra that installs it. The provider declares the
contract version it implements and the seam compares it with the one the
core speaks.

Every test here that substitutes a provider does so through `sys.modules`
under `patch.dict`, and clears the seam's one-per-process cache before and
after, so the real engine is resolved afresh by whatever runs next.
"""

import importlib
import importlib.abc
import importlib.machinery
import inspect
import json
import sys
import tomllib
import types
from pathlib import Path
from typing import Protocol
from unittest import TestCase
from unittest.mock import patch

import machinome.mesh_engine as seam

ROOT = Path(__file__).resolve().parents[1]
PROVIDER = 'machinome.manifold.engine'

#: design.md Decision 2's refusal, written out here.
REFUSAL = (
    'faceted fusion Bracket requires the mesh engine because unioning its '
    'children; install it with \'pip install "machinome[manifold]"\'. Exact '
    'geometry does not need it: a model whose every compared part is exact '
    'is decided by the boundary-representation kernel')


def contract_members():
    """The operation names `MeshEngine` declares, from its Protocols."""
    names = set()
    for cls in seam.MeshEngine.__mro__:
        if cls in (object, Protocol) or cls.__module__ == 'typing':
            continue
        names.update(name for name, value in vars(cls).items()
                     if not name.startswith('_') and callable(value))
    return names


class _SeamCacheCleared(TestCase):

    def setUp(self):
        seam.mesh_engine.cache_clear()
        self.addCleanup(seam.mesh_engine.cache_clear)


class ProviderTest(_SeamCacheCleared):

    def test_the_provider_resolves_and_speaks_the_core_contract(self):
        engine = seam.mesh_engine()

        self.assertIsInstance(engine, types.ModuleType)
        self.assertEqual(engine.__name__, PROVIDER)
        self.assertEqual(seam.CONTRACT, 1)
        self.assertEqual(engine.CONTRACT, seam.CONTRACT)
        self.assertEqual(seam.PROVIDER, PROVIDER)
        self.assertIs(seam.require_mesh_engine('a test', 'it asks'), engine)

    def test_the_contract_names_ten_operations(self):
        self.assertEqual(contract_members(), {
            'solid_from_mesh', 'fault', 'mesh_arrays', 'centred_box',
            'placed_solid', 'unite_solids',
            'intersect_solids', 'is_empty', 'volume',
            'identity'})

    def test_every_contract_member_is_a_function_the_provider_defines(self):
        engine = seam.mesh_engine()

        for name in sorted(contract_members()):
            with self.subTest(name):
                member = getattr(engine, name)
                self.assertTrue(inspect.isfunction(member))
                self.assertEqual(member.__module__, PROVIDER)

    def test_resolution_happens_once_per_process(self):
        with patch.object(seam.importlib, 'import_module',
                          wraps=importlib.import_module) as imported:
            first = seam.mesh_engine()
            seam.mesh_engine()
            seam.require_mesh_engine('one', 'reason')
            seam.require_mesh_engine('two', 'reason')

        self.assertIsNotNone(first)
        self.assertEqual(imported.call_count, 1)

    def test_the_package_metadata_declares_a_manifold_extra(self):
        project = tomllib.loads(
            (ROOT / 'pyproject.toml').read_text())['project']

        self.assertIn('manifold', project['optional-dependencies'])

    def test_the_package_exports_no_operation(self):
        import machinome.manifold

        for name in sorted(contract_members()):
            with self.subTest(name):
                with self.assertRaises(AttributeError):
                    getattr(machinome.manifold, name)


class AbsentEngineTest(_SeamCacheCleared):

    def test_asking_answers_none_without_raising(self):
        with patch.dict(sys.modules, {PROVIDER: None}):
            self.assertIsNone(seam.mesh_engine())

    def test_requiring_names_the_engine_the_caller_and_the_install(self):
        with patch.dict(sys.modules, {PROVIDER: None}):
            with self.assertRaises(seam.MeshEngineUnavailable) as raised:
                seam.require_mesh_engine('faceted fusion Bracket',
                                         'unioning its children')

        self.assertEqual(str(raised.exception), REFUSAL)


def _stub(**attributes):
    module = types.ModuleType(PROVIDER)
    for name, value in attributes.items():
        setattr(module, name, value)
    return module


class ContractMismatchTest(_SeamCacheCleared):

    def assert_refused(self, provider, stated):
        for resolve in (seam.mesh_engine,
                        lambda: seam.require_mesh_engine('a', 'b')):
            seam.mesh_engine.cache_clear()
            with patch.dict(sys.modules, {PROVIDER: provider}):
                with self.assertRaises(seam.MeshEngineIncompatible) as raised:
                    resolve()
            self.assertEqual(
                str(raised.exception),
                f'The mesh engine {PROVIDER} {stated}, but this machinome '
                f'speaks mesh engine contract version 1; install the engine '
                f'released with this machinome')

    def test_a_provider_declaring_another_version_is_refused(self):
        self.assert_refused(_stub(CONTRACT=2), 'declares contract version 2')

    def test_a_provider_declaring_no_version_is_refused(self):
        self.assert_refused(_stub(), 'declares none')

    def test_a_refusal_is_not_cached(self):
        with patch.dict(sys.modules, {PROVIDER: _stub(CONTRACT=2)}):
            with self.assertRaises(seam.MeshEngineIncompatible):
                seam.mesh_engine()
        self.assertIsNotNone(seam.mesh_engine())


class _BrokenProviderFinder(importlib.abc.MetaPathFinder,
                            importlib.abc.Loader):
    """Finds the provider, then fails to import it from inside, as a
    provider whose own kernel cannot load would."""

    def find_spec(self, name, path=None, target=None):
        if name == PROVIDER:
            return importlib.machinery.ModuleSpec(name, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        raise ImportError('manifold3d failed to load')


class BrokenEngineTest(_SeamCacheCleared):

    def test_an_import_error_from_inside_the_provider_surfaces(self):
        import machinome.manifold as package

        finder = _BrokenProviderFinder()
        saved = getattr(package, 'engine', None)
        sys.meta_path.insert(0, finder)
        try:
            with patch.dict(sys.modules):
                sys.modules.pop(PROVIDER, None)
                with self.assertRaises(ImportError) as raised:
                    seam.mesh_engine()
                self.assertEqual(str(raised.exception),
                                 'manifold3d failed to load')
                with self.assertRaises(ImportError):
                    seam.require_mesh_engine('a', 'b')
        finally:
            sys.meta_path.remove(finder)
            if saved is not None:
                package.engine = saved


#: Ask the seam whether the engine is there, then require it, and report
#: both as JSON on the last line.
ASK_AND_REQUIRE = '''
import json
import machinome.mesh_engine as seam
report = {}
try:
    report['asked'] = repr(seam.mesh_engine())
except ImportError as raised:
    report['asked'] = f'{type(raised).__name__}: {raised}'
try:
    seam.require_mesh_engine('faceted fusion Bracket',
                             'unioning its children')
except Exception as raised:
    report['required'] = f'{type(raised).__name__}: {raised}'
print(json.dumps(report))
'''


class AbsentKernelTest(TestCase):
    """The engine's module is in every install, its kernel only with the
    `manifold` extra: an absent manifold3d is an absent engine, a broken
    one reports itself."""

    def ask(self, **blocking):
        from .mesh_engine_absent import run_python

        run = run_python(ASK_AND_REQUIRE, **blocking)
        lines = run.stdout.strip().splitlines()
        self.assertTrue(lines, run.output)
        return json.loads(lines[-1])

    def test_an_absent_kernel_is_an_absent_engine(self):
        report = self.ask(absent=('manifold3d',))

        self.assertEqual(report['asked'], 'None')
        self.assertEqual(report['required'],
                         f'MeshEngineUnavailable: {REFUSAL}')

    def test_an_absent_provider_is_an_absent_engine(self):
        report = self.ask(absent=('machinome.manifold',))

        self.assertEqual(report['asked'], 'None')
        self.assertEqual(report['required'],
                         f'MeshEngineUnavailable: {REFUSAL}')

    def test_a_broken_kernel_reports_its_own_failure(self):
        report = self.ask(broken=('manifold3d',), blocked=False)

        self.assertEqual(report['asked'], 'ImportError: broken manifold3d')
        self.assertEqual(report['required'],
                         'ImportError: broken manifold3d')
