"""Where a tick's graph evaluations go, attributed to the SEARCH paths
and to the classification of the skeleton / level that sent them there."""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import shape_of
from solid_node.scad_expression import GraphValue, as_node
import solid_node.simulation.program as P
import solid_node.simulation.run as R

TALLY = Counter()
CALLS = Counter()
TOTAL = [0]

_evaluate = GraphValue.evaluate


def counting(self, values):
    TOTAL[0] += 1
    return _evaluate(self, values)


GraphValue.evaluate = counting

_walk_searched = P._Walk._searched
_plan_searched = P.JumpPlan._searched
_run_searched = R.Run._searched
_run_constraint = R.Run._searched_constraint


def attributed(label):
    def wrap(original, key):
        def wrapper(*args, **kwargs):
            before = TOTAL[0]
            try:
                return original(*args, **kwargs)
            finally:
                TALLY[key(*args)] += TOTAL[0] - before
                CALLS[key(*args)] += 1
        return wrapper
    return wrap


def walk_key(self, jump, *rest):
    return ('walk crossing',
            f'skeleton {shape_of(as_node(self.reading.plan.skeleton))}',
            f'level {shape_of(as_node(jump.argument))}')


def plan_key(self, jump, *rest):
    return ('jump crossing', 'skeleton n/a',
            f'level {shape_of(as_node(jump.argument))}')


def run_key(self, edge, key, *rest):
    return ('stop localization', 'edge ' + edge.kind, '')


def constraint_key(self, *rest):
    return ('constraint localization', '', '')


P._Walk._searched = attributed('')(_walk_searched, walk_key)
P.JumpPlan._searched = attributed('')(_plan_searched, plan_key)
R.Run._searched = attributed('')(_run_searched, run_key)
R.Run._searched_constraint = attributed('')(_run_constraint, constraint_key)


def dump(ticks):
    print(f'total evaluations {TOTAL[0]}  ({TOTAL[0] / ticks:.0f}/tick)')
    for key, count in TALLY.most_common():
        print(f'   {count:9d} ({100.0 * count / TOTAL[0]:5.1f}%) in '
              f'{CALLS[key]:6d} calls  {" | ".join(p for p in key if p)}')
    charged = sum(TALLY.values())
    print(f'   {TOTAL[0] - charged:9d} '
          f'({100.0 * (TOTAL[0] - charged) / TOTAL[0]:5.1f}%) elsewhere')
