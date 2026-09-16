import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import report
from solid_node.simulation import Sim
from tests.running_project.machine import Clearing, Train
from tests.clearing_project.machine import CurtaInterface
from tests.carriage_project.machine import ShiftedCarry, RangedBlock, CurtaCarriage

for name, cls in (('Train', Train), ('Clearing', Clearing),
                  ('CurtaInterface', CurtaInterface),
                  ('ShiftedCarry', ShiftedCarry),
                  ('RangedBlock', RangedBlock),
                  ('CurtaCarriage', CurtaCarriage)):
    sim = Sim(cls(), 0.1)
    report(name, sim.program)
