# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node.assembly import AssemblyNode
from .parts import Cube


class TwoArbors(AssemblyNode):
    """Red fixture: two instances of ONE class, `centre` and `third`,
    each holding a `wheel` and a `rod`, with the two wheels overlapping.
    Every leaf name repeats, so only a node's path below the node under
    test tells the two wheels apart in a failure message (OpenSpec change
    `name-solids-by-path`, from 3DPrintedClocks' mantel clock 34). No
    child is given `name=`: the names are the ones the tree derives."""

    def __init__(self):
        self.centre = TrainArbor()
        self.third = TrainArbor()
        super().__init__()
        self.third.translate([2, 0, 0])

    def render(self):
        return [self.centre, self.third]


class TrainArbor(AssemblyNode):

    def __init__(self):
        self.wheel = Cube(4.0)
        self.rod = Cube(1.0)
        super().__init__()
        self.rod.translate([0, 0, 10])

    def render(self):
        return [self.wheel, self.rod]
