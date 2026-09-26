# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Checks, statically, that the project stays inside the machinome
universe."""

import sys


class Vet:
    """Checks, statically, that the project stays inside the machinome
    universe."""

    # Vet constructs no node: it declares its own reference, takes no
    # --set, and with no reference vets every declared model rather than
    # the default one.
    needs_node = False

    def add_arguments(self, parser):
        parser.add_argument(
            'reference', nargs='?',
            help='A declared model name, package.module:Class, '
                 'path/to/file.py, or path/to/file.py:Class; every declared '
                 'model when omitted')
        parser.add_argument(
            '--tests', action='store_true',
            help='Also vet the companion tests of every vetted module, and '
                 'their closures')
        parser.add_argument(
            '--json', action='store_true',
            help='Print one JSON object a host can read')

    def handle(self, args):
        # Imported here, not at module scope, so `machinome -h` pays for
        # none of it; vet imports no kernel and no node module either way.
        from machinome.manifest import ProjectManifestError
        from machinome.vet import CannotVet, render_json, render_text, vet

        try:
            report = vet(reference=args.reference, tests=args.tests)
        except (ProjectManifestError, CannotVet) as error:
            sys.stderr.write(f'Error: {error}\n')
            sys.exit(2)
        sys.stdout.write(render_json(report) if args.json
                         else render_text(report))
        sys.exit(0 if report.pure else 1)
