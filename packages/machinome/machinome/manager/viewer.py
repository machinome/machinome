# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Reports the installed viewer bundle and its API version as JSON."""

import json
import sys

from machinome import viewer as viewers


class Viewer:
    """Reports the installed viewer bundle and its API version as JSON."""

    needs_node = False

    def add_arguments(self, parser):
        pass

    def handle(self, args):
        # The web viewer's report, asked through the seam: every refusal on
        # standard error, nothing on standard output (`viewer-seam`).
        try:
            report = viewers.require('web', 'embed',
                                     'machinome viewer').describe()
        except (ImportError, LookupError, RuntimeError, OSError) as error:
            sys.stderr.write(f'{error}\n')
            sys.exit(1)
        print(json.dumps(report))
