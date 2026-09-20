# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Belt pitch geometry, independent of mounting frame and tooth profile.

Lengths share one unit; angles, when present, use degrees. Pitch circles
are not pulley tooth-tip or flank surfaces: those offsets belong to callers.
"""

from math import pi


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
