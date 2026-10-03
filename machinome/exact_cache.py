# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Memos over exact shape handles and the artifact files they came from.

Kernel-agnostic memoization: every cache here is keyed on a file, an
observation or the identity of a handle the exact engine returned, never
on a shape's own contents, and fills itself by asking the engine
(`machinome.exact_engine`) for the operation. No function here reads,
measures or places a shape itself. Importing this module imports no
engine; the engine is resolved at the first miss.
"""

from collections import OrderedDict
import os
import struct

from machinome._artifact import ArtifactChanged, observe_artifact
from machinome.exact_engine import require_exact_engine


_shape_cache = {}

# The cache key of every shape `_shape_cache` currently holds, by object
# address. An address is only a safe identity while something keeps the
# object alive, and `_shape_cache` is exactly that: an entry here is added
# and removed with the shape it names, so an address can never be reused
# behind a surviving entry.
#
# A shape cannot be its own key: OCCT's sameness compares the underlying
# TShape and IGNORES location, so a shape and a differently placed copy of
# it would compare the same -- keying placements on the shape would serve
# one part's placement for another's.
_shape_keys = {}

# The observation each cached shape was loaded FROM, by shape cache key --
# recorded only when the file was the same before and after the read. The
# in-process key above stays `(path, float mtime)`; this is what lets the
# verdict store (ADR-156) digest the very bytes a compared shape came from,
# and refuse a persistent identity when the path has changed since.
_shape_observations = {}

# One placed shape per (shape cache key, exact matrix bytes), and one
# bounding box per shape cache key. A placement runs a full transform over
# the B-rep -- 6-19 ms on real parts -- and an animated assertion places the
# same solid by the same matrix at every candidate pair it visits.
#
# This is deliberately access ordered and bounded. A trajectory can contain
# indefinitely many distinct poses, so insertion-order-only eviction would
# unnecessarily discard a useful working set and unbounded retention would
# retain every old shape for the lifetime of the process.
_PLACEMENT_CACHE_LIMIT = 512
_placement_cache = OrderedDict()
_bounds_cache = {}

# One (F, 2, 3) float64 array of local face AABBs per shape cache key,
# beside `_bounds_cache`. It is safe to cache under that key because the
# engine's `face_bounds` is a pure function of the exact geometry: it takes
# every box without reading a triangulation, so no triangulation a shape
# may come to carry -- attached, replaced, or discarded after this entry is
# filled -- can ever change what is already served under this identity.
_face_box_cache = {}

_NEEDED_BY = 'reading exact geometry'


def _engine(reason):
    return require_exact_engine(_NEEDED_BY, reason)


def _reset_placement_cache():
    """Drop retained exact placements for direct isolation or a new run.

    This is intentionally an internal seam: callers can clear a process-local
    working set, but cannot configure or inspect cache policy as public API.
    """
    _placement_cache.clear()


def _evict(brep_file):
    """Drop every cached artifact derived from a rebuilt file."""
    for key in [key for key in _shape_cache if key[0] == brep_file]:
        _shape_keys.pop(id(_shape_cache.pop(key)), None)
        _shape_observations.pop(key, None)
        _bounds_cache.pop(key, None)
        _face_box_cache.pop(key, None)
        for placement in [placement for placement in _placement_cache
                          if placement[0] == key]:
            del _placement_cache[placement]


def _observed(path):
    try:
        return observe_artifact(path)
    except (OSError, ArtifactChanged):
        return None


def cached_shape(brep_file):
    """Load one immutable shape per ``(path, mtime)``, through the engine.

    The file is observed before and after the read, and the load
    observation is recorded beside the shape only when the two agree: the
    file the shape was read from is then exactly that observation's.
    """
    mtime = os.path.getmtime(brep_file)
    key = (brep_file, mtime)
    cached = _shape_cache.get(key)
    if cached is None:
        engine = _engine(f'{brep_file} is a BREP to load')
        _evict(brep_file)
        before = _observed(brep_file)
        cached = engine.read_brep(brep_file)
        after = _observed(brep_file)
        _shape_cache[key] = cached
        _shape_keys[id(cached)] = key
        if before is not None and before == after:
            _shape_observations[key] = before
    return cached


def shape_load_observation(key):
    """The observation the shape cached under `key` was loaded from, or
    None when its load was not observed coherently or it is gone."""
    return _shape_observations.get(key)


def shape_identity(shape):
    """The cache key of a shape this module holds, or None.

    None means "no stable identity": a shape composed for this comparison
    or read from a node whose BREP is not current. A caller keying work on
    geometry must not cache such a shape's results.
    """
    return _shape_keys.get(id(shape))


def cached_bounding_box(shape):
    """The shape's local bounding box, ``((xmin, ymin, zmin), (xmax, ymax,
    zmax))``, computed once per cached shape.

    A shape with no cache identity -- one composed for this comparison, or
    read from a node whose BREP is not current -- is measured directly,
    every time.
    """
    key = _shape_keys.get(id(shape))
    if key is None:
        return _engine('its bounding box is measured').bounds(shape)
    bounds = _bounds_cache.get(key)
    if bounds is None:
        bounds = _engine('its bounding box is measured').bounds(shape)
        _bounds_cache[key] = bounds
    return bounds


def cached_face_boxes(shape):
    """The shape's local per-face bounding boxes, an ``(F, 2, 3)`` array,
    computed once per cached shape identity -- mirrors
    ``cached_bounding_box`` exactly, including its escape hatch: a shape
    with no cache identity is measured directly, every time, and never
    cached.
    """
    key = _shape_keys.get(id(shape))
    if key is None:
        return _engine('its face boxes are measured').face_bounds(shape)
    boxes = _face_box_cache.get(key)
    if boxes is None:
        boxes = _engine('its face boxes are measured').face_bounds(shape)
        _face_box_cache[key] = boxes
    return boxes


def cached_placement(shape, matrix):
    """Place a local shape by the framework's composed 4x4 matrix, through
    the engine's `placed_shape`.

    Cached per ``(shape cache key, exact matrix bytes)``, so a solid placed by
    the same matrix twice while retained is transformed once. The matrix is
    compared by the exact IEEE-754 values sent to the kernel: a placement
    difference too small to see (including signed zero) is still a
    different placement, and this cache introduces no tolerance or rounding
    of its own. A shape with no cache identity is placed uncached.
    """
    key = _shape_keys.get(id(shape))
    if key is None:
        return _engine('it is placed').placed_shape(shape, matrix)
    values = tuple(float(matrix[row, column])
                   for row in range(3) for column in range(4))
    placement = (key, struct.pack('!12d', *values))
    placed = _placement_cache.get(placement)
    if placed is None:
        placed = _engine('it is placed').placed_shape(shape, matrix)
        while len(_placement_cache) >= _PLACEMENT_CACHE_LIMIT:
            _placement_cache.popitem(last=False)
        _placement_cache[placement] = placed
    else:
        _placement_cache.move_to_end(placement)
    return placed
