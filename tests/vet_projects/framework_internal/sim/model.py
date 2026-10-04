# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node import AssemblyNode
from machinome.core.loader import load_node
import machinome.core.expressions
import machinome.node
import machinome.simulation
import machinome.motion
import machinome.occt.engine
import machinome.node.openscad

BUILDER = machinome.core.builder.Builder
LOADED = load_node


class Machine(AssemblyNode):
    pass
