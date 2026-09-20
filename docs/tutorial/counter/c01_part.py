"""Chapter 1: a part."""
import cadquery as cq

from machinome.node import CadQueryNode


class Base(CadQueryNode):
    """A plate with a bore for the arbor, and a post to read the drums
    against."""

    color = '#5b6770'

    def render(self):
        plate = (cq.Workplane('XY')
                 .box(100, 60, 8, centered=(True, True, False))
                 .translate((0, 0, -8))
                 .faces('>Z').workplane().hole(8.2))
        post = (cq.Workplane('XY')
                .box(8, 6, 36, centered=(True, True, False))
                .translate((0, -28, 0)))
        return plate.union(post)
