"""Spike 4: what an ARBITRARY union order does, measured.

`_ordered` is monkeypatched to return the candidate edges in DECLARATION
order instead of Kahn order -- no worktree file is touched. Nothing else
needs patching: the reduced fixture's relations each carry a self-read,
so ADR-121's rest rule already leaves them alone at the rest render and
`_ordered` is the only thing in the way.

The ground truth is `reduced.FixedZero`, whose laws are the SAME laws with
`shift` frozen at the literal 0, and which the framework orders correctly
today.
"""

import json

from solid_node.simulation import program as P
from solid_node.simulation import Sim
from reduced import FixedZero, ShiftedCarry


def run(root, label, order=None):
    original = P._ordered
    if order is not None:
        P._ordered = lambda kept, nodes: [kept[i] for i in order]
    try:
        sim = Sim(root, dt=.02)
        print(f'{label}: edges ' + ' | '.join(
            edge.description for edge in sim._run.program.edges))
        command = sim.move('crank', by=2, duration=1.0)
        sim.run(1.2)
        print(f'  {command.status} {json.dumps(sim.state, sort_keys=True)}')
        return sim.state
    finally:
        P._ordered = original


def main():
    truth = run(FixedZero(), 'ground truth (shift frozen at 0, Kahn)')
    declaration = run(ShiftedCarry(), 'union, DECLARATION order', order=(0, 1, 2))
    reversed_order = run(ShiftedCarry(), 'union, REVERSED order', order=(2, 1, 0))

    print()
    for label, state in (('declaration', declaration), ('reversed', reversed_order)):
        for key in ('lower.turn', 'higher.turn', 'carry.travel'):
            a, b = truth[key], state[key]
            print(f'{label:12s} {key:14s} truth={a!r} got={b!r} '
                  f'{"AGREE" if a == b else "DIFFER by " + repr(b - a)}')


if __name__ == '__main__':
    main()
