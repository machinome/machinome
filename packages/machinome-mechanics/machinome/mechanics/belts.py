# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Belt pitch geometry, independent of mounting frame and tooth profile.

Lengths share one unit; angles, when present, use degrees. Pitch circles
are not pulley tooth-tip or flank surfaces: those offsets belong to callers.
"""

from math import pi

from machinome.math import atan2, floor, sqrt


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
    points, _, _ = _tangent_geometry(centre_a, radius_a, centre_b, radius_b,
                                     sense_a, sense_b)
    return points


def _tangent_geometry(centre_a, radius_a, centre_b, radius_b, sense_a, sense_b):
    """Contacts, unit normal and span length, including limiting tangency."""
    dx, dy = centre_b[0] - centre_a[0], centre_b[1] - centre_a[1]
    separation_squared = dx * dx + dy * dy
    reach_a, reach_b = sense_a * radius_a, sense_b * radius_b
    difference = reach_a - reach_b
    height = sqrt(separation_squared - difference * difference)
    normal_x = (dx * difference - dy * height) / separation_squared
    normal_y = (dy * difference + dx * height) / separation_squared
    points = ((centre_a[0] + reach_a * normal_x,
               centre_a[1] + reach_a * normal_y),
              (centre_b[0] + reach_b * normal_x,
               centre_b[1] + reach_b * normal_y))
    return points, (normal_x, normal_y), height


def belt_path_metrics(centres, radii, senses=None):
    """Measure an ordered closed pitch path in the caller's XY plane.

    Centers/radii share one length unit; senses are literal +1 clockwise,
    -1 counterclockwise, default all +1, as in belt_tangent_points. Return
    a dict with tuple fields: spans[i] is (start_xy, unit_direction_xy,
    length) leaving circle i; wrap_angles (degrees in [0,360)) and
    arc_lengths are circle-indexed; stations are starts of span0, arc1,
    span1, ..., arc0. Scalar length is their total. Distance zero is the
    departure from circle 0; coincident directions mean zero wrap.

    At least two circles and matching sequence lengths are required.
    Tangent domain errors propagate unchanged. Zero radii and limiting
    zero-length spans retain a defined direction. Supported raw deferred
    coordinates/radii use the same formula; topology and senses are static.

    Prusa and Hangprinter rotate arc_lengths by one entry for their
    after-span arc indexing. Their turn strings, pitch fits and mounting
    frames are not interpreted here; neither is Thor's legacy full-turn
    policy at coincident contacts. No route discovery or belt mesh is done.
    """
    count = len(centres)
    if count < 2:
        raise ValueError('a closed belt path requires at least two circles')
    if senses is None:
        senses = (1,) * count
    if len(radii) != count or len(senses) != count:
        raise ValueError('centres, radii and senses must have the same length')
    spans, normals = [], []
    for i in range(count):
        j = (i + 1) % count
        points, normal, length = _tangent_geometry(
            centres[i], radii[i], centres[j], radii[j], senses[i], senses[j])
        spans.append((points[0], (normal[1], -normal[0]), length))
        normals.append(normal)
    wraps, arcs = [], []
    for i, sense in enumerate(senses):
        arrival = atan2(sense * normals[i-1][1], sense * normals[i-1][0])
        departure = atan2(sense * normals[i][1], sense * normals[i][0])
        angle = sense * (arrival - departure)
        angle = angle - 360 * floor(angle / 360)
        # Tiny negative roundoff can make the first reduction round to 360.
        # Reduce once more to keep the half-open interval, without an epsilon
        # deadband or a numeric-only branch that would diverge under a driver.
        angle = angle - 360 * floor(angle / 360)
        wraps.append(angle)
        arcs.append(radii[i] * angle * (pi / 180))
    stations, at = [], 0
    for i, span in enumerate(spans):
        stations.extend((at, at + span[2]))
        at = at + span[2] + arcs[(i+1) % count]
    return dict(spans=tuple(spans), wrap_angles=tuple(wraps),
                arc_lengths=tuple(arcs), stations=tuple(stations), length=at)
