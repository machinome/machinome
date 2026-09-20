"""Your first machine: one part, one input, one slider."""
import cadquery as cq

from machinome.node import AssemblyNode, CadQueryNode
from machinome.simulation import Driver


class Block(CadQueryNode):

    def render(self):
        return (cq.Workplane('XY')
                .box(50, 50, 50, centered=(True, True, False))
                .faces('>Z').workplane().hole(20))


class Lifter(AssemblyNode):

    lift = Driver(default=0.0, range=(0.0, 80.0), unit='mm')

    block = Block()

    def simulate(self):
        self.block.translate([0, 0, self.lift])
