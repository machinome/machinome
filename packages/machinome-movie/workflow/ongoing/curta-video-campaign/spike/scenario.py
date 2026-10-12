"""Spike question 2: the scenario 23 + 145 through the framework's public Sim.

Run with the workspace venv, the Curta project on PYTHONPATH and as the
working directory (its model imports `simulation.*`):

    env -C <Curta> PYTHONPATH=<Curta> <venv>/bin/python <this file> <out.json>

Records, for every request, what the framework returned (`input`, `by`,
`to`, `origin`, `end`, `admitted`, each commit's `relations`, `fraction`,
`value`, `targets`, and `stops`), the bank (`sim.snapshot().values`) before
the first request and after each, the result register read with the
project's `register_reading`, and the wall time of each request. Floats are
written by `json.dumps`, which writes the shortest repr that round-trips, so
the file carries them at full precision.
"""

import json
import sys
import time

from machinome.simulation import Sim
from simulation.clocked import ClockedCurta, register_reading


def number(value):
    """A bank or commit value as JSON: a Python float or int kept exactly."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    # numpy scalars and anything else with a float value: record the type too.
    if hasattr(value, 'item'):
        return value.item()
    raise TypeError(f'unexpected value {value!r} of type {type(value).__name__}')


def request_record(request):
    return {
        'input': request.input,
        'by': None if request.by is None else number(request.by),
        'to': None if request.to is None else number(request.to),
        'origin': number(request.origin),
        'end': number(request.end),
        'admitted': number(request.admitted),
        'commits': [{
            'relations': list(commit.relations),
            'fraction': number(commit.fraction),
            'value': number(commit.value),
            'targets': {k: number(v) for k, v in commit.targets.items()},
        } for commit in request.commits],
        'stops': [{
            'coordinate': stop.coordinate, 'side': stop.side,
            'bound': number(stop.bound), 'value': number(stop.value),
            'input': number(stop.input), 'fraction': number(stop.fraction),
        } for stop in request.stops],
        'types': {
            'origin': type(request.origin).__name__,
            'end': type(request.end).__name__,
            'fractions': sorted({type(c.fraction).__name__ for c in request.commits}),
            'targets': sorted({type(v).__name__ for c in request.commits for v in c.targets.values()}),
        },
    }


def bank(sim):
    return {k: number(v) for k, v in sorted(sim.snapshot().values.items())}


STEPS = [
    ('move', 'digit_1', {'to': 3}),
    ('move', 'digit_2', {'to': 2}),
    ('trigger', 'Turn crank', {}),
    ('read', 23, {}),
    ('move', 'digit_1', {'to': 5}),
    ('move', 'digit_2', {'to': 4}),
    ('move', 'digit_3', {'to': 1}),
    ('trigger', 'Turn crank', {}),
    ('read', 168, {}),
]


def main(out):
    started = time.perf_counter()
    sim = Sim(ClockedCurta())
    construction = time.perf_counter() - started
    record = {
        'model': 'simulation.clocked:ClockedCurta',
        'construction_seconds': construction,
        # Private attribute, read only to compare with the export's identity.
        'identity_private': getattr(getattr(sim, '_clocked', None), 'identity', None),
        'bank_before': bank(sim),
        'requests': [],
        'readings': [],
    }
    for kind, subject, args in STEPS:
        if kind == 'read':
            reading = register_reading(sim)
            record['readings'].append({'expected': subject, 'read': reading,
                                       'turns': register_reading(sim, True)})
            continue
        t0 = time.perf_counter()
        if kind == 'move':
            request = sim.move(subject, **args)
        else:
            request = sim.trigger(subject)
        seconds = time.perf_counter() - t0
        if request is None:
            raise SystemExit(f'{kind} {subject!r} returned no request')
        entry = {'step': [kind, subject, args], 'seconds': seconds,
                 **request_record(request), 'bank_after': bank(sim)}
        record['requests'].append(entry)
    # The same scenario a second time from reset, to show it is deterministic.
    sim.reset()
    again = []
    for kind, subject, args in STEPS:
        if kind == 'read':
            continue
        request = sim.move(subject, **args) if kind == 'move' else sim.trigger(subject)
        again.append({**request_record(request), 'bank_after': bank(sim)})
    first = [{k: v for k, v in r.items() if k not in ('step', 'seconds')}
             for r in record['requests']]
    record['repeat_identical'] = first == again
    with open(out, 'w') as f:
        json.dump(record, f, indent=1)
        f.write('\n')
    for r in record['requests']:
        print(f"{r['step'][0]:8} {r['step'][1]!r:14} {r['seconds']*1000:9.1f} ms "
              f"origin {r['origin']!r} end {r['end']!r} admitted {r['admitted']!r} "
              f"commits {len(r['commits'])} stops {len(r['stops'])}")
    print('readings', record['readings'])
    print('construction', round(construction, 2), 's; repeat identical', record['repeat_identical'])


if __name__ == '__main__':
    main(sys.argv[1])
