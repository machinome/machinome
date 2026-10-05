# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node.assembly import AssemblyNode
import sys

sys.path.insert(0, 'upstream')
from sys import path  # noqa: E402


class Machine(AssemblyNode):
    pass
