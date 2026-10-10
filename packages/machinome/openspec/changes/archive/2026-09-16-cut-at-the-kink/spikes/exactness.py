"""How far a SEARCHED crossing on a kinked skeleton sits from the exact
solution, on the `CurtaInterface` fixture."""
import os, sys
from fractions import Fraction
ROOT = os.environ['WT']; sys.path.insert(0, ROOT)
from solid_node.simulation import Sim
from tests.clearing_project.machine import (CurtaInterface, ORIGIN, SWEEP,
                                            RESULT_START, station)

DT = 1.0 / 60.0
sim = Sim(CurtaInterface(), DT, record=4000)
sim.move('clearing', by=1.0, duration=1.0)
sim.run(1.0)

start = RESULT_START + station(0, False)
# reach == 0  <=>  ORIGIN + SWEEP * (control - 0.1) / 0.8 == start
control_star = 0.1 + 0.8 * (start - ORIGIN) / SWEEP
tick = int(control_star / DT) + 1          # ticks are 1-based in the record
left = (tick - 1) * DT
exact = (control_star - left) / DT
print('exact control at reach == 0 :', repr(control_star))
print('tick', tick, 'exact t', repr(exact))
for entry in sim.crossings:
    if entry.coordinate != 'result0.turn' or entry.tick != tick:
        continue
    print(f'  recorded {entry.primitive:>6s} level {entry.level!r:>8s} '
          f't {entry.t!r}  error {entry.t - exact!r}')
