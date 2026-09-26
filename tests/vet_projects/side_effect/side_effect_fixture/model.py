# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

import os

from machinome.node import AssemblyNode

MARKER = os.path.join(os.path.dirname(__file__), 'marker')
with open(MARKER, 'w') as stream:
    stream.write('imported')


class Machine(AssemblyNode):
    pass
