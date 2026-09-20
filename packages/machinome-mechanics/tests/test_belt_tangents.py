# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Independent tangent references, perpendicularity and traversal checks."""

import math

import pytest
from solid2 import get_animation_time

from machinome_mechanics import belt_tangent_points
from tests.test_mechanisms import _eval_openscad_expr


def reference(a, ra, b, rb, sa, sb):
    # A separate angular construction: project the normal onto center travel.
    bearing = math.atan2(b[1] - a[1], b[0] - a[0])
    angle = bearing + math.acos((sa * ra - sb * rb) / math.dist(a, b))
    return ((a[0] + sa * ra * math.cos(angle), a[1] + sa * ra * math.sin(angle)),
            (b[0] + sb * rb * math.cos(angle), b[1] + sb * rb * math.sin(angle)))


def test_known_outer_and_inner_contacts():
    assert belt_tangent_points((0, 0), 2, (10, 0), 2) == ((0, 2), (10, 2))
    p, q = belt_tangent_points((0, 0), 2, (10, 0), 3, 1, -1)
    assert p == pytest.approx((1, math.sqrt(3)))
    assert q == pytest.approx((8.5, -1.5 * math.sqrt(3)))


@pytest.mark.parametrize('sa,sb', [(1, 1), (-1, -1), (1, -1), (-1, 1)])
@pytest.mark.parametrize('a,b,ra,rb', [((0, 0), (10, 0), 2, 3),
                                    ((3, -5), (-12, 27), 4, 7),
                                    ((100, 200), (100, 180), 5, .25)])
def test_contacts_close_are_perpendicular_and_follow_the_selected_turn(a, b, ra, rb, sa, sb):
    p, q = belt_tangent_points(a, ra, b, rb, sa, sb)
    expected = reference(a, ra, b, rb, sa, sb)
    assert p == pytest.approx(expected[0])
    assert q == pytest.approx(expected[1])
    direction = (q[0] - p[0], q[1] - p[1])
    assert math.dist(p, a) == pytest.approx(ra)
    assert math.dist(q, b) == pytest.approx(rb)
    for point, centre, sense in ((p, a, sa), (q, b, sb)):
        radial = (point[0] - centre[0], point[1] - centre[1])
        dot = sum(x * y for x, y in zip(radial, direction))
        cross = radial[0] * direction[1] - radial[1] * direction[0]
        assert dot == pytest.approx(0, abs=1e-10)
        assert cross * sense < 0
    reversed_points = belt_tangent_points(b, rb, a, ra, -sb, -sa)
    assert reversed_points[0] == pytest.approx(q)
    assert reversed_points[1] == pytest.approx(p)


def test_domain_limits_are_not_clamped():
    with pytest.raises(ValueError):
        belt_tangent_points((0, 0), 2, (4, 0), 3, 1, -1)
    with pytest.raises(ValueError):
        belt_tangent_points((0, 0), 10, (4, 0), 1)
    with pytest.raises(ZeroDivisionError):
        belt_tangent_points((0, 0), 2, (0, 0), 2)
    assert belt_tangent_points((0, 0), 2, (5, 0), 3, 1, -1) == ((2, 0), (2, 0))


@pytest.mark.parametrize('ra,rb', [(0, 0), (0, 2), (2, 0)])
def test_zero_radius_is_a_point_contact(ra, rb):
    a, b = (0, 0), (10, 0)
    p, q = belt_tangent_points(a, ra, b, rb)
    assert math.dist(a, p) == pytest.approx(ra)
    assert math.dist(b, q) == pytest.approx(rb)


@pytest.mark.parametrize('sa,sb', [(1, 1), (-1, -1), (1, -1), (-1, 1)])
def test_symbolic_centres_and_radii_match_independent_angular_reference(sa, sb):
    t = get_animation_time()
    points = belt_tangent_points((t, 2 * t), 2 + t / 10, (20 - t, 7), 3, sa, sb)
    for value in (-1, 0, .25, 1, 2):
        expected = reference((value, 2 * value), 2 + value / 10, (20 - value, 7), 3, sa, sb)
        for point, target in zip(points, expected):
            assert tuple(_eval_openscad_expr(x, value) for x in point) == pytest.approx(target)
