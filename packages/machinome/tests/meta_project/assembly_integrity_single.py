# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from .parts import Cube


class AssemblyIntegritySingle(Cube):
    """A rigid root is already a valid one-piece assembly selection."""
