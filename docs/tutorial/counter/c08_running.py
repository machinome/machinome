"""Chapter 8: a machine with history."""
from machinome.math import floor
from machinome.motion.joints import Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.parameters import Length
from machinome.simulation import Button, Driver, Instruction, Turn

from .c03_dimensions import (DRUM_RADIUS, KNOB_RADIUS, PLATE_LENGTH,
                             POST_DEPTH, Base, Crank as PlainCrank)
from .c04_relations import TENS_SEAT, UNITS_SEAT, Drum, window

TOOTH = 36.0             # the ratchet's pitch: ten teeth per turn


class Crank(PlainCrank):
    """The crank of chapter 3, with a ratchet: it never turns back past
    the last tooth it passed."""

    turn = Revolute(axis=(0, 0, 1), unit='deg',
                    range=(lambda turn: TOOTH * floor(turn / TOOTH), None))


class Counter(AssemblyNode):

    time = Time.running()

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

    instructions = {
        'Turn once': Instruction(by={'crank': 360.0}, duration=2.0),
        'Back a bit': Instruction(by={'crank': -30.0}, duration=0.5),
    }
    controls = {
        'turn the crank': Turn(handle, crank),
        'one turn': Button(handle, 'Turn once'),
    }

    def render(self):
        self.units_drum.translate([0, 0, UNITS_SEAT])
        self.tens_drum.translate([0, 0, TENS_SEAT])

    def check(self):
        if self.arm_length + KNOB_RADIUS > PLATE_LENGTH / 2:
            raise ValueError(
                f'{self.name}: an arm of {self.arm_length} mm hangs the knob '
                f'past the plate, which is {PLATE_LENGTH} mm long')
        if self.post_offset - POST_DEPTH / 2 <= DRUM_RADIUS:
            raise ValueError(
                f'{self.name}: a post {self.post_offset} mm from the axis '
                f'cuts into drums of radius {DRUM_RADIUS} mm')
