# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Assertions 2 and 3 of `machinome vet`, and the finding kinds.

OpenSpec change ``vet-the-project`` (design D5, D7). In every vetted
file: no dynamic route around the declaration, no kernel IO entry point,
no framework internal, no write; and every declared adapter source stays
under the project root. Each fixture raises exactly the findings listed
here, so a rule that fires too widely fails as surely as one that does
not fire.
"""

import os
from unittest import TestCase

from .vet_support import (copy_fixture, findings, fixture_root, kinds,
                          line_of, model_report, run_vet)

DUNDERS = ('__subclasses__', '__globals__', '__builtins__', '__loader__',
           '__spec__', '__code__', '__closure__', '__mro__', '__bases__',
           '__base__', '__path__')

SIXTEEN = {
    'outside-universe', 'kernel-io', 'framework-internal', 'file-write',
    'dynamic-route', 'import-system', 'denied-dunder', 'denied-builtin',
    'shadowing', 'unparseable', 'unresolved-import', 'escaped-module',
    'unresolved-reference', 'source-absolute', 'source-escapes',
    'jscad-source',
}


def at(fixture, text, kind, name, path='sim/model.py'):
    return (path, line_of(fixture, path, text), kind, name)


class KernelIoTest(TestCase):
    """(5.1)"""

    def test_kernel_io_by_alias_from_import_prefix_and_chain(self):
        fixture = 'kernel_io_dotted'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, 'import cadquery.importers', 'kernel-io',
               'cadquery.importers'),
            at(fixture, 'from build123d import import_step', 'kernel-io',
               'build123d.import_step'),
            at(fixture, "np.load('table.npy')", 'kernel-io', 'numpy.load'),
            at(fixture, 'cq.importers.importStep(path)', 'kernel-io',
               'cadquery.importers'),
        })

    def test_the_pure_apis_raise_nothing(self):
        # np.linspace, trimesh.creation.cylinder and the project's own
        # `blueprints.load` are in the fixture above and absent from its
        # findings; json.load, bound by import, is in the pure project.
        report = run_vet('pure_project')

        self.assertTrue(model_report(report).pure)

    def test_an_io_method_on_an_unbound_receiver(self):
        fixture = 'kernel_io_method'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, ".export('out.stl')", 'kernel-io', 'export')})


class FrameworkInternalTest(TestCase):
    """(5.2)"""

    def test_the_loader_by_import_and_the_builder_by_chain(self):
        fixture = 'framework_internal'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, 'from machinome.core.loader import load_node',
               'framework-internal', 'machinome.core.loader'),
            at(fixture, 'BUILDER = machinome.core.builder.Builder',
               'framework-internal', 'machinome.core.builder'),
        })

    def test_production_writers_do_not_enter_the_pure_model_contract(self):
        fixture = 'production_writers'
        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, 'from machinome.model import ModelSnapshot',
               'framework-internal', 'machinome.model.ModelSnapshot'),
            at(fixture, 'from machinome.production.profile import Production',
               'framework-internal', 'machinome.production.profile'),
        })


class ExactEngineInternalTest(TestCase):
    """The exact internals and the engine's file operations are framework
    internals; the engine's other operations and the seam's error types are
    contract (OpenSpec change `exact-engine`, design.md Decision 14)."""

    def test_internals_are_found_and_the_contract_passes(self):
        fixture = 'exact_engine_internals'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, 'from machinome.engine.brep import write_brep',
               'framework-internal', 'machinome.engine.brep.write_brep'),
            at(fixture, 'import machinome.brep_artifacts',
               'framework-internal', 'machinome.brep_artifacts'),
            at(fixture, 'LOAD = machinome.brep_cache.cached_shape',
               'framework-internal', 'machinome.brep_cache'),
        })


class LeafModuleTest(TestCase):
    """The leaf modules at their final addresses are contract members
    (OpenSpec change `lean-install`, `vet` "A framework internal is a
    finding"): vet judges a name by its place in the universe, so this
    passes before the change as after it."""

    def test_a_leaf_module_passes(self):
        self.assertEqual(findings(run_vet('leaf_modules')), set())


class FileWriteTest(TestCase):
    """(5.3)"""

    def test_writes_are_found_and_reads_are_not(self):
        fixture = 'file_write'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, "open(p, 'w')", 'file-write', 'open'),
            at(fixture, "open(p, mode='a')", 'file-write', 'open'),
            at(fixture, "open(p, mode='a+')", 'file-write', 'open'),
            at(fixture, 'open(p, mode)', 'file-write', 'open'),
            at(fixture, 'opener = open', 'file-write', 'open'),
            at(fixture, 'Path(p).write_text(text)', 'file-write',
               'write_text'),
            at(fixture, 'Path(p).parent.mkdir(parents=True)', 'file-write',
               'mkdir'),
        })


class OsRestrictionTest(TestCase):
    """(5.4)"""

    def test_os_path_and_listing_pass_and_the_rest_of_os_does_not(self):
        fixture = 'os_restricted'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, 'from os import system', 'outside-universe',
               'os.system'),
            at(fixture, 'from os import *', 'outside-universe', 'os.*'),
            at(fixture, 'os.makedirs(HERE)', 'outside-universe',
               'os.makedirs'),
            at(fixture, "os.environ.get('HOME')", 'outside-universe',
               'os.environ'),
            at(fixture, "os.system('true')", 'outside-universe',
               'os.system'),
        })

    def test_pathlib_passes_whole(self):
        self.assertTrue(run_vet('pathlib_allowed').pure)


class DynamicRouteTest(TestCase):
    """(5.5)"""

    def test_eval_exec_compile_and_import_by_name(self):
        fixture = 'dynamic_eval'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, "VALUE = eval('1 + 1')", 'dynamic-route', 'eval'),
            at(fixture, 'ALIAS = eval', 'dynamic-route', 'eval'),
            at(fixture, "exec('x = 1')", 'dynamic-route', 'exec'),
            at(fixture, "CODE = compile(", 'dynamic-route', 'compile'),
            at(fixture, "MATH = __import__('math')", 'dynamic-route',
               '__import__'),
        })

    def test_importlib_and_runpy_are_dynamic_routes_only(self):
        fixture = 'dynamic_importlib'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, 'import importlib', 'dynamic-route', 'importlib'),
            at(fixture, 'import runpy', 'dynamic-route', 'runpy'),
            at(fixture, 'from importlib import import_module',
               'dynamic-route', 'importlib'),
        })


class ImportSystemTest(TestCase):
    """(5.6)"""

    def test_sys_path_by_chain_and_by_from_import(self):
        fixture = 'sys_path'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, 'import sys', 'outside-universe', 'sys'),
            at(fixture, 'sys.path.insert', 'import-system', 'sys.path'),
            at(fixture, 'from sys import path', 'outside-universe', 'sys'),
            at(fixture, 'from sys import path', 'import-system', 'sys.path'),
        })

    def test_sys_modules_assignment(self):
        fixture = 'sys_modules'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, 'import sys', 'outside-universe', 'sys'),
            at(fixture, "sys.modules['gears']", 'import-system',
               'sys.modules'),
        })


class DeniedDunderTest(TestCase):
    """(5.7)"""

    def test_each_dunder_as_an_attribute_and_as_a_bare_name(self):
        fixture = 'dunder_attribute'
        found = findings(run_vet(fixture))

        for name in DUNDERS:
            with self.subTest(name=name):
                self.assertIn(at(fixture, f'obj.{name}', 'denied-dunder',
                                 name), found)
                self.assertIn(at(fixture, name, 'denied-dunder', name,
                                 path='sim/names.py'), found)
        self.assertIn(at(fixture, 'type(Probe()).__mro__', 'denied-dunder',
                         '__mro__'), found)
        self.assertEqual({finding[2] for finding in found}, {'denied-dunder'})

    def test_each_dunder_as_a_string_literal(self):
        fixture = 'dunder_literal'
        found = findings(run_vet(fixture))

        for name in DUNDERS:
            with self.subTest(name=name):
                self.assertIn(at(fixture, f"getattr(obj, '{name}')",
                                 'denied-dunder', name), found)
        self.assertIn(at(fixture, "f'__globals__'", 'denied-dunder',
                         '__globals__'), found)
        self.assertEqual({finding[2] for finding in found}, {'denied-dunder'})

    def test_a_package_redirecting_its_own_imports(self):
        fixture = 'dunder_path'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, '__path__.append', 'denied-dunder', '__path__',
               path='sim/__init__.py')})


class DeniedBuiltinTest(TestCase):
    """(5.8)"""

    def test_breakpoint_help_and_input_and_not_open(self):
        fixture = 'denied_builtin'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, "input('size? ')", 'denied-builtin', 'input'),
            at(fixture, 'breakpoint()', 'denied-builtin', 'breakpoint'),
            at(fixture, 'help(len)', 'denied-builtin', 'help'),
        })

    def test_a_name_the_file_binds_is_not_the_built_in(self):
        # A class-body child `input = InputArbor()` used as
        # `input.turn.drives(...)`, `from re import compile` then
        # `compile(p)`, and a parameter `help`: each is the project's own
        # name, and raises nothing (Poleni-1709, Pascaline-module).
        report = run_vet('bound_builtin')

        self.assertEqual(findings(report), set())
        self.assertTrue(model_report(report).pure)


class SourcesTest(TestCase):
    """(5.9)"""

    def test_a_literal_under_the_root_passes_without_the_file(self):
        root = fixture_root('pure_project')
        # The pure project declares `stl_source = '../meshes/part.stl'`,
        # which lies under its root and does not exist: vet never opens a
        # source, so it need not be there.
        self.assertFalse(os.path.exists(os.path.join(root, 'meshes')))

        self.assertTrue(run_vet(root).pure)

    def test_a_computed_source_passes(self):
        self.assertTrue(run_vet('computed_source_passes').pure)

    def test_an_absolute_source(self):
        fixture = 'source_absolute'

        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, "stl_source = '/etc/model.stl'", 'source-absolute',
               'stl_source')})

    def test_an_escaping_source_and_none(self):
        fixture = 'source_escapes'

        # `link/gear.stl` names no link in the repository's copy, so it
        # resolves under the root; `stl_source = None` is never a finding.
        self.assertEqual(findings(run_vet(fixture)), {
            at(fixture, "scad_source = '../../../outside.scad'",
               'source-escapes', 'scad_source')})

    def test_a_source_that_escapes_through_a_symbolic_link(self):
        outside, root = copy_fixture(self, 'source_escapes')
        os.symlink(outside, os.path.join(root, 'sim', 'link'))

        self.assertIn(at(root, "stl_source = 'link/gear.stl'",
                         'source-escapes', 'stl_source'),
                      findings(run_vet(root)))

    def test_a_jscad_source(self):
        fixture = 'jscad_source'

        report = run_vet(fixture)

        self.assertEqual(findings(report), {
            at(fixture, "jscad_source = 'part.jscad'", 'jscad-source',
               'jscad_source')})
        self.assertFalse(report.pure)


class TestsTierTest(TestCase):
    """(5.10)"""

    def test_a_companion_may_use_the_test_frameworks(self):
        report = run_vet('tests_tier', tests=True)

        gear = model_report(report, 'gear')
        self.assertIn('sim/test_gear.py', gear.files)
        self.assertEqual(gear.findings, ())
        self.assertTrue(gear.pure)

    def test_a_model_module_may_not_import_unittest(self):
        expected = at('tests_tier', 'import unittest', 'outside-universe',
                      'unittest', path='sim/bad.py')
        for tests in (False, True):
            with self.subTest(tests=tests):
                report = run_vet('tests_tier', tests=tests)
                self.assertEqual(findings(report, 'bad'), {expected})


class KindsTest(TestCase):
    """(5.11) Exactly sixteen kinds, declared as the module's constants."""

    def test_the_declared_kinds_are_the_sixteen(self):
        from machinome.vet import assertions

        self.assertEqual(len(assertions.KINDS), 16)
        self.assertEqual(set(assertions.KINDS), SIXTEEN)
        constants = {value for name, value in vars(assertions).items()
                     if name.isupper() and isinstance(value, str)}
        self.assertEqual(constants, SIXTEEN)

    def test_every_fixture_raises_only_declared_kinds(self):
        from machinome.vet import assertions

        for name in sorted(os.listdir(fixture_root(''))):
            with self.subTest(fixture=name):
                for tests in (False, True):
                    report = run_vet(name, tests=tests)
                    for model in report.models:
                        self.assertLessEqual(
                            {finding.kind for finding in model.findings},
                            set(assertions.KINDS))
                        self.assertLessEqual(kinds(report, model.name)
                                             if len(report.models) > 1
                                             else kinds(report),
                                             SIXTEEN)
