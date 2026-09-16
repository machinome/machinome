"""How much of a searched skeleton/level graph actually MOVES along the path.

For every `_Walk._searched` call, report the graph size and the size of
the sub-graph reachable from a name whose delta is non-zero (plus, for a
level, the driven coordinate's own name).
"""
from collections import Counter

from solid_node.expression_graph import postorder
from solid_node.scad_expression import as_node
import solid_node.simulation.program as P
from solid_node.simulation import Sim
from simulation.running import OperatingCurta

SK = Counter()   # (total, moving) -> calls
LV = Counter()
ARMED = [False]


def cone(root, moving_names):
    """(total nodes, nodes whose value depends on a moving name)."""
    order = list(postorder([root]))
    moves = {}
    for node in order:
        if node.kind == 'name':
            moves[node] = node.text in moving_names
        elif not node.children:
            moves[node] = False
        else:
            moves[node] = any(moves[c] for c in node.children)
    return len(order), sum(1 for node in order if moves[node])


_searched = P._Walk._searched


def watched(self, jump, t, right, own_left, branches, own_at):
    if ARMED[0]:
        moving = {name for name, value in self.delta.items() if value}
        moving.discard(self.own)
        SK[cone(as_node(self.plan.skeleton), moving)] += 1
        LV[cone(as_node(jump.argument), moving | {self.own})] += 1
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


def dump(name, tally):
    calls = sum(tally.values())
    total = sum(t * n for (t, _m), n in tally.items())
    moving = sum(m * n for (_t, m), n in tally.items())
    print(f'-- {name}: {calls} searched calls, '
          f'{total / calls:.0f} nodes/graph, {moving / calls:.1f} moving '
          f'({100 * moving / total:.1f}%)')
    for (t, m), n in sorted(tally.items()):
        print(f'     {t:5d} nodes, {m:4d} moving   x {n}')


dump('skeleton', SK)
dump('level', LV)
