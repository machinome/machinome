"""Fixed-ring relative motion, not a positive reduction magnitude."""

import pytest
from solid2 import get_animation_time

from machinome_mechanics import cycloidal_ratio
from machinome_mechanics.gears import cycloidal_ratio as family_helper
from tests.test_mechanisms import _eval_openscad_expr


def test_measured_twenty_lobe_reference():
    assert family_helper is cycloidal_ratio
    ratio = cycloidal_ratio(20, 21)
    assert ratio == -0.05
    assert 360 * ratio == -18
    assert 7200 * ratio == -360
    assert -7200 * ratio == 360
    assert 0 * ratio == 0


@pytest.mark.parametrize('lobes,pins', [(20, 21), (59, 60), (12, 14), (4, 9)])
def test_fixed_ring_relative_mesh_and_count_scaling(lobes, pins):
    ratio = cycloidal_ratio(lobes, pins)
    for angle in (-10000, -720, -1, 0, 0.125, 90, 360, 7200, 10000):
        output = angle * ratio
        # Independent relative mesh identity in the eccentric-carrier frame.
        assert lobes * (output - angle) == pytest.approx(
            pins * (0 - angle), rel=1e-12, abs=1e-8)
    for scale in (2, 3, 11):
        assert cycloidal_ratio(scale * lobes, scale * pins) == pytest.approx(ratio)


@pytest.mark.parametrize('lobes,pins,expected', [
    (20, 20, 0), (20, 19, 0.05), (-20, 21, 2.05),
    (2.5, 3.5, -0.4), (20, 0, 1),
])
def test_arithmetic_is_not_a_physical_count_validator(lobes, pins, expected):
    assert cycloidal_ratio(lobes, pins) == pytest.approx(expected)


def test_zero_lobes_propagates_division_error():
    with pytest.raises(ZeroDivisionError):
        cycloidal_ratio(0, 21)


def test_actual_deferred_counts_and_angle():
    time = get_animation_time()
    ratio = cycloidal_ratio(20 + time, 21 + 2 * time)
    output = (360 * time - 90) * ratio
    for value in (-0.5, 0, 0.25, 1, 2):
        lobes, pins = 20 + value, 21 + 2 * value
        numeric = cycloidal_ratio(lobes, pins)
        evaluated_ratio = _eval_openscad_expr(ratio, value)
        evaluated_output = _eval_openscad_expr(output, value)
        angle = 360 * value - 90
        assert evaluated_ratio == pytest.approx(numeric, rel=1e-12, abs=1e-12)
        assert evaluated_output == pytest.approx(angle * numeric, abs=1e-10)
        assert lobes * (evaluated_output - angle) == pytest.approx(
            -pins * angle, rel=1e-12, abs=1e-8)


def test_actual_deferred_input_stays_unwrapped():
    time = get_animation_time()
    output = 7200 * time * cycloidal_ratio(20, 21)
    for value in (-2, -1, 0, 0.25, 1, 2):
        assert _eval_openscad_expr(output, value) == pytest.approx(-360 * value)
