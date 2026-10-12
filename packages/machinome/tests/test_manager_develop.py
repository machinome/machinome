# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`machinome develop`: a builder loop beside the viewer that serves.

The viewer is chosen by `--viewer`, the project's declared viewer or the
web viewer, and asked through the seam `machinome.viewer` to serve the
build directory in this process (OpenSpec change `viewer-seam`): its
session is told when a build is published, and stopped when the loop ends.
The builder remains a spawned child handed a module-level target. Every test
but the last stands a fake web viewer in at the seam, so the suite says the
same thing with or without the viewer installed.
"""

import argparse
import io
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from argparse import Namespace
from contextlib import redirect_stderr
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock, call

import machinome.viewer as viewers
from machinome.core.builder import BuildOutcome
from machinome.manager.develop import Develop, run_builder

BUILD_DIR = '/work/project/_build'
REPOSITORY = Path(__file__).resolve().parents[3]


def default_args(**overrides):
    values = dict(
        path='.',
        web=False,
        web_dev=False,
        debug_builder=False,
        no_web=False,
        callback=None,
        viewer=None,
    )
    values.update(overrides)
    return Namespace(**values)


def fake_web():
    """A web viewer as the seam resolves it: it serves and embeds."""
    provider = MagicMock(name='machinome.viewer.web')
    provider.NAME = 'web'
    provider.CONTRACT = viewers.CONTRACT
    provider.OPERATIONS = frozenset({'present', 'capture', 'serve', 'embed'})
    return provider


class DevelopHarness(TestCase):
    """Patch the seams every scenario shares."""

    def setUp(self):
        self.develop = Develop()
        self.develop.parser = argparse.ArgumentParser()
        self.web = fake_web()
        self.session = self.web.serve.return_value
        real = viewers.viewer

        def resolve(name):
            if name == 'web':
                return self.web
            return real(name)

        patches = [
            patch.object(viewers, 'viewer', side_effect=resolve),
            patch('machinome.manager.develop.get_build_dir', return_value=BUILD_DIR),
            patch('machinome.manager.develop.Process'),
        ]
        (self.resolved, self.get_build_dir,
         self.process) = (p.start() for p in patches)
        for p in patches:
            self.addCleanup(p.stop)

    def builders(self, *exitcodes):
        """Builder processes ending in one whose join interrupts the loop."""
        instances = []
        for code in exitcodes:
            instance = MagicMock(exitcode=code)
            instance.join.return_value = None
            instances.append(instance)
        last = MagicMock()
        last.join.side_effect = KeyboardInterrupt
        instances.append(last)
        return instances

    def run_develop(self, args, *exitcodes):
        instances = self.builders(*exitcodes)
        self.process.side_effect = instances
        with self.assertRaises(SystemExit) as raised:
            self.develop.handle(args)
        return raised.exception.code

    def refused(self, args):
        """Run `args`, expecting one refusal line and nothing started."""
        with redirect_stderr(io.StringIO()) as errors, \
                self.assertRaises(SystemExit) as raised:
            self.develop.handle(args)
        self.assertEqual(raised.exception.code, 1)
        self.web.serve.assert_not_called()
        self.process.assert_not_called()
        lines = errors.getvalue().splitlines()
        self.assertEqual(len(lines), 1, lines)
        return lines[0]


class DefaultViewerTest(DevelopHarness):

    def test_the_web_viewer_serves_by_default(self):
        self.assertEqual(self.run_develop(default_args()), 0)
        self.resolved.assert_any_call('web')
        self.web.describe.assert_called_once_with()
        self.web.serve.assert_called_once_with(BUILD_DIR)
        self.session.stop.assert_called_once_with()

    def test_default_without_the_viewer_fails_even_with_openscad_available(self):
        self.resolved.side_effect = viewers.absent('web')
        with patch('machinome.node.openscad.binary.openscad_binary',
                   return_value='/usr/bin/openscad') as openscad:
            line = self.refused(default_args())
        self.assertEqual(
            line, 'Error: the web viewer needs machinome.viewer.web, which '
                  'is not installed; install it with '
                  '\'pip install "machinome[viewer]"\'')
        openscad.assert_not_called()

    def test_a_viewer_without_its_bundle_is_refused_before_any_child(self):
        self.web.describe.side_effect = FileNotFoundError(
            'Viewer bundle not found at /x/machinome-viewer.js.')
        line = self.refused(default_args())
        self.assertEqual(
            line, 'Error: Viewer bundle not found at /x/machinome-viewer.js.')

    def test_the_project_s_viewer_is_asked(self):
        project = tempfile.mkdtemp(prefix='develop-project-viewer-')
        self.addCleanup(shutil.rmtree, project, ignore_errors=True)
        Path(project, 'pyproject.toml').write_text(
            '[tool.machinome]\nmodel = "demo:Demo"\nviewer = "openscad"\n')
        Path(project, 'demo.py').write_text('')
        line = self.refused(default_args(path=os.path.join(project,
                                                           'demo.py')))
        self.assertEqual(
            line,
            'Error: machinome develop needs a viewer that can serve, and the '
            "openscad viewer, this project's viewer "
            '(`[tool.machinome] viewer`), cannot; the viewers that can: web; '
            'name one with --viewer')


class ExplicitViewerTest(DevelopHarness):

    def test_web_without_the_viewer_fails_naming_the_extra(self):
        self.resolved.side_effect = viewers.absent('web')
        line = self.refused(default_args(web=True))
        self.assertIn('pip install "machinome[viewer]"', line)

    def test_explicit_web_uses_the_same_browser_viewer(self):
        self.run_develop(default_args(web=True))
        self.web.serve.assert_called_once_with(BUILD_DIR)

    def test_the_viewer_flag_names_the_viewer(self):
        self.run_develop(default_args(viewer='web'))
        self.web.serve.assert_called_once_with(BUILD_DIR)

    def test_a_viewer_that_does_not_serve_is_refused_by_name(self):
        line = self.refused(default_args(viewer='openscad'))
        self.assertEqual(
            line,
            'Error: machinome develop needs a viewer that can serve, and the '
            'openscad viewer cannot; the viewers that can: web')

    def test_an_unknown_viewer_is_refused(self):
        line = self.refused(default_args(viewer='povray'))
        self.assertEqual(line, "Error: no viewer is named 'povray'; the "
                               'viewers are openscad, web')

    def test_web_with_another_viewer_is_an_argument_error(self):
        with redirect_stderr(io.StringIO()), \
                self.assertRaises(SystemExit) as raised:
            self.develop.handle(default_args(web=True, viewer='openscad'))
        self.assertEqual(raised.exception.code, 2)
        self.web.serve.assert_not_called()
        self.process.assert_not_called()

    def test_web_dev_serves_the_page_directly_and_says_so(self):
        with self.assertLogs('manager.develop', level='WARNING') as logged:
            self.run_develop(default_args(web_dev=True))
        self.web.serve.assert_called_once_with(BUILD_DIR)
        self.assertIn(
            '--web-dev no longer does anything: the development page is '
            'served directly, with no separate frontend process.',
            '\n'.join(logged.output))

    def test_debug_web_is_no_longer_an_option(self):
        parser = argparse.ArgumentParser()
        Develop().add_arguments(parser)
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(['--debug-web'])

    def test_the_options(self):
        parser = argparse.ArgumentParser()
        Develop().add_arguments(parser)
        args = parser.parse_args(['--viewer', 'web'])
        self.assertEqual(args.viewer, 'web')
        self.assertIsNone(parser.parse_args([]).viewer)

    def test_a_server_that_cannot_listen_is_one_line(self):
        self.web.serve.side_effect = viewers.ViewerError(
            'the web viewer cannot serve on port 8000: Address already in '
            'use')
        with redirect_stderr(io.StringIO()) as errors, \
                self.assertRaises(SystemExit) as raised:
            self.develop.handle(default_args())
        self.assertEqual(raised.exception.code, 1)
        self.assertEqual(errors.getvalue(),
                         'Error: the web viewer cannot serve on port 8000: '
                         'Address already in use\n')
        self.process.assert_not_called()


class ViewerSessionLifecycleTest(DevelopHarness):

    def test_first_run_failure_stops_the_session_and_exits(self):
        builder = MagicMock(exitcode=1)
        builder.join.return_value = None
        self.process.side_effect = [builder]
        with self.assertRaises(SystemExit):
            self.develop.handle(default_args())
        self.assertEqual(self.process.call_args_list, [
            call(target=run_builder, args=('.', [], False, None, 'web')),
        ])
        self.session.stop.assert_called_once_with()
        self.session.reload.assert_not_called()

    def test_each_rebuild_reloads_the_open_pages_in_place(self):
        self.run_develop(default_args(), BuildOutcome.RENDERED.value,
                         BuildOutcome.SOURCE_CHANGED.value)
        # Served once; told twice that a build was published, once per
        # builder that went before; stopped once by the interrupt.
        self.web.serve.assert_called_once_with(BUILD_DIR)
        self.assertEqual(self.session.reload.call_count, 2)
        self.session.stop.assert_called_once_with()

    def test_first_builder_invocation_is_not_flagged_as_reload(self):
        self.run_develop(default_args())
        self.assertEqual(self.process.call_args_list[0],
                         call(target=run_builder,
                              args=('.', [], False, None, 'web')))

    def test_second_builder_invocation_is_flagged_as_reload(self):
        self.run_develop(default_args(), 0)
        self.assertEqual(self.process.call_args_list[1],
                         call(target=run_builder,
                              args=('.', [], True, None, 'web')))

    def test_callback_is_passed_to_the_builder(self):
        self.run_develop(default_args(callback='http://listener/build-ready'))
        self.assertEqual(self.process.call_args_list[0], call(
            target=run_builder,
            args=('.', [], False, 'http://listener/build-ready', 'web'),
        ))

    def test_the_builder_is_handed_the_chosen_viewer(self):
        with patch('machinome.manager.develop.Builder') as builder:
            run_builder('.', [], False, None, 'web')
        self.assertEqual(builder.call_args.kwargs['viewer'], 'web')

    def test_develop_runs_no_viewer_program(self):
        import machinome.manager.develop as module
        source = Path(module.__file__).read_text()
        self.assertNotIn('Popen', source)
        self.assertNotIn('machinome.viewer.web', source)


class NoWebModeTest(DevelopHarness):
    """`--no-web` runs the builder watch loop alone, for a host that
    publishes its own view of the completed build directory."""

    def test_no_web_starts_the_builder_without_a_viewer(self):
        self.run_develop(default_args(no_web=True))
        self.web.serve.assert_not_called()
        self.assertEqual(self.process.call_args_list, [
            call(target=run_builder, args=('.', [], False, None, None)),
        ])

    def test_no_web_does_not_need_the_viewer_or_openscad(self):
        self.resolved.side_effect = viewers.absent('web')
        self.run_develop(default_args(no_web=True))
        self.resolved.assert_not_called()
        self.assertEqual(self.process.call_count, 1)

    def test_no_web_passes_the_callback_to_the_builder(self):
        self.run_develop(default_args(no_web=True, callback='http://listener/build-ready'))
        self.assertEqual(self.process.call_args_list, [
            call(target=run_builder,
                 args=('.', [], False, 'http://listener/build-ready', None)),
        ])

    def test_no_web_reload_cycle_reloads_no_viewer(self):
        self.run_develop(default_args(no_web=True), BuildOutcome.SOURCE_CHANGED.value)
        self.web.serve.assert_not_called()
        self.session.reload.assert_not_called()
        self.assertEqual(self.process.call_args_list, [
            call(target=run_builder, args=('.', [], False, None, None)),
            call(target=run_builder, args=('.', [], True, None, None)),
        ])

    def test_no_web_rejects_an_explicit_web_request(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.develop.handle(default_args(no_web=True, web_dev=True))
        self.web.serve.assert_not_called()

    def test_no_web_rejects_the_explicit_web_spelling(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.develop.handle(default_args(no_web=True, web=True))
        self.web.serve.assert_not_called()


class CallbackValidationTest(DevelopHarness):

    def test_web_dev_rejects_callback_before_any_process(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.develop.handle(default_args(
                web_dev=True, callback='http://listener/build-ready'))
        self.web.serve.assert_not_called()
        self.process.assert_not_called()


class TakenPortTest(TestCase):
    """(`viewer-seam`) The web viewer serves in this process: a port another
    listener holds is refused by `serve` at once, and the command writes
    one line and exits 1, starting no builder."""

    def test_a_taken_port_is_one_line_and_exit_one(self):
        from machinome.viewer.web.bundle import has_bundle
        if not has_bundle():
            self.skipTest('machinome-viewer has no built bundle')
        held = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(held.close)
        held.bind(('0.0.0.0', 0))
        held.listen()
        port = held.getsockname()[1]
        project = tempfile.mkdtemp(prefix='develop-taken-port-')
        self.addCleanup(shutil.rmtree, project, ignore_errors=True)
        Path(project, 'pyproject.toml').write_text(
            '[tool.machinome]\nmodel = "demo:Demo"\n')
        environment = dict(os.environ, MACHINOME_PORT=str(port),
                           SOLID_BUILD_DIR=os.path.join(project, '_build'))
        started = time.monotonic()
        run = subprocess.run(
            [sys.executable, '-c',
             'from machinome.cli import manage; manage()', 'develop'],
            cwd=project, env=environment, capture_output=True, text=True,
            timeout=120)
        elapsed = time.monotonic() - started
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        errors = [line for line in run.stderr.splitlines()
                  if line.startswith('Error:')]
        self.assertEqual(
            errors, [f'Error: the web viewer cannot serve on port {port}: '
                     'Address already in use'], run.stderr)
        self.assertFalse(os.path.exists(os.path.join(project, '_build',
                                                     'viewer.json')))
        self.assertLess(elapsed, 30)
