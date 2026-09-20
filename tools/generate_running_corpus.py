# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Regenerate the running mode's cross-runtime conformance corpus.

ADR-022 recorded one `$t` semantics reimplemented in several runtimes
that must agree function for function, and `generate_parity_fixture.py`
closed that from the producer's side. The RUN is the same shape of
problem one layer up: a published program is executed by the framework's
own run and, from cycle 5, by a worker in the browser, and nothing but a
corpus can say they agree.

So this writes `tests/running-corpus.json` from the framework's OWN run.
Every expected value in it is a value the run PRODUCED -- never one
recomputed a second way -- which is what makes a disagreement mean the
other runtime drifted. The framework's suite replays it
(`tests/test_running_corpus.py`); the viewer commits a copy and replays
it against the worker.

The machines are the fixtures cycles 1 to 3 already built
(`tests/running_project/machine.py`), one per shape the run has to be
answerable for: an affine chain with a kink and a wiring, each jump
primitive, a multi-source law with a gate, the Pascaline-shaped carry, a
ratchet whose bound is an expression over its own coordinate, a stop on
one group while another runs, two stops in one tick, a fold and a stop in
one tick, and a law that READS THE COORDINATE IT DRIVES, whose dial holds
at its gap while the ring sweeps past it. Their scripts move, rate,
trigger both instruction forms, and take and restore a snapshot.

`uncovered_features` REFUSES to write a corpus that misses any of the
features the export capability lists, so the corpus's width is a
property of this tool rather than of whoever last edited the machine
list -- and the framework's suite tests that refusal directly, so the
width is visible without running this at all.

Run from the framework worktree root:

    PYTHONPATH="$PWD" python tools/generate_running_corpus.py [OUTPUT]
"""

import json
import os
import sys

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FIXTURE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'tests', 'running-corpus.json')

sys.path.insert(0, ROOT)

from machinome.core.serializer import (  # noqa: E402
    compiled_program, document_body, drivers_table, instructions_table,
    serialize_node, symbolic_document,
)
from machinome.simulation import Sim  # noqa: E402
from machinome.simulation.enumeration import (  # noqa: E402
    bind_declared_defaults,
)
from machinome.simulation.run import _TOLERANCE  # noqa: E402

from tests.carriage_project import machine as carriage  # noqa: E402
from tests.running_project import machine as machines  # noqa: E402


def machine_class(name):
    """One corpus machine by name, from either fixture package."""
    found = getattr(machines, name, None)
    if found is None:
        found = getattr(carriage, name)
    return found


#: The keys of a published document the RUN is answerable for. `root`,
#: `pieces` and `animation` are left out on purpose: the tree and the
#: meshes are what the geometry tests cover, and what the run executes is
#: the program.
DOCUMENT_KEYS = ('format', 'version', 'drivers', 'instructions',
                 'bindings', 'program')

#: Every feature the corpus must exercise, as the export capability lists
#: them. A corpus missing one is refused rather than written.
REQUIRED = (
    'floor', 'ceil', 'sign', '%', 'a comparison',
    'a multi-source law',
    'a stop located inside a tick',
    'a bound stated as an expression',
    'a bound reading another coordinate',
    'a stop reached by the motion of what a bound reads',
    'a command retired blocked',
    'a rate',
    'a snapshot',
    'a restore',
    'a relative instruction',
    'an absolute instruction',
    'a tick carrying both a crossing and a stop',
    'a law that reads the coordinate it drives',
    'a self-read coordinate holding at its gate while its input moves on',
    'a tick carrying both a self-read crossing and a stop',
    'a switched source',
    'a selection crossing inside a tick',
    'a tick carrying both a selection crossing and a stop',
    'an in-block gate crossing inside a tick',
    'a stop on a kinked determiner inside a tick',
    'an explicit play edge',
    'play retention and reversal release',
    'play pickup at both flanks',
    'a three-edge play cascade',
    'a downstream play stop located from its driver',
    'non-integer play contact',
    'split play requests',
    'play snapshot replay',
)

#: The CONTINUOUS SELECTIONS of the symbolic vocabulary, each of which
#: returns one of its operands exactly: a law built over them is
#: piecewise affine, and the framework's run cuts it at them rather than
#: searching it. A consumer re-derives this from the published
#: expression, exactly as `_kinked_laws` does below.
KINKS = ('abs', 'min', 'max')

COMPARISONS = ('<', '<=', '>', '>=', '==', '!=')


#: One entry per machine: its class name, its step size, how many ticks
#: to run, and the script applied BEFORE the tick each entry names.
CORPUS = (
    {'name': 'PlayCorpus', 'dt': 1.0, 'steps': 8, 'script': [
        {'tick': 1, 'move': {'input': 'dial', 'to': 100.0,
                             'duration': 1.0}, 'handle': 'play0'},
        {'tick': 2, 'move': {'input': 'dial', 'to': 40.0,
                             'duration': 1.0}, 'handle': 'play1'},
        {'tick': 3, 'snapshot': 'play'},
        {'tick': 3, 'move': {'input': 'dial', 'to': -100.0,
                             'duration': 1.0}, 'handle': 'play2'},
        {'tick': 5, 'restore': 'play'},
        {'tick': 6, 'move': {'input': 'dial', 'to': 100.0,
                             'duration': 1.0}, 'handle': 'play3'},
    ]},
    {'name': 'MeasuredPlayCorpus', 'dt': 0.5, 'steps': 10, 'script': [
        {'tick': 1, 'move': {'input': 'dial', 'to': 3.2757369,
                             'duration': 0.5}, 'handle': 'measured0'},
        {'tick': 2, 'move': {'input': 'dial', 'to': 1590.0,
                             'duration': 1.0}, 'handle': 'measured1'},
        {'tick': 4, 'move': {'input': 'dial', 'to': 1580.0,
                             'duration': 0.5}, 'handle': 'measured2'},
        {'tick': 5, 'move': {'input': 'dial', 'to': 1000.0,
                             'duration': 0.5}, 'handle': 'measured3'},
        {'tick': 6, 'move': {'input': 'dial', 'to': 500.0,
                             'duration': 0.5}, 'handle': 'measured4'},
        {'tick': 7, 'move': {'input': 'dial', 'to': 0.0,
                             'duration': 0.5}, 'handle': 'measured5'},
    ]},
    # The Curta bench's shape, at two step sizes: an affine chain, a
    # `clamp01` kink, a wiring into a plain port, a rate, both
    # instruction forms, and a snapshot restored a few ticks later.
    {'name': 'Train', 'dt': 0.05, 'steps': 30, 'script': [
        {'tick': 1, 'move': {'input': 'crank', 'by': 20.0,
                             'duration': 0.5}, 'handle': 'h0'},
        {'tick': 2, 'rate': {'input': 'lever', 'rate': 4.0},
         'handle': 'h1'},
        {'tick': 14, 'trigger': 'Advance', 'handles': ['h2']},
        {'tick': 20, 'snapshot': 'a'},
        {'tick': 25, 'restore': 'a'},
    ]},
    {'name': 'Train', 'dt': 0.1, 'steps': 20, 'script': [
        {'tick': 1, 'move': {'input': 'crank', 'to': 40.0,
                             'duration': 0.5}, 'handle': 'h0'},
        {'tick': 9, 'trigger': 'Wind', 'handles': ['h1', 'h2']},
    ]},
    # The pilot's illustration: one `floor` per crank revolution.
    {'name': 'Window', 'dt': 0.05, 'steps': 24, 'script': [
        {'tick': 1, 'move': {'input': 'crank', 'by': 500.0,
                             'duration': 1.0}, 'handle': 'h0'},
    ]},
    # The same window written with `%`.
    {'name': 'Remainder', 'dt': 0.05, 'steps': 24, 'script': [
        {'tick': 1, 'move': {'input': 'crank', 'by': 500.0,
                             'duration': 1.0}, 'handle': 'h0'},
    ]},
    # `wrap`, which is a `ceil`.
    {'name': 'Wrapped', 'dt': 0.05, 'steps': 20, 'script': [
        {'tick': 1, 'move': {'input': 'crank', 'by': 800.0,
                             'duration': 0.8}, 'handle': 'h0'},
    ]},
    # A `sign` that genuinely jumps.
    {'name': 'Throwing', 'dt': 0.05, 'steps': 20, 'script': [
        {'tick': 1, 'move': {'input': 'crank', 'by': 40.0,
                             'duration': 0.8}, 'handle': 'h0'},
    ]},
    # A comparison as a gate factor, over two sources, engaging
    # mid-tick.
    {'name': 'Clutch', 'dt': 0.05, 'steps': 24, 'script': [
        {'tick': 1, 'move': {'input': 'shaft', 'by': 60.0,
                             'duration': 1.0}, 'handle': 'h0'},
        {'tick': 4, 'move': {'input': 'sleeve', 'by': 2.0,
                             'duration': 0.4}, 'handle': 'h1'},
    ]},
    # The Pascaline-shaped carry, multi-source with a `floor` the
    # integration subtracts, at two step sizes.
    {'name': 'CarryLead', 'dt': 0.05, 'steps': 24, 'script': [
        {'tick': 1, 'move': {'input': 'column', 'by': 500.0,
                             'duration': 1.0}, 'handle': 'h0'},
        {'tick': 6, 'move': {'input': 'tens_entry', 'by': 2.0,
                             'duration': 0.4}, 'handle': 'h1'},
    ]},
    {'name': 'CarryLead', 'dt': 0.1, 'steps': 14, 'script': [
        {'tick': 1, 'move': {'input': 'column', 'by': 500.0,
                             'duration': 1.0}, 'handle': 'h0'},
    ]},
    # A bound stated as an expression over the joint's OWN coordinate:
    # reverse is blocked at the last seated tooth.
    {'name': 'Ratchet', 'dt': 0.05, 'steps': 20, 'script': [
        {'tick': 1, 'move': {'input': 'arbor', 'by': 10.0,
                             'duration': 0.2}, 'handle': 'h0'},
        {'tick': 8, 'move': {'input': 'arbor', 'by': -20.0,
                             'duration': 0.4}, 'handle': 'h1'},
    ]},
    # A stop on one group while an unrelated input runs its whole tick,
    # from an instruction that claims both.
    {'name': 'Swept', 'dt': 0.01, 'steps': 16, 'script': [
        {'tick': 1, 'trigger': 'Sweep', 'handles': ['h0', 'h1']},
    ]},
    # Two groups reaching two bounds at two fractions of one tick.
    {'name': 'TwoStops', 'dt': 0.05, 'steps': 12, 'script': [
        {'tick': 1, 'move': {'input': 'lever_in', 'by': 10.0,
                             'duration': 0.25}, 'handle': 'h0'},
        {'tick': 1, 'move': {'input': 'steer', 'by': 20.0,
                             'duration': 0.25}, 'handle': 'h1'},
    ]},
    # A `wrap` fold and a stop in ONE tick: the crossing is located
    # inside the segment before the stop and recorded at its fraction OF
    # THE TICK.
    {'name': 'StopAndJump', 'dt': 0.05, 'steps': 12, 'script': [
        {'tick': 1, 'move': {'input': 'crank', 'by': 30.0,
                             'duration': 0.05}, 'handle': 'h0'},
    ]},
    # A law that READS THE COORDINATE IT DRIVES: the Curta's clearing
    # rack, reduced. The dial clears to its gap and HOLDS there, bit for
    # bit, while the ring goes on sweeping past it -- which is the one
    # thing a version 5 consumer cannot reproduce, and what the far-side
    # landing is pinned by.
    {'name': 'Clearing', 'dt': 0.05, 'steps': 24, 'script': [
        {'tick': 1, 'move': {'input': 'ring', 'by': 600.0,
                             'duration': 0.6}, 'handle': 'h0'},
        {'tick': 16, 'move': {'input': 'ring', 'by': 300.0,
                              'duration': 0.3}, 'handle': 'h1'},
    ]},
    # The same law at a coarser step, swept BACKWARD from inside the
    # station, so the dial lands on the band's other edge.
    {'name': 'Clearing', 'dt': 0.1, 'steps': 12, 'script': [
        {'tick': 1, 'move': {'input': 'ring', 'to': 480.0,
                             'duration': 0.2}, 'handle': 'h0'},
        {'tick': 4, 'move': {'input': 'ring', 'by': -600.0,
                             'duration': 0.6}, 'handle': 'h1'},
    ]},
    # A self-read crossing and a STOP in one tick, and a declared range
    # the setter drives the dial into after the gate has cut: the bound
    # wins over the landing the same segment reported.
    {'name': 'StoppedClearing', 'dt': 0.05, 'steps': 16, 'script': [
        {'tick': 1, 'move': {'input': 'ring', 'by': 600.0,
                             'duration': 0.25}, 'handle': 'h0'},
        {'tick': 1, 'move': {'input': 'gauge_in', 'by': 100.0,
                             'duration': 0.25}, 'handle': 'h1'},
        {'tick': 1, 'move': {'input': 'setter', 'by': 100.0,
                             'duration': 0.25}, 'handle': 'h2'},
    ]},
    # A BLOCK: a union of dependencies the carriage SELECTS, ordered
    # once per piece. The crank turns the lower wheel, the lever is
    # tripped by whichever wheel the carriage has brought under it, and
    # the higher wheel is advanced by the lever at one position and by
    # the crank at the other -- so each member reads a coordinate the
    # other determines, through a comparison on a live input. Cranking
    # by `2.0` over `0.3 s` at this `dt` gives six ticks of `1/3`, so the
    # lever's `carry.travel` crosses the higher wheel's `>= 0.5` gate
    # STRICTLY INSIDE tick 2 rather than landing on a tick boundary --
    # which is what makes this scenario discriminate the block's order
    # (`pin-the-block-order` design.md section 1): a consumer that
    # executes the published members in listing order reads the lever
    # before the lower wheel has pushed it through the detent and loses
    # a sixth of a turn that never heals.
    {'name': 'ShiftedCarry', 'dt': 0.05, 'steps': 20, 'script': [
        {'tick': 1, 'move': {'input': 'crank', 'by': 2.0,
                             'duration': 0.3}, 'handle': 'h0'},
        {'tick': 8, 'move': {'input': 'shift', 'by': 1.0,
                             'duration': 0.2}, 'handle': 'h1'},
        {'tick': 14, 'move': {'input': 'crank', 'by': 2.0,
                              'duration': 0.3}, 'handle': 'h2'},
    ]},
    # A SELECTION CROSSING and a STOP in one tick: the lever is driven
    # into its declared range a third of the way along a tick whose
    # second half hands it to the other wheel.
    {'name': 'RangedBlock', 'dt': 0.05, 'steps': 8, 'script': [
        {'tick': 1, 'move': {'input': 'spin', 'by': 2.0,
                             'duration': 0.05}, 'handle': 'h0'},
        {'tick': 1, 'move': {'input': 'shift', 'by': 1.0,
                             'duration': 0.05}, 'handle': 'h1'},
        {'tick': 4, 'move': {'input': 'crank', 'by': 1.0,
                             'duration': 0.05}, 'handle': 'h2'},
    ]},
    # A bound that READS OTHER COORDINATES, both ways round: the plug
    # turns with the pins cleared, and the withdrawal that follows is
    # stopped by a coordinate that does not move in the tick that stops
    # it -- the capture.
    {'name': 'Captured', 'dt': 0.05, 'steps': 16, 'script': [
        {'tick': 1, 'move': {'input': 'twist', 'by': 30.0,
                             'duration': 0.1}, 'handle': 'h0'},
        {'tick': 6, 'move': {'input': 'feed', 'by': -5.0,
                             'duration': 0.1}, 'handle': 'h1'},
        {'tick': 10, 'snapshot': 'a'},
        {'tick': 12, 'move': {'input': 'twist', 'by': -30.0,
                              'duration': 0.1}, 'handle': 'h2'},
        {'tick': 14, 'restore': 'a'},
    ]},
    # A STOP on a determiner that is KINKED and carries NO jump plan at
    # all: the Curta bench's own `4 + 72 * clamp01((lever - 113.5)/11.25)`
    # with a range on the slide it drives. The bound lies on the law's
    # SLOPED piece and the tick starts on the FLAT one below it, so a
    # consumer that divides once over the whole tick puts the stop at
    # half way and admits 0.875 degrees of lever travel that never
    # happened. The law publishes `affine: false`, so a consumer that has
    # not learned to cut at a kink must SEARCH it -- which is correct,
    # and lands inside this corpus's own comparison window.
    {'name': 'KinkedStop', 'dt': 0.1, 'steps': 4, 'script': [
        {'tick': 1, 'move': {'input': 'lever', 'by': 40.0,
                             'duration': 0.1}, 'handle': 'h0'},
    ]},
)


def document_of(name, factory=None):
    """The program-bearing keys of the document `name` publishes."""
    node = (factory or machine_class(name))()
    bind_declared_defaults(node)
    program, initial = compiled_program(node)
    with symbolic_document(node) as (declarations, instructions):
        root = serialize_node(node, lambda rigid: rigid.name,
                              graph_values=True)
        drivers = drivers_table(declarations)
        events = instructions_table(
            instructions, version_five_or_above=program is not None)
    body = document_body(node, root, drivers, events, program, initial)
    return {key: body[key] for key in DOCUMENT_KEYS if key in body}


def run_machine(entry):
    """One machine's whole run, tick by tick."""
    sim = Sim(machine_class(entry['name'])(), entry['dt'],
              record=entry['steps'] + 1)
    script = {}
    for action in entry['script']:
        script.setdefault(action['tick'], []).append(action)
    handles = {}
    snapshots = {}
    crossings_seen = 0
    stops_seen = 0
    ticks = []
    for step in range(1, entry['steps'] + 1):
        for action in script.get(step, ()):
            apply_action(sim, action, handles, snapshots)
        sim.run(entry['dt'])
        crossings = sim.crossings[crossings_seen:]
        stops = sim.stops[stops_seen:]
        crossings_seen = len(sim.crossings)
        stops_seen = len(sim.stops)
        ticks.append({
            'tick': sim.tick,
            'bank': sim.state,
            'crossings': [{'relation': one.relation,
                           'coordinate': one.coordinate,
                           'primitive': one.primitive,
                           'level': one.level,
                           't': one.t} for one in crossings],
            'stops': [{'coordinate': one.coordinate, 'bound': one.bound,
                       'value': one.value, 't': one.t,
                       'inputs': list(one.inputs)} for one in stops],
            'commands': [{'handle': handle, 'status': command.status,
                          'admitted': command.admitted}
                         for handle, command in handles.items()],
        })
    return ticks


def apply_action(sim, action, handles, snapshots):
    if 'move' in action:
        request = dict(action['move'])
        handles[action['handle']] = sim.move(request.pop('input'), **request)
    elif 'rate' in action:
        handles[action['handle']] = sim.rate(action['rate']['input'],
                                             action['rate']['rate'])
    elif 'trigger' in action:
        issued = sim.trigger(action['trigger'])
        for handle, command in zip(action['handles'], issued):
            handles[handle] = command
    elif 'snapshot' in action:
        snapshots[action['snapshot']] = sim.snapshot()
    elif 'restore' in action:
        sim.restore(snapshots[action['restore']])
    else:
        raise SystemExit(f'unknown script action {action!r}')


def uncovered_features(machines):
    """Every feature of `REQUIRED` no machine in `machines` exercises.

    Mirrors `generate_parity_fixture.uncovered_builtins`: the inventory
    is stated here rather than inferred, so adding a machine cannot
    narrow the corpus by accident and removing one cannot narrow it at
    all -- this refuses to write instead.
    """
    seen = set()
    for entry in machines:
        program = entry['document'].get('program') or {}
        play_edges = [edge for edge in program.get('edges', ())
                      if edge.get('kind') == 'play']
        if play_edges:
            seen.add('an explicit play edge')
            if len(play_edges) >= 3:
                seen.add('a three-edge play cascade')
            if any(not float(edge['low']).is_integer()
                   or not float(edge['high']).is_integer()
                   for edge in play_edges):
                seen.add('non-integer play contact')
            if any('snapshot' in action for action in entry['script']) \
                    and any('restore' in action for action in entry['script']):
                seen.add('play snapshot replay')
            moves = [action for action in entry['script'] if 'move' in action]
            targets = [(action['move'].get('input'), action['move'].get('to'))
                       for action in moves if action['move'].get('to') is not None]
            if any(a[0] == b[0] == c[0]
                   and (a[1] < b[1] < c[1] or a[1] > b[1] > c[1])
                   for a, b, c in zip(targets, targets[1:], targets[2:])):
                seen.add('split play requests')
            banks = [tick['bank'] for tick in entry['ticks']]
            retained = play_edges[0]['gives'][0]
            source = play_edges[0]['needs'][0]
            deltas = [b[retained] - a[retained]
                      for a, b in zip(banks, banks[1:])]
            source_deltas = [b[source] - a[source]
                             for a, b in zip(banks, banks[1:])]
            if any(deltas[index] and deltas[index + 1] == 0.0
                   and source_deltas[index] * source_deltas[index + 1] < 0
                   for index in range(len(deltas) - 1)):
                seen.add('play retention and reversal release')
            if any(delta > 0 for delta in deltas) \
                    and any(delta < 0 for delta in deltas):
                seen.add('play pickup at both flanks')
            chained = {edge['gives'][0] for edge in play_edges[1:]}
            if any(stop['coordinate'] in chained for tick in entry['ticks']
                   for stop in tick['stops']):
                seen.add('a downstream play stop located from its driver')
        for edge in program.get('edges', ()):
            if edge['kind'] == 'law' and len(edge['needs']) > 1:
                seen.add('a multi-source law')
            for plan in edge.get('plans') or ():
                if plan is None:
                    continue
                for jump in plan['jumps']:
                    primitive = jump['primitive']
                    seen.add('a comparison' if primitive in COMPARISONS
                             else primitive)
        bindings = {item['name']: item['expression']
                    for item in entry['document'].get('bindings', ())}
        banked = set(program.get('coordinates') or ())
        for identifier, span in (program.get('spans') or {}).items():
            for side in ('low', 'high'):
                if not isinstance(span[side], dict):
                    continue
                seen.add('a bound stated as an expression')
                names = free_names(span[side]['expression'], bindings)
                if (names - {identifier}) & banked:
                    seen.add('a bound reading another coordinate')
        for instruction in entry['document'].get('instructions', {}).values():
            seen.add('an absolute instruction' if 'targets' in instruction
                     else 'a relative instruction')
        for action in entry['script']:
            for key, feature in (('rate', 'a rate'),
                                 ('snapshot', 'a snapshot'),
                                 ('restore', 'a restore')):
                if key in action:
                    seen.add(feature)
        # The driven ends a law of this machine READS: `needs` met with
        # `gives`, which is where the self-read is published and the one
        # thing a version 5 consumer reads as something else.
        reads = set()
        for edge in program.get('edges', ()):
            if edge['kind'] != 'law':
                continue
            reads |= set(edge['needs']) & set(edge['gives'])
        if reads:
            seen.add('a law that reads the coordinate it drives')
        sources = program.get('sources') or {}
        # The coordinates whose determiner is a law that is PIECEWISE
        # AFFINE and carries no jump plan: a stop on one cannot be
        # located by dividing once over the tick.
        kinked = _kinked_laws(program, bindings)
        # The BLOCK and its SELECTORS, re-derived from the published
        # edges exactly as a consumer must: no key carries either.
        gives, selectors = _selection(program, bindings)
        if any(set(edge['needs']) & gives
               for index, edge in enumerate(program.get('edges', ()))
               if index in selectors):
            seen.add('a switched source')
        previous = None
        for tick in entry['ticks']:
            if tick['stops']:
                seen.add('a stop located inside a tick')
            for identifier in reads:
                if previous is None:
                    continue
                held = previous[identifier] == tick['bank'][identifier]
                moved = any(previous[reaching] != tick['bank'][reaching]
                            for reaching in sources.get(identifier, ())
                            if reaching in tick['bank'])
                if held and moved:
                    seen.add('a self-read coordinate holding at its gate '
                             'while its input moves on')
            if tick['stops'] and any(one['coordinate'] in reads
                                     for one in tick['crossings']):
                seen.add('a tick carrying both a self-read crossing and '
                         'a stop')
            for stop in tick['stops']:
                # A stop whose coordinate holds the SAME value before and
                # after its tick was reached by the motion of what the
                # bound reads, not by the coordinate's own.
                identifier = stop['coordinate']
                before = (previous[identifier] if previous is not None
                          else (program.get('coordinates') or {})
                          .get(identifier, {}).get('initial'))
                if before is not None and before == tick['bank'].get(
                        identifier):
                    seen.add('a stop reached by the motion of what a '
                             'bound reads')
            selection = [one for one in tick['crossings']
                         if one['primitive'] in selectors.get(
                             _member_of(program, one['coordinate']), ())]
            if selection:
                seen.add('a selection crossing inside a tick')
                if tick['stops']:
                    seen.add('a tick carrying both a selection crossing '
                             'and a stop')
            # An IN-BLOCK GATE CROSSING located strictly inside a tick:
            # the previous tick's bank is what "moved" is measured
            # against, so the first tick (no predecessor) is skipped.
            if previous is not None:
                changed = {name for name, value in tick['bank'].items()
                           if previous.get(name) != value}
                for crossing in tick['crossings']:
                    if not 0 < crossing['t'] < 1:
                        continue
                    index = _member_of(program, crossing['coordinate'])
                    if index not in selectors:
                        continue
                    gates, blockers = _in_block_names(
                        program['edges'][index], crossing['primitive'],
                        bindings, gives)
                    if not any(names & changed for names in gates):
                        continue
                    if any(names & changed or not names <= set(tick['bank'])
                           for names in blockers):
                        continue
                    seen.add('an in-block gate crossing inside a tick')
            for stop in tick['stops']:
                if stop['coordinate'] in kinked and 0 < stop['t'] < 1:
                    seen.add('a stop on a kinked determiner inside a tick')
            if tick['stops'] and tick['crossings']:
                seen.add('a tick carrying both a crossing and a stop')
            for command in tick['commands']:
                if command['status'] == 'blocked':
                    seen.add('a command retired blocked')
            previous = tick['bank']
    return [feature for feature in REQUIRED if feature not in seen]


def _kinked_laws(program, bindings):
    """The coordinates a law with NO jump plan drives whose expression
    carries a KINK, re-derived from the published document as a consumer
    must: the plan is `null` and the expression calls `abs`, `min` or
    `max`."""
    found = set()
    for edge in program.get('edges', ()):
        if edge.get('kind') != 'law':
            continue
        plans = edge.get('plans') or [None] * len(edge.get('gives', ()))
        for index, name in enumerate(edge.get('gives', ())):
            if plans[index] is not None:
                continue
            expressions = edge.get('expressions') or []
            if index >= len(expressions) or expressions[index] is None:
                continue
            if _calls(expressions[index], bindings) & set(KINKS):
                found.add(name)
    return found


def _calls(expression, bindings):
    """Every function `expression` calls, through the document's own
    ordered `bindings` table."""
    from machinome.core.expressions import parse
    from machinome.expression_graph import postorder

    found, pending, seen = set(), [expression], set()
    while pending:
        text = str(pending.pop())
        if text in seen:
            continue
        seen.add(text)
        for item in postorder([parse(text)]):
            if item.kind == 'call':
                found.add(item.op)
            elif item.kind == 'name' and item.text in bindings:
                pending.append(bindings[item.text])
    return found


def _member_of(program, coordinate):
    """The index of the edge that determines `coordinate`, or None."""
    for index, edge in enumerate(program.get('edges', ())):
        if coordinate in edge.get('gives', ()):
            return index
    return None


def _selection(program, bindings):
    """`(what the blocks give, {edge index: its selector primitives})`,
    re-derived from the published edges the way a consumer must.

    A BLOCK is a strongly connected component of the graph over the
    edges' own `needs` and `gives` with `needs` met with `gives`
    excluded; a SELECTOR is a jump of a member's plan whose `level` --
    placeholders resolved transitively into their own jumps' levels --
    names no id the block gives. The primitives reported here are the
    ones a selector of that member has and no OTHER jump of it has, so a
    crossing carrying one is a selection crossing and not a gate that
    happens to share an operator.
    """
    edges = [edge for edge in program.get('edges', ())
             if edge.get('kind') != 'check']
    determiner = {name: index for index, edge in enumerate(edges)
                  for name in edge.get('gives', ())}
    after = {}
    for index, edge in enumerate(edges):
        own = set(edge.get('gives', ()))
        after[index] = {determiner[name] for name in edge.get('needs', ())
                        if name in determiner and name not in own}
    members = set()
    for start in after:
        seen, pending = set(), list(after[start])
        while pending:
            node = pending.pop()
            if node in seen:
                continue
            seen.add(node)
            pending.extend(after[node])
        if start in seen:
            members.add(start)
    gives = {name for index in members
             for name in edges[index].get('gives', ())}
    selectors = {}
    for index in members:
        found, other = set(), set()
        for plan in edges[index].get('plans') or ():
            if plan is None:
                continue
            levels = {jump['name']: jump['level'] for jump in plan['jumps']}
            for jump in plan['jumps']:
                names, pending = set(), [jump['level']]
                while pending:
                    text = str(pending.pop())
                    for name in free_names(text, bindings):
                        if name in levels:
                            pending.append(levels[name])
                        else:
                            names.add(name)
                if names & gives:
                    other.add(jump['primitive'])
                else:
                    found.add(jump['primitive'])
        selectors[index] = found - other
    return gives, selectors


def _in_block_names(edge, primitive, bindings, gives):
    """`(gates, selectors)` for `edge`'s jumps carrying `primitive`, each
    a list of the free names its level reads (resolved transitively
    through `bindings`, exactly as `_selection` resolves a level).

    A GATE names a coordinate `gives` holds OTHER than `edge`'s own
    driven end, ADR-121's self-read excluded because a self-read imposes
    no order; a SELECTOR names none of `gives` at all. A jump naming
    only `edge`'s own driven end is neither, and is not returned.
    """
    own = set(edge.get('gives', ()))
    gates, selectors = [], []
    for plan in edge.get('plans') or ():
        if plan is None:
            continue
        levels = {jump['name']: jump['level'] for jump in plan['jumps']}
        for jump in plan['jumps']:
            if jump['primitive'] != primitive:
                continue
            names, pending = set(), [jump['level']]
            while pending:
                text = str(pending.pop())
                for name in free_names(text, bindings):
                    if name in levels:
                        pending.append(levels[name])
                    else:
                        names.add(name)
            reaches = (names & gives) - own
            if reaches:
                gates.append(reaches)
            elif not names & gives:
                selectors.append(names)
    return gates, selectors


def free_names(expression, bindings):
    """Every free name `expression` reads, through the document's own
    ordered `bindings` table."""
    from machinome.core.expressions import parse
    from machinome.expression_graph import postorder

    found = set()
    pending = [expression]
    seen = set()
    while pending:
        text = pending.pop()
        if text in seen:
            continue
        seen.add(text)
        for item in postorder([parse(text)]):
            if item.kind != 'name':
                continue
            if item.text in bindings:
                pending.append(bindings[item.text])
            else:
                found.add(item.text)
    return found


def build():
    documents = {}
    found = []
    for entry in CORPUS:
        name = entry['name']
        if name not in documents:
            documents[name] = document_of(name)
        found.append({
            'name': name,
            'dt': entry['dt'],
            'steps': entry['steps'],
            'document': documents[name],
            'script': entry['script'],
            'ticks': run_machine(entry),
        })
    missing = uncovered_features(found)
    if missing:
        raise SystemExit(
            f'the corpus exercises neither {", nor ".join(missing)}, so it '
            f'would pin a run narrower than the one this framework can '
            f'execute; add a machine to CORPUS that does')
    return {
        'generated_by': 'tools/generate_running_corpus.py',
        'corpus': 'tests/running_project/machine.py',
        'tolerance': {'float': _TOLERANCE},
        'machines': found,
    }


def main():
    fixture = build()
    path = os.path.abspath(FIXTURE)
    with open(path, 'w') as handle:
        json.dump(fixture, handle, indent=2)
        handle.write('\n')
    ticks = sum(len(entry['ticks']) for entry in fixture['machines'])
    names = sorted({entry['name'] for entry in fixture['machines']})
    print(f'{path}: {len(fixture["machines"])} scenarios over '
          f'{len(names)} machines ({", ".join(names)}), {ticks} ticks, '
          f'{os.path.getsize(path)} bytes')


if __name__ == '__main__':
    main()
