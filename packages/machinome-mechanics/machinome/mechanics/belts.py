# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Belt pitch geometry, independent of mounting frame and tooth profile.

Lengths share one unit; angles, when present, use degrees. Pitch circles
are not pulley tooth-tip or flank surfaces: those offsets belong to callers.
"""

from math import pi

from machinome.math import sqrt


def pulley_pitch_radius(teeth, pitch):
    """Return the pitch radius for a tooth count and linear tooth pitch.

    The circumference is teeth * pitch; the result has pitch's length
    unit. It is frame-independent, with no rotational zero or handedness.
    Physical inputs are a positive integer count and positive pitch, but no
    rounding or clamping is performed: zero and signed inputs keep arithmetic
    behavior, and raw symbolic inputs retain the same definition.

    Thor uses 2 mm GT2 pitch; Open Robot Actuator uses 3 mm AT3 pitch.
    Printer callers keep their fitted pitch and subtract their own surface
    allowance after this calculation. No tooth profile is generated here.
    """
    return teeth * pitch / (2 * pi)


def belt_tangent_points(centre_a, radius_a, centre_b, radius_b, sense_a=1, sense_b=1):
    """Return directed tangent contacts (point_a, point_b) in the XY plane.

    Centers and nonnegative radii use one length unit. Each sense is +1 for
    clockwise or -1 for counterclockwise travel around its circle. Equal
    senses select an outer tangent; opposite senses select an inner tangent.
    For centers (0, 0), (10, 0) and equal positive radii, default senses
    select the upper tangent, traveled toward +X. Reversing the route swaps
    circles and negates both senses. There is no angular zero or phase.

    Centers must differ and admit the requested common tangent. Unreachable
    numeric geometry raises the underlying sqrt/division error; nothing is
    clamped. At limiting tangency the two contacts coincide. A zero radius
    yields its center. Raw symbolic coordinates/radii share the same law.

    Thor and Prusa3-vanilla map their own belt-back turn markers to these
    explicit senses; this helper neither reads circles nor generates a belt.
    """
    dx, dy = centre_b[0] - centre_a[0], centre_b[1] - centre_a[1]
    separation_squared = dx * dx + dy * dy
    reach_a, reach_b = sense_a * radius_a, sense_b * radius_b
    difference = reach_a - reach_b
    height = sqrt(separation_squared - difference * difference)
    normal_x = (dx * difference - dy * height) / separation_squared
    normal_y = (dy * difference + dx * height) / separation_squared
    return ((centre_a[0] + reach_a * normal_x,
             centre_a[1] + reach_a * normal_y),
            (centre_b[0] + reach_b * normal_x,
             centre_b[1] + reach_b * normal_y))
