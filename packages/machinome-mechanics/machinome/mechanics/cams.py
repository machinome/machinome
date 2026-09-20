# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Periodic follower envelopes: degree timing, caller-owned displacement axis."""

from machinome.math import clamp01, cos, floor


def harmonic_cam_lift(angle, lift, rise_span=180, return_span=180):
    """Return a half-cosine rise/return displacement with a base dwell.

    ``lift`` is the signed full peak displacement, in caller units. Angle
    and spans are degrees: zero starts the rise, followed immediately by
    the return, then zero displacement until the next 360-degree cycle.
    Negative angles traverse the same periodic envelope backwards. The
    caller owns the physical axis, mounting sign and phase subtraction.

    Physical spans are positive and sum to at most 360. They are not
    validated or repaired; numeric zero spans raise division errors.
    Numeric and supported deferred values share this arithmetic definition.
    The clamps define the rise/return intervals, not tolerance correction.

    Leonardo's hammer uses rise 240 and return 80, its physical cam return
    45. Deepseek's sawmill uses 180/180 with lift twice its FEED_THROW.
    This envelope neither generates a cam profile nor certifies contact.
    """
    phase = angle - 360 * floor(angle / 360)
    rise = clamp01(phase / rise_span)
    fall = clamp01((phase - rise_span) / return_span)
    return lift * (cos(180 * fall) - cos(180 * rise)) / 2
