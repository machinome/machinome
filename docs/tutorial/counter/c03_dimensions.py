"""Chapter 3: dimensions in one place."""
import cadquery as cq

from machinome.node import AssemblyNode, CadQueryNode
from machinome.motion.joints import Revolute
from machinome.parameters import Length
from machinome.simulation import Driver

PLATE_LENGTH = 100.0     # constants: where things sit, never what is built
PLATE_WIDTH = 60.0
PLATE_THICKNESS = 8.0
POST_WIDTH = 8.0
POST_DEPTH = 6.0
KNOB_RADIUS = 5.0
DRUM_RADIUS = 20.0       # fixed by the digit artwork of chapter 4


class Base(CadQueryNode):

    color = '#5b6770'

    bore = Length(8.2, min=1)
    post_offset = Length(28.0, min=1)
    post_height = Length(36.0, min=1)

    def render(self):
        plate = (cq.Workplane('XY')
                 .box(PLATE_LENGTH, PLATE_WIDTH, PLATE_THICKNESS,
                      centered=(True, True, False))
                 .translate((0, 0, -PLATE_THICKNESS))
                 .faces('>Z').workplane().hole(self.bore))
        post = (cq.Workplane('XY')
                .box(POST_WIDTH, POST_DEPTH, self.post_height,
                     centered=(True, True, False))
                .translate((0, -self.post_offset, 0)))
        return plate.union(post)


class Crank(CadQueryNode):

    color = '#c8553d'

    diameter = Length(8.0, min=1)
    arm_length = Length(40.0, min=10)
    arm_height = Length(40.0, min=1)

    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        top = self.arm_height + 6
        shaft = (cq.Workplane('XY').workplane(offset=-PLATE_THICKNESS)
                 .circle(self.diameter / 2).extrude(top + PLATE_THICKNESS))
        arm = (cq.Workplane('XY').workplane(offset=self.arm_height)
               .center((self.arm_length - 4) / 2, 0)
               .rect(self.arm_length + 4, 8).extrude(6))
        knob = (cq.Workplane('XY').workplane(offset=top)
                .center(self.arm_length - 4, 0)
                .circle(KNOB_RADIUS).extrude(20))
        return shaft.union(arm).union(knob)


class Counter(AssemblyNode):

    shaft = Length(8.0, min=1)
    clearance = Length(0.1, min=0)
    arm_length = Length(40.0, min=10)
    arm_height = Length(40.0, min=1)
    post_offset = Length(28.0, min=1)
    post_height = Length(36.0, min=1)

    bore = shaft + 2 * clearance

    crank = Driver(default=0.0, range=(0.0, 3600.0), unit='deg')

    base = Base(bore=bore, post_offset=post_offset, post_height=post_height)
    handle = Crank(diameter=shaft, arm_length=arm_length,
                   arm_height=arm_height)

    crank.drives(handle.turn)

    def check(self):
        if self.arm_length + KNOB_RADIUS > PLATE_LENGTH / 2:
            raise ValueError(
                f'{self.name}: an arm of {self.arm_length} mm hangs the knob '
                f'past the plate, which is {PLATE_LENGTH} mm long')
