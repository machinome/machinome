# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from .library import WIDTH


class Wide(CadQueryNode):
    """A leaf whose dimension comes through a sibling package's
    `__init__.py`, which re-exports it from the module defining it."""

    def render(self):
        return cq.Workplane('XY').box(WIDTH, 2, 2)
