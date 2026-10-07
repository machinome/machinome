# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A library facade beside the nodes, defining nothing of its own.

Like 3DPrintedClocks' `clocks/__init__.py`, it re-exports every name of
its modules, so a node importing from the package runs this file and,
through it, the module that defines the name.
"""

from .measures import *  # noqa: F401,F403
