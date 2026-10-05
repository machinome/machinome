# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Assertion 1 of `machinome vet`: the model closure, resolved statically.

OpenSpec change ``vet-the-project`` (design D4). From every model the
manifest declares, each import statement -- wherever it sits: module
level, a function body, a guarded `try` -- is resolved to files under the
project root without importing anything, and every package `__init__.py`
on the way is vetted, because Python runs it. A name that does not
resolve under the root must be a universe member.
"""

import os
from unittest import TestCase

from .vet_support import (copy_fixture, findings, kinds, line_of,
                          model_report, run_vet)


class ThePureProjectTest(TestCase):
    """(4.1) The vetted files are the model's closure and nothing else."""

    def test_the_pure_project_is_pure(self):
        report = run_vet('pure_project')

        model = model_report(report)
        self.assertEqual(model.findings, ())
        self.assertTrue(model.pure)
        self.assertTrue(report.pure)

    def test_the_vetted_files_are_the_model_closure(self):
        model = model_report(run_vet('pure_project'))

        self.assertEqual(model.files, (
            'sim/__init__.py', 'sim/helpers.py', 'sim/model.py',
            'sim/parts/__init__.py', 'sim/parts/gear.py'))
        self.assertNotIn('sim/test_model.py', model.files)


class ResolutionScenarioTest(TestCase):
    """(4.2) One test per scenario of "Vet resolves the model closure
    statically"."""

    def test_a_package_init_on_the_path_is_vetted(self):
        report = run_vet('init_on_path')

        model = model_report(report)
        self.assertIn('sim/__init__.py', model.files)
        self.assertIn(('sim/__init__.py',
                       line_of('init_on_path', 'sim/__init__.py',
                               'import subprocess'),
                       'outside-universe', 'subprocess'), findings(report))
        self.assertFalse(model.pure)

    def test_a_function_local_import_is_vetted(self):
        report = run_vet('function_local')

        self.assertIn(('sim/model.py',
                       line_of('function_local', 'sim/model.py',
                               'import tempfile'),
                       'outside-universe', 'tempfile'), findings(report))

    def test_a_guarded_import_is_vetted(self):
        report = run_vet('guarded')

        self.assertIn(('sim/model.py',
                       line_of('guarded', 'sim/model.py', 'import socket'),
                       'outside-universe', 'socket'), findings(report))

    def test_a_relative_import_is_followed(self):
        model = model_report(run_vet('pure_project'))

        # `from .helpers import pitch` in sim/model.py, and `from . import
        # helpers` in the package's own __init__.
        self.assertIn('sim/helpers.py', model.files)

    def test_a_module_that_is_not_there(self):
        report = run_vet('unresolved_import')

        self.assertIn(('sim/model.py',
                       line_of('unresolved_import', 'sim/model.py',
                               'import sim.missing'),
                       'unresolved-import', 'sim.missing'), findings(report))
        self.assertFalse(report.pure)

    def test_a_star_import_vets_every_module_in_the_package(self):
        report = run_vet('star_import')

        model = model_report(report)
        self.assertIn('sim/parts/a.py', model.files)
        self.assertIn('sim/parts/b.py', model.files)
        self.assertIn(('sim/parts/b.py',
                       line_of('star_import', 'sim/parts/b.py',
                               'import pickle'),
                       'outside-universe', 'pickle'), findings(report))


class ClosureFindingTest(TestCase):
    """(4.3) Each closure finding, with its path, line, kind and name."""

    def test_a_stdlib_module_outside_the_universe(self):
        report = run_vet('outside_stdlib')

        self.assertEqual(findings(report), {(
            'sim/model.py',
            line_of('outside_stdlib', 'sim/model.py', 'import subprocess'),
            'outside-universe', 'subprocess')})

    def test_a_third_party_package_outside_the_universe(self):
        report = run_vet('outside_thirdparty')

        self.assertEqual(findings(report), {(
            'sim/model.py',
            line_of('outside_thirdparty', 'sim/model.py', 'import yaml'),
            'outside-universe', 'yaml')})

    def test_a_project_file_shadowing_a_universe_name(self):
        report = run_vet('shadowing')

        model = model_report(report)
        self.assertIn(('json.py', None, 'shadowing', 'json'),
                      findings(report))
        # The import resolves to the project file, as it does at run
        # time, and the file is vetted as project code.
        self.assertIn('json.py', model.files)
        self.assertFalse(report.pure)

    def test_a_file_that_does_not_parse(self):
        report = run_vet('unparseable')

        model = model_report(report)
        broken = [finding for finding in model.findings
                  if finding.kind == 'unparseable']
        self.assertEqual(len(broken), 1, model.findings)
        self.assertEqual(broken[0].path, 'sim/broken.py')
        self.assertEqual(broken[0].line,
                         line_of('unparseable', 'sim/broken.py', 'def broken('))
        self.assertTrue(broken[0].name)
        self.assertFalse(model.pure)

    def test_a_latin_1_coding_declaration_still_parses(self):
        model = model_report(run_vet('unparseable'))

        self.assertIn('sim/latin.py', model.files)
        self.assertNotIn('sim/latin.py',
                         {finding.path for finding in model.findings})

    def test_a_module_that_escapes_through_a_symbolic_link(self):
        outside, root = copy_fixture(self, 'escaped_module')
        target = os.path.join(outside, 'vendor.py')
        with open(target, 'w') as stream:
            stream.write('import subprocess\n')
        os.symlink(target, os.path.join(root, 'sim', 'vendor.py'))

        report = run_vet(root)

        model = model_report(report)
        self.assertIn(('sim/model.py',
                       line_of(root, 'sim/model.py', 'import sim.vendor'),
                       'escaped-module', 'sim.vendor'), findings(report))
        # The escaped file is not vetted: its `subprocess` is not seen.
        self.assertNotIn('outside-universe', kinds(report))
        self.assertFalse(any('vendor' in path for path in model.files))

    def test_a_reference_that_resolves_to_no_file(self):
        report = run_vet('unresolved_reference')

        model = model_report(report)
        self.assertEqual(model.reference, 'sim.absent:Machine')
        self.assertEqual(
            [(finding.kind, finding.name) for finding in model.findings],
            [('unresolved-reference', 'sim.absent:Machine')])
        self.assertFalse(model.pure)
