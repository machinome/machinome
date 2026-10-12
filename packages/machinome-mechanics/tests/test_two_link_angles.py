"""Independent forward closure and legacy law checks for planar reach."""

import math

import pytest
from solid2 import get_animation_time

from machinome_mechanics import two_link_angles
from machinome_mechanics.linkages import two_link_angles as family_helper
from tests.test_mechanisms import _eval_openscad_expr


def _endpoint(angles, first, second):
    shoulder, elbow = map(math.radians, angles)
    return (first * math.cos(shoulder) + second * math.cos(shoulder + elbow),
            first * math.sin(shoulder) + second * math.sin(shoulder + elbow))


def test_reference_and_exports():
    assert family_helper is two_link_angles
    assert two_link_angles(3, 4, 5, 5) == pytest.approx((113.130102354, -120))
    assert two_link_angles(3, 4, 5, 5, -1) == pytest.approx((-6.869897646, 120))


@pytest.mark.parametrize('side', [1, -1])
@pytest.mark.parametrize('first,second', [(5, 5), (5, 3), (3, 5), (80, 121)])
def test_forward_closure_quadrants_and_knee_side(side, first, second):
    low, high = abs(first - second), first + second
    for fraction in (0.01, 0.25, 0.7, 0.99):
        distance = low + fraction * (high - low)
        for bearing in (-175, -95, -15, 0, 45, 125, 180):
            x = distance * math.cos(math.radians(bearing))
            y = distance * math.sin(math.radians(bearing))
            angles = two_link_angles(x, y, first, second, side)
            assert _endpoint(angles, first, second) == pytest.approx((x, y), abs=1e-10)
            knee = (first * math.cos(math.radians(angles[0])),
                    first * math.sin(math.radians(angles[0])))
            assert side * (x * knee[1] - y * knee[0]) > 0


@pytest.mark.parametrize('side', [1, -1])
def test_tangent_limits(side):
    assert two_link_angles(8, 0, 5, 3, side) == pytest.approx((0, 0))
    assert _endpoint(two_link_angles(2, 0, 5, 3, side), 5, 3) == pytest.approx((2, 0))
    assert _endpoint(two_link_angles(2, 0, 3, 5, side), 3, 5) == pytest.approx((2, 0))


@pytest.mark.parametrize('x,y,first,second,error', [
    (9, 0, 5, 3, ValueError), (1, 0, 5, 3, ValueError),
    (0, 0, 5, 5, ZeroDivisionError),
    (3, 0, 0, 3, ZeroDivisionError), (3, 0, 3, 0, ZeroDivisionError),
])
def test_invalid_geometry_is_not_clamped(x, y, first, second, error):
    with pytest.raises(error):
        two_link_angles(x, y, first, second)


@pytest.mark.parametrize('side', [1, -1])
def test_simultaneously_deferred_geometry(side):
    t = get_animation_time()
    expressions = two_link_angles(3 + t, 2 - t, 5 + t / 2, 4 - t / 4, side)
    for time in (-1, 0, 0.25, 1, 2):
        first, second = 5 + time / 2, 4 - time / 4
        x, y = 3 + time, 2 - time
        evaluated = tuple(_eval_openscad_expr(expr, time) for expr in expressions)
        assert evaluated == pytest.approx(two_link_angles(x, y, first, second, side), abs=1e-10)
        assert _endpoint(evaluated, first, second) == pytest.approx((x, y), abs=1e-10)


def test_albert_compensating_bearing_is_preserved():
    first, second = 35, 52
    for height in (67.4, 68.671, 75, 82, 86.8):
        knee = math.acos((first**2 + second**2 - height**2) / (2 * first * second)) - math.pi
        hip = -math.atan2(second * math.sin(knee), first + second * math.cos(knee))
        assert two_link_angles(height, 0, first, second) == pytest.approx(
            (math.degrees(hip), math.degrees(knee)), abs=1e-10)
