# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Machinome Studio: the project hub and the floor a maker opens a project in.

Run ``machinome studio --projects-dir PATH`` to serve the project hub over a
folder of projects and, for each project opened from it, a session of its
own: the agents its profile declares, the model build and watch, the browser
viewer and the conversation. The project folder and the port may also come
from a studio configuration file. ``python -m machinome.studio`` serves the
same hub without agents. The Machinome manual describes both.

The root reads ``create_app`` from its module on first use, so ``machinome
-h`` and the package's build hooks load none of the application.
"""

__all__ = ["create_app"]


def __getattr__(name):
    if name == "create_app":
        from .app import create_app

        return create_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
