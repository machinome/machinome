# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""`machinome studio`, the command this package contributes through the
entry-point group `machinome.commands` (framework ADR-189, change
`join-studio`).

The module imports the standard library alone, so `machinome -h` pays for
it only the class; `handle` imports the orchestrator, which starts the hub
as `python -m machinome.studio.orchestrator` does.
"""

import argparse
from pathlib import Path


class Studio:
    """Open the studio: the project hub and its agents, in the browser"""

    needs_node = False

    def add_arguments(self, parser):
        parser.add_argument(
            '--projects-dir', type=Path, default=None, metavar='PATH',
            help='exact directory containing project repositories (default: '
                 "the studio configuration file's projects key)")
        parser.add_argument(
            '--port', type=int, default=None, metavar='PORT',
            help="local browser port (default: FLOOR_PORT, the configuration "
                 "file's port, else 9000)")
        # The launcher's own two options, hidden from its help as there.
        parser.add_argument('--machinome-command', help=argparse.SUPPRESS)
        parser.add_argument('--backend-command', action='append', default=[],
                            metavar='BACKEND=COMMAND', help=argparse.SUPPRESS)

    def handle(self, args):
        from machinome.studio import orchestrator

        orchestrator.run(args)
