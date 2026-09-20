# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Rotation and tangent travel at a constant pitch/contact radius.

Angles are unwrapped degrees, positive by the right-hand rule about the wheel
axis. Positive travel follows its surface tangent in that rotational sense.
Projects supply the sign that maps this tangent onto their rack, belt or rope
axis, and add their own rest position. No slip or changing winding radius is
modelled. Dragon R1 negates this travel for its rack; Thor uses it for belt
travel at each pulley's pitch circle.
"""

from math import pi


def rolling_travel(angle, radius):
    """Return signed tangent displacement for ``angle`` degrees at ``radius``.

    The result is ``angle * radius * pi / 180``, in the radius's length unit,
    zero at zero angle, without wrapping. Use the pitch/contact radius, not a
    toothed wheel's outside radius. The physical radius is positive; zero and
    negative values retain ordinary arithmetic behavior. Numeric and symbolic
    arguments share this formula; dimensional class-body tokens are unsupported.
    """
    return angle * radius * (pi / 180)
