# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node.assembly import AssemblyNode
from .bolt import RepeatedBolt
from .bushings import BushingA, BushingB


class PiecesAssembly(AssemblyNode):

    def render(self):
        return [
            RepeatedBolt().translate([0, 0, 0]),
            RepeatedBolt().translate([10, 0, 0]),
            RepeatedBolt().translate([20, 0, 0]),
            BushingA(),
            BushingB(),
        ]
