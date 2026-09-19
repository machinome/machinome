# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The ``machinome-viewer`` command: describe, serve, capture.

These three commands are how machinome uses the viewer. ``describe`` is
the same answer the ``machinome.viewer`` entry point gives, for a caller
that would rather not import anything; ``serve`` is the process
``machinome develop`` launches beside its builder; ``capture`` is the process
``machinome snapshot --renderer web`` launches on its staged document.
"""

import argparse
import json
import logging
import sys

from machinome_viewer.bundle import BundleMissing, BundleStale, describe

logger = logging.getLogger('viewer.cli')

# The development page is a static file this package carries; there is
# no second frontend process to start or proxy any more (design D13,
# D14). A released machinome's `machinome develop --web-dev` still passes
# `--start-frontend` (`machinome/manager/develop.py:49-51`), so these
# three flags go on being ACCEPTED, changing nothing, so that command
# keeps working rather than turning into an argparse error on a flag the
# maker never typed. This is a compatibility promise, not an oversight:
# a later change must not remove them as unused.
FRONTEND_FLAG_NOTICE = (
    '%s no longer does anything: the development page is served '
    'directly, with no separate frontend process.'
)


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


def build_parser():
    parser = argparse.ArgumentParser(
        prog='machinome-viewer',
        description='The browser viewer for machinome models.',
    )
    commands = parser.add_subparsers(dest='command', title='Commands')

    commands.add_parser(
        'describe',
        help='Print the installed bundle path, export page and API version as JSON',
    )

    serve = commands.add_parser(
        'serve', help='Serve a published build directory to the development app')
    serve.add_argument('--build-dir', required=True,
                       help='The published build directory to serve')
    serve.add_argument('--port', type=int, default=None,
                       help='Port to listen on (default: MACHINOME_PORT or 8000)')
    serve.add_argument('--dev', action='store_true',
                       help='Deprecated, accepted and ignored: the development page is '
                            'served directly, with no npm dev server to proxy to')
    serve.add_argument('--frontend-port', type=int, default=None,
                       help='Deprecated, accepted and ignored: there is no frontend '
                            'process left to configure')
    serve.add_argument('--start-frontend', action='store_true',
                       help='Deprecated, accepted and ignored: there is no npm dev '
                            'server left to start')

    capture = commands.add_parser(
        'capture',
        help='Photograph a staged document into a transparent PNG',
    )
    capture.add_argument('staging',
                         help='Directory holding viewer.json and the model files it names')
    capture.add_argument('-o', '--output', required=True, help='PNG to write')
    capture.add_argument('--imgsize', type=_imgsize, default=(1920, 1080),
                         metavar='WxH', help='Image size (default: 1920x1080)')
    capture.add_argument('--time', type=float, default=0.0,
                         help='Animation time, 0.0 to 1.0 (default: 0.0)')
    capture.add_argument('--view', type=_view, default=None, metavar='EYE,TARGET',
                         help='Camera eye and target: ex,ey,ez,tx,ty,tz')
    capture.add_argument('--up', type=_triple, default=None, metavar='X,Y,Z',
                         help='Camera up direction')
    capture.add_argument('--fov', type=float, default=None,
                         help='Vertical field of view in degrees')
    return parser


def run_describe(args):
    # `BundleStale` joins `BundleMissing` with ADR-059: the two ways this
    # package declines to answer for a bundle, reported the same way --
    # the reason and the remedy on stderr, nothing on stdout, non-zero.
    # A caller parses stdout, so a refusal must never put prose there.
    try:
        described = describe()
    except (BundleMissing, BundleStale) as error:
        sys.stderr.write(f'{error}\n')
        return 1
    print(json.dumps(described))
    return 0


def run_serve(args):
    from machinome_viewer.server import WebViewer

    for flag, given in (
        ('--dev', args.dev),
        ('--start-frontend', args.start_frontend),
        ('--frontend-port', args.frontend_port is not None),
    ):
        if given:
            logger.warning(FRONTEND_FLAG_NOTICE, flag)
    WebViewer(args.build_dir, dev=args.dev, port=args.port,
              frontend=args.frontend_port).start()
    return 0


def run_capture(args):
    from machinome_viewer.capture import Capture, CaptureError, mount_options

    if not 0.0 <= args.time <= 1.0:
        sys.stderr.write(f'Error: --time must be between 0.0 and 1.0, got {args.time}\n')
        return 2
    options = mount_options(time=args.time, view=args.view, up=args.up, fov=args.fov)
    try:
        Capture(args.staging).render(args.output, args.imgsize, options)
    except CaptureError as error:
        sys.stderr.write(f'Error: {error}\n')
        return 1
    return 0


COMMANDS = {
    'describe': run_describe,
    'serve': run_serve,
    'capture': run_capture,
}


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    return COMMANDS[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
