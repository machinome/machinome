# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The exact engine seam, `machinome.exact_engine` (OpenSpec change
`exact-engine`, capability `exact-engine-dependency`).

The core names its exact engine in one place and resolves it on first use:
`exact_engine()` answers the engine or None, `require_exact_engine()` the
engine or one actionable refusal naming the install. The provider declares
the contract version it implements and the seam compares it with the one
the core speaks.

Every test here that substitutes a provider does so through `sys.modules`
under `patch.dict`, and clears the seam's one-per-process cache before and
after, so the real engine is resolved afresh by whatever runs next.
"""

import importlib
import importlib.abc
import importlib.machinery
import inspect
import sys
import tomllib
import types
from pathlib import Path
from typing import Protocol
from unittest import TestCase
from unittest.mock import patch

import machinome.exact_engine as seam

ROOT = Path(__file__).resolve().parents[1]
PROVIDER = 'machinome.occt.engine'


def contract_members():
    """The operation names `ExactEngine` declares, from its Protocols."""
    names = set()
    for cls in seam.ExactEngine.__mro__:
        if cls in (object, Protocol) or cls.__module__ == 'typing':
            continue
        names.update(name for name, value in vars(cls).items()
                     if not name.startswith('_') and callable(value))
    return names


class _SeamCacheCleared(TestCase):

    def setUp(self):
        seam.exact_engine.cache_clear()
        self.addCleanup(seam.exact_engine.cache_clear)


class ProviderTest(_SeamCacheCleared):

    def test_the_provider_resolves_and_speaks_the_core_contract(self):
        engine = seam.exact_engine()

        self.assertIsNotNone(engine)
        self.assertEqual(engine.__name__, PROVIDER)
        self.assertEqual(engine.CONTRACT, seam.CONTRACT)
        self.assertIs(seam.require_exact_engine('a test', 'it asks'), engine)

    def test_the_contract_names_thirteen_operations(self):
        self.assertEqual(contract_members(), {
            'as_shape', 'compound', 'read_brep', 'write_brep', 'write_stl',
            'placed_shape', 'fuse_shapes',
            'intersect_shapes', 'solid_count', 'solid_volume', 'bounds',
            'face_bounds', 'mutually_outside'})

    def test_every_contract_member_is_a_function_the_provider_defines(self):
        engine = seam.exact_engine()

        for name in sorted(contract_members()):
            with self.subTest(name):
                member = getattr(engine, name)
                self.assertTrue(inspect.isfunction(member))
                self.assertEqual(member.__module__, PROVIDER)

    def test_resolution_happens_once_per_process(self):
        with patch.object(seam.importlib, 'import_module',
                          wraps=importlib.import_module) as imported:
            first = seam.exact_engine()
            seam.exact_engine()
            seam.require_exact_engine('one', 'reason')
            seam.require_exact_engine('two', 'reason')

        self.assertIsNotNone(first)
        self.assertEqual(imported.call_count, 1)

    def test_the_package_metadata_declares_an_occt_extra(self):
        project = tomllib.loads(
            (ROOT / 'pyproject.toml').read_text())['project']

        self.assertIn('occt', project['optional-dependencies'])


class AbsentEngineTest(_SeamCacheCleared):

    def test_asking_answers_none_without_raising(self):
        with patch.dict(sys.modules, {PROVIDER: None}):
            self.assertIsNone(seam.exact_engine())

    def test_requiring_names_the_engine_the_caller_and_the_install(self):
        with patch.dict(sys.modules, {PROVIDER: None}):
            with self.assertRaises(seam.ExactEngineUnavailable) as raised:
                seam.require_exact_engine('exact fusion Bracket',
                                          'fusing its exact children')

        message = str(raised.exception)
        self.assertIn('exact engine', message)
        self.assertIn('exact fusion Bracket', message)
        self.assertIn('fusing its exact children', message)
        self.assertIn('pip install "machinome[occt]"', message)


def _stub(**attributes):
    module = types.ModuleType(PROVIDER)
    for name, value in attributes.items():
        setattr(module, name, value)
    return module


class ContractMismatchTest(_SeamCacheCleared):

    def assert_refused(self, provider, declared):
        for resolve in (seam.exact_engine,
                        lambda: seam.require_exact_engine('a', 'b')):
            seam.exact_engine.cache_clear()
            with patch.dict(sys.modules, {PROVIDER: provider}):
                with self.assertRaises(seam.ExactEngineIncompatible) as raised:
                    resolve()
            message = str(raised.exception)
            self.assertIn(str(seam.CONTRACT), message)
            self.assertIn(declared, message)
            self.assertIn(PROVIDER, message)

    def test_a_provider_declaring_another_version_is_refused(self):
        self.assert_refused(_stub(CONTRACT=2), '2')

    def test_a_provider_declaring_no_version_is_refused(self):
        self.assert_refused(_stub(), 'none')

    def test_a_refusal_is_not_cached(self):
        with patch.dict(sys.modules, {PROVIDER: _stub(CONTRACT=2)}):
            with self.assertRaises(seam.ExactEngineIncompatible):
                seam.exact_engine()
        self.assertIsNotNone(seam.exact_engine())


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
        raise ModuleNotFoundError("No module named 'OCP'", name='OCP')


class BrokenEngineTest(_SeamCacheCleared):

    def test_an_import_error_from_inside_the_provider_surfaces(self):
        finder = _BrokenProviderFinder()
        package = sys.modules.get('machinome.occt')
        saved = {}
        if package is not None and hasattr(package, 'engine'):
            saved['engine'] = package.engine
        sys.meta_path.insert(0, finder)
        try:
            with patch.dict(sys.modules):
                sys.modules.pop(PROVIDER, None)
                with self.assertRaises(ModuleNotFoundError) as raised:
                    seam.exact_engine()
                self.assertEqual(raised.exception.name, 'OCP')
                with self.assertRaises(ModuleNotFoundError):
                    seam.require_exact_engine('a', 'b')
        finally:
            sys.meta_path.remove(finder)
            if package is not None and 'engine' in saved:
                package.engine = saved['engine']
