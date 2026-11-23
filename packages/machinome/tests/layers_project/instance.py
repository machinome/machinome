# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A node that assigns `layers` on the instance, which is refused."""

from solid2 import cube

from machinome.node.assembly import AssemblyNode
from machinome.node.solid2 import Solid2Node

from .layers import ELECTRICAL


class Assigning(Solid2Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layers = ELECTRICAL

    def render(self):
        return cube(2)


class Assigned(AssemblyNode):
    contact = Assigning()
