# Machinome Mechanics - Mechanical formula helpers for Machinome projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Circle geometry and planar joint angles a linkage keeps asking for.

Where two arcs cross, what angle a triangle of three known sides makes,
and how high a rigid link stands when its ends are pulled apart. Each of
them was written out longhand in at least one project, numerically only,
and broke the first time a driver symbol reached it.

Coordinates are plain ``(x, y)`` 2-tuples in whatever plane the caller
is working in; angles are degrees.

``side``. A circle-circle intersection has two answers, and naming which
one by a sign is only meaningful against a stated direction. Here the
direction is from ``centre_a`` to ``centre_b``: ``side = 1`` is the
intersection to its left (counter-clockwise from it), ``side = -1`` to
its right. A grasshopper escapement finds its nib this way, as
``circle_intersection((0, 0), radius, pivot, arm, side)``.

No guards. An unreachable configuration -- circles too far apart or one
inside the other, a triangle whose sides do not close, a link shorter
than its offset -- reaches ``sqrt`` or ``acos`` of an out-of-range value
and raises numerically, exactly as ``machinome.math`` raises, and
evaluates to NaN symbolically, exactly as OpenSCAD and the viewer do.
That is the honest answer: a guard would have to invent a pose that
does not exist.
"""

from machinome.math import acos, atan2, cos, sin, sqrt


def circle_intersection(centre_a, radius_a, centre_b, radius_b, side=1):
    """The ``(x, y)`` at distance ``radius_a`` from ``centre_a`` and
    ``radius_b`` from ``centre_b``, on the side named.

    ``side = 1`` picks the intersection to the left of the direction
    from ``centre_a`` to ``centre_b``, ``side = -1`` the one to its
    right. See the module docstring.
    """
    ax, ay = centre_a
    bx, by = centre_b
    vx, vy = bx - ax, by - ay
    distance = sqrt(vx * vx + vy * vy)
    along = ((distance * distance - radius_b * radius_b + radius_a * radius_a)
             / (2 * distance))
    across = side * sqrt(radius_a * radius_a - along * along)
    unit_x, unit_y = vx / distance, vy / distance
    return (ax + along * unit_x - across * unit_y,
            ay + along * unit_y + across * unit_x)


def triangle_angle(opposite, adjacent_a, adjacent_b):
    """The angle, in degrees, of a triangle opposite the side
    ``opposite``, between the sides ``adjacent_a`` and ``adjacent_b``:
    the law of cosines, ``acos((a^2 + b^2 - opposite^2) / (2 a b))``.
    """
    return acos((adjacent_a * adjacent_a + adjacent_b * adjacent_b
                 - opposite * opposite)
                / (2 * adjacent_a * adjacent_b))


def link_rise(link, offset):
    """The height of a rigid link of length ``link`` whose ends are
    ``offset`` apart horizontally: ``sqrt(link^2 - offset^2)``.
    """
    return sqrt(link * link - offset * offset)


def two_link_angles(x, y, first_length, second_length, side=1):
    """Return absolute shoulder and relative elbow angles for target (x, y).

    The pivot is (0, 0), lengths are positive in the target's unit, and
    angles are degrees from +X toward +Y. The second absolute bearing is
    shoulder + elbow. Literal side +1 places the knee left of the
    pivot-to-target direction; -1 places it right. No branch tracking,
    reach guard, servo offset or tolerance clamp is inferred.

    Require nonzero target distance between the difference and sum of
    the lengths. Division/domain errors propagate numerically. Supported
    deferred operands use exactly the same arithmetic. A hexapod leg keeps
    its tibia offset outside; a quadruped on a vertical leg supplies
    (height, 0) after its own guard.
    """
    distance = sqrt(x * x + y * y)
    shoulder = atan2(y, x) + side * triangle_angle(
        second_length, first_length, distance)
    elbow = side * (triangle_angle(distance, first_length, second_length) - 180)
    return shoulder, elbow


def four_bar_pose(angle, crank_pivot, rocker_pivot, crank_length,
                  coupler_length, rocker_length, side=1):
    """Return the moving ends and absolute output bearings of a four-bar.

    Fixed pivots A=crank_pivot and D=rocker_pivot share the length unit of
    the positive crank, coupler and rocker lengths. Angle is the absolute
    crank bearing in degrees from +X toward +Y. Moving ends are B (crank)
    and C (rocker); literal side +1 selects C left of D-to-B, -1 right.

    The dict contains crank_end B, rocker_end C, rocker_angle D-to-C and
    coupler_angle B-to-C. The rocker bearing retains the constructed
    center bearing plus signed closure; the coupler uses principal atan2.
    Neither promises continuous unwrapping. Domain/division errors propagate;
    numeric and supported deferred geometry share the same formula.

    A double-wishbone suspension keeps its ride inversion and authored
    offsets outside; a walking linkage takes its two selected closures
    before its remaining rigid triangles.
    """
    bx = crank_pivot[0] + crank_length * cos(angle)
    by = crank_pivot[1] + crank_length * sin(angle)
    dx, dy = rocker_pivot
    vx, vy = bx - dx, by - dy
    distance = sqrt(vx * vx + vy * vy)
    rocker_angle = atan2(vy, vx) + side * triangle_angle(
        coupler_length, rocker_length, distance)
    cx = dx + rocker_length * cos(rocker_angle)
    cy = dy + rocker_length * sin(rocker_angle)
    return dict(crank_end=(bx, by), rocker_end=(cx, cy),
                rocker_angle=rocker_angle, coupler_angle=atan2(cy - by, cx - bx))
