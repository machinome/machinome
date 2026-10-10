"""Does the corpus's `ShiftedCarry` scenario DISCRIMINATE the block order?

Design evidence for `pin-the-block-order`. Nothing in `solid_node/` is
edited: `_Block._order` is monkeypatched at RUNTIME to return the members
in LISTING order -- what a consumer that executes the published order
does -- and the run is replayed against the producer's own values under
the corpus's own tolerance.

Run from the framework worktree root:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
      ../../../.venv/bin/python <this file> [dt] [duration]
"""

import json
import os
import sys

ROOT = os.getcwd()
sys.path.insert(0, ROOT)

from solid_node.simulation import program as program_module      # noqa: E402
from solid_node.simulation.run import _TOLERANCE                 # noqa: E402

from tools.generate_running_corpus import (                      # noqa: E402
    _member_of, _selection, document_of, free_names, run_machine,
)

CORPUS = os.path.join(ROOT, 'tests', 'running-corpus.json')


##############################################
# The patch: the members in the order they are LISTED

_original_order = program_module._Block._order


def listing_order(self, forced, left, right):
    return tuple(range(len(self.members)))


class listing:
    """`with listing():` -- the block ordered as a version 6 consumer
    would execute the published edges."""

    def __enter__(self):
        program_module._Block._order = listing_order

    def __exit__(self, *exc):
        program_module._Block._order = _original_order


##############################################
# Comparison, under the corpus's own rule

def close(left, right):
    window = _TOLERANCE * max(1.0, abs(left), abs(right))
    return abs(left - right) <= window


def compare(expected, found):
    """Every disagreement between two tick logs, as text."""
    complaints = []
    for step, (want, got) in enumerate(zip(expected, found), 1):
        where = f'tick {want["tick"]}'
        for key, value in want['bank'].items():
            mine = got['bank'][key]
            if not close(value, mine):
                complaints.append(
                    f'{where} {key}: corpus {value!r} vs listing order '
                    f'{mine!r} (delta {abs(value - mine):.6g})')
        if len(want['crossings']) != len(got['crossings']):
            complaints.append(
                f'{where}: {len(want["crossings"])} crossing(s) in the '
                f'corpus, {len(got["crossings"])} under listing order')
        else:
            for a, b in zip(want['crossings'], got['crossings']):
                for field in ('relation', 'coordinate', 'primitive', 'level'):
                    if a[field] != b[field]:
                        complaints.append(
                            f'{where} crossing {field}: {a[field]!r} vs '
                            f'{b[field]!r}')
                if not close(a['t'], b['t']):
                    complaints.append(
                        f'{where} crossing t: {a["t"]!r} vs {b["t"]!r}')
        if len(want['stops']) != len(got['stops']):
            complaints.append(
                f'{where}: {len(want["stops"])} stop(s) in the corpus, '
                f'{len(got["stops"])} under listing order')
        for a, b in zip(want['commands'], got['commands']):
            if a['status'] != b['status']:
                complaints.append(f'{where} {a["handle"]}: {a["status"]} vs '
                                  f'{b["status"]}')
            elif not close(a['admitted'], b['admitted']):
                complaints.append(
                    f'{where} {a["handle"]} admitted: {a["admitted"]!r} vs '
                    f'{b["admitted"]!r}')
    return complaints


##############################################
# In-block gate crossings, re-derived as a consumer must

def _levels(edge, bindings):
    """`[(primitive, {free names of the level, placeholders resolved})]`
    for every jump of an edge's plans."""
    found = []
    for plan in edge.get('plans') or ():
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
            found.append((jump['primitive'], names))
    return found


def gate_crossings(document, ticks):
    """Every IN-BLOCK GATE CROSSING located strictly inside a tick.

    A GATE of a block member is a jump whose level reads a coordinate
    ANOTHER member of the block determines -- the member's OWN driven end
    excluded, because ADR-121's self-read imposes no order. A crossing
    counts when a gate of that member carries its primitive and an
    in-block coordinate that gate reads MOVED across the tick, and no
    SELECTOR of that member carrying the same primitive reads anything
    that moved -- so the crossing cannot be one of the member's own
    selectors sharing an operator.
    """
    program = document['program']
    bindings = {item['name']: item['expression']
                for item in document.get('bindings', ())}
    gives, _ = _selection(program, bindings)
    edges = [edge for edge in program.get('edges', ())
             if edge.get('kind') != 'check']
    found, previous = [], None
    for tick in ticks:
        if previous is None:
            previous = tick['bank']
            continue
        moved = {name for name, value in tick['bank'].items()
                 if previous.get(name) != value}
        for crossing in tick['crossings']:
            index = _member_of(program, crossing['coordinate'])
            if index is None or index not in range(len(edges)):
                continue
            own = set(edges[index].get('gives', ()))
            if not (gives & own):
                continue
            gates, selectors = [], []
            for primitive, names in _levels(edges[index], bindings):
                if primitive != crossing['primitive']:
                    continue
                reaches = (names & gives) - own
                if reaches:
                    gates.append(reaches)
                elif not names & gives:
                    selectors.append(names)
            if not any(reaches & moved for reaches in gates):
                continue
            if any(names & moved or not names <= set(tick['bank'])
                   for names in selectors):
                continue
            found.append((tick['tick'], crossing))
        previous = tick['bank']
    return found


##############################################

def report(title, entry, document, expected=None):
    print(f'\n### {title}')
    print(f'    script: {json.dumps(entry["script"])}')
    print(f'    dt {entry["dt"]}, {entry["steps"]} steps')
    produced = run_machine(entry) if expected is None else expected
    with listing():
        replayed = run_machine(entry)
    complaints = compare(produced, replayed)
    if complaints:
        print(f'    LISTING ORDER DIVERGES, {len(complaints)} disagreement(s):')
        for line in complaints[:12]:
            print(f'      {line}')
        if len(complaints) > 12:
            print(f'      ... and {len(complaints) - 12} more')
    else:
        print('    LISTING ORDER PASSES: every tick within the corpus '
              'tolerance, every discrete field equal')
    gates = gate_crossings(document, produced)
    print(f'    in-block gate crossings strictly inside a tick '
          f'(unpatched): {len(gates)}')
    for tick, crossing in gates:
        print(f'      tick {tick}: {crossing["coordinate"]} '
              f'{crossing["primitive"]} on {crossing["level"]} '
              f'relation={crossing["relation"]} t={crossing["t"]!r}')
    final = produced[-1]['bank']
    mine = replayed[-1]['bank']
    print('    final bank:')
    for key in sorted(final):
        mark = '' if close(final[key], mine[key]) else '   <-- DIFFERS'
        print(f'      {key}: producer {final[key]!r} / listing '
              f'{mine[key]!r}{mark}')
    return produced


def main():
    with open(CORPUS) as handle:
        fixture = json.load(handle)
    committed = next(entry for entry in fixture['machines']
                     if entry['name'] == 'ShiftedCarry')
    document = document_of('ShiftedCarry')
    print(f'tolerance: {_TOLERANCE!r} relative, '
          f'window = tol * max(1, |a|, |b|)')

    report('1. The COMMITTED script (crank by 2.0 over 0.2 s)',
           {'name': 'ShiftedCarry', 'dt': committed['dt'],
            'steps': committed['steps'], 'script': committed['script']},
           document, expected=committed['ticks'])

    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
    dt = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
    candidate = {'name': 'ShiftedCarry', 'dt': dt, 'steps': 20, 'script': [
        {'tick': 1, 'move': {'input': 'crank', 'by': 2.0,
                             'duration': duration}, 'handle': 'h0'},
        {'tick': 8, 'move': {'input': 'shift', 'by': 1.0,
                             'duration': 0.2}, 'handle': 'h1'},
        {'tick': 14, 'move': {'input': 'crank', 'by': 2.0,
                              'duration': duration}, 'handle': 'h2'},
    ]}
    report(f'2. The CANDIDATE script (crank by 2.0 over {duration} s)',
           candidate, document)


if __name__ == '__main__':
    main()
