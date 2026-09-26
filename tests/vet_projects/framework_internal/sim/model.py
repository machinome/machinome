# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.node import AssemblyNode
from machinome.core.loader import load_node
import machinome.core.expressions
import machinome.node
import machinome.simulation
import machinome.motion
import machinome.exact
import machinome.openscad

BUILDER = machinome.core.builder.Builder
LOADED = load_node


class Machine(AssemblyNode):
    pass
