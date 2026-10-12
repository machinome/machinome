# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Reference phase, no-slip arc identities and deferred pulley motion."""

import math

import pytest
from solid2 import get_animation_time

from machinome_mechanics import belt_pulley_angle
from tests.test_mechanisms import _eval_openscad_expr


@pytest.mark.parametrize('sense', [1, -1])
def test_contact_station_is_the_unwrapped_angle_reference(sense):
    for turns in (-3, -.25, 0, .25, 2):
        position = 10 + turns * 4 * math.pi
        assert belt_pulley_angle(position, 2, 90, 10, sense) == pytest.approx(
            90 - sense * turns * 360, abs=1e-12)


@pytest.mark.parametrize('sense', [1, -1])
@pytest.mark.parametrize('radius', [2, 6.375, -2])
def test_arc_identity_and_path_origin_invariance(sense, radius):
    for position in (-40, 0, 3, 1000):
        angle = belt_pulley_angle(position, radius, -137, 21, sense)
        assert math.radians(-137 - angle) * radius == pytest.approx(
            sense * (position - 21))
        assert belt_pulley_angle(position + 300, radius, -137, 321, sense) == pytest.approx(angle)


def test_zero_radius_is_not_clamped():
    with pytest.raises(ZeroDivisionError):
        belt_pulley_angle(10, 0, 90)


def test_default_station_and_clockwise_sense():
    assert belt_pulley_angle(math.pi, 2, 90) == pytest.approx(0)
    assert belt_pulley_angle(0, 2, 450) == 450


@pytest.mark.parametrize('sense', [1, -1])
def test_deferred_position_radius_contact_and_station_match_numeric_reference(sense):
    t = get_animation_time()
    expr = belt_pulley_angle(10 + 30*t, 2+t/10, 90+2*t, 7-t, sense)
    for value in (-2, 0, .25, 1, 3):
        expected = 90+2*value - sense * math.degrees(
            ((10+30*value) - (7-value)) / (2+value/10))
        assert _eval_openscad_expr(expr, value) == pytest.approx(expected)
