# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.node import AssemblyNode
import os

from machinome.node import StepNode

HERE = os.path.dirname(__file__)


class Part(StepNode):
    step_source = os.path.join(HERE, 'x.step')


class Machine(AssemblyNode):
    pass
