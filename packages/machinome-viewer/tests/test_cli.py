# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from unittest import TestCase
from unittest.mock import patch

from machinome_viewer import cli
from machinome_viewer.bundle import BundleMissing, BundleStale


class DescribeCommandTest(TestCase):

    def test_prints_the_installed_viewer_as_one_json_object(self):
        output = io.StringIO()
        with patch.object(cli, 'describe', return_value={
                 'path': '/tmp/machinome-viewer.js', 'index': '/tmp/index.html',
                 'apiVersion': 5, 'documentVersions': [1, 2, 3, 4, 5],
                 'version': '0.1.0'}), \
             redirect_stdout(output):
            status = cli.main(['describe'])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue()), {
            'path': '/tmp/machinome-viewer.js', 'index': '/tmp/index.html',
            'apiVersion': 5, 'documentVersions': [1, 2, 3, 4, 5],
            'version': '0.1.0',
        })

    def test_a_missing_bundle_exits_nonzero_with_the_remedy_and_no_stdout(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(cli, 'describe', side_effect=BundleMissing()), \
             redirect_stdout(output), redirect_stderr(errors):
            status = cli.main(['describe'])
        self.assertEqual(status, 1)
        self.assertEqual(output.getvalue(), '')
        self.assertIn('npm', errors.getvalue())

    def test_a_stale_bundle_exits_nonzero_with_the_reason_and_no_stdout(self):
        # ADR-059: a stale bundle that cannot be rebuilt is a broken
        # installation, reported exactly as an absent one is -- because
        # the alternative is a confident answer for a file that refuses
        # what the answer says it renders.
        output, errors = io.StringIO(), io.StringIO()
        stale = BundleStale(
            'Viewer bundle /tmp/dist/machinome-viewer.js is older than '
            '/tmp/src/viewer.ts and was not rebuilt: the widget\'s '
            'dependencies are not installed, and a rebuild never installs '
            'them. Remedy: cd /tmp && npm ci && npm run build.')
        with patch.object(cli, 'describe', side_effect=stale), \
             redirect_stdout(output), redirect_stderr(errors):
            status = cli.main(['describe'])
        self.assertEqual(status, 1)
        self.assertEqual(output.getvalue(), '')
        self.assertIn('older than', errors.getvalue())
        self.assertIn('npm', errors.getvalue())


class CaptureCommandTest(TestCase):

    def parse(self, *argv):
        return cli.build_parser().parse_args(['capture', 'staged', '-o', 'out.png', *argv])

    def test_camera_options_are_parsed_into_tuples(self):
        args = self.parse('--view', '1,2,3,4,5,6', '--up', '0,0,1', '--fov', '22.5',
                          '--imgsize', '320x240', '--time', '0.25')
        self.assertEqual(args.view, ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)))
        self.assertEqual(args.up, (0.0, 0.0, 1.0))
        self.assertEqual(args.fov, 22.5)
        self.assertEqual(args.imgsize, (320, 240))
        self.assertEqual(args.time, 0.25)

    def test_a_malformed_view_is_refused(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.parse('--view', '1,2,3')

    def test_time_outside_the_cycle_is_refused_before_capturing(self):
        errors = io.StringIO()
        with patch('machinome_viewer.capture.Capture') as capture, \
             redirect_stderr(errors):
            status = cli.main(['capture', 'staged', '-o', 'out.png', '--time', '1.5'])
        self.assertEqual(status, 2)
        self.assertIn('--time', errors.getvalue())
        capture.assert_not_called()

    def test_the_options_reach_the_capture_as_mount_options(self):
        with patch('machinome_viewer.capture.Capture') as capture:
            status = cli.main([
                'capture', 'staged', '-o', 'out.png', '--imgsize', '100x50',
                '--time', '0.5', '--view', '1,2,3,0,0,0', '--up', '0,0,1',
                '--fov', '22.5',
            ])
        self.assertEqual(status, 0)
        capture.assert_called_once_with('staged')
        capture.return_value.render.assert_called_once_with('out.png', (100, 50), {
            'animation': 'external', 'time': 0.5, 'driverControls': 'none',
            'partControls': 'none',
            'view': {'camera': [1.0, 2.0, 3.0], 'target': [0.0, 0.0, 0.0]},
            'up': [0.0, 0.0, 1.0], 'fov': 22.5,
        })

    def test_an_instant_on_a_running_document_exits_nonzero_by_name(self):
        # The refusal is the capture's, raised before any browser starts,
        # and the command reports it the way it reports every other
        # thing the photograph cannot be.
        from machinome_viewer.capture import CaptureError
        errors = io.StringIO()
        with patch('machinome_viewer.capture.Capture') as capture, \
             redirect_stderr(errors):
            capture.return_value.render.side_effect = CaptureError(
                '--time 0.5 means nothing to a document carrying a program')
            status = cli.main(['capture', 'staged', '-o', 'out.png',
                               '--time', '0.5'])
        self.assertEqual(status, 1)
        self.assertIn('--time', errors.getvalue())
        self.assertIn('program', errors.getvalue())

    def test_a_capture_failure_is_reported_and_exits_nonzero(self):
        from machinome_viewer.capture import CaptureError
        errors = io.StringIO()
        with patch('machinome_viewer.capture.Capture') as capture, \
             redirect_stderr(errors):
            capture.return_value.render.side_effect = CaptureError('no browser')
            status = cli.main(['capture', 'staged', '-o', 'out.png'])
        self.assertEqual(status, 1)
        self.assertIn('no browser', errors.getvalue())


class ServeCommandTest(TestCase):

    def test_serve_requires_a_build_directory(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cli.build_parser().parse_args(['serve'])

    def test_serve_starts_the_viewer_on_the_build_directory(self):
        with patch('machinome_viewer.server.WebViewer') as viewer:
            status = cli.main(['serve', '--build-dir', '/some/_build', '--port', '8123'])
        self.assertEqual(status, 0)
        viewer.assert_called_once_with('/some/_build', dev=False, port=8123, frontend=None)
        viewer.return_value.start.assert_called_once_with()

    def test_the_frontend_flags_are_accepted_and_do_nothing(self):
        # A released machinome's `machinome develop --web-dev` passes
        # `--start-frontend` (development-server spec's compatibility
        # promise): the command must keep parsing and working, starting
        # no second process.
        with patch('multiprocessing.Process') as process, \
             patch('machinome_viewer.server.WebViewer') as viewer:
            status = cli.main([
                'serve', '--build-dir', '/some/_build', '--start-frontend',
                '--dev', '--frontend-port', '3123',
            ])
        self.assertEqual(status, 0)
        process.assert_not_called()
        viewer.assert_called_once_with('/some/_build', dev=True, port=None, frontend=3123)
        viewer.return_value.start.assert_called_once_with()


class ModuleEntryTest(TestCase):

    def test_the_package_runs_as_a_module_through_the_interpreter(self):
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, '-m', 'machinome_viewer', 'describe'],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        reported = json.loads(result.stdout)
        self.assertIn('apiVersion', reported)
        self.assertEqual(reported['documentVersions'],
                         [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
