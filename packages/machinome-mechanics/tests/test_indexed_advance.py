"""Independent turn accounting, callback boundaries and actual deferred values."""

import math

import pytest
from machinome.math import clamp01, cos
from solid2 import get_animation_time

from machinome_mechanics import indexed_advance
from machinome_mechanics.indexing import indexed_advance as family_helper
from tests.test_mechanisms import _eval_openscad_expr


def reference(angle, increment, stroke, origin=0):
    turns, offset = divmod(angle - origin, 360)
    return turns * increment + stroke(origin + offset)


def test_signed_linear_stroke_and_exports():
    assert indexed_advance is family_helper
    assert [indexed_advance(a, 7.5, lambda p: 7.5*p/360)
            for a in (-720, -90, 0, 180, 360, 810)] == pytest.approx(
                [-15, -1.875, 0, 3.75, 7.5, 16.875])


def test_current_pascaline_shifted_window():
    stroke = lambda p: 36 * clamp01((p - 325) / 34)
    assert [indexed_advance(a, 36, stroke, 325)
            for a in (0, 324, 325, 342, 359, 360, 685, 719)] == pytest.approx(
                [0, 0, 0, 18, 36, 36, 36, 72])


@pytest.mark.parametrize('origin', [-725, -45, 0, 325, 810])
def test_callback_once_absolute_phase_and_signed_seams(origin):
    for turn in (-5, -1, 0, 1, 4):
        for offset in (0, 1e-7, 34, 180, 359.9999999):
            seen = []
            def stroke(phase):
                seen.append(phase)
                return 3 + (phase-origin) / 40
            value = indexed_advance(origin + 360*turn + offset, 9, stroke, origin)
            assert len(seen) == 1
            assert origin <= seen[0] < origin + 360
            assert seen[0] == pytest.approx(origin + offset)
            assert value == pytest.approx(9*turn + 3 + offset/40)


def test_continuity_is_not_invented():
    assert indexed_advance(359.999, 10, lambda p: 0) == 0
    assert indexed_advance(360, 10, lambda p: 0) == 10
    assert indexed_advance(-0.001, 10, lambda p: 0) == -10
    assert indexed_advance(720, 10, lambda p: 4) == 24


@pytest.mark.parametrize('increment', [0, -7.5, 7.5])
def test_nonlinear_rise_hold_reference_and_translation(increment):
    numeric = lambda p: increment * (1-math.cos(math.radians(min(p, 180))))/2
    for angle in (-1080.001, -720, -0.001, 0, 90, 180, 359.999, 360, 765, 1440):
        value = indexed_advance(angle, increment, numeric)
        assert value == pytest.approx(reference(angle, increment, numeric))
        assert indexed_advance(angle+720, increment, numeric) == pytest.approx(
            value + 2*increment, abs=1e-12)


def test_callback_exception_propagates():
    failure = RuntimeError('stroke failed')
    def broken(phase):
        raise failure
    with pytest.raises(RuntimeError) as error:
        indexed_advance(50, 7.5, broken)
    assert error.value is failure


def test_actual_deferred_shifted_carry():
    time = get_animation_time()
    expression = indexed_advance(1440*time-360, 36,
                                 lambda p: 36*clamp01((p-325)/34), 325)
    numeric = lambda p: 36*max(0, min(1, (p-325)/34))
    for angle in (-755, -395.001, -395, -360, 0, 324.999, 325, 342, 359,
                  360, 684.999, 685, 719, 1440):
        assert _eval_openscad_expr(expression, (angle+360)/1440) == pytest.approx(
            reference(angle, 36, numeric, 325), abs=1e-10)


def test_actual_deferred_all_operands_and_callback_once():
    time = get_animation_time()
    origin = 325 + time
    increment = 36 - time
    seen = []
    def stroke(phase):
        seen.append(phase)
        return increment * (1-cos((phase-origin)/2)) / 2
    expression = indexed_advance(900*time, increment, stroke, origin)
    assert len(seen) == 1
    for value in (-2, -1, 0, 0.25, 0.5, 1, 2):
        numeric = lambda p: (36-value)*(1-math.cos(math.radians((p-325-value)/2)))/2
        assert _eval_openscad_expr(expression, value) == pytest.approx(
            reference(900*value, 36-value, numeric, 325+value), abs=1e-10)
