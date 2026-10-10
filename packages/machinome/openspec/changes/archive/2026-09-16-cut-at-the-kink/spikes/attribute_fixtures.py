import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attribute
from solid_node.simulation import Sim
from tests.clearing_project.machine import CurtaInterface
from tests.running_project.machine import Clearing

sim = Sim(CurtaInterface(), 1.0 / 60.0)
sim.move('clearing', by=1.0, duration=1.0)
attribute.TOTAL[0] = 0; attribute.TALLY.clear(); attribute.CALLS.clear()
sim.run(1.0)
print('== CurtaInterface, 60 ticks')
attribute.dump(60)

sim = Sim(Clearing(), 0.1)
sim.move('ring', by=600.0, duration=1.0)
attribute.TOTAL[0] = 0; attribute.TALLY.clear(); attribute.CALLS.clear()
sim.run(1.0)
print('== Clearing, 10 ticks')
attribute.dump(10)
