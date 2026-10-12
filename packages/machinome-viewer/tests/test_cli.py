# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`python -m machinome.viewer.web`: the framework's `machinome viewer`, run
by this interpreter with the same parser (change `viewer-command`). The
verbs themselves, their options, refusals and signals, are the framework's
and are tested with its command (`packages/machinome/tests/
test_manager_viewer.py`)."""

import io
import json
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from unittest import TestCase
from unittest.mock import Mock, patch

import machinome.viewer as viewers
from machinome.viewer.web import cli

REPORT = {'path': '/tmp/machinome-viewer.js', 'index': '/tmp/index.html',
          'apiVersion': 5, 'documentVersions': [1, 2, 3, 4, 5],
          'version': '0.1.0'}


def provider():
    viewer = Mock(OPERATIONS=frozenset({'present', 'capture', 'serve',
                                        'embed'}))
    viewer.describe.return_value = REPORT
    return viewer


class ModuleCommandTest(TestCase):

    def run_main(self, *argv):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(viewers, 'require', return_value=provider()) \
                as required, redirect_stdout(output), redirect_stderr(errors):
            status = cli.main(list(argv))
        return status, output.getvalue(), errors.getvalue(), required

    def test_describe_prints_the_report_through_the_seam(self):
        status, output, _, required = self.run_main('describe')
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output), REPORT)
        required.assert_called_once_with('web', 'embed',
                                         'machinome viewer describe')

    def test_no_verb_prints_the_report(self):
        status, output, _, required = self.run_main()
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output), REPORT)
        required.assert_called_once_with('web', 'embed', 'machinome viewer')

    def test_the_deprecated_serve_flags_are_refused(self):
        for flag in (('--start-frontend',), ('--dev',),
                     ('--frontend-port', '3123')):
            with self.subTest(flag=flag[0]):
                with patch('machinome.viewer.web.server.WebViewer') as served, \
                        patch.object(viewers, 'require') as required, \
                        redirect_stderr(io.StringIO()) as errors, \
                        self.assertRaises(SystemExit) as raised:
                    cli.main(['serve', '--build-dir', '/some/_build', *flag])
                self.assertEqual(raised.exception.code, 2)
                self.assertIn('unrecognized arguments', errors.getvalue())
                served.assert_not_called()
                required.assert_not_called()

    def test_its_usage_is_the_framework_command_s(self):
        with redirect_stdout(io.StringIO()) as output, \
                self.assertRaises(SystemExit) as raised:
            cli.main(['-h'])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn('usage: machinome viewer', output.getvalue())
        for verb in ('describe', 'serve', 'capture'):
            self.assertIn(verb, output.getvalue())


class ModuleEntryTest(TestCase):

    def test_the_package_runs_as_a_module_through_the_interpreter(self):
        result = subprocess.run(
            [sys.executable, '-m', 'machinome.viewer.web', 'describe'],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        reported = json.loads(result.stdout)
        self.assertIn('apiVersion', reported)
        self.assertEqual(reported['documentVersions'],
                         [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
