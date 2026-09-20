from machinome.motion.joints import Prismatic
from machinome.node import AssemblyNode
from machinome.parameters import Length
from machinome.simulation import Driver
from machinome_mechanics import piston_height


class Piston(AssemblyNode):
    rod_length = Length(60)
    rise = Prismatic(axis=(0, 0, 1), unit="mm")


def slider_crank(engine, piston):
    radius = engine.crank_radius
    length = piston.rod_length
    return lambda angle: piston_height(angle, radius, length)


class Engine(AssemblyNode):
    crank_radius = Length(15)
    crank = Driver(default=0, range=(0, 360), unit="deg")
    piston = Piston()
    crank.drives(piston.rise, law=slider_crank)
