# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Layers declared against alphabetical order: a node's keys are in the
order its classes declare them, base before subclass."""

from solid2 import cube

from machinome.node.solid2 import Solid2Node

from .layers import ELECTRICAL, MECHANICAL


class Pair(Solid2Node):
    layers = (MECHANICAL, ELECTRICAL)

    def render(self):
        return cube(2)


class Foundation(Solid2Node):
    layers = MECHANICAL

    def render(self):
        return cube(2)


class Topped(Foundation):
    layers = ELECTRICAL
