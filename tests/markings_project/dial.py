# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The exact part: a dial whose digits are wrapped around it.

The originating shape, and the Curta's own. It matters here for two
reasons beyond the wrap: it writes a `.brep`, so "the solid is
byte-identical with and without the marking" is a real comparison of
exact geometry, and it declares a tessellation precision that is NOT the
framework's default, so a decal meshed at the default instead of at the
part's own declared value is a failure a test can see.
"""

import cadquery as cq

from solid_node.motion.joints import Revolute
from solid_node.node import CadQueryNode
from solid_node.node.markings import Marking, Svg, Wrapped

#: The Curta's own results-dial radius, and the height of the drum the
#: artwork is wrapped on.
DIAL_RADIUS = 9.45
DIAL_HEIGHT = 12.0

#: Where the artwork's own origin lands on the drum.
DIAL_ARTWORK_AT = (0.0, 0.0, 6.0)

#: Declared, and deliberately not `ExactLeafNode`'s 0.1: the decal is
#: meshed to the part's precision, not to the framework's.
DIAL_DEFLECTION = 0.05


class Dial(CadQueryNode):
    """A drum that turns on its own bearing and reads out through the
    artwork wrapped around it."""

    linear_deflection = DIAL_DEFLECTION

    turn = Revolute(axis=(0, 0, 1), unit='deg')

    digits = Marking(
        Svg('label.svg'),
        Wrapped(axis=(0, 0, 1), radius=DIAL_RADIUS, at=DIAL_ARTWORK_AT,
                start=0.0),
        color='#FFFFFF',
    )

    def render(self):
        return cq.Workplane('XY').cylinder(DIAL_HEIGHT, DIAL_RADIUS)
