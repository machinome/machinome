# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import dimensions


class Peg(CadQueryNode):
    """A leaf reaching a sibling module through its own package.

    `from . import dimensions` names the package that contains this file,
    whose `__init__.py` is the root assembly importing every node.
    """

    def render(self):
        return cq.Workplane('XY').box(1, 1, dimensions.HEIGHT)
