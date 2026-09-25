# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""The browser viewer for machinome models, packaged for pip.

The package carries the built ``machinome-viewer.js`` bundle, the standalone
export page, the development app and the development server that serves a
published build to it, and the headless browser capture behind
``machinome snapshot --renderer web``. machinome reaches all of it through
one entry point and three commands; it never imports this package's code.
"""

__version__ = "0.7.0"
