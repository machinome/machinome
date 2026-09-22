# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Print producer-owned source-timing evidence; never write another repository.

Run from the framework worktree with PYTHONPATH=. for compact fixtures. Add
the unchanged Curta repository to PYTHONPATH and pass --curta for project
diagnostics. JSON contains the real document, full records and content hashes.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

from machinome.simulation import Sim
from tests.test_running_document import document


def provenance():
    paths = ('machinome/simulation/program.py', 'machinome/simulation/run.py',
             'machinome/simulation/trajectory.py', 'machinome/core/serializer.py',
             'tools/generate_source_timing_fixtures.py',
             'tests/carriage_project/timed_carry.py')
    return {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in paths}


def run_case(name, model, requests, portions=None):
    began = time.monotonic()
    node = model()
    sim = Sim(node, dt=.1, record=4096, meshes=False)
    exported = document(node)
    rows = []

    def move(driver, target):
        started = time.monotonic()
        crossings_before, stops_before = len(sim.crossings), len(sim.stops)
        command = sim.move(driver, to=target)
        result = dict(driver=driver, to=target, status=command.status,
                      admitted=command.admitted, bank=dict(sim.state),
                      crossings=[asdict(entry) for entry in sim.crossings[crossings_before if portions else 0:]],
                      stops=[asdict(entry) for entry in sim.stops[stops_before if portions else 0:]],
                      seconds=time.monotonic()-started)
        assert command.status in ('completed', 'blocked'), result
        return result

    for index, (driver, target) in enumerate(requests):
        if portions and index == len(requests)-1:
            snapshot = sim.snapshot()
        rows.append(move(driver, target))
    result = dict(name=name, document=exported, rows=rows)
    if portions:
        whole = dict(sim.state)
        assert abs(whole['ones.turn']-724) < 1e-8
        assert abs(whole['tens.turn']-704) < 1e-8
        assert abs(whole['lever.travel']) < 1e-8
        sim.restore(snapshot)
        result['partitioned'] = [move('crank_angle', 90+90*n/portions)
                                 for n in range(1, portions+1)]
        assert all(abs(whole[key]-value) <= 1e-9*max(1, abs(value), abs(whole[key]))
                   for key, value in sim.state.items())
    result['seconds'] = time.monotonic()-began
    return result


def build(curta=False, case=None):
    if curta:
        from simulation.result_carry_graph_repro import ConstrainedResultCarryGraphRepro
        from simulation.tools.result_carry_graph_scope import result_graph
        models = [(f'curta-{n}', result_graph(n)) for n in (6, 7, 11)]
        models.append(('curta-11-constrained', ConstrainedResultCarryGraphRepro))
        requests = [('digit', 0), ('height', 9), ('crank_angle', 90), ('crank_angle', 180)]
    else:
        from tests.carriage_project.timed_carry import timed_carry, InheritedCrossings
        from tests.carriage_project.machine import FixedZero, ShiftedCarry
        models = [('fixed', FixedZero), ('shifted', ShiftedCarry),
                  ('landed', timed_carry()), ('later', timed_carry(later=True)),
                  ('nonuniform', timed_carry(nonuniform=True)),
                  ('curved', timed_carry(nonuniform='curved')),
                  ('range', timed_carry(bound=2)), ('contact', timed_carry(contact=True)),
                  ('crossing-budget', InheritedCrossings)]
        requests = [('crank', 4), ('crank', 0), ('crank', 4)]
    if case is not None:
        models = [(name, model) for name, model in models if name == case]
        if not models:
            raise ValueError(f'unknown fixture {case}')
    return dict(producer_sha256=provenance(),
                project_checkpoint='8852677' if curta else None,
                record_mode='delta' if curta else 'cumulative',
                cases=[run_case(name, model, requests, 12 if curta else None)
                       for name, model in models])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--curta', action='store_true')
    parser.add_argument('--case')
    args = parser.parse_args()
    print(json.dumps(build(args.curta, args.case), separators=(',', ':')))
