"""Independent piecewise envelopes and actual deferred arithmetic."""

import math

import pytest
from solid2 import get_animation_time

from machinome_mechanics import harmonic_cam_lift
from machinome_mechanics.cams import harmonic_cam_lift as family_helper
from tests.test_mechanisms import _eval_openscad_expr


def reference(angle, lift, rise, fall):
    phase = angle % 360
    if phase <= rise:
        return lift * (1 - math.cos(math.pi * phase / rise)) / 2
    if phase < rise + fall:
        return lift * (1 + math.cos(math.pi * (phase - rise) / fall)) / 2
    return 0.0


def test_full_peak_lift_not_half_throw():
    assert harmonic_cam_lift is family_helper
    assert [harmonic_cam_lift(a, 10) for a in (0, 90, 180, 270, 360)] == pytest.approx([0, 5, 10, 5, 0])


@pytest.mark.parametrize('rise,fall', [(180, 180), (240, 80), (240, 45), (75, 120)])
def test_piecewise_reference_signed_turns_and_transitions(rise, fall):
    phases = [i / 2 for i in range(721)]
    phases += [boundary + eps for boundary in (0, rise, rise + fall, 360)
               for eps in (-1e-7, 0, 1e-7)]
    for turn in (-3, -1, 0, 1, 4):
        for phase in phases:
            angle = phase + 360 * turn
            assert harmonic_cam_lift(angle, 18, rise, fall) == pytest.approx(
                reference(angle, 18, rise, fall), abs=2e-12)


def test_distinct_hammer_and_profile_returns():
    assert harmonic_cam_lift(280, 18, 240, 80) == pytest.approx(9)
    assert harmonic_cam_lift(262.5, 18, 240, 45) == pytest.approx(9)
    assert harmonic_cam_lift(300, 18, 240, 80) > 0
    assert harmonic_cam_lift(300, 18, 240, 45) == 0


def test_linear_signed_lift_and_symmetric_cosine():
    for angle in (-1440, -721, -360.001, -90, 0, 90, 180, 270, 1440.1):
        expected = 7 * (1 - math.cos(math.radians(angle)))
        assert harmonic_cam_lift(angle, 14) == pytest.approx(expected, abs=1e-12)
        assert harmonic_cam_lift(angle, -14) == pytest.approx(-expected, abs=1e-12)
        assert harmonic_cam_lift(angle, 0) == 0


@pytest.mark.parametrize('rise,fall', [(0, 180), (180, 0), (0, 0)])
def test_zero_span_is_not_repaired(rise, fall):
    with pytest.raises(ZeroDivisionError):
        harmonic_cam_lift(90, 10, rise, fall)


def test_no_physical_span_validation_is_invented():
    assert harmonic_cam_lift(90, 10, -180, 180) == -10
    assert harmonic_cam_lift(180, 10, 360, 360) == pytest.approx(5)


@pytest.mark.parametrize('rise,fall', [(180, 180), (240, 80), (240, 45)])
def test_actual_deferred_angle(rise, fall):
    time = get_animation_time()
    expression = harmonic_cam_lift(1440 * time - 360, 18, rise, fall)
    for angle in (-721, -360, -0.001, 0, 90, 180, 239.9, 240, 262.5, 280, 285, 320, 360, 1440):
        value = (angle + 360) / 1440
        assert _eval_openscad_expr(expression, value) == pytest.approx(
            reference(angle, 18, rise, fall), abs=1e-10)


def test_actual_deferred_lift_and_spans():
    time = get_animation_time()
    expression = harmonic_cam_lift(160 + 50*time, 18 + time, 180 + time, 100 - time)
    for value in (-1, 0, 0.25, 1, 2):
        assert _eval_openscad_expr(expression, value) == pytest.approx(
            reference(160 + 50*value, 18 + value, 180 + value, 100 - value), abs=1e-10)
