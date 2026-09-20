# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Circumference and degree conventions independently pin rolling travel."""

import math

import pytest
from solid2 import get_animation_time

from machinome_mechanics import rolling_travel


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
