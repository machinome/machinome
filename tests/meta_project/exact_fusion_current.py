# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""An exact fusion for the `exact-engine` change's currency guard.

One leaf declares `optimize = False`, so the builder prepares it on every
build whether or not its artifacts are current: the case that made
`ExactLeafNode.materialize` convert, and so resolve the exact engine, for
nothing (design.md Decision 7).
"""

import cadquery as cq

from machinome.node import CadQueryNode, FusionNode


class Hub(CadQueryNode):

    def render(self):
        return (cq.Workplane('XY').box(12, 12, 6)
                .faces('>Z').workplane().hole(4))


class Pin(CadQueryNode):

    optimize = False

    def render(self):
        return cq.Workplane('XY').circle(2).extrude(10).translate((0, 0, -5))


class PinnedHub(FusionNode):

    def __init__(self):
        self.hub = Hub()
        self.pin = Pin()
        super().__init__()

    def render(self):
        return [self.hub, self.pin]
