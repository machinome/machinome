"""Public-API Curta replay; prints complete evidence and changes no project file."""
import argparse
import hashlib
import json
from pathlib import Path
import time

from machinome.simulation import Sim
from simulation.result_carry_graph_repro import ConstrainedResultCarryGraphRepro
from simulation.tools.result_carry_graph_scope import result_graph


def emit(**record):
    print(json.dumps(record, sort_keys=True), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stations', type=int, default=11)
    parser.add_argument('--portions', type=int, default=12)
    parser.add_argument('--constrained', action='store_true')
    args = parser.parse_args()
    emit(configuration=vars(args), candidate_sha256={
        name: hashlib.sha256(Path(name).read_bytes()).hexdigest()
        for name in ('machinome/simulation/program.py',
                     'machinome/simulation/run.py',
                     'machinome/simulation/trajectory.py')})
    model = ConstrainedResultCarryGraphRepro if args.constrained else result_graph(args.stations)
    started = time.monotonic()
    sim = Sim(model(), dt=.1, record=64)

    def move(name, target):
        before = time.monotonic()
        emit(request=name, target=target)
        command = sim.move(name, to=target)
        emit(request=name, target=target, status=command.status,
             admitted=command.admitted, seconds=time.monotonic()-before,
             bank=dict(sim.state))
        assert command.status == 'completed', command
        return command.admitted

    for name, value in (('digit', 0), ('height', 9), ('crank_angle', 90)):
        move(name, value)
    saved = sim.snapshot()
    whole_admitted = move('crank_angle', 180)
    whole = dict(sim.state)
    assert abs(whole['ones.turn']-724) < 1e-8
    assert abs(whole['tens.turn']-704) < 1e-8
    assert abs(whole['lever.travel']) < 1e-8
    if args.portions > 1:
        sim.restore(saved)
        admitted = sum(move('crank_angle', 90+90*n/args.portions)
                       for n in range(1, args.portions+1))
        divided = dict(sim.state)
        errors = {name: divided[name]-value for name, value in whole.items()}
        disagreements = {name: error for name, error in errors.items()
                         if abs(error) > 1e-9*max(1, abs(whole[name]), abs(divided[name]))}
        emit(partition_errors=errors, disagreements=disagreements,
             whole_admitted=whole_admitted, divided_admitted=admitted)
        assert not disagreements, disagreements
        assert abs(admitted-whole_admitted) <= 1e-9*max(1, abs(whole_admitted))
    emit(passed=True, total_seconds=time.monotonic()-started)


if __name__ == '__main__':
    main()
