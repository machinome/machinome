# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import json

from machinome.node.assembly import AssemblyNode

LOAD = json.load


class Machine(AssemblyNode):
    pass
