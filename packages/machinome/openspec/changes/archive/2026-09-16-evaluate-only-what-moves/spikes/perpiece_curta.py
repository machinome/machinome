"""Would a PER-PIECE classification (cut-at-the-kink design.md 8) solve
the Curta's searched crossings?

At every `_Walk._searched` call, substitute into the skeleton and the
level every kink node whose own level keeps ONE SIGN over the piece
(so `max(0, x)` with x <= 0 becomes the constant 0, and `sin` of it a
constant), then re-classify with cycle 1's prototype classifier.
"""
import sys
from collections import Counter

import os
WT = os.environ['WT']
sys.path.insert(0, os.path.join(
    WT, 'openspec/changes/archive/2026-09-16-cut-at-the-kink/spikes'))
from classify import shape_of                      # noqa: E402

from solid_node.expression_graph import ExpressionNode, postorder  # noqa: E402
from solid_node.scad_expression import as_node, GraphValue         # noqa: E402
import solid_node.simulation.program as P                          # noqa: E402
from solid_node.simulation import Sim                              # noqa: E402
from simulation.running import OperatingCurta                      # noqa: E402

KINKS = ('min', 'max', 'abs')
SAMPLES = 9
SK = Counter()
LV = Counter()
ARMED = [False]


def substituted(root, sample_values):
    """`root` with every single-signed kink replaced by the operand it
    selects over the whole piece."""
    replaced = {}
    for node in postorder([root]):
        children = tuple(replaced.get(c, c) for c in node.children)
        fresh = (node if children == node.children
                 else ExpressionNode(node.kind, node.op, children, node.text))
        if node.kind == 'call' and node.op in KINKS:
            picks = set()
            for values in sample_values:
                try:
                    if node.op == 'abs':
                        level = GraphValue(node.children[0]).evaluate(values)
                        picks.add(level >= 0)
                    else:
                        a = GraphValue(node.children[0]).evaluate(values)
                        b = GraphValue(node.children[1]).evaluate(values)
                        picks.add((a <= b) if node.op == 'min' else (a >= b))
                except Exception:
                    picks.add(None)
            if len(picks) == 1:
                pick = picks.pop()
                if pick is True:
                    fresh = (children[0] if node.op != 'abs' else children[0])
                elif pick is False:
                    fresh = (children[1] if node.op != 'abs'
                             else ExpressionNode('unary', '-', (children[0],)))
        replaced[node] = fresh
    return replaced[root]


_searched = P._Walk._searched


def watched(self, jump, t, right, own_left, branches, own_at):
    if ARMED[0]:
        points = [t + (right - t) * k / (SAMPLES - 1) for k in range(SAMPLES)]
        sk_values = []
        for s in points:
            values = P._along(self.start, self.delta, s)
            values.update(branches)
            sk_values.append(values)
        lv_values = []
        for s in points:
            values = P._along(self.start, self.delta, s)
            values[self.own] = own_left
            values.update(branches)
            lv_values.append(values)
        root = as_node(self.plan.skeleton)
        SK[(str(shape_of(root)),
            str(shape_of(substituted(root, sk_values))))] += 1
        root = as_node(jump.argument)
        LV[(str(shape_of(root)),
            str(shape_of(substituted(root, lv_values))))] += 1
    return _searched(self, jump, t, right, own_left, branches, own_at)


P._Walk._searched = watched

sim = Sim(OperatingCurta(), dt=.1)
sim.move('digit_1', to=0)
sim.move('digit_2', to=0)
sim.move('crank_rotation', by=360, duration=2)
ARMED[0] = True
for _ in range(3):
    sim.run(.1)
ARMED[0] = False

for name, tally in (('skeleton', SK), ('level', LV)):
    print(f'-- {name}: {sum(tally.values())} searched calls')
    for (before, after), count in tally.most_common():
        print(f'     whole-tick {before:12s} -> per-piece {after:12s}  x {count}')
