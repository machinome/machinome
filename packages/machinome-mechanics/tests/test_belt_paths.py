# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Closed-route measurements against independent angular constructions."""

import math

import pytest
from solid2 import get_animation_time

from machinome_mechanics import belt_path_metrics
from tests.test_mechanisms import _eval_openscad_expr


def reference(centres, radii, senses):
    n = len(centres)
    normals, spans = [], []
    for i, a in enumerate(centres):
        j = (i + 1) % n
        b = centres[j]
        bearing = math.atan2(b[1] - a[1], b[0] - a[0])
        angle = bearing + math.acos(
            (senses[i] * radii[i] - senses[j] * radii[j]) / math.dist(a, b))
        normal = (math.cos(angle), math.sin(angle))
        normals.append(normal)
        p = tuple(a[k] + senses[i] * radii[i] * normal[k] for k in (0, 1))
        q = tuple(b[k] + senses[j] * radii[j] * normal[k] for k in (0, 1))
        spans.append((p, (normal[1], -normal[0]), math.dist(p, q)))
    wraps = []
    for i, s in enumerate(senses):
        arrival = math.atan2(s * normals[i-1][1], s * normals[i-1][0])
        departure = math.atan2(s * normals[i][1], s * normals[i][0])
        wraps.append(math.degrees((s * (arrival - departure)) % math.tau))
    arcs = tuple(r * math.radians(w) for r, w in zip(radii, wraps))
    stations, at = [], 0
    for i, span in enumerate(spans):
        stations.extend((at, at + span[2]))
        at += span[2] + arcs[(i+1) % n]
    return dict(spans=tuple(spans), wrap_angles=tuple(wraps), arc_lengths=arcs,
                stations=tuple(stations), length=at)


def assert_metrics(actual, expected, evaluate=lambda x: x):
    assert actual.keys() == expected.keys()
    for name in ('wrap_angles', 'arc_lengths', 'stations'):
        assert isinstance(actual[name], tuple)
        assert tuple(map(evaluate, actual[name])) == pytest.approx(expected[name], abs=1e-10)
    assert isinstance(actual['spans'], tuple)
    for (start, direction, length), target in zip(actual['spans'], expected['spans']):
        assert tuple(map(evaluate, start)) == pytest.approx(target[0], abs=1e-10)
        assert tuple(map(evaluate, direction)) == pytest.approx(target[1], abs=1e-10)
        assert evaluate(length) == pytest.approx(target[2], abs=1e-10)
    assert evaluate(actual['length']) == pytest.approx(expected['length'], abs=1e-10)


def test_equal_two_pulley_route_pins_all_output_fields():
    assert_metrics(belt_path_metrics(((0, 0), (10, 0)), (2, 2)), {
        'spans': (((0, 2), (1, 0), 10), ((10, -2), (-1, 0), 10)),
        'wrap_angles': (180, 180), 'arc_lengths': (2*math.pi, 2*math.pi),
        'stations': (0, 10, 10+2*math.pi, 20+2*math.pi), 'length': 20+4*math.pi})


@pytest.mark.parametrize('senses', [(1, 1, 1), (1, -1, 1), (-1, 1, -1)])
def test_unequal_three_circle_indexing_and_reversal(senses):
    centres, radii = ((0, 0), (30, 5), (15, -20)), (2, 4, 3)
    result = belt_path_metrics(centres, radii, senses)
    assert_metrics(result, reference(centres, radii, senses))
    for i, span in enumerate(result['spans']):
        assert result['stations'][2*i+1] - result['stations'][2*i] == pytest.approx(span[2])
        end = result['stations'][2*i+2] if i < 2 else result['length']
        assert end - result['stations'][2*i+1] == pytest.approx(result['arc_lengths'][(i+1)%3])
    reverse = belt_path_metrics(centres[::-1], radii[::-1], tuple(-s for s in senses[::-1]))
    assert reverse['length'] == pytest.approx(result['length'])
    assert reverse['wrap_angles'] == pytest.approx(result['wrap_angles'][::-1])
    for i, span in enumerate(reverse['spans']):
        original = result['spans'][(1-i) % 3]
        assert span[0] == pytest.approx(tuple(original[0][k] + original[1][k]*original[2] for k in (0, 1)))
        assert span[1] == pytest.approx(tuple(-v for v in original[1]))
        assert span[2] == pytest.approx(original[2])


def test_two_unequal_pulleys_match_closed_length_formula():
    small, large, distance = 3, 7, 30
    alpha = math.asin((large-small)/distance)
    expected = 2*math.sqrt(distance**2-(large-small)**2) + math.pi*(small+large) + 2*(large-small)*alpha
    result = belt_path_metrics(((0, 0), (distance, 0)), (small, large))
    assert result['length'] == pytest.approx(expected)
    assert result['wrap_angles'] == pytest.approx((180-2*math.degrees(alpha), 180+2*math.degrees(alpha)))


def test_collinear_middle_circle_has_zero_not_full_turn():
    result = belt_path_metrics(((0, 0), (10, 0), (20, 0)), (2, 2, 2))
    assert result['wrap_angles'] == (180, 0, 180)
    assert result['arc_lengths'][1] == 0
    assert result['length'] == pytest.approx(40+4*math.pi)


def test_collinear_roundoff_cannot_return_a_full_turn_at_the_seam():
    centres = ((96527.2157689035, 549738.8829412318),
               (791140.0713444261, -151976.87425406382),
               (676158871.5592293, -682425815.1458279))
    result = belt_path_metrics(centres, (2, 2, 2))
    assert result['wrap_angles'][1] == 0
    assert result['arc_lengths'][1] == 0
    assert all(0 <= angle < 360 for angle in result['wrap_angles'])
    assert result['length'] == pytest.approx(
        sum(math.dist(centres[i], centres[(i+1)%3]) for i in range(3)) + 4*math.pi)
    t = get_animation_time()
    symbolic = belt_path_metrics(tuple((x+t, y) for x, y in centres), (2, 2, 2))
    assert _eval_openscad_expr(symbolic['wrap_angles'][1], 0) == 0


def test_near_seam_wrap_is_not_tolerance_clamped():
    result = belt_path_metrics(((0, 0), (10, 0), (20, 1e-7)), (2, 2, 2))
    assert 359.999 < result['wrap_angles'][1] < 360


@pytest.mark.parametrize('radii', [(0, 0), (0, 2), (2, 0)])
def test_zero_radius_retains_direction_without_radius_division(radii):
    result = belt_path_metrics(((0, 0), (10, 0)), radii)
    assert_metrics(result, reference(((0, 0), (10, 0)), radii, (1, 1)))
    for i, radius in enumerate(radii):
        if radius == 0:
            assert result['arc_lengths'][i] == 0
        assert math.hypot(*result['spans'][i][1]) == pytest.approx(1)


def test_limiting_inner_tangents_do_not_normalize_zero_spans():
    result = belt_path_metrics(((0, 0), (5, 0)), (2, 3), (1, -1))
    assert all(span[2] == 0 for span in result['spans'])
    assert all(math.hypot(*span[1]) == pytest.approx(1) for span in result['spans'])
    assert result['wrap_angles'] == (0, 0)
    assert result['stations'] == (0, 0, 0, 0)
    assert result['length'] == 0


@pytest.mark.parametrize('centres,radii,senses', [([], [], None), ([(0, 0)], [1], None),
    ([(0, 0), (10, 0)], [1], None), ([(0, 0), (10, 0)], [1, 1], [1])])
def test_malformed_static_topology_is_rejected(centres, radii, senses):
    with pytest.raises(ValueError, match='at least two|same length'):
        belt_path_metrics(centres, radii, senses)


def test_geometric_domain_errors_are_not_clamped():
    with pytest.raises(ValueError):
        belt_path_metrics(((0, 0), (4, 0)), (2, 3), (1, -1))
    with pytest.raises(ZeroDivisionError):
        belt_path_metrics(((0, 0), (0, 0)), (2, 2))


@pytest.mark.parametrize('senses', [(1, 1, 1), (1, -1, 1)])
def test_deferred_centres_and_radii_match_independent_reference(senses):
    t = get_animation_time()
    result = belt_path_metrics(((t, 2*t), (30-t, 5), (15, -20)), (2+t/10, 4, 3), senses)
    for value in (-1, 0, .25, 1, 2):
        expected = reference(((value, 2*value), (30-value, 5), (15, -20)), (2+value/10, 4, 3), senses)
        assert_metrics(result, expected, lambda x: _eval_openscad_expr(x, value))
