# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node.assembly import AssemblyNode
from solid2 import cylinder, translate
from . import TwoCylinders


class TwoCylindersTwice(AssemblyNode):

    def render(self):
        return [
            TwoCylinders(),
            TwoCylinders().rotate(180, [1, 0, 0]),
        ]
