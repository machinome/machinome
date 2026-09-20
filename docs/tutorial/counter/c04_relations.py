"""Chapter 4: one coordinate drives another."""
import cadquery as cq

from machinome.math import clamp01, floor
from machinome.node import AssemblyNode, CadQueryNode
from machinome.node.markings import Marking, Svg, Wrapped
from machinome.motion.joints import Revolute
from machinome.parameters import Length
from machinome.simulation import Driver

from .c03_dimensions import (DRUM_RADIUS, KNOB_RADIUS, PLATE_LENGTH,
                             Base, Crank)

DRUM_HEIGHT = 10.0
UNITS_SEAT = 12.0        # where each drum sits on the arbor
TENS_SEAT = 24.0


class Drum(CadQueryNode):
    """A number drum: a ring that runs on the arbor, carrying ten digits."""

    color = '#2b2d42'

    bore = Length(8.2, min=1)

    turn = Revolute(axis=(0, 0, 1), unit='deg')

    digits = Marking(
        Svg('digits.svg'),
        Wrapped(axis=(0, 0, 1), radius=DRUM_RADIUS, at=(0, 0, 0), start=-72),
        color='#ffffff',
    )

    def render(self):
        return (cq.Workplane('XY')
                .circle(DRUM_RADIUS).circle(self.bore / 2)
                .extrude(DRUM_HEIGHT))


class RatioCounter(AssemblyNode):
    """The drums follow the crank at a fixed ratio: a revolution counter."""

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
    units_drum = Drum(bore=bore)
    tens_drum = Drum(bore=bore)

    crank.drives(handle.turn)
    handle.turn.drives(units_drum.turn, ratio=0.1)
    units_drum.turn.drives(tens_drum.turn, ratio=0.1)

    def render(self):
        self.units_drum.translate([0, 0, UNITS_SEAT])
        self.tens_drum.translate([0, 0, TENS_SEAT])

    def check(self):
        if self.arm_length + KNOB_RADIUS > PLATE_LENGTH / 2:
            raise ValueError(
                f'{self.name}: an arm of {self.arm_length} mm hangs the knob '
                f'past the plate, which is {PLATE_LENGTH} mm long')


def window(width):
    """The law of a counter drum: it advances one digit during the last
    `width` degrees of each turn of what drives it, and holds still the
    rest of the time."""
    def law(driver, driven):
        return lambda angle: (
            36 * floor(angle / 360)
            + 36 * clamp01((angle - 360 * floor(angle / 360)
                            - (360 - width)) / width))
    return law


class Counter(AssemblyNode):
    """The drums advance one digit at a time: a tally counter."""

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
    units_drum = Drum(bore=bore)
    tens_drum = Drum(bore=bore)

    crank.drives(handle.turn)
    handle.turn.drives(units_drum.turn, law=window(60))
    units_drum.turn.drives(tens_drum.turn, law=window(36))

    def render(self):
        self.units_drum.translate([0, 0, UNITS_SEAT])
        self.tens_drum.translate([0, 0, TENS_SEAT])

    def check(self):
        if self.arm_length + KNOB_RADIUS > PLATE_LENGTH / 2:
            raise ValueError(
                f'{self.name}: an arm of {self.arm_length} mm hangs the knob '
                f'past the plate, which is {PLATE_LENGTH} mm long')
