# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""``python -m machinome.viewer.web``: the console script, through an interpreter.

Running it this way uses the viewer installed beside that interpreter,
whatever else is on the PATH. The framework itself runs no program of the
viewer's: it reaches the package through its seam of viewers.
"""

import sys

from machinome.viewer.web.cli import main

sys.exit(main())
