# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The browser viewer for solid-node models, packaged for pip.

The package carries the built ``solid-widget.js`` bundle, the standalone
export page, the development app and the development server that serves a
published build to it, and the headless browser capture behind
``solid snapshot --renderer web``. solid-node reaches all of it through
one entry point and three commands; it never imports this package's code.
"""

__version__ = "0.2.0"
