"""The README's machine: the tutorial's revolution counter, every moving
part placed by a frame on a frame."""
import cadquery as cq

from machinome.motion.joints import Revolute
from machinome.node.assembly import AssemblyNode
from machinome.node.cadquery import CadQueryNode
from machinome.node.frames import Frame
from machinome.parameters import Length
from machinome.simulation import Driver

from .c03_dimensions import (KNOB_RADIUS, PLATE_LENGTH, PLATE_THICKNESS,
                             PLATE_WIDTH, POST_DEPTH, POST_WIDTH, DRUM_RADIUS)
from .c04_relations import DRUM_HEIGHT, TENS_SEAT, UNITS_SEAT


class Base(CadQueryNode):
    """A plate with a bore for the arbor, and a post to read the drums
    against."""

    color = '#5b6770'

    bore = Length(8.2, min=1)
    post_offset = Length(28.0, min=1)
    post_height = Length(36.0, min=1)

    axle = Frame()                  # the bore's line, up through the plate

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
    """The arbor, its arm and the knob, in one piece."""

    color = '#c8553d'

    diameter = Length(8.0, min=1)
    arm_length = Length(40.0, min=10)
    arm_height = Length(40.0, min=1)

    arbor = Frame()                 # the arbor's line, where it meets the plate

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


class Drum(CadQueryNode):
    """A number drum: a ring that runs on the arbor."""

    color = '#2b2d42'

    bore = Length(8.2, min=1)

    axle = Frame()                  # the bore's line, z up

    def render(self):
        return (cq.Workplane('XY')
                .circle(DRUM_RADIUS).circle(self.bore / 2)
                .extrude(DRUM_HEIGHT))


class Counter(AssemblyNode):
    """The drums follow the crank at a fixed ratio: a revolution counter."""

    shaft = Length(8.0, min=1)
    clearance = Length(0.1, min=0)
    arm_length = Length(40.0, min=10)
    arm_height = Length(40.0, min=1)
    post_offset = Length(28.0, min=1)
    post_height = Length(36.0, min=1)

    bore = shaft + 2 * clearance

    units_seat = Frame(at=(0, 0, UNITS_SEAT))
    tens_seat = Frame(at=(0, 0, TENS_SEAT))

    crank = Driver(default=0.0, range=(0.0, 3600.0), unit='deg')

    base = Base(bore=bore, post_offset=post_offset, post_height=post_height)
    handle = Crank(diameter=shaft, arm_length=arm_length,
                   arm_height=arm_height)
    units_drum = Drum(bore=bore)
    tens_drum = Drum(bore=bore)

    turn = handle.arbor.on(base.axle, Revolute())
    units = units_drum.axle.on(units_seat, Revolute())
    tens = tens_drum.axle.on(tens_seat, Revolute())

    crank.drives(turn)
    turn.drives(units, ratio=0.1)
    units.drives(tens, ratio=0.1)

    def check(self):
        if self.arm_length + KNOB_RADIUS > PLATE_LENGTH / 2:
            raise ValueError(
                f'{self.name}: an arm of {self.arm_length} mm hangs the knob '
                f'past the plate, which is {PLATE_LENGTH} mm long')
