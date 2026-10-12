# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import sys
import logging
from machinome import viewer as viewers
from machinome.core.loader import ProjectManifestError, load_node, select_model
from machinome.core.export import (
    ExportModelPathError, WidgetBundleMissing, embedder, export_node,
)
from machinome.manifest import reference_origin


logger = logging.getLogger('manager.export')


class Export:
    """Exports a node as a static embeddable artifact: manifest.json
    plus the STL meshes, ready to be served by any static file host."""

    needs_node = True

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--output',
            type=str,
            default='export',
            help='Output directory (default: export)',
        )
        parser.add_argument(
            '--fps',
            type=int,
            default=30,
            help='Animation frames per second (default: 30)',
        )
        parser.add_argument(
            '--frames',
            type=int,
            default=360,
            help='Number of frames in one animation cycle, '
                 'the resolution of $t (default: 360)',
        )
        parser.add_argument(
            '--viewer',
            metavar='NAME',
            default=None,
            help='The viewer whose files the export embeds (default: the '
                 f"project's viewer, else {viewers.DEFAULTS['embed']})",
        )
        parser.add_argument(
            '--no-widget',
            dest='widget',
            action='store_false',
            help='Export only manifest and models, without the '
                 'embeddable viewer (index.html + machinome-viewer.js)',
        )

    def handle(self, args):
        # The viewer whose files the export embeds, chosen and asked before
        # anything is loaded or written; `--no-widget` asks none.
        viewer = None
        if args.widget:
            try:
                try:
                    viewer = viewers.resolve(
                        'embed', 'machinome export',
                        getattr(args, 'viewer', None),
                        reference_origin(args.path)).NAME
                except ImportError as absent:
                    raise WidgetBundleMissing(absent) from None
                embedder(viewer)
            except (WidgetBundleMissing, LookupError, RuntimeError,
                    ProjectManifestError) as error:
                sys.stderr.write(f'Error: {error}\n')
                sys.exit(1)

        try:
            selection = select_model(args.path)
            selection.anchor()
            node = load_node(selection.reference,
                             overrides=getattr(args, 'set', None))
        except Exception as e:
            sys.stderr.write(f'Error loading node: {e}\n')
            sys.exit(1)

        try:
            export_node(node, args.output,
                        fps=args.fps, frames=args.frames,
                        widget=args.widget, viewer=viewer)
        except (ExportModelPathError, WidgetBundleMissing) as error:
            sys.stderr.write(f'Error: {error}\n')
            sys.exit(1)

        print(f'Exported to {args.output}')
