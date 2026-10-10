"""Measure, read-only, what a boundary-distance tier in front of the B-rep
Boolean would see: for every pair that reaches the engine's common after
the face-box tier, the extrema distance and its cost, the Boolean's cost
and emptiness, and the witness's cost. Wraps the engine's module-level
functions and runs `machinome test` in-process. Writes one JSON line per
common to $MEASURE_OUT and a summary at exit.

usage: python measure.py <machinome test args...>
"""
import atexit, json, os, sys, time
import numpy as np

OUT = os.environ['MEASURE_OUT']
records = []
current = {}

import machinome.engine.brep as brep
import machinome.test as mtest

_boolean = brep._boolean
_witness = brep._false_empty_witness
_intersect = brep.intersect_shapes
_faces_disjoint = mtest._faces_disjoint
_mutually_outside = brep.mutually_outside

from OCP.BRepExtrema import BRepExtrema_DistShapeShape as _DSS
from OCP.Extrema import Extrema_ExtFlag_MIN, Extrema_ExtAlgo_Tree, Extrema_ExtAlgo_Grad
VARIANTS = {}
if os.environ.get('MEASURE_VARIANTS') and os.environ.get('MEASURE_DEFAULT', '1') != '0':
    VARIANTS = {
        'min_tree': lambda a, b: _DSS(a, b, Extrema_ExtFlag_MIN, Extrema_ExtAlgo_Tree),
        'min_tree_mt': lambda a, b: _threaded(a, b, Extrema_ExtAlgo_Tree),
        'min_grad_mt': lambda a, b: _threaded(a, b, Extrema_ExtAlgo_Grad),
    }


def _threaded(a, b, algo):
    # The engine's _distance sets SetMultiThread after the two-shape
    # constructor has already performed, so it runs single-threaded; this
    # variant loads, sets the flag, then performs.
    d = _DSS()
    d.LoadS1(a)
    d.LoadS2(b)
    d.SetFlag(Extrema_ExtFlag_MIN)
    d.SetAlgo(algo)
    d.SetMultiThread(True)
    d.Perform()
    return d

tier = {'faces_disjoint_calls': 0, 'faces_disjoint_true': 0, 'faces_disjoint_s': 0.0,
        'mutually_outside_calls': 0, 'mutually_outside_true': 0, 'mutually_outside_s': 0.0}


def faces_disjoint(*args):
    t = time.perf_counter()
    r = _faces_disjoint(*args)
    tier['faces_disjoint_s'] += time.perf_counter() - t
    tier['faces_disjoint_calls'] += 1
    tier['faces_disjoint_true'] += bool(r)
    return r


def mutually_outside(first, second):
    t = time.perf_counter()
    r = _mutually_outside(first, second)
    tier['mutually_outside_s'] += time.perf_counter() - t
    tier['mutually_outside_calls'] += 1
    tier['mutually_outside_true'] += bool(r)
    return r


def boolean(operation, left, right, a, b):
    t = time.perf_counter()
    try:
        return _boolean(operation, left, right, a, b)
    finally:
        if operation == 'intersection':
            current['boolean_s'] = time.perf_counter() - t


def witness(first, second):
    t = time.perf_counter()
    try:
        w = _witness(first, second)
        current['witness'] = None if w is None else [float(x) for x in w]
        return w
    except Exception as error:
        current['witness_error'] = repr(error)[:200]
        raise
    finally:
        current['witness_s'] = time.perf_counter() - t


def bounds_overlap(a, b):
    (l1, h1), (l2, h2) = brep.bounds(a), brep.bounds(b)
    return bool(all(h1[i] >= l2[i] and h2[i] >= l1[i] for i in range(3)))


def intersect_shapes(first, second, first_name, second_name):
    global current
    current = {'first': first_name, 'second': second_name}
    f, s = brep.as_shape(first), brep.as_shape(second)
    current['faces'] = [len(brep._faces(f)), len(brep._faces(s))]
    t = time.perf_counter()
    try:
        current['bounds_overlap'] = bounds_overlap(f, s)
    except Exception as error:
        current['bounds_error'] = repr(error)[:200]
    current['bounds_s'] = time.perf_counter() - t
    t = time.perf_counter()
    if os.environ.get('MEASURE_DEFAULT', '1') != '0':
        try:
            current['distance'] = float(brep._distance(f, s))
        except Exception as error:
            current['distance_error'] = repr(error)[:200]
    else:
        try:
            current['distance'] = float(_threaded(f, s, Extrema_ExtAlgo_Grad).Value())
        except Exception as error:
            current['distance_error'] = repr(error)[:200]
    current['distance_s'] = time.perf_counter() - t
    if VARIANTS:
        for label, make in VARIANTS.items():
            t = time.perf_counter()
            try:
                d = make(f, s)
                current[label] = float(d.Value()) if d.IsDone() else None
            except Exception as error:
                current[label + '_error'] = repr(error)[:200]
            current[label + '_s'] = time.perf_counter() - t
    t = time.perf_counter()
    try:
        result = _intersect(first, second, first_name, second_name)
        current['empty'] = brep.solid_count(result) == 0
        current['volume'] = float(brep.solid_volume(result)) if not current['empty'] else 0.0
        return result
    except Exception as error:
        current['refused'] = type(error).__name__
        raise
    finally:
        current['total_s'] = time.perf_counter() - t
        records.append(current)
        with open(OUT, 'a') as out:
            out.write(json.dumps(current) + '\n')


brep._boolean = boolean
brep._false_empty_witness = witness
brep.intersect_shapes = intersect_shapes
brep.mutually_outside = mutually_outside
mtest._faces_disjoint = faces_disjoint

started = time.perf_counter()


def summary():
    rs = records
    empties = [r for r in rs if r.get('empty')]
    positive = [r for r in empties if r.get('distance', 0) > 0]
    zero = [r for r in empties if r.get('distance', 1) == 0]
    far_bounds = [r for r in empties if r.get('bounds_overlap') is False]
    sm = lambda L, k: sum(r.get(k, 0.0) for r in L)
    out = {
        'wall_s': time.perf_counter() - started,
        'tier': tier,
        'commons': len(rs), 'empty': len(empties), 'nonempty': len(rs) - len(empties),
        'refused': sum(1 for r in rs if 'refused' in r),
        'empty_positive_distance': len(positive),
        'empty_zero_distance': len(zero),
        'empty_tiny_distance_le_1e-6': sum(1 for r in empties if 0 < r.get('distance', 1) <= 1e-6),
        'empty_bounds_disjoint': len(far_bounds),
        'distance_s_all': sm(rs, 'distance_s'),
        'distance_s_on_empty_positive': sm(positive, 'distance_s'),
        'boolean_s_all': sm(rs, 'boolean_s'),
        'boolean_s_on_empty_positive': sm(positive, 'boolean_s'),
        'witness_s_all': sm(rs, 'witness_s'),
        'witness_s_on_empty_positive': sm(positive, 'witness_s'),
        'witness_s_on_empty_zero': sm(zero, 'witness_s'),
        'bounds_s_all': sm(rs, 'bounds_s'),
        'total_s_all': sm(rs, 'total_s'),
        'distance_min_on_empty': min((r['distance'] for r in empties if 'distance' in r), default=None),
        'distance_max_on_nonempty': max((r['distance'] for r in rs if not r.get('empty') and 'distance' in r), default=None),
    }
    for label in VARIANTS:
        out[label + '_s_all'] = sm(rs, label + '_s')
        out[label + '_disagreements'] = sum(
            1 for r in rs if label in r and 'distance' in r and r[label] is not None
            and abs(r[label] - r['distance']) > 1e-9 * max(1.0, r['distance']))
        out[label + '_unsound'] = sum(
            1 for r in rs if r.get(label) and r.get('distance') == 0)
    with open(OUT + '.summary.json', 'w') as f:
        json.dump(out, f, indent=1)
    sys.stderr.write('\nMEASURE SUMMARY ' + json.dumps(out) + '\n')


atexit.register(summary)

from machinome.cli import manage
sys.argv = ['machinome'] + sys.argv[1:]
try:
    manage()
except SystemExit as e:
    sys.stderr.write(f'machinome exited {e.code}\n')
