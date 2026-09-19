# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The same dial, declaring no marking.

Same class name and same parameters, so it keys the same `uniq_id`, and
the same render and the same declared precision, so its `.stl` and
`.brep` are the bytes `dial.Dial`'s must equal. It is a different module
only so that the two parts have artifact paths of their own to compare.
"""

import cadquery as cq

from machinome.motion.joints import Revolute
from machinome.node import CadQueryNode

from .dial import DIAL_DEFLECTION, DIAL_HEIGHT, DIAL_RADIUS


class Dial(CadQueryNode):
    """`dial.Dial` without its digits."""

    linear_deflection = DIAL_DEFLECTION

    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cq.Workplane('XY').cylinder(DIAL_HEIGHT, DIAL_RADIUS)
