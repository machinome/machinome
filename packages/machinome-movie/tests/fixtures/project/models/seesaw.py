"""A seesaw: the fixture machine of the Videomaker test suite."""

from machinome.node import AssemblyNode, CadQueryNode


class Block(CadQueryNode):
    """A box, which is all the geometry a fixture needs."""

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
