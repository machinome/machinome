# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The faceted part: a committed mesh carrying two markings.

An `StlNode` writes no `.brep` and declares no `linear_deflection`, so
it is the half of every invariant that reads the framework's default
rather than a part's own declaration. It carries two markings, one of
them inherited from a plain mixin in another directory, so a part with
two decals and the mixin rule are the same fixture.
"""

from machinome.node import StlNode
from machinome.node.markings import Marking, Svg, Wrapped

from .decals.badge import BadgeDecal

#: The radius the band is wrapped at: clear of the plate, which is what
#: makes a wrapped decal on a faceted part a question about the decal's
#: own mesh and not about the part's surface.
BAND_RADIUS = 12.0


class Plate(BadgeDecal, StlNode):
    """A plate wearing the mixin's badge and a band of its own."""

    stl_source = 'plate.stl'

    band = Marking(
        Svg('label.svg'),
        Wrapped(axis=(0, 0, 1), radius=BAND_RADIUS, at=(0, 0, 10.0)),
        color='#C0C0C0',
    )
