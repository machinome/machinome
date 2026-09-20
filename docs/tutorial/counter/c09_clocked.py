"""Chapter 9: a machine that remembers."""
from machinome.math import clamp01, floor
from machinome.node import AssemblyNode
from machinome.parameters import Length
from machinome.simulation import Driver, Instruction, State

from .c03_dimensions import (DRUM_RADIUS, KNOB_RADIUS, PLATE_LENGTH,
                             POST_DEPTH, Base)
from .c04_relations import TENS_SEAT, UNITS_SEAT, Drum
from .c08_running import Crank


def phase(crank):
    """Where the crank stands within its current turn, 0 to 360."""
    return crank - 360 * floor(crank / 360)


def strokes(sources, targets):
    return lambda crank, units, tens: floor(crank / 360)


def advance(sources, targets):
    return lambda crank, units, tens: ((units + 1) % 10,
                                       (tens + (units == 9)) % 10)


def units_pose(sources, driven):
    return lambda crank, units: (
        36 * units + 36 * clamp01((phase(crank) - 300) / 60))


def tens_pose(sources, driven):
    return lambda crank, units, tens: (
        36 * tens + 36 * clamp01((phase(crank) - 300) / 60) * (units == 9))


class Counter(AssemblyNode):

    shaft = Length(8.0, min=1)
    clearance = Length(0.1, min=0)
    arm_length = Length(40.0, min=10)
    arm_height = Length(40.0, min=1)
    post_offset = Length(28.0, min=1)
    post_height = Length(36.0, min=1)

    bore = shaft + 2 * clearance

    crank = Driver(default=0.0, range=(0.0, 3600.0), unit='deg')
    units = State(default=0, range=(0, 9), dtype=int)
    tens = State(default=0, range=(0, 9), dtype=int)

    base = Base(bore=bore, post_offset=post_offset, post_height=post_height)
    handle = Crank(diameter=shaft, arm_length=arm_length,
                   arm_height=arm_height)
    units_drum = Drum(bore=bore)
    tens_drum = Drum(bore=bore)

    crank.drives(handle.turn)
    (crank & units).drives(units_drum.turn, law=units_pose)
    (crank & units & tens).drives(tens_drum.turn, law=tens_pose)
    (crank & units & tens).commits((units, tens), at=strokes, law=advance)

    instructions = {
        'Turn once': Instruction(by={'crank': 360.0}, duration=2.0),
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
