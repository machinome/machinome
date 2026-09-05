# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""``python -m solid_node_viewer``: the console script, through an interpreter.

solid-node runs the viewer this way so that the viewer installed beside the
interpreter running ``solid`` is the one used, whatever else is on the PATH.
"""

import sys

from solid_node_viewer.cli import main

sys.exit(main())
