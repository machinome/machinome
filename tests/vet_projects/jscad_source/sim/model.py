# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.node import AssemblyNode
from machinome.node import JScadNode


class Part(JScadNode):
    jscad_source = 'part.jscad'


class Machine(AssemblyNode):
    pass
