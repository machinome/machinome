import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import report
from solid_node.simulation import Sim
from simulation.running import OperatingCurta

sim = Sim(OperatingCurta(), dt=.1)
report('OperatingCurta', sim.program)
