# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Independent circumference references for belt pitch geometry."""

import math

import pytest
from solid2 import get_animation_time

from machinome_mechanics import pulley_pitch_radius, rolling_angle, rolling_travel


@pytest.mark.parametrize("teeth,pitch", [(117, 2), (10, 3), (30, 3), (16, 2.001)])
def test_pulley_circumference_contains_the_given_linear_pitches(teeth, pitch):
    radius = pulley_pitch_radius(teeth, pitch)
    assert math.tau * radius == pytest.approx(teeth * pitch)
    assert rolling_travel(360 / teeth, radius) == pytest.approx(pitch)
    assert rolling_angle(pitch, radius) == pytest.approx(360 / teeth)


def test_radius_does_not_include_a_surface_offset():
    assert pulley_pitch_radius(20, 2) == pytest.approx(6.366197723675814)
    assert pulley_pitch_radius(20, 2) - .254 == pytest.approx(6.112197723675814)


@pytest.mark.parametrize("teeth,pitch", [(0, 2), (16, 0), (-16, 2), (16, -2), (2.5, 3)])
def test_degenerate_and_fractional_inputs_retain_arithmetic(teeth, pitch):
    assert pulley_pitch_radius(teeth, pitch) * math.tau == pytest.approx(teeth * pitch)


def test_symbolic_count_and_pitch_keep_one_circumference_definition():
    time = get_animation_time()
    expression = str(pulley_pitch_radius(16 + time, 2 + time / 10))
    for value in (-2, 0, .5, 1, 3):
        evaluated = eval(expression.replace('$t', repr(value)), {'__builtins__': {}})
        assert math.tau * evaluated == pytest.approx((16 + value) * (2 + value / 10))
