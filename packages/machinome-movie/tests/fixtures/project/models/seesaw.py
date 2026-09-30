"""A seesaw: the fixture machine of the Videomaker test suite."""

from machinome.node import AssemblyNode, CadQueryNode
from machinome.motion.ports import Time

class Block(CadQueryNode):
    """A box, which is all the geometry a fixture needs."""
    color = '#8f9aa3'  # a colour of its own, so a highlight can tint and dim it
    def render(self):
        import cadquery as cq

        return cq.Workplane().box(40, 10, 10)


class Beam(AssemblyNode):
    plank = Block(name='Plank')
    weight = Block(name='Weight')
    pivot = Block()


class Seesaw(AssemblyNode):
    base = Block(name='Base')
    stand = Block(name='Stand')
    beam = Beam(name='Beam')
    time = Time(loop=20)

    def render(self):
        # At rest: the base on the ground, the stand upright on it, and the
        # beam's pivot on the stand, 55 above the ground, where it turns.
        self.base.translate([0, 0, 5])
        self.stand.rotate(90, [0, 1, 0]).translate([0, 0, 30])
        self.beam.pivot.rotate(90, [0, 0, 1])
        self.beam.plank.translate([0, 0, 10])
        self.beam.weight.translate([-15, 0, 20])
        self.beam.translate([0, 0, 55])

    def simulate(self):
        # Through the 20 s loop the beam tips from -20 to 20 degrees and
        # back: level and rising at 5 s, at the top at 10 s, level and
        # falling at 15 s (the marks of the fixture take).
        self.beam.rotate(20 - 4 * abs(self.time - 10), [0, 1, 0])
