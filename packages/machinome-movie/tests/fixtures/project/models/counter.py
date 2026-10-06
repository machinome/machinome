"""A clocked counter: the fixture machine of the Videomaker suite's takes.

Copied from the machinome framework's tutorial, `docs/tutorial/counter/`
at framework commit 6a575f02dc63acefdc7b791b471e3c5291530f81: the model of
chapter 9 (`c09_clocked.py`, "a machine that remembers") with the pieces of
chapters 3, 4 and 8 it imports, gathered in one file, and `digits.svg`
beside it. The framework is licensed Apache-2.0; nothing here is changed
but the imports and the name of chapter 3's crank, `PlainCrank`.
"""
import cadquery as cq
from machinome.math import clamp01, floor
from machinome.motion.joints import Revolute
from machinome.node.assembly import AssemblyNode
from machinome.node.cadquery import CadQueryNode
from machinome.node.markings import Marking, Svg, Wrapped
from machinome.parameters import Length
from machinome.simulation import Driver, Instruction, State

PLATE_LENGTH = 100.0     # constants: where things sit, never what is built
PLATE_WIDTH = 60.0
PLATE_THICKNESS = 8.0
POST_WIDTH = 8.0
POST_DEPTH = 6.0
KNOB_RADIUS = 5.0
DRUM_RADIUS = 20.0       # fixed by the digit artwork of chapter 4
DRUM_HEIGHT = 10.0
UNITS_SEAT = 12.0        # where each drum sits on the arbor
TENS_SEAT = 24.0
TOOTH = 36.0             # the ratchet's pitch: ten teeth per turn


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


class PlainCrank(CadQueryNode):

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


class Crank(PlainCrank):
    """The crank of chapter 3, with a ratchet: it never turns back past
    the last tooth it passed."""

    turn = Revolute(axis=(0, 0, 1), unit='deg',
                    range=(lambda turn: TOOTH * floor(turn / TOOTH), None))


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
