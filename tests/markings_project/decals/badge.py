# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A marking declared in a plain mixin, exactly as the Curta declares
its dial faces: `class FittedDialType1(ClearingGearFit, ResultsDialType1)`.

`BadgeDecal` is not a node and says nothing about rigidity. Python calls
`__set_name__` on the marking whatever the metaclass, so the marking is
named and its declaring module captured here -- which is why
`badge.svg` resolves against THIS directory and not against the
directory of whatever node class ends up wearing it. `badge.svg` exists
only here, so a resolution against the wearing module would not find a
file at all.
"""

from solid_node.node.markings import Flat, Marking, Svg

#: The top face of the plate the badge is stuck to.
BADGE_PLANE_Z = 2.0


class BadgeDecal:
    """A badge on the part's top face."""

    badge = Marking(
        Svg('badge.svg'),
        Flat(at=(0.0, 0.0, BADGE_PLANE_Z), normal=(0, 0, 1),
             x_axis=(1, 0, 0)),
        color='#FFFFFF',
    )


class MissingBadgeDecal:
    """A mixin naming an artwork that is not there.

    Inert until a node class wears it, which is the point: a mixin is
    not a node and never reaches `NodeMeta`, so the refusal belongs to
    the class that inherits it -- and the path it names must resolve
    against THIS directory, where `no-such-badge.svg` is just as absent
    as it is anywhere else.
    """

    badge = Marking(
        Svg('no-such-badge.svg'),
        Flat(at=(0.0, 0.0, BADGE_PLANE_Z), normal=(0, 0, 1),
             x_axis=(1, 0, 0)),
        color='#FFFFFF',
    )
