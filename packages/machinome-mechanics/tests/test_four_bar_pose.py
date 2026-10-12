"""A driven four-bar closes independently of its circle construction."""

import math

import pytest
from solid2 import get_animation_time

from machinome_mechanics import four_bar_pose
from machinome_mechanics.linkages import four_bar_pose as family_helper
from tests.test_mechanisms import _eval_openscad_expr


def _circle_point(a, radius_a, b, radius_b, side):
    distance = math.dist(a, b)
    ux, uy = ((b[i] - a[i]) / distance for i in range(2))
    along = (radius_a**2 - radius_b**2 + distance**2) / (2 * distance)
    across = side * math.sqrt(radius_a**2 - along**2)
    return (a[0] + along*ux - across*uy, a[1] + along*uy + across*ux)


def _check(pose, angle, a, d, crank, coupler, rocker, side):
    b, c = pose['crank_end'], pose['rocker_end']
    assert b == pytest.approx((a[0] + crank*math.cos(math.radians(angle)),
                               a[1] + crank*math.sin(math.radians(angle))), abs=1e-10)
    assert c == pytest.approx(_circle_point(d, rocker, b, coupler, side), abs=1e-10)
    assert math.dist(a, b) == pytest.approx(crank, abs=1e-10)
    assert math.dist(b, c) == pytest.approx(coupler, abs=1e-10)
    assert math.dist(d, c) == pytest.approx(rocker, abs=1e-10)
    cross = (b[0]-d[0])*(c[1]-d[1]) - (b[1]-d[1])*(c[0]-d[0])
    assert side*cross > 0
    for bearing, start, length in ((pose['rocker_angle'], d, rocker),
                                   (pose['coupler_angle'], b, coupler)):
        assert (start[0]+length*math.cos(math.radians(bearing)),
                start[1]+length*math.sin(math.radians(bearing))) == pytest.approx(c, abs=1e-10)


def test_reference_result_and_constructed_bearing():
    assert family_helper is four_bar_pose
    pose = four_bar_pose(90, (0, 0), (4, 0), 3, 4, 3, -1)
    assert set(pose) == {'crank_end', 'rocker_end', 'rocker_angle', 'coupler_angle'}
    assert pose['crank_end'] == pytest.approx((0, 3))
    assert pose['rocker_end'] == pytest.approx((4, 3))
    assert pose['rocker_angle'] == pytest.approx(90)
    assert pose['coupler_angle'] == pytest.approx(0, abs=1e-12)
    other = four_bar_pose(90, (0, 0), (4, 0), 3, 4, 3)
    assert other['rocker_end'] == pytest.approx((1.12, -0.84))
    assert other['rocker_angle'] == pytest.approx(196.260204708, abs=1e-8)
    assert other['rocker_angle'] > 180  # Do not normalize Dragon's part rotation.


@pytest.mark.parametrize('side', [1, -1])
@pytest.mark.parametrize('scale', [0.8, 1, 1.4])
def test_complete_turns_and_shifted_pivots(side, scale):
    a, d = (2*scale, -3*scale), (8*scale, -3*scale)
    for angle in range(-360, 721, 15):
        pose = four_bar_pose(angle, a, d, 2*scale, 6*scale, 4*scale, side)
        _check(pose, angle, a, d, 2*scale, 6*scale, 4*scale, side)


@pytest.mark.parametrize('side', [1, -1])
def test_straight_closure_limits(side):
    outer = four_bar_pose(0, (0, 0), (8, 0), 2, 4, 2, side)
    assert outer['rocker_end'] == pytest.approx((6, 0), abs=1e-12)
    inner = four_bar_pose(0, (0, 0), (6, 0), 2, 2, 6, side)
    assert inner['rocker_end'] == pytest.approx((0, 0), abs=1e-12)


@pytest.mark.parametrize('d,coupler,rocker,error', [
    ((20, 0), 4, 3, ValueError), ((3, 0), 4, 1, ValueError),
    ((2, 0), 4, 4, ZeroDivisionError), ((5, 0), 3, 0, ZeroDivisionError),
])
def test_invalid_closures_are_not_clamped(d, coupler, rocker, error):
    with pytest.raises(error):
        four_bar_pose(0, (0, 0), d, 2, coupler, rocker)


@pytest.mark.parametrize('side', [1, -1])
def test_simultaneously_deferred_geometry(side):
    t = get_animation_time()
    symbolic = four_bar_pose(25+30*t, (t, 1+2*t), (6+t, -1+t),
                             2+0.1*t, 6+0.2*t, 4+0.1*t, side)
    for time in (-1, 0, 0.25, 1, 2):
        args = (25+30*time, (time, 1+2*time), (6+time, -1+time),
                2+0.1*time, 6+0.2*time, 4+0.1*time, side)
        numeric = four_bar_pose(*args)
        evaluated = {
            key: tuple(_eval_openscad_expr(v, time) for v in value)
            if isinstance(value, tuple) else _eval_openscad_expr(value, time)
            for key, value in symbolic.items()
        }
        for key in numeric:
            assert evaluated[key] == pytest.approx(numeric[key], abs=1e-10)
        _check(evaluated, *args)
