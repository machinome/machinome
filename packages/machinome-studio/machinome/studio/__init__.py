# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Machinome Studio's floor: the local service a maker opens a project in.

Run ``machinome-studio --projects-dir PATH`` to serve the project hub over
a folder of projects and, for each project opened from it, a session of its
own: the agents its profile declares, the model build and watch, the
browser viewer and the conversation. The project folder and the port may
also come from a studio configuration file. ``python -m floor`` serves the
same hub without agents. The manual under ``docs/`` describes both.
"""

from .app import create_app

__all__ = ["create_app"]
