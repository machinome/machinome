# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Regenerate the CLOCKED mode's cross-runtime conformance corpus.

`generate_running_corpus.py`'s pattern, one discipline over: a version 8
document is executed by the framework's own clocked executor and, from
cycle 5, by the browser viewer, and nothing but a corpus can say they
agree.

So this writes `tests/clocked-corpus.json` from the framework's OWN
clocked executor. Every expected value in it is a value the executor
PRODUCED -- never one recomputed a second way -- which is what makes a
disagreement mean the other runtime drifted. The framework replays it
(`tests/test_clocked_corpus.py`); the viewer commits a copy and replays
it against the browser.

**Agreement is EXACT, bit for bit.** That is the one substantive
difference from the running corpus, which compares floats within the
run's own `1e-9`. A clocked executor has no such window: there is no
`dt`, so nothing is an increment; every event is SOLVED by division,
never searched; and two relations are ONE event exactly when their
landings are the SAME float. A consumer agreeing only within a tolerance
would merge events this framework keeps apart and split events it joins,
which is precisely what the discipline exists to be right about. The file
therefore carries `"tolerance": {"float": 0.0}` as a field of its own
rather than a convention of its reader.

The claim RESTS on operations that are exact or identically rounded in
both runtimes: IEEE `+`, `-`, `*`, `/` and `sqrt`, which the standard
requires correctly rounded; the truncated remainder, which is exact, and
the floored remainder composed from it, whose correction is one addition;
`floor`, `ceil`, `abs`, `sign`, `min`, `max` and the comparisons, which
select rather than round; and the LANDING WALK, which is a bisection in
the ordinal space of a double's own bits and which a second runtime must
reproduce as a bit walk rather than by stepping a small quantity. A
TRANSCENDENTAL and a POWER are OUTSIDE the claim -- neither is correctly
rounded -- so `uncovered_features`' companion `inexact_operations`
REFUSES a machine carrying one in a published commit law, event level,
constraint level or chain.

`uncovered_features` REFUSES to write a corpus that misses any feature
the export capability lists, so the corpus's width is a property of this
tool rather than of whoever last edited the machine list -- and the
framework's suite tests both refusals directly, so the width is visible
without running this at all.

Run from the framework worktree root:

    PYTHONPATH="$PWD" python tools/generate_clocked_corpus.py [OUTPUT]
"""

import json
import math
import os
import sys

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
FIXTURE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'tests', 'clocked-corpus.json')

sys.path.insert(0, ROOT)

from solid_node.core.expressions import parse  # noqa: E402
from solid_node.core.serializer import (  # noqa: E402
    compiled_clocked, document_body, drivers_table, instructions_table,
    serialize_node, symbolic_document,
)
from solid_node.expression_graph import postorder  # noqa: E402
from solid_node.scad_expression import GraphValue  # noqa: E402
from solid_node.simulation import Sim  # noqa: E402
from solid_node.simulation.enumeration import (  # noqa: E402
    bind_declared_defaults,
)

#: Where the corpus machines live. Each is a class of one of these
#: modules, addressed by class name.
MODULES = ('calculator', 'clearing', 'counter', 'decorative', 'freeze',
           'gate', 'lock', 'outside', 'pawl', 'pendulum', 'register',
           'ties', 'units')

#: The keys of a published document the CLOCKED executor is answerable
#: for. `root`, `pieces` and `animation` are left out on purpose: the
#: tree and the meshes are what the geometry tests cover, and what the
#: executor runs is the machine.
DOCUMENT_KEYS = ('format', 'version', 'drivers', 'states', 'instructions',
                 'bindings', 'clocked')

COMPARISONS = ('<', '<=', '>', '>=', '==', '!=')

#: The calls the exactness claim does NOT cover: neither a transcendental
#: nor a power is correctly rounded by IEEE, so libm and V8 need not
#: agree in the last bit. `sqrt` is admitted -- the standard requires it
#: correctly rounded.
INEXACT_CALLS = ('sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2')

#: Every feature the corpus must exercise, as the export capability lists
#: them. A corpus missing one is refused rather than written.
REQUIRED = (
    'floor', 'ceil', 'sign', 'a comparison',
    'a commit law taking a remainder of a negative operand',
    'a multi-source commit law',
    'a commit writing several targets',
    'an integer state rounded once',
    'an integer state whose law lands exactly halfway',
    'a scaled state',
    'a rising step that fires',
    'a falling step that fires nothing',
    'a kinked event level',
    'two relations landing on one float',
    'two surfaces one representable value apart',
    'two relations writing one state at one landing',
    'an event level that reads the state it commits',
    'one state written by two relations on two inputs',
    'a request clipped at a numeric bound',
    'a request clipped at a bound stated as an expression',
    'a bound reading another coordinate',
    'a bound reading its own coordinate',
    'a bound pair both of whose sides read the own coordinate',
    'a constraint level partitioned at its own jump surfaces',
    'a kinked constraint level',
    'a request admitted at zero travel',
    'a declared range nothing binds',
    'a bank standing outside a bound and moving back inside it',
    'an end-of-request judgement refusing a request',
    'a chain composed through an intermediate port',
    'a snapshot', 'a restore', 'a reset',
    'an instruction played as a request BY a travel',
    'an instruction played as a request TO a target',
    'a banked clock',
    'an event located on the clock',
    'a time request refused for running backwards',
    'a time request no bound clips',
    'a request refused for exceeding the crossing maximum',
    'a strict surface reached exactly',
    'a stop from a coordinate at zero',
)


#: One entry per machine: its class name and the script applied to it,
#: step by step. Every step is recorded, refusals included.
CORPUS = (
    # Cycle 1's counter: three strokes with a carry, a FALLING step that
    # fires nothing, a snapshot, a restore, a reset, and a request that
    # would cross more surfaces than one relation is admitted.
    {'name': 'Counter', 'script': [
        {'move': {'input': 'crank', 'by': 3700.0}},
        {'snapshot': 'a'},
        {'move': {'input': 'crank', 'by': -800.0}},
        {'restore': 'a'},
        {'move': {'input': 'crank', 'to': 4000.0}},
        {'reset': True},
        {'move': {'input': 'crank', 'by': 400000.0}},
    ]},
    # A KINKED event level, cut at its own breakpoint.
    {'name': 'KinkedCounter', 'script': [
        {'move': {'input': 'crank', 'by': -400.0}},
        {'move': {'input': 'crank', 'by': 1500.0}},
    ]},
    # The Curta's own shape in three wheels: a multi-source, multi-target
    # stroke over a NEGATIVE operand, and a clearing sweep whose event
    # level reads the digit it writes.
    {'name': 'Register', 'script': [
        {'move': {'input': 'operand', 'to': 4}},
        {'move': {'input': 'crank', 'by': 1100.0}},
        {'move': {'input': 'ring', 'by': 500.0}},
        {'reset': True},
        {'move': {'input': 'operand', 'to': -1}},
        {'move': {'input': 'crank', 'by': 400.0}},
    ]},
    {'name': 'Clearer', 'script': [
        {'move': {'input': 'ring', 'by': 60.0}},
        {'move': {'input': 'ring', 'by': -60.0}},
    ]},
    # The anti-reversal pawl: a bound reading its OWN coordinate, whose
    # level is partitioned at its own `floor` surfaces.
    {'name': 'Pawl', 'script': [
        {'move': {'input': 'crank', 'by': 1100.0}},
        {'move': {'input': 'crank', 'by': -30.0}},
    ]},
    # A plain NUMERIC range on a lift that simply stops at 9 mm.
    {'name': 'Stroke', 'script': [
        {'move': {'input': 'lift', 'by': 12.0}},
        {'move': {'input': 'crank', 'by': 400.0}},
    ]},
    # A SCALED driver reaching the same numeric bound.
    {'name': 'ScaledStroke', 'script': [
        {'move': {'input': 'lift', 'by': 30.0}},
    ]},
    # The note's interlock sketch, AS WRITTEN: a bound over another
    # coordinate that stops the CRANK at phase 1.
    {'name': 'Lock', 'script': [
        {'move': {'input': 'selector', 'by': 3.0}},
        {'move': {'input': 'crank', 'by': 400.0}},
    ]},
    # The same, with a KINKED constraint level.
    {'name': 'Kinked', 'script': [
        {'move': {'input': 'selector', 'by': 9.0}},
        {'move': {'input': 'crank', 'by': 90.0}},
    ]},
    # The correction, and ADR-126's acceptance fixture: a FREEZE, both
    # bounds reading the own coordinate, admitting ZERO travel off rest.
    {'name': 'Freeze', 'script': [
        {'move': {'input': 'selector', 'by': 3.0}},
        {'move': {'input': 'crank', 'by': 200.0}},
        {'move': {'input': 'selector', 'by': 3.0}},
        {'move': {'input': 'crank', 'by': 160.0}},
        {'move': {'input': 'selector', 'by': 3.0}},
    ]},
    # A bound reading a STATE the same request writes: the clip is read
    # ONCE, over the bank as it stands when the request begins.
    {'name': 'Gate', 'script': [
        {'move': {'input': 'crank', 'by': 1000.0}},
        {'move': {'input': 'crank', 'by': 800.0}},
    ]},
    # The other half: the commit SHUTS the gate, so the end-of-request
    # judgement refuses the whole request.
    {'name': 'Shut', 'script': [
        {'move': {'input': 'crank', 'by': 1000.0}},
    ]},
    # Two relations landing on ONE float, and the same pair written the
    # other way round.
    {'name': 'SamePair', 'script': [
        {'move': {'input': 'crank', 'by': 200.0}},
    ]},
    {'name': 'SwappedPair', 'script': [
        {'move': {'input': 'crank', 'by': 200.0}},
    ]},
    # Two surfaces ONE representable value apart, taken as two events.
    {'name': 'UlpPair', 'script': [
        {'move': {'input': 'crank', 'by': 200.0}},
    ]},
    # A strict and a non-strict comparison on one surface, driven
    # THROUGH it and -- after a reset -- ONTO it. A request that ends
    # exactly on a STRICT surface fires NOTHING: its landing is the
    # first value beyond the endpoint, which this request's path does
    # not contain. The next request begins on that surface and fires
    # it, one representable value along. The non-strict twin lands ON
    # the threshold and fires on the FIRST request (closure 1 of
    # `publish-the-clocked-machine`).
    {'name': 'Strict', 'script': [
        {'move': {'input': 'crank', 'to': 150.0}},
        {'move': {'input': 'crank', 'by': 50.0}},
        {'reset': True},
        {'move': {'input': 'crank', 'to': 100.0}},
        {'move': {'input': 'crank', 'by': 1.0}},
        {'move': {'input': 'crank', 'by': 1.0}},
    ]},
    {'name': 'NonStrict', 'script': [
        {'move': {'input': 'crank', 'to': 100.0}},
        {'move': {'input': 'crank', 'by': 1.0}},
    ]},
    # ELAPSED x MEMORY: a banked clock, an event located on it, and a
    # time request refused for running BACKWARDS.
    {'name': 'Regulator', 'script': [
        {'move': {'input': 'time', 'by': 5.0}},
        {'snapshot': 'b'},
        {'move': {'input': 'time', 'by': -1.0}},
        {'move': {'input': 'time', 'by': 0.0}},
        {'restore': 'b'},
    ]},
    # A clock nothing clips, beside a DRIVER that is clipped.
    {'name': 'Lift', 'script': [
        {'move': {'input': 'time', 'by': 4.0}},
        {'move': {'input': 'lift', 'by': 12.0}},
    ]},
    # A relation whose only moving source is the clock.
    {'name': 'ClockAlone', 'script': [
        {'move': {'input': 'time', 'by': 3.0}},
    ]},
    # A declared range NOTHING binds, and one placed where the rest
    # value is not.
    {'name': 'Decorative', 'script': [
        {'move': {'input': 'crank', 'by': 800.0}},
    ]},
    {'name': 'Untouchable', 'script': [
        {'move': {'input': 'crank', 'by': 800.0}},
    ]},
    # A SCALED state, and an integer state rounded ONCE at the commit.
    {'name': 'Scaled', 'script': [
        {'move': {'input': 'crank', 'by': 400.0}},
    ]},
    {'name': 'Rounded', 'script': [
        {'move': {'input': 'crank', 'by': 400.0}},
    ]},
    {'name': 'JumpsOnly', 'script': [
        {'move': {'input': 'crank', 'by': 4000.0}},
    ]},
    # A bank standing OUTSIDE a bound, moving back inside it -- and,
    # first, pushed FURTHER out from a coordinate standing at exactly
    # zero, which admits zero travel and reports its stop exactly as
    # the high-bound mirror `Outside` does (closure 1 of
    # `publish-the-clocked-machine`).
    {'name': 'Standing', 'script': [
        {'move': {'input': 'feed', 'by': -1.0}},
        {'move': {'input': 'feed', 'by': 5.0}},
        {'move': {'input': 'crank', 'by': 400.0}},
    ]},
    # A `ceil` event and a `sign` event, which no fixture of cycles 1 to
    # 3 states.
    {'name': 'Ceiling', 'script': [
        {'move': {'input': 'crank', 'by': 500.0}},
    ]},
    {'name': 'Signed', 'script': [
        {'move': {'input': 'shuttle', 'by': 10.0}},
    ]},
    # Two relations writing ONE state at ONE landing: the request is
    # refused and commits nothing.
    {'name': 'Conflict', 'script': [
        {'move': {'input': 'crank', 'by': 200.0}},
    ]},
    # The Curta-shaped machine: four wheels of one class, two writers per
    # digit, a selector wired through an intermediate PORT, a ratchet, a
    # freeze, and a law that lands an integer state on an EXACT HALF.
    {'name': 'Calculator', 'script': [
        {'move': {'input': 'operand', 'to': 4}},
        {'move': {'input': 'crank', 'by': 1100.0}},
        {'move': {'input': 'setting', 'by': 1.0}},
        {'move': {'input': 'crank', 'by': -30.0}},
        {'move': {'input': 'crank', 'by': 10.0}},
        {'move': {'input': 'setting', 'by': 2.0}},
        {'move': {'input': 'ring', 'by': 500.0}},
        {'move': {'input': 'feed', 'by': 350.0}},
        {'snapshot': 'c'},
        {'move': {'input': 'feed', 'by': 200.0}},
        {'restore': 'c'},
        {'reset': True},
        # An INSTRUCTION played as a request, in each of its two forms,
        # and -- from the same bank -- the relative one made BY HAND, so
        # the fixture pins that the two are the same request and not
        # merely that both were accepted (OpenSpec change
        # ``play-the-instruction``, design section 8). `Stroke` crosses
        # the stroke event at 360, so the triggered step carries commits
        # and not merely a bank.
        {'trigger': 'Set four'},
        {'snapshot': 'd'},
        {'trigger': 'Stroke'},
        {'restore': 'd'},
        {'move': {'input': 'crank', 'by': 360.0}},
    ]},
)


def machine_class(name):
    """One corpus machine by class name, from the clocked fixtures."""
    from importlib import import_module

    for module in MODULES:
        found = getattr(import_module(f'tests.clocked_project.{module}'),
                        name, None)
        if found is not None:
            return found
    raise SystemExit(f'no clocked fixture declares {name!r}')


def document_of(name):
    """The machine-bearing keys of the document `name` publishes."""
    node = machine_class(name)()
    bind_declared_defaults(node)
    clocked, bank = compiled_clocked(node)
    with symbolic_document(node) as (declarations, instructions):
        root = serialize_node(node, lambda rigid: rigid.name,
                              graph_values=True)
        drivers = drivers_table(declarations)
        events = instructions_table(instructions,
                                    version_five_or_above=clocked is not None)
    body = document_body(node, root, drivers, events, None, bank,
                         clocked=clocked)
    return {key: body[key] for key in DOCUMENT_KEYS if key in body}


def run_machine(entry):
    """One machine's whole script, step by step, recording EVERY step --
    the ones the executor refused included."""
    node = machine_class(entry['name'])()
    bind_declared_defaults(node)
    sim = Sim(node)
    snapshots = {}
    found = []
    for step in entry['script']:
        found.append(apply_step(sim, step, snapshots))
    return found


def apply_step(sim, step, snapshots):
    """One script step, as the fixture records it.

    A TRIGGER is recorded in exactly the shape a request is recorded in,
    because an instruction under a clocked root IS one request -- so the
    fixture pins what a BUTTON does and not merely that one was accepted
    (OpenSpec change ``play-the-instruction``, design section 8). The
    declared `duration` is deliberately not recorded: it is published in
    the document this fixture already carries verbatim, and the machine
    does not read it.

    A step the executor REFUSED is recorded as the refusal's KIND and the
    qualified names its message must name, with the bank AFTER it -- which
    is the bank before it, a refused request committing nothing. The
    message TEXT is deliberately not pinned: prose is edited for clarity
    and a fixture that pinned it would make every such edit a
    regeneration, while the KIND and the NAMES are the contract a second
    runtime must reproduce.
    """
    if 'move' in step or 'trigger' in step:
        before = dict(sim.state)
        if 'move' in step:
            request = dict(step['move'])
            input_id = request.pop('input')

            def made():
                return sim.move(input_id, **request)
        else:
            def made():
                return sim.trigger(step['trigger'])

        try:
            result = made()
        except Exception as failure:
            named = sorted(name for name in before
                           if name in str(failure))
            named.extend(sorted(
                coordinate for coordinate in _coordinates(failure)
                if coordinate not in named))
            return {'bank': dict(sim.state),
                    'refused': {'kind': type(failure).__name__,
                                'names': named}}
        return {
            'bank': dict(sim.state),
            'admitted': result.admitted,
            # BOTH ENDS of the path travelled, in the input's NATIVE
            # units -- the units every commit's `value` speaks, so a
            # consumer drawing the transition compares like with like.
            'origin': result.origin,
            'end': result.end,
            'commits': [{'relations': list(one.relations),
                         'fraction': one.fraction,
                         'value': one.value,
                         'targets': dict(one.targets)}
                        for one in result.commits],
            'stops': [{'coordinate': one.coordinate, 'side': one.side,
                       'bound': one.bound, 'value': one.value,
                       'input': one.input, 'fraction': one.fraction}
                      for one in result.stops],
        }
    if 'snapshot' in step:
        snapshots[step['snapshot']] = sim.snapshot()
    elif 'restore' in step:
        sim.restore(snapshots[step['restore']])
    elif 'reset' in step:
        sim.reset()
    else:
        raise SystemExit(f'unknown script step {step!r}')
    return {'bank': dict(sim.state)}


def _coordinates(failure):
    """The quoted qualified names a refusal's message carries."""
    import re

    return [found for found in re.findall(r"'([A-Za-z_][\w.]*)'",
                                          str(failure))]


##############################################
# Reading a published document back


def free_names(expression, bindings):
    """Every free name `expression` reads, through the document's own
    ordered `bindings` table."""
    found, pending, seen = set(), [expression], set()
    while pending:
        text = str(pending.pop())
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


def calls(expression, bindings):
    """Every function `expression` calls and every operator it applies,
    through the document's own ordered `bindings` table."""
    found, pending, seen = set(), [expression], set()
    while pending:
        text = str(pending.pop())
        if text in seen:
            continue
        seen.add(text)
        for item in postorder([parse(text)]):
            if item.kind == 'call':
                found.add(item.op)
            elif item.kind == 'binop':
                found.add(item.op)
            elif item.kind == 'name' and item.text in bindings:
                pending.append(bindings[item.text])
    return found


def _table(document):
    return {entry['name']: entry['expression']
            for entry in document.get('bindings', ())}


def _clocked_expressions(document):
    """Every expression the published `clocked` object carries, by where
    it stands: the commit laws and event levels, and the constraint
    chains, bounds and jump plans."""
    clocked = document.get('clocked') or {}
    found = []
    for commit in clocked.get('commits', ()):
        found.append(('an event level', commit['at']['level']))
        for expression in commit['law']:
            found.append(('a commit law', expression))
    for bound in clocked.get('bounds', ()):
        found.append(('a chain', bound['value']))
        if not isinstance(bound['bound'], (int, float)):
            found.append(('a bound', bound['bound']))
        plan = bound['plan']
        if plan is None:
            continue
        found.append(('a constraint level', plan['skeleton']))
        for jump in plan['jumps']:
            found.append(('a constraint level', jump['level']))
    return found


def _initial(document):
    """The bank the machine RESTS at, derived from the document exactly
    as a consumer derives it: every declared driver and every declared
    state at its declared default, with the clock at zero where there is
    one. A clocked bank holds nothing else, which is why the document
    publishes no table of it."""
    bank = {identifier: entry['default']
            for identifier, entry in document['drivers'].items()}
    bank.update({identifier: entry['default']
                 for identifier, entry in document['states'].items()})
    clock = (document.get('clocked') or {}).get('clock')
    if clock is not None:
        bank[clock] = 0.0
    return bank


def _evaluated(expression, values):
    if isinstance(expression, (int, float)):
        return float(expression)
    return GraphValue(parse(str(expression))).evaluate(values)


def _level(bound, bank, bindings, own):
    """One compiled constraint's LEVEL over `bank`, formed the way a
    consumer forms it: the chain, the bound with the coordinate's own
    value held under the published own-name, and the subtraction `side`
    names."""
    values = dict(bank)
    for name, expression in bindings.items():
        try:
            values[name] = _evaluated(expression, values)
        except (ValueError, KeyError, ZeroDivisionError):
            continue
    chain = _evaluated(bound['value'], values)
    values[own] = chain
    held = _evaluated(bound['bound'], values)
    return chain - held if bound['side'] == 'high' else held - chain


##############################################
# The two refusals


def non_finite_records(machines):
    """Every `(machine, step, where)` a machine RECORDS that is not a
    finite number.

    A commit that computes an infinity or a NaN refuses the request and
    banks nothing (`clocked.py`'s `_not_a_value`, and the export
    requirement's rule for a consumer), so no recorded bank, commit or
    admitted travel can carry one. Asserted here rather than assumed:
    `json.dump` would write such a value as the non-standard token
    `Infinity` or `NaN`, which a strict JSON reader in a second runtime
    refuses to parse at all -- the fixture would fail as a FILE, with
    nothing to say why (follow-up of 2026-09-17 to ADR-128).
    """
    found = []

    def walk(value, machine, step, where):
        if isinstance(value, bool):
            return
        if isinstance(value, (int, float)):
            if not math.isfinite(value):
                found.append((machine, step, where))
        elif isinstance(value, dict):
            for key, entry in value.items():
                walk(entry, machine, step, f'{where}.{key}')
        elif isinstance(value, (list, tuple)):
            for index, entry in enumerate(value):
                walk(entry, machine, step, f'{where}[{index}]')

    for entry in machines:
        for step, recorded in enumerate(entry['requests']):
            walk(recorded, entry['name'], step, 'the step')
    return found


def inexact_operations(machines):
    """Every `(machine, where, operation)` a machine publishes that the
    EXACTNESS claim does not cover.

    A transcendental and a power are not correctly rounded by IEEE, so
    two runtimes' libraries need not agree in the last bit. The claim
    therefore covers no machine that uses one in a published COMMIT LAW,
    EVENT LEVEL, CONSTRAINT LEVEL or CHAIN, and this REFUSES one rather
    than leaving the limitation to be remembered. A machine that needed
    one would need a tolerance declared for ITSELF, beside the file's
    own, and not a window the whole fixture relaxes into.

    `sqrt` is admitted: IEEE requires it correctly rounded. A POSE is not
    examined -- `pendulum`'s `sin` is in the geometry, which the corpus
    does not record at all.
    """
    found = []
    for entry in machines:
        document = entry['document']
        bindings = _table(document)
        for where, expression in _clocked_expressions(document):
            for operation in sorted(calls(expression, bindings)):
                if operation in INEXACT_CALLS or operation == '^':
                    found.append((entry['name'], where, operation))
    return found


def uncovered_features(machines):
    """Every feature of `REQUIRED` no machine in `machines` exercises.

    Mirrors `generate_running_corpus.uncovered_features`: the inventory
    is stated here rather than inferred, so adding a machine cannot
    narrow the corpus by accident and removing one cannot narrow it at
    all -- this refuses to write instead.
    """
    seen = set()
    for entry in machines:
        document = entry['document']
        clocked = document['clocked']
        bindings = _table(document)
        states = document['states']
        bank_ids = set(document['drivers']) | set(states)
        own = clocked['own']
        clock = clocked['clock']
        if clock is not None:
            seen.add('a banked clock')
            bank_ids.add(clock)

        writers = {}
        for commit in clocked['commits']:
            primitive = commit['at']['primitive']
            seen.add('a comparison' if primitive in COMPARISONS
                     else primitive)
            if len(commit['sources']) > 1:
                seen.add('a multi-source commit law')
            if len(commit['targets']) > 1:
                seen.add('a commit writing several targets')
            if 'kinked' in commit['shapes'].values():
                seen.add('a kinked event level')
            if clock is not None and clock in commit['shapes']:
                seen.add('an event located on the clock')
            reads = free_names(commit['at']['level'], bindings)
            if reads & set(commit['targets']):
                seen.add('an event level that reads the state it commits')
            for target in commit['targets']:
                writers.setdefault(target, []).append(
                    frozenset(commit['shapes']))
        for entries in writers.values():
            if len(entries) > 1 and not set.intersection(
                    *(set(one) for one in entries)):
                seen.add('one state written by two relations on two inputs')

        sides = {}
        for bound in clocked['bounds']:
            if not bound['shapes']:
                seen.add('a declared range nothing binds')
            for shape in bound['shapes'].values():
                if shape['level'] == 'kinked' or 'kinked' in shape['jumps']:
                    seen.add('a kinked constraint level')
            if isinstance(bound['bound'], (int, float)):
                continue
            names = free_names(bound['bound'], bindings)
            if own in names:
                seen.add('a bound reading its own coordinate')
                sides.setdefault(bound['coordinate'], set()).add(
                    bound['side'])
            if names & bank_ids:
                seen.add('a bound reading another coordinate')
        if any(len(found) == 2 for found in sides.values()):
            seen.add('a bound pair both of whose sides read the own '
                     'coordinate')

        by_side = {(bound['coordinate'], bound['side']): bound
                   for bound in clocked['bounds']}
        laws = [expression for where, expression
                in _clocked_expressions(document) if where == 'a commit law']
        remainders = any('%' in calls(expression, bindings)
                         for expression in laws)
        halves = _lands_on_a_half(clocked, states, bindings)
        if _through_a_port(entry) and clocked['bounds']:
            seen.add('a chain composed through an intermediate port')

        banks = [_initial(document)]
        outside = False
        for script_step, step in zip(entry['script'], entry['requests']):
            before = banks[-1]
            banks.append(step['bank'])
            moved = script_step.get('move')
            played = script_step.get('trigger')
            if played is not None:
                # An instruction under a clocked root is ONE request over
                # the driver it names, so a triggered step is read here
                # exactly as a request step is -- and which FORM was
                # played is read off the published table, the way a
                # consumer reads it.
                declared = document['instructions'][played]
                if 'by' in declared:
                    seen.add('an instruction played as a request BY a '
                             'travel')
                    moved = {'input': next(iter(declared['by']))}
                else:
                    seen.add('an instruction played as a request TO a '
                             'target')
                    moved = {'input': next(iter(declared['targets']))}
            if moved is not None:
                origin = before.get(moved['input'])
                if (origin == 0.0 and step.get('stops')
                        and step.get('admitted') == 0.0):
                    # Closure 1(b): the low side of a bound stops a
                    # coordinate standing at exactly zero, where the ulp
                    # of the value itself is a denormal.
                    seen.add('a stop from a coordinate at zero')
                for one in step.get('commits') or ():
                    if origin is not None and one['value'] in (
                            math.nextafter(origin, math.inf),
                            math.nextafter(origin, -math.inf)):
                        # Closure 1(a): a STRICT surface the previous
                        # request ended exactly on, fired by this one at
                        # the first representable value past it.
                        seen.add('a strict surface reached exactly')
            refused = step.get('refused')
            if refused is not None:
                seen.add({
                    'ClockedError':
                        'two relations writing one state at one landing',
                    'JointRangeError':
                        'an end-of-request judgement refusing a request',
                    'ValueError':
                        'a time request refused for running backwards',
                    'TooManyEvents':
                        'a request refused for exceeding the crossing '
                        'maximum',
                }.get(refused['kind'], refused['kind']))
                continue
            commits = step.get('commits')
            if commits is None:
                continue
            if commits:
                seen.add('a rising step that fires')
                if remainders and any(value < 0 for value
                                      in step['bank'].values()):
                    seen.add('a commit law taking a remainder of a '
                             'negative operand')
                for one in commits:
                    if len(one['relations']) > 1:
                        seen.add('two relations landing on one float')
                    for target, value in one['targets'].items():
                        if states[target]['dtype'] == 'int':
                            seen.add('an integer state rounded once')
                        if states[target]['scale'] is not None:
                            seen.add('a scaled state')
                        if target in halves:
                            seen.add('an integer state whose law lands '
                                     'exactly halfway')
                values = sorted(one['value'] for one in commits)
                if any(math.nextafter(low, math.inf) == high
                       for low, high in zip(values, values[1:])):
                    seen.add('two surfaces one representable value apart')
            elif step['admitted'] < 0:
                seen.add('a falling step that fires nothing')
            if step['stops']:
                if step['admitted'] == 0.0:
                    seen.add('a request admitted at zero travel')
                for stop in step['stops']:
                    bound = by_side[(stop['coordinate'], stop['side'])]
                    if isinstance(bound['bound'], (int, float)):
                        seen.add('a request clipped at a numeric bound')
                    else:
                        seen.add('a request clipped at a bound stated as '
                                 'an expression')
                    if bound['plan'] is not None:
                        seen.add('a constraint level partitioned at its '
                                 'own jump surfaces')
            elif clock is not None and step['admitted'] != 0.0:
                seen.add('a time request no bound clips')

        for bound in clocked['bounds']:
            levels = []
            for bank in banks:
                try:
                    levels.append(_level(bound, bank, bindings, own))
                except (ValueError, KeyError, ZeroDivisionError):
                    levels.append(None)
            for index, level in enumerate(levels):
                if level is None or level <= 0:
                    continue
                if any(later is not None and later <= 0
                       for later in levels[index + 1:]):
                    outside = True
        if outside:
            seen.add('a bank standing outside a bound and moving back '
                     'inside it')

        for step in entry['script']:
            for key, feature in (('snapshot', 'a snapshot'),
                                 ('restore', 'a restore'),
                                 ('reset', 'a reset')):
                if key in step:
                    seen.add(feature)
    return [feature for feature in REQUIRED if feature not in seen]


def _lands_on_a_half(clocked, states, bindings):
    """The integer states whose commit law is a DIVISION BY TWO, which is
    how a law lands exactly halfway between two whole native units.

    Read off the published document as a consumer reads it, and not from
    the machine: the value a half-to-even rounding produces is what the
    corpus RECORDS, and this says which machine states the question.
    """
    found = set()
    for commit in clocked['commits']:
        for target, expression in zip(commit['targets'], commit['law']):
            if states.get(target, {}).get('dtype') != 'int':
                continue
            root = parse(str(expression))
            if (root.kind == 'binop' and root.op == '/'
                    and root.children[1].kind == 'num'
                    and float(root.children[1].text) == 2.0):
                found.add(target)
    return found


def _through_a_port(entry):
    """Whether this machine's chains are composed through an intermediate
    PORT.

    A port composed THROUGH leaves no trace in the document -- which is
    the requirement, and the reason this asks the fixture's own class
    rather than the published bytes.
    """
    from solid_node.motion.ports import declared_ports

    klass = machine_class(entry['name'])
    return bool(declared_ports(klass))


def build():
    documents = {}
    found = []
    for entry in CORPUS:
        name = entry['name']
        if name not in documents:
            documents[name] = document_of(name)
        found.append({
            'name': name,
            'document': documents[name],
            'script': entry['script'],
            'requests': run_machine(entry),
        })
    inexact = inexact_operations(found)
    if inexact:
        named = ', '.join(f'{machine} carries {operation!r} in {where}'
                          for machine, where, operation in inexact)
        raise SystemExit(
            f'the corpus claims EXACT agreement and {named}, which IEEE '
            f'does not require to be correctly rounded, so two runtimes '
            f'need not agree in the last bit; state that machine with a '
            f'tolerance of its own, or keep it out of the corpus')
    banked = non_finite_records(found)
    if banked:
        named = ', '.join(f'{machine} records a non-finite value at '
                          f'{where} of step {step}'
                          for machine, step, where in banked)
        raise SystemExit(
            f'a clocked machine can stand at no infinity and no NaN, and '
            f'{named}: a commit computing one refuses its request and '
            f'banks nothing, and a fixture carrying one is not even JSON '
            f'a second runtime can parse')
    missing = uncovered_features(found)
    if missing:
        raise SystemExit(
            f'the corpus exercises neither {", nor ".join(missing)}, so it '
            f'would pin a clocked executor narrower than the one this '
            f'framework can run; add a machine to CORPUS that does')
    return {
        'generated_by': 'tools/generate_clocked_corpus.py',
        'corpus': 'tests/clocked_project/',
        'tolerance': {'float': 0.0},
        'machines': found,
    }


def main():
    fixture = build()
    path = os.path.abspath(FIXTURE)
    with open(path, 'w') as handle:
        json.dump(fixture, handle, indent=2)
        handle.write('\n')
    steps = sum(len(entry['requests']) for entry in fixture['machines'])
    names = sorted({entry['name'] for entry in fixture['machines']})
    print(f'{path}: {len(fixture["machines"])} scenarios over '
          f'{len(names)} machines ({", ".join(names)}), {steps} steps, '
          f'{os.path.getsize(path)} bytes')


if __name__ == '__main__':
    main()
