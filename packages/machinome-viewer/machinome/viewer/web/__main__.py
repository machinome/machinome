# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``python -m machinome_viewer``: the console script, through an interpreter.

machinome runs the viewer this way so that the viewer installed beside the
interpreter running ``solid`` is the one used, whatever else is on the PATH.
"""

import sys

from machinome_viewer.cli import main

sys.exit(main())
