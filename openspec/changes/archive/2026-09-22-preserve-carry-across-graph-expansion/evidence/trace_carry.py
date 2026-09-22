"""Read-only call tracing of the originating Curta's unchanged bulk request.

Run with the isolated framework first on PYTHONPATH and the Curta project
second. Wrappers call the original functions once and return their results
unchanged unless --extra-cut explicitly requests a diagnostic counterfactual.
This is proposal evidence, not a solver implementation.
"""

import argparse
import json
from math import isclose
from unittest.mock import patch

from machinome.simulation import Sim
from machinome.simulation import program
from simulation.tools.result_carry_graph_scope import result_graph


WATCH = {'tens.turn', 'lever.travel', 'wheel_0.turn', 'wheel_1.turn'}
READS = WATCH | {'crank.turn', 'ones.turn'}


def measure(stations, extra_cut=None):
    sim = Sim(result_graph(stations)(), dt=.1, record=64)
    for name, target in (('digit', 0), ('height', 9), ('crank_angle', 90)):
        assert sim.move(name, to=target).status == 'completed'
    assert isclose(sim.state['tens.turn'], 281.6, rel_tol=0, abs_tol=1e-8)
    before = dict(sim.state)
    rows, partitions = [], []
    original_integrated = program._integrated
    original_partition = program._Block._partition

    def integrated(member, start, delta, crossings, tick, forced):
        answer = original_integrated(member, start, delta, crossings, tick, forced)
        if member.driven[0] in WATCH:
            rows.append({'driven': member.driven[0],
                         'start': {k: v for k, v in start.items() if k in READS},
                         'delta': {k: v for k, v in delta.items() if k in READS},
                         'increment': answer[0], 'landing': answer[1]})
        return answer

    def partition(block, starts, steps, crossings, tick):
        answer = original_partition(block, starts, steps, crossings, tick)
        if extra_cut is not None:
            answer = sorted(set(answer) | {extra_cut})
        partitions.append({'members': list(block.names), 'cuts': list(answer)})
        return answer

    with patch.object(program, '_integrated', integrated), \
            patch.object(program._Block, '_partition', partition):
        command = sim.move('crank_angle', to=180)
    return {'stations': stations, 'injected_cut': extra_cut,
            'status': command.status,
            'before': before, 'after': dict(sim.state),
            'partitions': partitions, 'members': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stations', type=int, choices=range(2, 12),
                        action='append')
    parser.add_argument('--extra-cut', type=float,
                        help='Diagnostic counterfactual only; adds an internal cut')
    args = parser.parse_args()
    print(json.dumps({'framework_module': program.__file__}), flush=True)
    for stations in args.stations or (6, 7, 11):
        print(json.dumps(measure(stations, args.extra_cut)), flush=True)
    print(json.dumps({'complete': True}), flush=True)
