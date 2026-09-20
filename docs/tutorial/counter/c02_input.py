"""Chapter 2: an input moves a body."""
import cadquery as cq

from machinome.node import AssemblyNode, CadQueryNode
from machinome.motion.joints import Revolute
from machinome.simulation import Driver

from .c01_part import Base


class Crank(CadQueryNode):
    """The arbor, its arm and the knob, in one piece."""

    color = '#c8553d'

    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        shaft = (cq.Workplane('XY').workplane(offset=-8)
                 .circle(4).extrude(48))
        arm = (cq.Workplane('XY').workplane(offset=40)
               .center(18, 0).rect(44, 8).extrude(6))
        knob = (cq.Workplane('XY').workplane(offset=46)
                .center(36, 0).circle(5).extrude(20))
        return shaft.union(arm).union(knob)


class Counter(AssemblyNode):

    crank = Driver(default=0.0, range=(0.0, 3600.0), unit='deg')

    base = Base()
    handle = Crank()

    crank.drives(handle.turn)
