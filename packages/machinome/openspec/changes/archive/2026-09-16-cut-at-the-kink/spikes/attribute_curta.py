import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attribute
from solid_node.simulation import Sim
from simulation.running import OperatingCurta

sim = Sim(OperatingCurta(), dt=.1)
sim.move('digit_1', to=0)
sim.move('digit_2', to=0)
sim.move('crank_rotation', by=360, duration=2)
attribute.TOTAL[0] = 0
attribute.TALLY.clear(); attribute.CALLS.clear()
for _ in range(3):
    sim.run(.1)
attribute.dump(3)
