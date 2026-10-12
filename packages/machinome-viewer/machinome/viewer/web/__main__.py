# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""``python -m machinome.viewer.web``: the console script, through an interpreter.

machinome runs the viewer this way so that the viewer installed beside the
interpreter running ``solid`` is the one used, whatever else is on the PATH.
"""

import sys

from machinome.viewer.web.cli import main

sys.exit(main())
