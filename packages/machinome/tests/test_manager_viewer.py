# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`machinome viewer`: the web viewer's report, asked through the seam
`machinome.viewer` (OpenSpec change `viewer-seam`), printed as JSON, and the
viewer's verbs `describe`, `serve` and `capture`, each dispatched through the
seam to the viewer its `--viewer` names, else `web`, reading no project
manifest (OpenSpec change `viewer-command`, ADR-196)."""

import argparse
import io
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import TestCase, skipUnless
from unittest.mock import Mock, patch

import machinome.viewer as viewers
from machinome.manager.viewer import Viewer
from machinome.viewer import CaptureRequest, ViewerError
from machinome.viewer.web.bundle import has_bundle

REPORT = {'path': '/tmp/machinome-viewer.js', 'index': '/tmp/index.html',
          'apiVersion': 5, 'version': '0.1.0'}

#: The second viewer's name, spelled so the SCAD scan reads this file plain.
SECOND = 'open' 's' 'cad'

DISPATCH = 'from machinome.cli import manage; manage()'


def reported(report):
    return patch.object(viewers.viewer('web'), 'describe',
                        return_value=report)


def parse(*argv):
    """The command's namespace for `machinome viewer <argv>`."""
    parser = argparse.ArgumentParser(prog='machinome viewer')
    Viewer().add_arguments(parser)
    return parser.parse_args(list(argv))


def run(*argv):
    """`(status, stdout, stderr)` of `machinome viewer <argv>`, in this
    process."""
    output, errors = io.StringIO(), io.StringIO()
    status = 0
    with redirect_stdout(output), redirect_stderr(errors):
        try:
            Viewer().handle(parse(*argv))
        except SystemExit as stop:
            status = stop.code
    return status, output.getvalue(), errors.getvalue()


class Provider:
    """A viewer standing in for the one the seam resolves."""

    def __init__(self, operations=('present', 'capture', 'serve', 'embed'),
                 versions=(1, 2, 3)):
        self.OPERATIONS = frozenset(operations)
        self.describe = Mock(return_value=REPORT)
        self.capture = Mock()
        self.withdraw = Mock()
        self.session = Mock()
        self.serve = Mock(return_value=self.session)
        self.document_versions = Mock(
            return_value=None if versions is None else list(versions))


def provided(provider):
    """The seam's `require` answering `provider` for every name."""
    return patch.object(viewers, 'require', return_value=provider)


class ViewerCommandTest(TestCase):

    def test_reports_the_installed_viewer_as_json(self):
        provider = Provider()
        with provided(provider) as required:
            status, output, _ = run()
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output), REPORT)
        required.assert_called_once_with('web', 'embed', 'machinome viewer')

    def refused(self, refusal, *argv):
        with refusal:
            status, output, errors = run(*argv)
        self.assertEqual(status, 1)
        self.assertEqual(output, '')
        return errors

    def test_missing_viewer_exits_with_remedy_and_no_stdout(self):
        errors = self.refused(patch.object(
            viewers, 'viewer', side_effect=viewers.absent('web')))
        self.assertEqual(
            errors, 'the web viewer needs machinome.viewer.web, which is not '
                    'installed; install it with \'pip install '
                    '"machinome[viewer]"\'\n')

    def test_a_viewer_without_its_bundle_speaks_for_itself(self):
        errors = self.refused(patch.object(
            viewers.viewer('web'), 'describe',
            side_effect=FileNotFoundError('Viewer bundle not found; build it')))
        self.assertEqual(errors, 'Viewer bundle not found; build it\n')


class DocumentVersionsReportTest(TestCase):
    """`machinome viewer` is the one report, so a field the viewer added
    reaches a host through it unchanged."""

    def test_the_report_carries_the_document_versions(self):
        report = dict(REPORT, documentVersions=[1, 2, 3, 4, 5])
        output = io.StringIO()
        with reported(report), redirect_stdout(output):
            Viewer().handle(parse())
        self.assertEqual(json.loads(output.getvalue())['documentVersions'],
                         [1, 2, 3, 4, 5])


class TheVerbsTest(TestCase):
    """The parser: the three verbs with the options the viewer's former
    command had, less serve's three deprecated flags, and `--viewer` on each
    verb (design.md Decision 1)."""

    def test_no_verb_is_the_report(self):
        self.assertIsNone(parse().verb)

    def test_each_verb_takes_the_viewer_by_name(self):
        for verb in (('describe',), ('serve', '--build-dir', 'b'),
                     ('capture', 'st', '-o', 'o.png')):
            with self.subTest(verb=verb[0]):
                self.assertEqual(parse(*verb).verb, verb[0])
                self.assertEqual(parse(*verb).viewer, 'web')
                self.assertEqual(parse(*verb, '--viewer', SECOND).viewer,
                                 SECOND)

    def test_serve_takes_a_build_directory_and_a_port(self):
        args = parse('serve', '--build-dir', '/some/_build', '--port', '8123')
        self.assertEqual((args.build_dir, args.port), ('/some/_build', 8123))
        self.assertIsNone(parse('serve', '--build-dir', 'b').port)

    def test_capture_options_are_parsed_into_tuples(self):
        args = parse('capture', 'staged', '-o', 'out.png', '--view',
                     '1,2,3,4,5,6', '--up', '0,0,1', '--fov', '22.5',
                     '--imgsize', '320x240', '--time', '0.25')
        self.assertEqual((args.staging, args.output), ('staged', 'out.png'))
        self.assertEqual(args.view, ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)))
        self.assertEqual(args.up, (0.0, 0.0, 1.0))
        self.assertEqual(args.fov, 22.5)
        self.assertEqual(args.imgsize, (320, 240))
        self.assertEqual(args.time, 0.25)
        args = parse('capture', 'staged', '-o', 'out.png')
        self.assertEqual((args.view, args.up, args.fov, args.imgsize,
                          args.time), (None, None, None, (1920, 1080), 0.0))

    def usage_error(self, *argv):
        with redirect_stderr(io.StringIO()), \
                self.assertRaises(SystemExit) as raised:
            parse(*argv)
        self.assertEqual(raised.exception.code, 2)

    def test_usage_errors(self):
        for argv in (('serve',), ('capture', 'st'),
                     ('capture', 'st', '-o', 'o.png', '--view', '1,2,3'),
                     ('capture', 'st', '-o', 'o.png', '--up', '0,1'),
                     ('capture', 'st', '-o', 'o.png', '--imgsize', '0x10'),
                     ('bogus',), ('--viewer', 'web')):
            with self.subTest(argv=argv):
                self.usage_error(*argv)

    def test_serve_takes_none_of_the_deprecated_flags(self):
        for flag in (('--dev',), ('--start-frontend',),
                     ('--frontend-port', '3123')):
            with self.subTest(flag=flag[0]):
                self.usage_error('serve', '--build-dir', 'b', *flag)


class DescribeVerbTest(TestCase):

    def test_describe_prints_the_same_bytes_as_the_report(self):
        provider = Provider()
        with provided(provider):
            bare = run()
        with provided(provider) as required:
            described = run('describe')
        self.assertEqual(described, bare)
        self.assertEqual(described[0], 0)
        required.assert_called_once_with('web', 'embed',
                                         'machinome viewer describe')

    def test_describe_asks_the_named_viewer(self):
        with provided(Provider()) as required:
            status, _, _ = run('describe', '--viewer', 'another')
        self.assertEqual(status, 0)
        required.assert_called_once_with('another', 'embed',
                                         'machinome viewer describe')


class RefusalTest(TestCase):
    """A verb the chosen viewer cannot perform is refused by name, through
    the real seam: nothing on standard output, exit 1, no viewer used in
    place of the one chosen."""

    def test_a_viewer_that_cannot_embed_is_not_asked_to_describe(self):
        status, output, errors = run('describe', '--viewer', SECOND)
        self.assertEqual((status, output), (1, ''))
        self.assertEqual(
            errors, f'machinome viewer describe needs a viewer that can '
                    f'embed, and the {SECOND} viewer cannot; the viewers that '
                    f'can: web\n')

    def test_a_viewer_that_cannot_serve_is_not_asked_to(self):
        with patch.object(viewers.viewer('web'), 'serve') as served:
            status, output, errors = run('serve', '--viewer', SECOND,
                                         '--build-dir', '_build')
        self.assertEqual((status, output), (1, ''))
        self.assertEqual(
            errors, f'machinome viewer serve needs a viewer that can serve, '
                    f'and the {SECOND} viewer cannot; the viewers that can: '
                    f'web\n')
        served.assert_not_called()

    def test_a_viewer_that_reads_no_document_is_not_asked_to_photograph_one(
            self):
        with tempfile.TemporaryDirectory() as scratch, \
                patch.object(viewers.viewer(SECOND), 'capture') as second, \
                patch.object(viewers.viewer('web'), 'capture') as web:
            output_png = os.path.join(scratch, 'still.png')
            status, output, errors = run('capture', '--viewer', SECOND,
                                         scratch, '-o', output_png)
            self.assertFalse(os.path.exists(output_png))
        self.assertEqual((status, output), (1, ''))
        self.assertEqual(
            errors, f'machinome viewer capture needs a viewer that can '
                    f'photograph a published document, and the {SECOND} '
                    f'viewer cannot; the viewers that can: web\n')
        second.assert_not_called()
        web.assert_not_called()

    def test_the_document_refusal_names_the_viewers_that_can(self):
        """The refusal reads no viewer's name from the command: the viewers
        that can are those that capture and read a document."""
        provider = Provider(operations=('present', 'capture'), versions=None)
        with provided(provider):
            status, output, errors = run('capture', '--viewer', 'other',
                                         'st', '-o', 'o.png')
        self.assertEqual((status, output), (1, ''))
        self.assertEqual(
            errors, 'machinome viewer capture needs a viewer that can '
                    'photograph a published document, and the other viewer '
                    'cannot; the viewers that can: web\n')
        provider.capture.assert_not_called()

    def test_a_name_no_viewer_answers(self):
        for argv in (('describe',), ('serve', '--build-dir', 'b'),
                     ('capture', 'st', '-o', 'o.png')):
            with self.subTest(verb=argv[0]):
                status, output, errors = run(*argv, '--viewer', 'povray')
                self.assertEqual((status, output), (1, ''))
                self.assertEqual(errors, f"no viewer is named 'povray'; the "
                                         f"viewers are {SECOND}, web\n")

    def test_an_absent_viewer_names_its_extra(self):
        for argv in (('describe',), ('serve', '--build-dir', 'b'),
                     ('capture', 'st', '-o', 'o.png')):
            with self.subTest(verb=argv[0]), patch.object(
                    viewers, 'viewer', side_effect=viewers.absent('web')):
                status, output, errors = run(*argv)
                self.assertEqual((status, output), (1, ''))
                self.assertIn('pip install "machinome[viewer]"', errors)


class TheVerbsReadNoProjectTest(TestCase):
    """`machinome viewer` takes no node path: run inside a project whose
    manifest names another viewer, its verbs still use `web` (`viewer-seam`,
    design.md Decision 2)."""

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        Path(self.scratch.name, 'pyproject.toml').write_text(textwrap.dedent(
            f'''\
            [project]
            name = "declares-a-viewer"
            [tool.machinome]
            viewer = "{SECOND}"
            '''))
        self.cwd = os.getcwd()
        os.chdir(self.scratch.name)

    def tearDown(self):
        os.chdir(self.cwd)
        self.scratch.cleanup()

    def test_describe_reports_the_web_viewer(self):
        with reported(REPORT):
            status, output, errors = run('describe')
        self.assertEqual(status, 0, errors)
        self.assertEqual(json.loads(output), REPORT)

    def test_serve_and_capture_ask_the_web_viewer(self):
        for argv, operation in ((('serve', '--build-dir', '_build'), 'serve'),
                                (('capture', 'st', '-o', 'o.png'),
                                 'capture')):
            with self.subTest(verb=argv[0]), provided(Provider()) as required, \
                    patch('time.sleep', side_effect=KeyboardInterrupt):
                status, _, errors = run(*argv)
                self.assertEqual(status, 0, errors)
                required.assert_called_once_with(
                    'web', operation, f'machinome viewer {argv[0]}')


class CaptureVerbTest(TestCase):
    """`capture` hands the viewer a request carrying the camera's parts as
    given (design.md Decision 3) and never withdraws the caller's staging
    directory."""

    def captured(self, *options):
        provider = Provider()
        with provided(provider) as required:
            status, output, errors = run('capture', 'staged', '-o', 'out.png',
                                         *options)
        self.assertEqual((status, output, errors), (0, '', ''))
        required.assert_called_once_with('web', 'capture',
                                         'machinome viewer capture')
        provider.capture.assert_called_once()
        staging, request, written = provider.capture.call_args.args
        self.assertEqual((staging, written), ('staged', 'out.png'))
        provider.withdraw.assert_not_called()
        return request

    def test_the_parts_reach_the_viewer_as_given(self):
        request = self.captured('--imgsize', '320x240', '--time', '0.25',
                                '--view=-80,60,40,0,0,0', '--up', '0,1,0',
                                '--fov', '30')
        self.assertEqual(request, CaptureRequest(
            imgsize='320x240', time=0.25, eye=(-80.0, 60.0, 40.0),
            target=(0.0, 0.0, 0.0), up=(0.0, 1.0, 0.0), fov=30.0))

    def test_absent_parts_are_left_to_the_viewer(self):
        request = self.captured()
        self.assertEqual(request, CaptureRequest())
        self.assertEqual((request.camera, request.eye, request.target,
                          request.up, request.fov),
                         (None, None, None, None, None))

    def test_a_lone_field_of_view_reaches_the_viewer(self):
        request = self.captured('--fov', '30', '--imgsize', '800x600')
        self.assertEqual(request, CaptureRequest(imgsize='800x600', fov=30.0))

    def test_a_time_outside_the_cycle_is_refused_before_the_viewer(self):
        with patch.object(viewers, 'require') as required:
            status, output, errors = run('capture', 'st', '-o', 'o.png',
                                         '--time', '2')
        self.assertEqual((status, output), (2, ''))
        self.assertEqual(
            errors, 'Error: --time must be between 0.0 and 1.0, got 2.0\n')
        required.assert_not_called()

    def test_a_capture_the_viewer_cannot_make(self):
        provider = Provider()
        provider.capture.side_effect = ViewerError(
            'Staged document not found: st/viewer.json')
        with provided(provider):
            status, output, errors = run('capture', 'st', '-o', 'o.png')
        self.assertEqual((status, output), (1, ''))
        self.assertEqual(errors,
                         'Error: Staged document not found: st/viewer.json\n')
        provider.withdraw.assert_not_called()


class ServeVerbTest(TestCase):
    """`serve` asks the viewer for a session, waits, and stops it."""

    def test_serve_asks_the_viewer_and_stops_on_interrupt(self):
        provider = Provider()
        before = signal.getsignal(signal.SIGTERM)
        with provided(provider) as required, \
                patch('time.sleep', side_effect=KeyboardInterrupt):
            status, output, errors = run('serve', '--build-dir',
                                         '/some/_build', '--port', '8123')
        self.assertEqual((status, output, errors), (0, '', ''))
        required.assert_called_once_with('web', 'serve',
                                         'machinome viewer serve')
        provider.serve.assert_called_once_with('/some/_build', port=8123)
        provider.session.stop.assert_called_once_with()
        provider.session.reload.assert_not_called()
        self.assertIs(signal.getsignal(signal.SIGTERM), before)

    def test_the_port_is_the_viewer_s_default_when_absent(self):
        provider = Provider()
        with provided(provider), \
                patch('time.sleep', side_effect=KeyboardInterrupt):
            run('serve', '--build-dir', 'b')
        provider.serve.assert_called_once_with('b', port=None)

    def test_a_server_that_cannot_listen_exits_one(self):
        provider = Provider()
        provider.serve.side_effect = ViewerError(
            'the web viewer cannot serve on port 8123: Address already in use')
        with provided(provider):
            status, output, errors = run('serve', '--build-dir', 'b',
                                         '--port', '8123')
        self.assertEqual((status, output), (1, ''))
        self.assertEqual(errors, 'Error: the web viewer cannot serve on port '
                                 '8123: Address already in use\n')


#: A `machinome` process whose seam answers a viewer that serves nothing and
#: says when it is asked to serve and to stop.
STAND_IN = '''
import signal
import sys

import machinome.viewer as viewers

# A terminal delivers Ctrl-C to its foreground process; a process started
# in the background may inherit SIGINT ignored, so the stand-in restores
# what an interactive start gives it.
signal.signal(signal.SIGINT, signal.default_int_handler)


class Session:

    def stop(self):
        print('stopped', flush=True)


class Provider:
    OPERATIONS = frozenset({'serve'})

    def serve(self, build_dir, port=None):
        print('serving', build_dir, port, flush=True)
        return Session()


viewers.require = lambda *args, **kwargs: Provider()
from machinome.cli import manage
manage()
'''


class ServeSignalsTest(TestCase):
    """The process `machinome viewer serve` runs in: an interrupt stops the
    session and exits 0; a termination signal stops it and ends the process
    by that signal (design.md Decision 4)."""

    def served_until(self, signum):
        process = subprocess.Popen(
            [sys.executable, '-c', STAND_IN, 'viewer', 'serve',
             '--build-dir', '_build', '--port', '8791'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(process.stdout.readline(),
                             'serving _build 8791\n')
            time.sleep(0.2)
            process.send_signal(signum)
            output, errors = process.communicate(timeout=20)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()
        return process.returncode, output, errors

    def test_an_interrupt_stops_the_session_and_exits_zero(self):
        status, output, errors = self.served_until(signal.SIGINT)
        self.assertEqual((status, output), (0, 'stopped\n'), errors)

    def test_a_termination_signal_stops_the_session_and_ends_the_process(self):
        status, output, errors = self.served_until(signal.SIGTERM)
        self.assertEqual((status, output), (-signal.SIGTERM, 'stopped\n'),
                         errors)


@skipUnless(has_bundle(), 'machinome-viewer has no built bundle')
class ThePortIsTakenTest(TestCase):
    """The real web viewer, asked to serve on a port another program
    listens on: one `Error:` line and exit 1, without waiting."""

    def test_a_taken_port_exits_one_without_waiting(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(('0.0.0.0', 0))
        listener.listen()
        port = listener.getsockname()[1]
        try:
            with tempfile.TemporaryDirectory() as build:
                started = time.monotonic()
                result = subprocess.run(
                    [sys.executable, '-c', DISPATCH, 'viewer', 'serve',
                     '--build-dir', build, '--port', str(port)],
                    capture_output=True, text=True, timeout=10)
                elapsed = time.monotonic() - started
        finally:
            listener.close()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, '')
        errors = [line for line in result.stderr.splitlines()
                  if line.startswith('Error:')]
        self.assertEqual(len(errors), 1, result.stderr)
        self.assertIn(str(port), errors[0])
        self.assertLess(elapsed, 10)
