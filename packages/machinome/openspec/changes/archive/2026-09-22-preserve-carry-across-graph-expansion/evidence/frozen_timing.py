"""Read-only check of the preserved frozen/selected equivalence contract."""

import json

from machinome.simulation import Sim
from machinome.simulation import program
from tests.carriage_project.machine import FixedZero, ShiftedCarry


def measure(model, portions):
    sim = Sim(model(), dt=.1)
    requests = []
    for portion in range(1, portions + 1):
        command = sim.move('crank', to=4 * portion / portions)
        requests.append({'status': command.status, 'admitted': command.admitted})
    return {'model': model.__name__, 'portions': portions,
            'requests': requests, 'bank': dict(sim.state),
            'blocks': sum(edge.kind == 'block' for edge in sim._run.program.edges)}


if __name__ == '__main__':
    print(json.dumps({'framework_module': program.__file__,
                      'runs': [measure(model, portions)
                               for model in (ShiftedCarry, FixedZero)
                               for portions in (1, 16)]}), flush=True)
