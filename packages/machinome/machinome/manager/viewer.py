# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Reports the installed viewer as JSON, and serves or photographs through a
viewer.

`machinome viewer` with no verb prints the web viewer's report, asked
through the seam of viewers `machinome.viewer` (OpenSpec change
`viewer-seam`). Its verbs `describe`, `serve` and `capture` are the viewer's
command: each asks the seam for the viewer its `--viewer` names, else `web`,
requiring the operation the verb needs, and a viewer that cannot perform it
is refused by name, never replaced. The command takes no node path and reads
no project manifest: it acts on the installation and on the directories it
is given (OpenSpec change `viewer-command`, ADR-196).

Only the standard library is imported here; the seam is imported when the
command runs, so the help of the command and of its verbs loads no viewer.
"""

import argparse
import json
import os
import signal
import sys
import time

#: The operation each verb asks the seam for.
OPERATIONS = {'describe': 'embed', 'serve': 'serve', 'capture': 'capture'}

#: What `capture` needs beyond the operation: the staging directory holds a
#: published document, which a viewer that reads none cannot photograph.
PUBLISHED = 'photograph a published document'

#: Every refusal of the seam and of a viewer's report: the sentence goes to
#: standard error, nothing to standard output.
REFUSALS = (ImportError, LookupError, RuntimeError, OSError)


def _triple(text):
    values = [float(value) for value in text.split(',')]
    if len(values) != 3:
        raise argparse.ArgumentTypeError('expected three comma-separated numbers')
    return tuple(values)


def _view(text):
    values = [float(value) for value in text.split(',')]
    if len(values) != 6:
        raise argparse.ArgumentTypeError(
            'expected six comma-separated numbers: eye x,y,z then target x,y,z')
    return tuple(values[:3]), tuple(values[3:])


def _imgsize(text):
    try:
        width, height = (int(value) for value in text.lower().split('x'))
    except ValueError:
        raise argparse.ArgumentTypeError('expected WIDTHxHEIGHT')
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError('expected positive dimensions')
    return width, height


def refuse(error):
    """Write a refusal on standard error and exit 1."""
    sys.stderr.write(f'{error}\n')
    sys.exit(1)


class Viewer:
    """Reports the installed viewer as JSON, and serves or photographs
    through a viewer."""

    needs_node = False

    def add_arguments(self, parser):
        verbs = parser.add_subparsers(dest='verb', title='Verbs')
        describe = verbs.add_parser(
            'describe',
            help="Print the viewer's bundle path, export page, API and "
                 "document versions as JSON, as machinome viewer does")
        serve = verbs.add_parser(
            'serve',
            help='Serve a published build directory to the development page')
        serve.add_argument('--build-dir', required=True,
                           help='The published build directory to serve')
        serve.add_argument('--port', type=int, default=None,
                           help='Port to listen on (default: MACHINOME_PORT '
                                'or 8000)')
        capture = verbs.add_parser(
            'capture',
            help='Photograph a staged document into a transparent PNG')
        capture.add_argument('staging',
                             help='Directory holding viewer.json and the '
                                  'model files it names')
        capture.add_argument('-o', '--output', required=True,
                             help='PNG to write')
        capture.add_argument('--imgsize', type=_imgsize, default=(1920, 1080),
                             metavar='WxH',
                             help='Image size (default: 1920x1080)')
        capture.add_argument('--time', type=float, default=0.0,
                             help='Animation time, 0.0 to 1.0 (default: 0.0)')
        capture.add_argument('--view', type=_view, default=None,
                             metavar='EYE,TARGET',
                             help='Camera eye and target: ex,ey,ez,tx,ty,tz')
        capture.add_argument('--up', type=_triple, default=None,
                             metavar='X,Y,Z', help='Camera up direction')
        capture.add_argument('--fov', type=float, default=None,
                             help='Vertical field of view in degrees')
        for verb in (describe, serve, capture):
            verb.add_argument('--viewer', default='web', metavar='NAME',
                              help='The viewer to ask (default: web)')

    def handle(self, args):
        verb = getattr(args, 'verb', None)
        if verb is None:
            # The web viewer's report, unchanged (`viewer-seam`).
            return self.describe('web', 'machinome viewer')
        needed_by = f'machinome viewer {verb}'
        if verb == 'describe':
            return self.describe(args.viewer, needed_by)
        if verb == 'serve':
            return self.serve(args, needed_by)
        return self.capture(args, needed_by)

    def describe(self, name, needed_by):
        from machinome import viewer as viewers
        try:
            report = viewers.require(name, 'embed', needed_by).describe()
        except REFUSALS as error:
            refuse(error)
        print(json.dumps(report))

    def serve(self, args, needed_by):
        from machinome import viewer as viewers
        try:
            provider = viewers.require(args.viewer, 'serve', needed_by)
        except REFUSALS as error:
            refuse(error)
        try:
            session = provider.serve(args.build_dir, port=args.port)
        except viewers.ViewerError as error:
            refuse(f'Error: {error}')
        wait(session)

    def capture(self, args, needed_by):
        if not 0.0 <= args.time <= 1.0:
            sys.stderr.write(f'Error: --time must be between 0.0 and 1.0, '
                             f'got {args.time}\n')
            sys.exit(2)
        from machinome import viewer as viewers
        try:
            provider = viewers.require(args.viewer, 'capture', needed_by)
            versions = provider.document_versions()
        except REFUSALS as error:
            refuse(error)
        if versions is None:
            refuse(unpublished(viewers, args.viewer, needed_by))
        eye, target = args.view if args.view is not None else (None, None)
        width, height = args.imgsize
        request = viewers.CaptureRequest(
            imgsize=f'{width}x{height}', time=args.time, eye=eye,
            target=target, up=args.up, fov=args.fov)
        # The staging directory is the caller's: it is photographed in
        # place and never withdrawn.
        try:
            provider.capture(args.staging, request, args.output)
        except viewers.ViewerError as error:
            refuse(f'Error: {error}')


def unpublished(viewers, name, needed_by):
    """The seam's sentence for a viewer that lacks what a verb needs, for a
    viewer that captures but reads no published document: the viewers that
    can are those that capture and read one."""
    able = []
    for known in sorted(viewers.EXTRAS):
        try:
            provider = viewers.viewer(known)
            if ('capture' in provider.OPERATIONS
                    and provider.document_versions() is not None):
                able.append(known)
        except REFUSALS:
            continue
    return (f'{needed_by} needs a viewer that can {PUBLISHED}, and the '
            f'{name} viewer cannot; the viewers that can: '
            f'{", ".join(able) or "none is installed"}')


def wait(session):
    """Serve until interrupted: an interrupt from the terminal stops the
    session and returns; a termination signal stops it and ends the process
    by that signal, as the server's own handling ended it before."""
    terminated = []

    def terminate(signum, frame):
        terminated.append(signum)
        raise KeyboardInterrupt

    previous = signal.signal(signal.SIGTERM, terminate)
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        session.stop()
        signal.signal(signal.SIGTERM, previous)
    if terminated:
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        os.kill(os.getpid(), signal.SIGTERM)
