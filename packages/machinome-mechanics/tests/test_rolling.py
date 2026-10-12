# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Circumference and degree conventions independently pin rolling travel."""

import math

import pytest
from solid2 import get_animation_time

from machinome_mechanics import rolling_angle, rolling_travel


@pytest.mark.parametrize("angle, turns", [(0, 0), (90, .25), (360, 1), (-720, -2)])
def test_travel_is_the_signed_fraction_of_a_circumference(angle, turns):
    assert rolling_travel(angle, 9) == pytest.approx(turns * math.tau * 9)


def test_pitch_count_and_radius_describe_the_same_belt_travel():
    # Thor's 117-tooth, 2 mm pitch pulley advances 234 mm per revolution.
    radius = 234 / math.tau
    assert rolling_travel(360, radius) == pytest.approx(234)
    assert rolling_travel(360 / 117, radius) == pytest.approx(2)


def test_zero_and_signed_radius_keep_arithmetic_behavior():
    assert rolling_travel(45, 0) == 0
    assert rolling_travel(180, -2) == pytest.approx(-math.tau)


def test_symbolic_angle_and_radius_preserve_the_same_law():
    time = get_animation_time()
    expression = str(rolling_travel(720 * time - 360, 2 + time))
    for value in (-.25, 0, .25, 1, 2):
        evaluated = eval(expression.replace('$t', repr(value)), {'__builtins__': {}})
        assert evaluated == pytest.approx((2 * value - 1) * math.tau * (2 + value))


@pytest.mark.parametrize("turns", [0, .25, 1, -2, 3.5])
def test_circumference_fractions_give_unwrapped_degrees(turns):
    assert rolling_angle(turns * math.tau * 9, 9) == pytest.approx(turns * 360)


def test_rolling_conversions_round_trip_both_directions():
    for radius in (.25, 9, -12):
        for angle in (-1080, -45, 0, 270, 765):
            assert rolling_angle(rolling_travel(angle, radius), radius) == pytest.approx(angle)
        for distance in (-110, -1, 0, .25, 123):
            assert rolling_travel(rolling_angle(distance, radius), radius) == pytest.approx(distance)


def test_angle_retains_signed_radius_and_refuses_zero_divisor():
    assert rolling_angle(math.tau, -2) == pytest.approx(-180)
    for distance in (0, 1, -1):
        with pytest.raises(ZeroDivisionError):
            rolling_angle(distance, 0)


def test_symbolic_travel_and_radius_preserve_the_inverse_law():
    time = get_animation_time()
    expression = str(rolling_angle(12 * time - 6, 2 + time))
    for value in (-.25, 0, .25, 1, 2):
        evaluated = eval(expression.replace('$t', repr(value)), {'__builtins__': {}})
        expected = math.degrees((12 * value - 6) / (2 + value))
        assert evaluated == pytest.approx(expected)
