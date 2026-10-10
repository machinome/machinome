# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A project using the exact stand-in beside the core's CadQuery leaf.

The native pin is fused into a CadQuery block, and compared with two
other CadQuery parts by exact assertions: one cutting half of it, one
clear of it.
"""

import cadquery as cq

from machinome.node.assembly import AssemblyNode
from machinome.node.cadquery import CadQueryNode
from machinome.node.fusion import FusionNode

from .exact_stand_in import NativeSolid


class Block(CadQueryNode):
    """The block the pin is fused into."""

    def render(self):
        return cq.Workplane('XY').box(20, 20, 10, centered=(True, True,
                                                            False))


class PinnedBlock(FusionNode):
    """The native pin fused exactly with a CadQuery block."""

    def __init__(self):
        self.block = Block()
        self.pin = NativeSolid()
        super().__init__()

    def render(self):
        return [self.block, self.pin]


class Probe(CadQueryNode):
    """Cuts the half of the pin with x > 0 over z in [0, 5]: 22.5 pi."""

    def render(self):
        return cq.Workplane('XY').box(10, 20, 5, centered=(False, True,
                                                           False))


class Clamp(CadQueryNode):
    """Clear of the pin."""

    def render(self):
        return cq.Workplane('XY').box(5, 5, 5).translate((20, 0, 0))


class ExactProject(AssemblyNode):

    def __init__(self):
        self.pinned_block = PinnedBlock()
        self.pin = NativeSolid()
        self.probe = Probe()
        self.clamp = Clamp()
        super().__init__()

    def render(self):
        self.pinned_block.translate([60, 0, 0])
        return [self.pinned_block, self.pin, self.probe, self.clamp]
