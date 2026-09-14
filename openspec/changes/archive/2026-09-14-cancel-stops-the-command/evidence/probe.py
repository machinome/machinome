from solid_node.node import AssemblyNode
from solid_node.motion.ports import Time
from solid_node.motion.joints import Prismatic
from solid_node.simulation import Driver, Sim


class Carriage(AssemblyNode):
    travel = Prismatic(axis=(1, 0, 0), range=(0, 12), unit="mm")


class Feed(AssemblyNode):
    time = Time.running()
    feed = Driver(default=0, unit="mm")
    carriage = Carriage()
    feed.drives(carriage.travel)


sim = Sim(Feed(), dt=0.02)
command = sim.move("feed", by=5, duration=0.2)
command.cancel()
sim.run(0.02)
print(command.status, command.admitted, sim.state, len(sim.commands))
sim.move("feed", by=1, duration=0.02)
