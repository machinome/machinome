"""Charge every GraphValue.evaluate of a Curta tick to its caller chain."""
import sys
from collections import Counter
from time import perf_counter

from solid_node.scad_expression import GraphValue
from solid_node.simulation import Sim
from simulation.running import OperatingCurta

TALLY = Counter()
TIME = Counter()
_evaluate = GraphValue.evaluate
ARMED = [False]


def charged(self, inputs):
    if not ARMED[0]:
        return _evaluate(self, inputs)
    frame = sys._getframe(1)
    chain = []
    for _ in range(6):
        if frame is None:
            break
        name = frame.f_code.co_name
        file = frame.f_code.co_filename.rsplit('/', 1)[-1]
        chain.append(f'{file}:{name}')
        frame = frame.f_back
    key = ' <- '.join(chain)
    began = perf_counter()
    try:
        return _evaluate(self, inputs)
    finally:
        TALLY[key] += 1
        TIME[key] += perf_counter() - began


GraphValue.evaluate = charged

sim = Sim(OperatingCurta(), dt=.1)
sim.move('digit_1', to=0)
sim.move('digit_2', to=0)
sim.move('crank_rotation', by=360, duration=2)
ARMED[0] = True
began = perf_counter()
for _ in range(3):
    sim.run(.1)
total = perf_counter() - began
calls = sum(TALLY.values())
print(f'3 ticks {total:.3f} s, {calls} evaluations')
for key, count in TALLY.most_common(18):
    print(f'{count:8d} ({100*count/calls:5.1f}%)  {TIME[key]:7.3f} s '
          f'({100*TIME[key]/total:5.1f}%)  {key}')
