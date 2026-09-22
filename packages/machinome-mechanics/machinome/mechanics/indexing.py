# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Accumulated indexed motion: degree input, caller-owned displacement stroke."""

from machinome.math import floor


def indexed_advance(angle, increment, stroke, phase_origin=0):
    """Add completed-turn increments to a caller's within-turn stroke.

    Angle and origin are degrees, with one turn fixed at 360. The pure
    ``stroke`` callable is invoked once at absolute phase in
    [phase_origin, phase_origin+360), NOT at phase measured from origin.
    Increment and stroke output share the caller's displacement unit,
    reference and positive direction. Signed turns remain unwrapped.

    Numeric and supported deferred values use the same formula. For deferred
    use the callback must itself support expression arithmetic: this does not
    make arbitrary Python branching or stateful callbacks symbolic. Callback
    errors propagate. Zero/negative increments and stroke offsets are retained.

    Seam continuity is caller-owned: the upper one-sided stroke limit must
    equal increment plus stroke(phase_origin). No continuity correction,
    geometry, reset or mounting policy is inferred.

    A calculator's carry uses origin 325 and its 36-degree cam stroke. A
    ratchet-fed sawmill uses origin zero, a 7.5-degree tooth step and its
    hook-derived stroke, then applies its reset outside this helper.
    """
    turns = floor((angle - phase_origin) / 360)
    phase = angle - 360 * turns
    return turns * increment + stroke(phase)
