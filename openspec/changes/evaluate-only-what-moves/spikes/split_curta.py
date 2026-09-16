"""Split a Curta tick into: expression evaluation, port resolution, the rest.

Low-overhead wall-clock wrappers (no cProfile), plus graph sizes.
"""
import sys
from collections import Counter
from time import perf_counter

from solid_node.scad_expression import GraphValue
from solid_node.expression_graph import postorder
import solid_node.motion.ports as ports
from solid_node.simulation import Sim
from simulation.running import OperatingCurta

EVAL_TIME = [0.0]
EVAL_CALLS = [0]
EVAL_NODES = [0]
SIZES = Counter()
DEPTH = [0]

_evaluate = GraphValue.evaluate
_size_cache = {}


def timed_evaluate(self, inputs):
    node = self._expression_node
    size = _size_cache.get(id(node))
    if size is None:
        size = sum(1 for _ in postorder([node]))
        _size_cache[id(node)] = size
    began = perf_counter()
    try:
        return _evaluate(self, inputs)
    finally:
        EVAL_TIME[0] += perf_counter() - began
        EVAL_CALLS[0] += 1
        EVAL_NODES[0] += size
        SIZES[size] += 1


PORT_TIME = [0.0]
PORT_CALLS = [0]
_declared_ports = ports.declared_ports


def timed_ports(*a, **k):
    if DEPTH[0]:
        return _declared_ports(*a, **k)
    DEPTH[0] = 1
    began = perf_counter()
    try:
        return _declared_ports(*a, **k)
    finally:
        PORT_TIME[0] += perf_counter() - began
        PORT_CALLS[0] += 1
        DEPTH[0] = 0


GraphValue.evaluate = timed_evaluate
ports.declared_ports = timed_ports

began = perf_counter()
sim = Sim(OperatingCurta(), dt=.1)
built = perf_counter() - began
print(f'constructed {built:.3f} s   '
      f'evaluate {EVAL_TIME[0]:.3f} s in {EVAL_CALLS[0]} calls   '
      f'declared_ports {PORT_TIME[0]:.3f} s in {PORT_CALLS[0]} top-level calls')

sim.move('digit_1', to=0)
sim.move('digit_2', to=0)
sim.move('crank_rotation', by=360, duration=2)

EVAL_TIME[0] = 0.0; EVAL_CALLS[0] = 0; EVAL_NODES[0] = 0; SIZES.clear()
PORT_TIME[0] = 0.0; PORT_CALLS[0] = 0

TICKS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
began = perf_counter()
for _ in range(TICKS):
    t0 = perf_counter()
    sim.run(.1)
    print(f'  tick {perf_counter() - t0:.3f} s', flush=True)
total = perf_counter() - began

print(f'{TICKS} ticks {total:.3f} s ({total / TICKS:.3f} s/tick)')
print(f'  GraphValue.evaluate  {EVAL_TIME[0]:.3f} s '
      f'({100 * EVAL_TIME[0] / total:.1f}%) in {EVAL_CALLS[0]} calls '
      f'({EVAL_CALLS[0] / TICKS:.0f}/tick), {EVAL_NODES[0]} node visits '
      f'({EVAL_NODES[0] / max(EVAL_CALLS[0], 1):.0f} nodes/call), '
      f'{1e6 * EVAL_TIME[0] / max(EVAL_CALLS[0], 1):.1f} us/call, '
      f'{1e9 * EVAL_TIME[0] / max(EVAL_NODES[0], 1):.0f} ns/node')
print(f'  declared_ports       {PORT_TIME[0]:.3f} s '
      f'({100 * PORT_TIME[0] / total:.1f}%) in {PORT_CALLS[0]} top-level calls')
print(f'  everything else      {total - EVAL_TIME[0] - PORT_TIME[0]:.3f} s '
      f'({100 * (total - EVAL_TIME[0] - PORT_TIME[0]) / total:.1f}%)')
print('  graph sizes (nodes: evaluations), largest 12:')
for size, count in sorted(SIZES.items())[-12:]:
    print(f'     {size:6d} nodes  x {count:6d}  = {size * count:9d} visits')
