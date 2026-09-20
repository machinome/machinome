# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Generate version-10 producer fixtures without rewriting the legacy corpus.

Run from the framework root: PYTHONPATH=. python tools/generate_time_drive_corpus.py
Expected values come from Sim, and documents from the normal producer path.
The independent viewer must copy/replay this file before claiming support.
"""

import json
from pathlib import Path

from machinome.simulation import Sim
from machinome.simulation.run import _TOLERANCE
from tests.running_project.time_drive import (
    affine, astrarium, curved_stop, gated, mixed, releasable, stopped,
)
from tools.generate_running_corpus import apply_action, document_of


SCENARIOS = (
    ('TimeAffine', affine, 0.1, 12, []),
    ('TimeEnabled', gated, 1, 5, [
        {'tick': 3, 'move': {'input': 'enabled', 'to': 0}, 'handle': 'off'},
        {'tick': 5, 'move': {'input': 'enabled', 'to': 1}, 'handle': 'on'},
    ]),
    ('AstrariumClock', astrarium, 1, 20, [
        {'tick': 3, 'move': {'input': 'enabled', 'to': 0}, 'handle': 'off'},
        {'tick': 4, 'move': {'input': 'wind', 'by': 2}, 'handle': 'wind'},
        {'tick': 5, 'move': {'input': 'enabled', 'to': 1}, 'handle': 'on'},
        {'tick': 6, 'snapshot': 'running'},
        {'tick': 17, 'move': {'input': 'enabled', 'to': 0}, 'handle': 'off2'},
        {'tick': 17, 'move': {'input': 'wind', 'by': 5}, 'handle': 'rewind'},
        {'tick': 17, 'move': {'input': 'enabled', 'to': 1}, 'handle': 'on2'},
        {'tick': 18, 'restore': 'running'},
        {'tick': 19, 'reset': True},
    ]),
    ('IndependentTimeDrives', stopped, 1, 5, [
        {'tick': 4, 'snapshot': 'stopped'},
        {'tick': 5, 'restore': 'stopped'},
    ]),
    ('TimeRelease', releasable, 1, 6, [
        {'tick': 5, 'move': {'input': 'release', 'to': 10}, 'handle': 'release'},
    ]),
    ('MixedTimeDrive', mixed, 1, 4, [
        {'tick': 1, 'rate': {'input': 'assist', 'rate': 1}, 'handle': 'assist'},
    ]),
    ('CurvedTimeStop', curved_stop, 2, 2, []),
)

REQUIRED = ('explicit time drives', 'uncommanded motion',
            'enable at nonzero time', 'winding and exhaustion',
            'independent time-drive stop', 'mixed command/time stop',
            'snapshot restore and reset', 'curved time stop')


def stop_record(stop):
    result = {'coordinate': stop.coordinate, 'bound': stop.bound,
              'value': stop.value, 't': stop.t, 'inputs': list(stop.inputs)}
    if stop.time_drives:
        result['time_drives'] = list(stop.time_drives)
    return result


def run(factory, dt, steps, script):
    sim = Sim(factory(), dt, record=steps*8, meshes=False)
    handles, snapshots, ticks = {}, {}, []
    for step in range(1, steps+1):
        crossings_seen, stops_seen = len(sim.crossings), len(sim.stops)
        for action in script:
            if action['tick'] != step:
                continue
            if 'reset' in action:
                sim.reset()
            else:
                apply_action(sim, action, handles, snapshots)
            if 'restore' in action or 'reset' in action:
                # Restore clears both rings. Do not lose a new event by
                # slicing it at the pre-restore cursor.
                crossings_seen = stops_seen = 0
        sim.run(dt)
        ticks.append({
            'tick': sim.tick, 'time': sim.time, 'bank': sim.state,
            'crossings': [
                {'relation': one.relation, 'coordinate': one.coordinate,
                 'primitive': one.primitive, 'level': one.level, 't': one.t}
                for one in sim.crossings[crossings_seen:]],
            'stops': [stop_record(one) for one in sim.stops[stops_seen:]],
            'commands': [
                {'handle': name, 'status': command.status,
                 'admitted': command.admitted}
                for name, command in handles.items()],
        })
    return ticks


def uncovered_features(machines):
    seen = set()
    for entry in machines:
        program = entry['document']['program']
        drives = program.get('time_drives', [])
        if not drives:
            continue
        seen.add('explicit time drives')
        initial = {key: spec['initial'] for key, spec in
                   program['coordinates'].items()}
        if not entry['script'] and any(t['bank'] != initial for t in entry['ticks']):
            seen.add('uncommanded motion')
        moves = [action['move'] for action in entry['script'] if 'move' in action]
        if any(action['tick'] > 1 and action.get('move', {}).get('input') == 'enabled'
               for action in entry['script']):
            values = [t['bank'].get('shaft.turn') for t in entry['ticks']]
            if any(a == b for a, b in zip(values, values[1:])):
                seen.add('enable at nonzero time')
        if any(move.get('input') == 'wind' for move in moves) and any(
                t['bank'].get('weight.drop') == 10 for t in entry['ticks']):
            seen.add('winding and exhaustion')
        if all(any(op in action for action in entry['script'])
               for op in ('snapshot', 'restore', 'reset')):
            seen.add('snapshot restore and reset')
        previous = initial
        for tick in entry['ticks']:
            for stop in tick['stops']:
                blocked = set(stop.get('time_drives', []))
                if not blocked:
                    continue
                if stop['inputs']:
                    seen.add('mixed command/time stop')
                if len(drives) > len(blocked) and any(
                        tick['bank'][key] != previous[key]
                        and set(program['sources'].get(key, [])) - blocked
                        for key in initial):
                    seen.add('independent time-drive stop')
                if entry['name'] == 'CurvedTimeStop' and 0 < stop['t'] < 1:
                    seen.add('curved time stop')
            previous = tick['bank']
    return [feature for feature in REQUIRED if feature not in seen]


def build():
    machines = [
        {'name': name, 'dt': dt, 'steps': steps, 'script': script,
         'document': document_of(name, factory),
         'ticks': run(factory, dt, steps, script)}
        for name, factory, dt, steps, script in SCENARIOS]
    missing = uncovered_features(machines)
    if missing:
        raise ValueError(f'Time-drive corpus lacks: {", ".join(missing)}')
    return {'generated_by': 'tools/generate_time_drive_corpus.py',
            'tolerance': {'float': _TOLERANCE}, 'machines': machines}


if __name__ == '__main__':
    path = Path(__file__).resolve().parents[1] / 'tests/time-drive-corpus.json'
    fixture = build()
    path.write_text(json.dumps(fixture, indent=2) + '\n')
    print(f'{path}: {len(fixture["machines"])} scenarios, '
          f'{sum(len(m["ticks"]) for m in fixture["machines"])} ticks')
