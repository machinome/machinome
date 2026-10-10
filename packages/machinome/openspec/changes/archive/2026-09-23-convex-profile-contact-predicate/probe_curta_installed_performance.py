"""Read-only, process-local timing of the current installed-profile trial."""

from collections import Counter, defaultdict
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from struct import pack
from time import perf_counter, process_time
import json
import os
import sys

import machinome.simulation.profile as profile
import machinome.simulation.run as run_module
from machinome.simulation import Sim
from simulation.tools.reverser_installed_trial import make_trial


EVIDENCE = Path('/home/asa/devel/machinome-studio/projects/Calculators/Curta-Type-I-3x/_build_checks/reverser-installed-profile-reference-a428dea.jsonl')
stats = defaultdict(float)
placement_keys = Counter()
pair_keys = Counter()
placed_cache = {}
pair_cache = {}
ordered_overlap = sha256()
memo = os.environ.get('MEMO') == '1'


def placement_key(profile_value, angle, xy):
    return (id(profile_value), *(pack('!d', float(x)) for x in (angle, *xy)))
original_overlap = profile.profile_overlap
original_placed = profile._placed
original_projection = profile._projection


def timed_placed(*args, **kwargs):
    start = process_time()
    try:
        key = placement_key(*args)
        if memo and key in placed_cache:
            stats['placed_hits'] += 1
            return placed_cache[key]
        result = original_placed(*args, **kwargs)
        if memo:
            placed_cache[key] = result
        return result
    finally:
        stats['placed_cpu'] += process_time() - start
        stats['placed_calls'] += 1


def timed_projection(*args, **kwargs):
    start = process_time()
    try:
        return original_projection(*args, **kwargs)
    finally:
        stats['projection_cpu'] += process_time() - start
        stats['projection_calls'] += 1


def timed_overlap(left, right, left_angle, right_angle, **kwargs):
    start = process_time()
    key = None
    if isinstance(left_angle, (int, float)) and isinstance(right_angle, (int, float)):
        left_xy = kwargs.get('left_xy', (0.0, 0.0))
        right_xy = kwargs.get('right_xy', (0.0, 0.0))
        left_key = placement_key(left, left_angle, left_xy)
        right_key = placement_key(right, right_angle, right_xy)
        placement_keys[left_key] += 1
        placement_keys[right_key] += 1
        key = (left_key, right_key)
        pair_keys[key] += 1
    try:
        if memo and key is not None and key in pair_cache:
            stats['pair_hits'] += 1
            result = pair_cache[key]
        else:
            result = original_overlap(left, right, left_angle, right_angle, **kwargs)
            if memo and key is not None:
                pair_cache[key] = result
        if key is not None:
            for part in (*left_key[1:], *right_key[1:]):
                ordered_overlap.update(part)
            ordered_overlap.update(pack('!d', result))
        return result
    finally:
        stats['overlap_cpu'] += process_time() - start
        stats['overlap_calls'] += 1
        stats['overlap_numeric_calls'] += isinstance(left_angle, (int, float)) and isinstance(right_angle, (int, float))


profile._placed = timed_placed
profile._projection = timed_projection
profile.profile_overlap = timed_overlap

captured_caches = []
original_scope = run_module._profile_integration_cache


@contextmanager
def capture_scope():
    with original_scope() as cache:
        captured_caches.append(cache)
        yield cache


run_module._profile_integration_cache = capture_scope


def deep_bytes(value, seen=None):
    if seen is None:
        seen = set()
    if id(value) in seen or isinstance(value, profile.ConvexProfile):
        return 0
    seen.add(id(value))
    size = sys.getsizeof(value)
    if isinstance(value, dict):
        size += sum(deep_bytes(key, seen) + deep_bytes(item, seen)
                    for key, item in value.items())
    elif isinstance(value, (list, tuple, set)):
        size += sum(deep_bytes(item, seen) for item in value)
    return size


def phase(label, action):
    before = dict(stats)
    start_cpu = process_time()
    start_wall = perf_counter()
    result = action()
    delta = {key: round(stats[key] - before.get(key, 0), 6) for key in stats}
    print(json.dumps({'phase': label, 'cpu': round(process_time() - start_cpu, 6),
                      'wall': round(perf_counter() - start_wall, 6),
                      'profile': delta, 'status': getattr(result, 'status', None)}, sort_keys=True), flush=True)
    return result


model = phase('make_trial', lambda: make_trial(EVIDENCE))
sim = phase('Sim_no_mesh', lambda: Sim(model(), dt=.1, meshes=False))
placement_keys.clear()
pair_keys.clear()
placed_cache.clear()
pair_cache.clear()
one_tick = os.environ.get('ONE_TICK') == '1'
request = phase('crank_request', lambda: sim.move('crank_rotation', to=18 if one_tick else 90,
                                                 duration=.1 if one_tick else .5))
phase('crank_run', lambda: sim.run(.1 if one_tick else .5))
print(json.dumps({'numeric_pair_calls': sum(pair_keys.values()),
                  'unique_pair_keys': len(pair_keys),
                  'max_pair_reuse': max(pair_keys.values(), default=0),
                  'placement_uses': sum(placement_keys.values()),
                  'unique_placements': len(placement_keys),
                  'max_placement_reuse': max(placement_keys.values(), default=0),
                  'ordered_overlap_sha256': ordered_overlap.hexdigest(),
                  'bank_bits_sha256': sha256(b''.join(
                      name.encode() + b'\0' + pack('!d', float(value))
                      for name, value in sorted(sim.state.items()))).hexdigest(),
                  'run_cache': None if not captured_caches else {
                      'pair_entries': len(captured_caches[-1].pairs),
                      'placement_entries': len(captured_caches[-1].placements),
                      'pair_incremental_bytes': deep_bytes(captured_caches[-1].pairs),
                      'placement_incremental_bytes': deep_bytes(captured_caches[-1].placements),
                      'largest_placed_value_bytes': max((deep_bytes(value)
                          for value in captured_caches[-1].placements.values()), default=0)}
                  }), flush=True)
print(json.dumps({'crank_status': request.status, 'crank_angle': sim.state['crank_rotation']}), flush=True)
request = phase('reverser_request_to_1_0475', lambda: sim.move('reverser_height', to=1.0475))
print(json.dumps({'reverser_status': request.status, 'reverser_height': sim.state['reverser_height']}), flush=True)
