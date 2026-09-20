"""Internal relative mesh identities with fixed and orbiting pinion centers."""

import pytest
from solid2 import get_animation_time

from machinome_mechanics import internal_mesh_angle
from machinome_mechanics.gears import internal_mesh_angle as family_helper
from tests.test_mechanisms import _eval_openscad_expr


def test_thor_fixed_carrier_and_unwrapped_sign():
    assert internal_mesh_angle is family_helper
    for angle in (-765, -360, -30, 0, 1, 30, 360, 765):
        assert internal_mesh_angle(angle, 60, 10) == 6 * angle


def test_opentorque_fixed_ring_and_carrier_frame():
    for input_angle in (-2880, -360, -1, 0, 10, 40, 25, 360, 2880):
        carrier = input_angle / 8
        absolute = internal_mesh_angle(0, 126, 54, carrier)
        # Independent external sun-to-planet relation, as in the project.
        relative = -(18 / 54) * (input_angle - carrier)
        assert absolute == pytest.approx(carrier + relative, abs=1e-12)
        assert absolute - carrier == pytest.approx(relative, abs=1e-12)
    assert internal_mesh_angle(0, 126, 54, 45) == pytest.approx(-60)


@pytest.mark.parametrize('ring_teeth,pinion_teeth', [(60, 10), (126, 54), (35, 12), (20.5, 4.5)])
def test_relative_identity_common_motion_and_scaling(ring_teeth, pinion_teeth):
    for ring in (-720, -17.5, 0, 81, 1440):
        for carrier in (-360, -1, 0, 45, 700):
            result = internal_mesh_angle(ring, ring_teeth, pinion_teeth, carrier)
            assert pinion_teeth * (result - carrier) == pytest.approx(
                ring_teeth * (ring - carrier), abs=1e-9)
            assert internal_mesh_angle(ring + 13, ring_teeth, pinion_teeth,
                                       carrier + 13) == pytest.approx(result + 13)
            assert internal_mesh_angle(ring, 3*ring_teeth, 3*pinion_teeth,
                                       carrier) == pytest.approx(result)
            assert internal_mesh_angle(carrier, ring_teeth, pinion_teeth,
                                       carrier) == carrier


@pytest.mark.parametrize('ring,pinion,expected', [(10, 10, 30), (0, 10, 5), (-60, 10, -145), (60, -10, -145)])
def test_nonphysical_counts_retain_arithmetic(ring, pinion, expected):
    assert internal_mesh_angle(30, ring, pinion, 5) == expected


def test_zero_pinion_raises():
    with pytest.raises(ZeroDivisionError):
        internal_mesh_angle(0, 60, 0)


def test_actual_deferred_all_operands():
    time = get_animation_time()
    expr = internal_mesh_angle(720*time - 90, 60 + time, 10 + time, 45*time)
    for value in (-2, -1, 0, 0.125, 1, 2):
        result = _eval_openscad_expr(expr, value)
        ring, carrier = 720*value - 90, 45*value
        assert result == pytest.approx(internal_mesh_angle(
            ring, 60 + value, 10 + value, carrier), abs=1e-10)
        assert (10 + value)*(result - carrier) == pytest.approx(
            (60 + value)*(ring - carrier), abs=1e-8)


def test_actual_deferred_fixed_ring_child_local_spin():
    time = get_animation_time()
    carrier = 360 * time
    local = internal_mesh_angle(0, 126, 54, carrier) - carrier
    for value in (-2, -1, 0, 0.125, 1, 2):
        assert _eval_openscad_expr(local, value) == pytest.approx(-840*value)
