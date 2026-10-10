"""Read-only pinned-project parity probe for this OpenSpec cycle.

Run from a Curta project checkout with PYTHONPATH selecting one framework
checkout, that project, and the workspace molejo/python package. This file
does not write or modify the originating project.
"""

import argparse
import hashlib
import json
import struct
import time

from machinome.scad_expression import as_node
from machinome.simulation import Sim
from machinome.simulation.program import _PathValue
from machinome.simulation.run import Run
from simulation.running import OperatingCurta


parser = argparse.ArgumentParser()
parser.add_argument('case', choices=('first48', 'turn', 'stop'))
args = parser.parse_args()

samples = hashlib.sha256()
sample_count = 0
active = []
original_search = Run._searched_constraint
original_bind = _PathValue.bind
original_at = _PathValue.at
original_bind_from = getattr(_PathValue, 'bind_from', None)


def searched(run, constraint, *rest):
    active.append(constraint)
    try:
        return original_search(run, constraint, *rest)
    finally:
        active.pop()


def record(path, inputs, result):
    global sample_count
    if not active or path.root is not as_node(active[-1].graph):
        return
    constraint = active[-1]
    fields = (constraint.identifier, constraint.side,
              tuple((name, struct.pack('!d', float(value)).hex())
                    for name, value in sorted(inputs.items())),
              struct.pack('!d', float(result)).hex())
    samples.update(repr(fields).encode('utf-8') + b'\n')
    sample_count += 1


def bound(path, inputs):
    result = original_bind(path, inputs)
    record(path, inputs, result)
    return result


def later(path, inputs):
    result = original_at(path, inputs)
    record(path, inputs, result)
    return result


def from_cache(path, inputs, previous):
    hit, result = original_bind_from(path, inputs, previous)
    if hit:
        record(path, inputs, result)
    return hit, result


Run._searched_constraint = searched
_PathValue.bind = bound
_PathValue.at = later
if original_bind_from is not None:
    _PathValue.bind_from = from_cache


def bank_hash(sim):
    values = tuple((name, struct.pack('!d', float(value)).hex())
                   for name, value in sorted(sim.state.items()))
    return len(values), hashlib.sha256(repr(values).encode('utf-8')).hexdigest()


start_cpu = time.process_time()
start_wall = time.perf_counter()
dt = 1/240 if args.case == 'first48' else .1
sim = Sim(OperatingCurta(), dt=dt, record=64)
init_cpu = time.process_time() - start_cpu

if args.case in ('first48', 'turn'):
    sim.move('digit_1', to=1)
    request = sim.move('crank_rotation', by=360, duration=2)
    sim.run(48/240 if args.case == 'first48' else 2)
    outcome = {'status': request.status,
               'admitted_hex': float(request.admitted).hex()}
else:
    sim.move('digit_3', to=3)
    sim.move('crank_rotation', to=160)
    sim.move('digit_3', to=0)
    before = sim.snapshot()
    request = sim.move('crank_rotation', by=10, duration=.1)
    sim.run(.1)
    after = sim.snapshot()
    first = (request.status, float(request.admitted).hex(), bank_hash(sim))
    sim.restore(before)
    replay = sim.move('crank_rotation', by=10, duration=.1)
    sim.run(.1)
    outcome = {'status': request.status,
               'admitted_hex': float(request.admitted).hex(),
               'replay_status': replay.status,
               'replay_admitted_hex': float(replay.admitted).hex(),
               'replay_snapshot_exact': sim.snapshot() == after,
               'first_and_replay': first}

length, digest = bank_hash(sim)
print(json.dumps({
    'case': args.case, 'dt': dt, 'program': sim.program.identity,
    'cpu_seconds': time.process_time() - start_cpu,
    'tick_cpu_seconds': time.process_time() - start_cpu - init_cpu,
    'wall_seconds': time.perf_counter() - start_wall,
    'bank_length': length, 'bank_sha256': digest,
    'bound_samples': sample_count, 'bound_samples_sha256': samples.hexdigest(),
    'outcome': outcome,
}, sort_keys=True))
