# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Finite pointwise contact profiles for a running machine's numeric bounds.

No CAD solid, mesh, tolerance, or continuous path certificate is inferred from
these authored planar polygons. A caller must establish that its polygons
actually cover the parts whose contact it models.
"""

from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from fractions import Fraction
from math import cos, isfinite, sin
from struct import pack, unpack


_DEGREE = 0.017453292519943295
_PAIR_LIMIT = 1024
_PLACEMENT_LIMIT = 256
_INTEGRATION_CACHE = ContextVar('profile_integration_cache', default=None)


class _IntegrationCache:
    __slots__ = ('pairs', 'placements')

    def __init__(self):
        self.pairs = OrderedDict()
        self.placements = OrderedDict()


class _CachedPlaced(tuple):
    """One successful placed value and its optional attempt-local search tree."""

    def __new__(cls, polygons):
        value = super().__new__(cls, polygons)
        value.box_tree = None
        return value


@contextmanager
def _profile_integration_cache():
    """Reuse successful pure contact work only for this integration attempt."""
    cache = _IntegrationCache()
    token = _INTEGRATION_CACHE.set(cache)
    try:
        yield cache
    finally:
        _INTEGRATION_CACHE.reset(token)


def _remember(entries, key, value, limit):
    entries[key] = value
    if len(entries) > limit:
        entries.popitem(last=False)


def _placement_key(profile, angle, xy):
    """Exact finite builtin operands only; never convert author objects."""
    if type(profile) is not ConvexProfile or type(xy) is not tuple or len(xy) != 2:
        return None
    operands = (angle, xy[0], xy[1])
    if any(type(value) not in (bool, int, float) for value in operands):
        return None
    try:
        bits = tuple(pack('!d', float(value)) for value in operands)
    except (TypeError, ValueError, OverflowError):
        return None
    if any(not isfinite(unpack('!d', value)[0]) for value in bits):
        return None
    return profile, bits


def _cached_placed(cache, pending, profile, angle, xy, key):
    if key is not None and key in pending:
        return pending[key]
    if key is not None and key in cache.placements:
        cache.placements.move_to_end(key)
        return cache.placements[key]
    placed = _placed(profile, angle, xy)
    if key is not None:
        placed = _CachedPlaced(placed)
        pending[key] = placed
    return placed


def _boxes_disjoint(left, right):
    return (left[2] < right[0] or right[2] < left[0] or
            left[3] < right[1] or right[3] < left[1])


def _tree_bounds(indices, placed):
    low_x, low_y, high_x, high_y = placed[indices[0]][2]
    for index in indices[1:]:
        box = placed[index][2]
        if box[0] < low_x: low_x = box[0]
        if box[1] < low_y: low_y = box[1]
        if box[2] > high_x: high_x = box[2]
        if box[3] > high_y: high_y = box[3]
    return (low_x, low_y, high_x, high_y)


def _box_tree(indices, placed, depth=0):
    """Comparison-only conservative hierarchy over validated placed boxes."""
    bounds = _tree_bounds(indices, placed)
    if len(indices) <= 4:
        return (bounds, tuple(indices), None, None)
    axis = depth % 2
    indices.sort(key=lambda index: (placed[index][2][axis], index))
    middle = len(indices) // 2
    return (bounds, None,
            _box_tree(indices[:middle], placed, depth + 1),
            _box_tree(indices[middle:], placed, depth + 1))


def _box_candidates(tree, box, placed, candidates):
    bounds, indices, left, right = tree
    if _boxes_disjoint(box, bounds):
        return
    if indices is not None:
        for index in indices:
            if not _boxes_disjoint(box, placed[index][2]):
                candidates.append(index)
    else:
        _box_candidates(left, box, placed, candidates)
        _box_candidates(right, box, placed, candidates)


def _finite(value, what):
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f'{what} must be a finite number') from exc
    if not isfinite(number):
        raise ValueError(f'{what} must be a finite number')
    return number


def _cross(a, b, c):
    return ((b[0] - a[0]) * (c[1] - a[1]) -
            (b[1] - a[1]) * (c[0] - a[0]))


def _on_segment(a, b, c):
    return (min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and
            min(a[1], b[1]) <= c[1] <= max(a[1], b[1]))


def _segments_meet(a, b, c, d):
    ab_c, ab_d = _cross(a, b, c), _cross(a, b, d)
    cd_a, cd_b = _cross(c, d, a), _cross(c, d, b)
    if ((ab_c > 0 > ab_d or ab_d > 0 > ab_c) and
            (cd_a > 0 > cd_b or cd_b > 0 > cd_a)):
        return True
    return ((ab_c == 0 and _on_segment(a, b, c)) or
            (ab_d == 0 and _on_segment(a, b, d)) or
            (cd_a == 0 and _on_segment(c, d, a)) or
            (cd_b == 0 and _on_segment(c, d, b)))


def _polygon(points, number):
    try:
        loop = tuple((_finite(x, 'profile x'), _finite(y, 'profile y'))
                     for x, y in points)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'profile polygon {number} has invalid vertices') from exc
    if len(loop) < 3 or len(set(loop)) != len(loop):
        raise ValueError(f'profile polygon {number} repeats a vertex or has fewer than three')
    exact = tuple((Fraction.from_float(x), Fraction.from_float(y))
                  for x, y in loop)
    size = len(exact)
    area = sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(exact, exact[1:] + exact[:1]))
    if area <= 0:
        raise ValueError(f'profile polygon {number} must have positive CCW area')
    for index in range(size):
        a, b, c = exact[index - 1], exact[index], exact[(index + 1) % size]
        turn = _cross(a, b, c)
        if turn < 0:
            raise ValueError(f'profile polygon {number} is not convex')
        if turn == 0:
            before = (b[0] - a[0], b[1] - a[1])
            after = (c[0] - b[0], c[1] - b[1])
            if before[0] * after[0] + before[1] * after[1] <= 0:
                raise ValueError(f'profile polygon {number} has a reversed collinear edge')
    for left in range(size):
        for right in range(left + 1, size):
            if right == left + 1 or (left == 0 and right == size - 1):
                continue
            if _segments_meet(exact[left], exact[(left + 1) % size],
                              exact[right], exact[(right + 1) % size]):
                raise ValueError(f'profile polygon {number} crosses itself')
    return loop


class ConvexProfile:
    """Immutable ordered convex loops for pointwise planar contact.

    Import from ``machinome.simulation.profile``. Each independent loop
    supplies finite CCW binary coordinates. Collinear corners are retained;
    invalid, repeated, crossing or concave loops are refused, never repaired.
    This value makes no claim that it covers an installed CAD part.
    """

    __slots__ = ('_polygons',)

    def __init__(self, polygons):
        try:
            loops = tuple(_polygon(points, number)
                          for number, points in enumerate(polygons))
        except TypeError as exc:
            raise ValueError('profile requires finite polygon loops') from exc
        if not loops:
            raise ValueError('profile requires at least one convex polygon')
        object.__setattr__(self, '_polygons', loops)

    @property
    def polygons(self):
        return self._polygons

    def __setattr__(self, name, value):
        raise AttributeError('ConvexProfile is immutable')

    def __delattr__(self, name):
        raise AttributeError('ConvexProfile is immutable')

    def _content_bytes(self):
        """Ordered binary content, including signed-zero bits, for one program."""
        data = [pack('!I', len(self._polygons))]
        for loop in self._polygons:
            data.append(pack('!I', len(loop)))
            for x, y in loop:
                data.extend((pack('!d', x), pack('!d', y)))
        return b''.join(data)

    def _published(self):
        """Flat exact point table; loops remain separate index runs."""
        points, polygons = [], []
        for loop in self._polygons:
            start = len(points)
            points.extend([x, y] for x, y in loop)
            polygons.append(list(range(start, len(points))))
        return {'points': points, 'polygons': polygons}


def _checked(value, what):
    if not isfinite(value):
        raise ValueError(f'{what} became nonfinite in profile placement')
    return value


def _placed(profile, angle, xy):
    if not isinstance(profile, ConvexProfile):
        raise TypeError('profile_overlap requires ConvexProfile operands')
    try:
        tx, ty = xy
    except (TypeError, ValueError) as exc:
        raise ValueError('profile XY translation requires two finite numbers') from exc
    tx, ty = _finite(tx, 'profile tx'), _finite(ty, 'profile ty')
    theta = _checked(_finite(angle, 'profile angle') * _DEGREE, 'profile theta')
    c, s = _checked(cos(theta), 'profile cosine'), _checked(sin(theta), 'profile sine')
    placed = []
    for loop in profile.polygons:
        points = []
        for x, y in loop:
            cx = _checked(c * x, 'profile x product')
            sy = _checked(s * y, 'profile y product')
            sx = _checked(s * x, 'profile x product')
            cy = _checked(c * y, 'profile y product')
            rx = _checked(_checked(cx - sy, 'profile rotated x') + tx,
                          'profile placed x')
            ry = _checked(_checked(sx + cy, 'profile rotated y') + ty,
                          'profile placed y')
            points.append((rx, ry))
        axes = []
        for index, u in enumerate(points):
            v = points[(index + 1) % len(points)]
            nx = _checked(u[1] - v[1], 'profile axis x')
            ny = _checked(v[0] - u[0], 'profile axis y')
            if nx == 0.0 and ny == 0.0:
                raise ValueError('profile edge collapsed after placement')
            axes.append((nx, ny))
        bounds = [points[0][0], points[0][1], points[0][0], points[0][1]]
        for x, y in points[1:]:
            if x < bounds[0]: bounds[0] = x
            if y < bounds[1]: bounds[1] = y
            if x > bounds[2]: bounds[2] = x
            if y > bounds[3]: bounds[3] = y
        placed.append((tuple(points), tuple(axes), tuple(bounds)))
    return tuple(placed)


def _projection(points, axis):
    nx, ny = axis
    values = []
    for x, y in points:
        px = _checked(x * nx, 'profile projection x')
        py = _checked(y * ny, 'profile projection y')
        values.append(_checked(px + py, 'profile projection'))
    low = high = values[0]
    for value in values[1:]:
        if value < low: low = value
        if value > high: high = value
    return low, high


def profile_overlap(left, right, left_angle, right_angle, *,
                    left_xy=(0.0, 0.0), right_xy=(0.0, 0.0)):
    """Return pointwise 1.0 for inclusive contact, else positive 0.0.

    Import from ``machinome.simulation.profile``. Angles are degrees;
    each profile rotates about its own origin, then translates in XY.
    Invalid polygons or nonfinite/collapsed placed geometry refuse rather
    than count as clearance. This is not continuous collision detection:
    a running Bound retains its existing path-sampling limit. The caller
    must independently prove that its authored loops cover installed parts.
    """
    from solid2.core.object_base import OpenSCADConstant
    from machinome.expression_graph import ExpressionNode
    from machinome.scad_expression import GraphValue, as_node
    positions = (left_angle, left_xy[0], left_xy[1],
                 right_angle, right_xy[0], right_xy[1])
    if any(isinstance(value, (OpenSCADConstant, ExpressionNode))
           for value in positions):
        if not isinstance(left, ConvexProfile) or not isinstance(right, ConvexProfile):
            raise TypeError('profile_overlap requires ConvexProfile operands')
        root = ExpressionNode('call', 'profileOverlap', (
            ExpressionNode('profile', value=left),
            ExpressionNode('profile', value=right),
            *(as_node(value) for value in positions)))
        return GraphValue(root)
    # Both complete profiles are prepared before any pairwise early return:
    # a distant AABB must not mask invalid transformed geometry.
    cache = _INTEGRATION_CACHE.get()
    if cache is None:
        left_placed = _placed(left, left_angle, left_xy)
        right_placed = _placed(right, right_angle, right_xy)
        pair_key = None
        pending = None
        right_reused = False
    else:
        left_key = _placement_key(left, left_angle, left_xy)
        right_key = _placement_key(right, right_angle, right_xy)
        pending = {}
        if left_key is None or right_key is None:
            # Uncertain input bypasses the entire memo, including the pure
            # other side; preserve the unmodified evaluator's work and error
            # order for custom conversion and indexing objects.
            pair_key = None
            right_reused = False
            left_placed = _placed(left, left_angle, left_xy)
            right_placed = _placed(right, right_angle, right_xy)
        else:
            pair_key = (left_key, right_key)
            if pair_key in cache.pairs:
                cache.pairs.move_to_end(pair_key)
                return cache.pairs[pair_key]
            right_reused = right_key in cache.placements
            # Publish neither new placement if either operand or SAT fails.
            left_placed = _cached_placed(cache, pending, left, left_angle, left_xy, left_key)
            right_placed = _cached_placed(cache, pending, right, right_angle, right_xy, right_key)
    tree = None
    new_tree = None
    if (right_reused and len(left_placed) >= 32 and len(right_placed) >= 16
            and len(left_placed) * len(right_placed) >= 512):
        tree = right_placed.box_tree
        if tree is None:
            # This candidate stays local until the entire predicate succeeds.
            new_tree = _box_tree(list(range(len(right_placed))), right_placed)
            tree = new_tree
    result = 0.0
    for a_points, a_axes, a_box in left_placed:
        if tree is None:
            candidates = right_placed
        else:
            indices = []
            _box_candidates(tree, a_box, right_placed, indices)
            indices.sort()
            candidates = (right_placed[index] for index in indices)
        for b_points, b_axes, b_box in candidates:
            if (a_box[2] < b_box[0] or b_box[2] < a_box[0] or
                    a_box[3] < b_box[1] or b_box[3] < a_box[1]):
                continue
            for axis in a_axes + b_axes:
                a_low, a_high = _projection(a_points, axis)
                b_low, b_high = _projection(b_points, axis)
                if a_high < b_low or b_high < a_low:
                    break
            else:
                result = 1.0
                break
        if result:
            break
    if cache is not None:
        for key, value in pending.items():
            _remember(cache.placements, key, value, _PLACEMENT_LIMIT)
        if pair_key is not None:
            _remember(cache.pairs, pair_key, result, _PAIR_LIMIT)
        if new_tree is not None:
            right_placed.box_tree = new_tree
    return result


def _profile_call(left, right, angle_a, tx_a, ty_a, angle_b, tx_b, ty_b):
    """The eight-operand graph operation, shared by both Python evaluators."""
    return profile_overlap(left, right, angle_a, angle_b,
                           left_xy=(tx_a, ty_a), right_xy=(tx_b, ty_b))
