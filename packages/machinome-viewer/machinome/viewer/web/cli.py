# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The ``solid-node-viewer`` command: describe, serve, capture.

These three commands are how solid-node uses the viewer. ``describe`` is
the same answer the ``solid_node.viewer`` entry point gives, for a caller
that would rather not import anything; ``serve`` is the process
``solid develop`` launches beside its builder; ``capture`` is the process
``solid snapshot --renderer web`` launches on its staged document.
"""

import argparse
import json
import sys

from solid_node_viewer.bundle import BundleMissing, describe


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
        prog='solid-node-viewer',
        description='The browser viewer for solid-node models.',
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
                       help='Port to listen on (default: SOLID_NODE_PORT or 8000)')
    serve.add_argument('--dev', action='store_true',
                       help='Proxy the page to the app\'s npm dev server instead of '
                            'serving the built app (for working on the viewer)')
    serve.add_argument('--frontend-port', type=int, default=None,
                       help='The npm dev server port proxied by --dev '
                            '(default: SOLID_NODE_FRONTEND_PORT or 3000)')
    serve.add_argument('--start-frontend', action='store_true',
                       help='Also start the npm dev server (implies --dev)')

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
    try:
        print(json.dumps(describe()))
    except BundleMissing as error:
        sys.stderr.write(f'{error}\n')
        return 1
    return 0


def run_serve(args):
    from multiprocessing import Process
    from solid_node_viewer.server import WebDevServer, WebViewer

    dev = args.dev or args.start_frontend
    frontend = None
    if args.start_frontend:
        frontend = Process(target=WebDevServer(port=args.frontend_port).start)
        frontend.start()
    try:
        WebViewer(args.build_dir, dev=dev, port=args.port,
                  frontend=args.frontend_port).start()
    finally:
        if frontend is not None:
            frontend.terminate()
            frontend.join()
    return 0


def run_capture(args):
    from solid_node_viewer.capture import Capture, CaptureError, mount_options

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
