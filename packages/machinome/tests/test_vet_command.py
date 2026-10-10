# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`machinome vet [reference] [--tests] [--json]`: the command and its
report.

OpenSpec change ``vet-the-project`` (design D2, D7, D8). Every test runs
the real command line in a fresh interpreter from inside a fixture
project, so what is asserted is what a host reading the output sees:
text for people, one JSON object for hosts, and the verdict in the exit
status.
"""

import json
import os
import shutil
import tempfile
from unittest import TestCase

import machinome

from .import_probe import probe
from .vet_support import fixture_root, line_of

DISPATCH = 'from machinome.cli import manage; manage()\n'

PREAMBLE = (
    f'machinome vet: universe machinome {machinome.__version__}\n'
    'Vet statically checks what this project declares; it is not a '
    'sandbox, and it\n'
    'does not hold against an author who sets out to evade it.\n'
)


#: The probe runs `python -c`, which puts the working directory first on
#: `sys.path`; the installed `machinome` script does not. Inside the
#: `shadowing` fixture that difference would let the fixture's own
#: `json.py` stand in for the standard library's in the vetting process
#: itself, so the probe runs with the safe path, as the script does.
SAFE_PATH = {'PYTHONSAFEPATH': '1'}


def machinome_vet(fixture, *argv, cwd=None):
    """Run `machinome vet` in a fixture project; returns the probe."""
    return probe(DISPATCH, argv=['vet', *argv], env=SAFE_PATH,
                 cwd=cwd or fixture_root(fixture))


class TextReportTest(TestCase):
    """(7.1)"""

    def test_the_pure_project_exits_zero_with_the_preamble(self):
        result = machinome_vet('pure_project')

        self.assertEqual(result.status, 0, result.stderr)
        self.assertTrue(result.stdout.startswith(PREAMBLE), result.stdout)
        self.assertEqual(result.stdout.splitlines()[-1], 'project  pure')
        self.assertEqual(result.stderr, '')

    def test_a_finding_is_one_line_under_its_model(self):
        result = machinome_vet('outside_stdlib')

        self.assertEqual(result.status, 1, result.stderr)
        line = line_of('outside_stdlib', 'sim/model.py', 'import subprocess')
        self.assertEqual(result.stdout[len(PREAMBLE):].splitlines(), [
            '',
            'sim.model:Machine  not pure',
            f'  sim/model.py:{line}  outside-universe  subprocess',
            'project  not pure',
        ])


class JsonReportTest(TestCase):
    """(7.2)"""

    def test_one_object_with_the_specified_keys(self):
        result = machinome_vet('pure_project', '--json')

        self.assertEqual(result.status, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(list(report),
                         ['universe', 'root', 'scope', 'pure', 'models'])
        self.assertEqual(report['universe'], {
            'name': 'machinome', 'version': machinome.__version__})
        self.assertEqual(report['root'], fixture_root('pure_project'))
        self.assertEqual(report['scope'], 'models')
        self.assertIs(report['pure'], True)
        (model,) = report['models']
        self.assertEqual(list(model),
                         ['name', 'reference', 'pure', 'files', 'findings'])
        self.assertIsNone(model['name'])
        self.assertEqual(model['reference'], 'sim.model:Machine')
        self.assertIs(model['pure'], True)
        self.assertEqual(model['findings'], [])
        self.assertEqual(model['files'], sorted(model['files']))

    def test_a_finding_in_json(self):
        result = machinome_vet('outside_stdlib', '--json')

        self.assertEqual(result.status, 1, result.stderr)
        (model,) = json.loads(result.stdout)['models']
        (finding,) = model['findings']
        self.assertEqual(list(finding), ['path', 'line', 'kind', 'name'])
        self.assertEqual(finding, {
            'path': 'sim/model.py',
            'line': line_of('outside_stdlib', 'sim/model.py',
                            'import subprocess'),
            'kind': 'outside-universe', 'name': 'subprocess'})

    def test_a_finding_with_no_line_is_null(self):
        result = machinome_vet('shadowing', '--json')

        (model,) = json.loads(result.stdout)['models']
        self.assertIn({'path': 'json.py', 'line': None, 'kind': 'shadowing',
                       'name': 'json'}, model['findings'])

    def test_two_runs_are_byte_identical(self):
        first = machinome_vet('two_models', '--json', '--tests')
        second = machinome_vet('two_models', '--json', '--tests')

        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stdout.count('\n'), 1)


class ModelsTest(TestCase):
    """(7.3)"""

    def test_every_model_with_no_reference_and_no_default(self):
        result = machinome_vet('two_models', '--json')

        self.assertEqual(result.status, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual([(model['name'], model['pure'])
                          for model in report['models']],
                         [('clock_a', True), ('clock_b', False)])
        self.assertIs(report['pure'], False)

    def test_a_single_reference(self):
        result = machinome_vet('two_models', 'clock_a', '--json')

        self.assertEqual(result.status, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual([model['name'] for model in report['models']],
                         ['clock_a'])
        self.assertEqual(report['models'][0]['reference'], 'sim.a:ClockA')
        self.assertIs(report['pure'], True)


class ScopeTest(TestCase):
    """(7.4)"""

    def test_the_companion_is_out_of_scope_by_default(self):
        result = machinome_vet('tests_scope', '--json')

        self.assertEqual(result.status, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['scope'], 'models')
        (model,) = report['models']
        self.assertIs(model['pure'], True)
        self.assertNotIn('sim/test_gear.py', model['files'])
        self.assertNotIn('tools/fetch.py', model['files'])

    def test_the_companions_are_in_scope_with_tests(self):
        result = machinome_vet('tests_scope', '--tests', '--json')

        self.assertEqual(result.status, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['scope'], 'tests')
        (model,) = report['models']
        self.assertIs(model['pure'], False)
        self.assertIn('sim/test_gear.py', model['files'])
        self.assertIn('sim/test.py', model['files'])
        self.assertNotIn('tools/fetch.py', model['files'])
        self.assertEqual(model['findings'], [{
            'path': 'sim/test_gear.py',
            'line': line_of('tests_scope', 'sim/test_gear.py',
                            'import subprocess'),
            'kind': 'outside-universe', 'name': 'subprocess'}])


class CannotVetTest(TestCase):
    """(7.5) Exit 2, the reason on standard error, nothing on standard
    output."""

    def scratch(self, manifest=None):
        root = os.path.realpath(tempfile.mkdtemp(prefix='machinome-vet-'))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        if manifest is not None:
            with open(os.path.join(root, 'pyproject.toml'), 'w') as stream:
                stream.write(manifest)
        return root

    def assertCannotVet(self, result, reason):
        self.assertEqual(result.status, 2, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertIn(reason, result.stderr)

    def test_no_manifest(self):
        result = machinome_vet(None, cwd=self.scratch())

        self.assertCannotVet(result, 'No pyproject.toml with [tool.machinome]')

    def test_a_malformed_manifest(self):
        result = machinome_vet(None, '--json',
                               cwd=self.scratch('[tool.machinome]\n'))

        self.assertCannotVet(result, 'no model reference')

    def test_a_directory_reference(self):
        result = machinome_vet('pure_project', 'sim/')

        self.assertCannotVet(result, 'package.module:Class')
        self.assertIn('path/to/file.py', result.stderr)


class HelpTest(TestCase):
    """(7.6)"""

    def test_vet_help_lists_its_own_options_and_no_set(self):
        result = probe(DISPATCH, argv=['vet', '-h'])

        self.assertEqual(result.status, 0, result.stderr)
        for option in ('reference', '--tests', '--json'):
            self.assertIn(option, result.stdout)
        self.assertNotIn('--set', result.stdout)

    def test_the_top_level_help_lists_vet_after_import_step(self):
        result = probe(DISPATCH, argv=['-h'])

        self.assertEqual(result.status, 0, result.stderr)
        self.assertIn('import-step,vet}', result.stdout)
