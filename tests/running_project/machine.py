# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The tiny machines the running mode is answerable to.

`TrainBody` is the shape the Curta bench has: a crank driving a train of
arbors through affine ratios, a lever driving a slide through a project
law with a KINK (`clamp01`), the root's own joint wired down into a
child's plain port, and two instructions -- one absolute, one relative.
It declares NO time base, so the same class poses untimed exactly as it
always did; `Train` and `LoopingTrain` are the two bases over it.

The rest of the module is one machine per refusal or per propagation
shape the cycle states: backward propagation, a conflicting rigid group,
a jump, a law that is not an expression, an author binding of a run-owned
coordinate, a guarded rest default, an opaque source, a declared range,
an unbound coordinate, a partially bound `Free`, and the plain port an
author's `simulate()` keeps in step with a run-owned coordinate.

The JUMP machines below are cycle 2's: one per jump primitive, one per
nesting and multi-source shape, one per refusal, and the two awkward
level quantities -- a moving divisor and a product of two sources -- the
crossing search has to answer for. Each running root subclasses an
untimed `...Body` twin, so the same law is read both ways and the
untimed reading is pinned by a control.

The STOP machines at the end are cycle 3's: a ratchet whose lower bound
is an expression over its own coordinate, a rack that stops while an
unrelated motor runs on, a coordinate two inputs share, two groups that
stop at two fractions of one tick, an open gate whose crank is coupled
to the stopped wheel only through a closed one, a stop and a jump
crossing in one tick, and a bound reached through a law that is not
affine. Each has its own untimed twin for the same reason.
"""

import math

from solid_node.math import abs, clamp01, floor, sign, sin, wrap
from solid_node.motion.joints import Bound, Free, Prismatic, Revolute
from solid_node.motion.ports import RotationalPort, Time
from solid_node.node import AssemblyNode
from solid_node.parameters import Flag
from solid_node.simulation import Button, Driver, Instruction, Turn

from .parts import Arbor, Block, Dial, Pin, Slide, Wheel


def tooth_window(source, target):
    """The Curta bench's law, as project code: the pinion turns 72
    degrees while the tooth is engaged and holds outside the window."""
    return lambda angle: 4 + 72 * clamp01((angle - 113.5) / 11.25)


def periodic_window(source, target):
    """The same window made periodic: the pilot's illustration of the
    whole feature. The pinion turns 72 degrees once per crank
    revolution, and the `floor` that resets the phase is a jump the run
    locates inside the tick and subtracts."""
    return lambda angle: 4 + 72 * clamp01(
        (angle - 360 * floor(angle / 360) - 113.5) / 11.25)


def remainder_window(source, target):
    """The same window written with `%` instead of `floor`. `%` is
    `fmod`, so it takes the sign of the DIVIDEND and jumps at every
    NONZERO integer of `angle / 360` -- and over a forward crank the two
    spellings read the same at every tick."""
    return lambda angle: 4 + 72 * clamp01(((angle % 360) - 113.5) / 11.25)


def wrapped(source, target):
    """`wrap()` is a `ceil` and needs nothing of its own. Every branch
    of this law has slope 2, so its integrated reading is twice the
    UNWRAPPED travel."""
    return lambda angle: 2 * wrap(angle, 360.0)


def reversing(source, target):
    """A `sign` that does NOT jump: the factor it multiplies vanishes
    where it flips, so the law is continuous and must read exactly like
    its `abs` twin."""
    return lambda x: 5 * (x - 50.0) * sign(x - 50.0)


def kinked(source, target):
    """That twin, with no jump node in it at all."""
    return lambda x: 5 * abs(x - 50.0)


def throwing(source, target):
    """A `sign` that genuinely jumps -- by `10 * x` at the crossing --
    so the two segments contribute and the jump does not."""
    return lambda x: 5 * x * sign(x - 50.0)


def clutch(sources, target):
    """The spike's clutch, in the vocabulary this cycle admits: a GATE
    FACTOR in a multi-source law. Open, the wheel holds; closed, the
    pair drives; closing, the wheel takes the travel AFTER engagement
    and never the jump the gate would have applied."""
    return lambda shaft, sleeve: -2 * shaft * (sleeve > 0.5)


def alternating(source, target):
    """A jump node whose argument contains another: the engagement
    happens on alternate revolutions only. Mechanically it is the
    alternating engagement a Pascaline column chain has."""
    def law(angle):
        w = floor(angle / 360)
        even = 1 - (w - 2 * floor(w / 2))
        return 72 * clamp01((angle - 360 * w - 113.5) / 11.25) * even

    return law


# The Pascaline module's carry, with round constants of the fixture's
# own so the worked numbers are exact: a column hands on CARRY_THROW per
# revolution of the column below it, shaped by one `clamp01` segment per
# piece of the cam.
CARRY_OPEN = 100.0
CARRY_PERIOD = 360.0
CARRY_THROW = 60.0
CARRY_SEGMENTS = ((100.0, 10.0, 20.0), (110.0, 40.0, 40.0))
DIGIT_STEP = 36.0


def handed_on(wheel, lead):
    """What the column below hands on, in the module's own shape.

    A non-zero `lead` makes the law DISCONTINUOUS at the window
    boundary, by `first_rise * lead / first_width`: the phase resets
    while the lead-shifted first segment still reads part-way up its
    ramp. The integrated reading subtracts that jump, so the throw comes
    out below `CARRY_THROW` by exactly that much.
    """
    turns = floor((wheel - CARRY_OPEN) / CARRY_PERIOD)
    phase = wheel - CARRY_PERIOD * turns
    advance = CARRY_THROW * turns
    for start, width, rise in CARRY_SEGMENTS:
        advance = advance + rise * clamp01((phase - start + lead) / width)
    return advance


def carried_column(sources, driven):
    """The module's own multi-source column law: what this column is
    entered with, plus what the column below hands on."""
    return lambda entry, below: DIGIT_STEP * entry + handed_on(below, 0.0)


def carried_column_lead(sources, driven):
    """The same law with the module's own lead, which makes it jump."""
    return lambda entry, below: DIGIT_STEP * entry + handed_on(below, 0.5)


def counter(source, target):
    """A law that can move its coordinate ONLY by jumping: every jump is
    subtracted, so it can never move it at all."""
    return lambda turns: floor(turns)


def settled(sources, target):
    """The Curta carry bench's shape: a jump-only term beside a sloped
    one. It COMPILES -- `enabled` still carries slope -- and the running
    reading gives the turns nothing."""
    return lambda enabled, turns: 9 * enabled + floor(turns)


def moving_divisor(sources, target):
    """A `%` whose divisor moves: its level quantity `a / b` is not
    affine, and a tick whose path takes `b` through zero has no level at
    all."""
    return lambda a, b: 0.5 * a + (a % b)


def non_affine(sources, target):
    """A level quantity that is a PRODUCT of two sources, so the
    crossing is bracketed and bisected rather than solved."""
    return lambda a, b: a * floor(a * b / 100.0)


def crowded(source, target):
    """A sawtooth whose period is ONE unit: a coarse enough tick crosses
    more surfaces than the run admits."""
    return lambda a: clamp01(a - floor(a)) * 0.5


def swinging(source, target):
    """A SMOOTH non-affine law: its partial in the input changes with
    state, so a two-sided reading of it disagrees -- by far more than
    the program's own `agreement` and by far less than the window the
    control measurement states. The pointer leads or lags the part and
    nothing is ever wrong, which is why `1e-3` admits it."""
    return lambda angle: 90 * sin(angle)


def stdlib_law(source, target):
    """A law over Python's own `math`: it cannot be applied to a
    symbol."""
    return lambda angle: 10 * math.sin(angle)


class TrainBody(AssemblyNode):
    """The machine, with no time base of its own."""

    crank = Driver(default=0.0, unit='deg')
    lever = Driver(default=100.0, range=(100, 140), unit='deg')

    spindle = Revolute(axis=(0, 0, 1), unit='deg')

    first = Arbor()
    second = Arbor()
    slide = Slide()
    wheel = Wheel(turn=spindle)

    crank.drives(first.turn, ratio=2.0)
    first.turn.drives(second.turn, ratio=-1.5)
    lever.drives(slide.travel, law=tooth_window)
    crank.drives(spindle, ratio=1.0)

    instructions = {
        'Park': Instruction({'crank': 40.0}, duration=0.5),
        'Advance': Instruction(by={'crank': 10.0}, duration=0.5),
        'Wind': Instruction(by={'crank': 10.0, 'lever': 5.0}, duration=0.5),
    }

    def render(self):
        self.second.translate([30.0, 0.0, 0.0])
        self.slide.translate([0.0, 40.0, 0.0])
        self.wheel.translate([0.0, -40.0, 0.0])


class Train(TrainBody):
    """The same machine, running."""

    time = Time.running()


class LoopingTrain(TrainBody):
    """The same machine, looping: the base this cycle leaves alone."""

    time = Time(loop=2.0)


class Backwards(AssemblyNode):
    """A relation the rest render solves BACKWARD: `second.turn` is the
    source as written and the driven end is what the crank reaches."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')

    first = Arbor()
    second = Arbor()

    crank.drives(first.turn, ratio=2.0)
    second.turn.drives(first.turn, ratio=4.0)

    def render(self):
        self.second.translate([30.0, 0.0, 0.0])


class Differential(AssemblyNode):
    """Two inputs prescribing one rigid group through a linear formula:
    the one conflict this cycle can reach."""

    time = Time.running()

    wrist_in = Driver(default=0.0, unit='deg')
    sum_in = Driver(default=0.0, unit='deg')

    wrist = Revolute(axis=(0, 0, 1), unit='deg')
    tool = Revolute(axis=(0, 1, 0), unit='deg')

    left = wrist + 2 * tool

    wrist_in.drives(wrist)
    wrist.drives(tool, ratio=1.0)
    sum_in.drives(left)

    block = Block()


class Stepped(AssemblyNode):
    """A running root whose law contains a jump."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    first = Arbor()

    crank.drives(first.turn, law=periodic_window)


class SteppedBody(AssemblyNode):
    """The same machine with no time base: it poses untimed unchanged."""

    crank = Driver(default=0.0, unit='deg')
    first = Arbor()

    crank.drives(first.turn, law=periodic_window)


class Stdlib(AssemblyNode):
    """A running root whose law calls Python's own `math`."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    first = Arbor()

    crank.drives(first.turn, law=stdlib_law)


class StdlibBody(AssemblyNode):
    """The same machine with no time base."""

    crank = Driver(default=0.0, unit='deg')
    first = Arbor()

    crank.drives(first.turn, law=stdlib_law)


class HandBound(AssemblyNode):
    """A law stated imperatively in `simulate()`: the run owns
    `first.turn`, so this is a double binding."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    first = Arbor()

    def simulate(self):
        self.first.turn = self.crank * 2


class Guarded(AssemblyNode):
    """The catalogue's rest-default idiom: it binds once, at the rest
    render, and never again while the run owns the coordinate."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    first = Arbor()
    slide = Slide()

    crank.drives(first.turn, ratio=2.0)

    def render(self):
        self.slide.translate([0.0, 40.0, 0.0])

    def simulate(self):
        if self.slide.travel.value is None:
            self.slide.travel = 4.0


class Opaque(AssemblyNode):
    """A relation into a bank coordinate sourced from a plain port the
    author's `simulate()` binds."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    relay = RotationalPort(unit='deg')
    first = Arbor()

    relay.drives(first.turn, ratio=1.0)

    def simulate(self):
        self.relay = self.crank * 3


class OpaqueBody(AssemblyNode):
    """The same machine with no time base."""

    crank = Driver(default=0.0, unit='deg')
    relay = RotationalPort(unit='deg')
    first = Arbor()

    relay.drives(first.turn, ratio=1.0)

    def simulate(self):
        self.relay = self.crank * 3


class RangedBody(AssemblyNode):
    """The same machine untimed, where a range still REFUSES a binding
    outside it: the control cycle 3 does not move."""

    crank = Driver(default=0.0, unit='deg')
    first = Arbor(turn=Revolute(axis=(0, 0, 1), range=(-90, 90), unit='deg'))

    crank.drives(first.turn, ratio=2.0)


class Ranged(RangedBody):
    """A joint whose declared range the crank drives it INTO.

    Cycle 1 failed the tick here. Cycle 3 stops `first.turn` at `90`
    inside the tick, commits it, and retires the command `blocked` with
    the travel it admitted -- the same declaration, read as the physical
    stop it states.
    """

    time = Time.running()


class RangedExactBody(AssemblyNode):
    """`Ranged`'s machine resting one tick short of its bound."""

    crank = Driver(default=40.0, unit='deg')
    first = Arbor(turn=Revolute(axis=(0, 0, 1), range=(-90, 90), unit='deg'))

    crank.drives(first.turn, ratio=2.0)


class RangedExact(RangedExactBody):
    """The same machine, running, resting at `first.turn == 80`: a move
    of `+5` on the crank lands it on exactly `90`, which is INSIDE the
    inclusive bound and therefore no stop at all."""

    time = Time.running()


class Unbound(AssemblyNode):
    """A joint nothing drives and no `simulate()` binds."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    first = Arbor()
    idle = Arbor()

    crank.drives(first.turn, ratio=2.0)

    def render(self):
        self.idle.translate([30.0, 0.0, 0.0])


class Chassis(AssemblyNode):
    """A body floating against the world: six freedoms, one joint."""

    pose = Free(at=(0, 0, 0))
    block = Block()


class Sixfree(AssemblyNode):
    """Four of the six bound by relations, two left to the open question
    of design.md section 2."""

    time = Time.running()

    lift = Driver(default=0.0, unit='mm')
    surge = Driver(default=0.0, unit='mm')
    sway = Driver(default=0.0, unit='mm')
    heading = Driver(default=0.0, unit='deg')

    chassis = Chassis()

    lift.drives(chassis.pose.z)
    surge.drives(chassis.pose.x)
    sway.drives(chassis.pose.y)
    heading.drives(chassis.pose.yaw)


class Readout(AssemblyNode):
    """The Pascaline module's idiom: a plain port an author's
    `simulate()` keeps in step with a coordinate an ANCESTOR bound."""

    turn = Revolute(axis=(0, 0, 1), unit='deg')
    readout = RotationalPort(unit='deg')

    block = Block()

    def simulate(self):
        self.readout = self.turn.value


class Follower(AssemblyNode):
    """A running root holding one."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')

    first = Arbor()
    gauge = Readout()

    crank.drives(first.turn, ratio=2.0)
    crank.drives(gauge.turn, ratio=2.0)

    def render(self):
        self.gauge.translate([0.0, 60.0, 0.0])


class BackDriven(AssemblyNode):
    """A relation whose driven end an author's `simulate()` binds and
    whose source is a joint coordinate: the rest render solves it
    BACKWARD, so a run that owns the source makes reading it backwards a
    double binding. No time base: the rule is the binder's, not the
    base's."""

    gauge = RotationalPort(unit='deg')
    first = Arbor()

    first.turn.drives(gauge, ratio=1.0)

    def simulate(self):
        self.gauge = 7.0


##############################################
# Cycle 2: the jump machines
#
# Each running root subclasses its own untimed `...Body`, so the one law
# is read both ways: untimed it poses absolutely, as it always did, and
# running it is integrated over the tick's segments.


class WindowBody(AssemblyNode):
    """The pilot's illustration, untimed: a crank and a pinion that
    turns 72 degrees once per revolution."""

    crank = Driver(default=100.0, unit='deg')
    pinion = Arbor()

    crank.drives(pinion.turn, law=periodic_window)


class Window(WindowBody):
    """The same machine, running."""

    time = Time.running()


class RemainderBody(AssemblyNode):
    """The same window written with `%`."""

    crank = Driver(default=100.0, unit='deg')
    pinion = Arbor()

    crank.drives(pinion.turn, law=remainder_window)


class Remainder(RemainderBody):
    time = Time.running()


class WrappedBody(AssemblyNode):
    """A `wrap`, which is a `ceil`."""

    crank = Driver(default=100.0, unit='deg')
    pinion = Arbor()

    crank.drives(pinion.turn, law=wrapped)


class Wrapped(WrappedBody):
    time = Time.running()


class ReverserBody(AssemblyNode):
    """A `sign` whose crossing contributes nothing."""

    crank = Driver(default=40.0, unit='deg')
    pinion = Arbor()

    crank.drives(pinion.turn, law=reversing)


class Reverser(ReverserBody):
    time = Time.running()


class KinkedBody(AssemblyNode):
    """Its continuous twin, with no jump node at all."""

    crank = Driver(default=40.0, unit='deg')
    pinion = Arbor()

    crank.drives(pinion.turn, law=kinked)


class Kinked(KinkedBody):
    time = Time.running()


class ThrowingBody(AssemblyNode):
    """A `sign` that genuinely jumps."""

    crank = Driver(default=40.0, unit='deg')
    pinion = Arbor()

    crank.drives(pinion.turn, law=throwing)


class Throwing(ThrowingBody):
    time = Time.running()


class AlternatingBody(AssemblyNode):
    """A jump nested in another jump's argument."""

    crank = Driver(default=100.0)
    pinion = Arbor()

    crank.drives(pinion.turn, law=alternating)


class Alternating(AlternatingBody):
    time = Time.running()


class ClutchBody(AssemblyNode):
    """The gate factor, over two sources and one joint path."""

    shaft = Driver(default=10.0, unit='deg')
    sleeve = Driver(default=0.0, unit='mm')
    wheel = Arbor()

    (shaft & sleeve).drives(wheel.turn, law=clutch)


class Clutch(ClutchBody):
    time = Time.running()


class CarryBody(AssemblyNode):
    """The Pascaline module's own shape: one driver and one JOINT
    COORDINATE as the two sources of a column's carry law."""

    column = Driver(default=100.0, unit='deg')
    tens_entry = Driver(default=0.0, unit='digit')

    units = Arbor()
    tens = Arbor()

    column.drives(units.turn, ratio=1.0)
    (tens_entry & units.turn).drives(tens.turn, law=carried_column)

    def render(self):
        self.tens.translate([30.0, 0.0, 0.0])


class Carry(CarryBody):
    time = Time.running()


class CarryLeadBody(AssemblyNode):
    """The same carry with the module's own lead, which makes the law
    jump at the window boundary."""

    column = Driver(default=100.0, unit='deg')
    tens_entry = Driver(default=0.0, unit='digit')

    units = Arbor()
    tens = Arbor()

    column.drives(units.turn, ratio=1.0)
    (tens_entry & units.turn).drives(tens.turn, law=carried_column_lead)

    def render(self):
        self.tens.translate([30.0, 0.0, 0.0])


class CarryLead(CarryLeadBody):
    time = Time.running()


class PortDrivenBody(AssemblyNode):
    """A jumping law driving a PLAIN PORT wired to a joint -- the
    Pascaline module's committed shape, and the one design.md section 9a
    refuses under a running root."""

    crank = Driver(default=100.0, unit='deg')
    register = RotationalPort(unit='deg')
    first = Arbor()

    register.drives(first.turn, ratio=1.0)
    crank.drives(register, law=periodic_window)


class PortDriven(PortDrivenBody):
    time = Time.running()


class PortDrivenJointBody(AssemblyNode):
    """The same relation stated into the joint coordinate the run owns,
    with the port following it: the migration the refusal asks for."""

    crank = Driver(default=100.0, unit='deg')
    register = RotationalPort(unit='deg')
    first = Arbor()

    crank.drives(first.turn, law=periodic_window)
    first.turn.drives(register, ratio=1.0)


class PortDrivenJoint(PortDrivenJointBody):
    time = Time.running()


class PortDrivenSmoothBody(AssemblyNode):
    """A CONTINUOUS law driving the same plain port: it compiles, so the
    refusal above is shown to be the jump's and not the port's."""

    crank = Driver(default=100.0, unit='deg')
    register = RotationalPort(unit='deg')
    first = Arbor()

    register.drives(first.turn, ratio=1.0)
    crank.drives(register, law=tooth_window)


class PortDrivenSmooth(PortDrivenSmoothBody):
    time = Time.running()


class OnlyJumpsBody(AssemblyNode):
    """A law that can only jump: arithmetic, not a mechanism."""

    turns = Driver(default=0.0)
    dial = Arbor()

    turns.drives(dial.turn, law=counter)


class OnlyJumps(OnlyJumpsBody):
    time = Time.running()


class SettledBody(AssemblyNode):
    """A jump-only term beside a sloped one: it compiles."""

    enabled = Driver(default=0.0)
    turns = Driver(default=0.0)
    dial = Arbor()

    (enabled & turns).drives(dial.turn, law=settled)


class Settled(SettledBody):
    time = Time.running()


class DivisorBody(AssemblyNode):
    """A `%` whose divisor a tick can take through zero."""

    a = Driver(default=10.0)
    b = Driver(default=-2.0)
    dial = Arbor()

    (a & b).drives(dial.turn, law=moving_divisor)


class Divisor(DivisorBody):
    time = Time.running()


class NonAffineBody(AssemblyNode):
    """A level quantity that is a product of two sources."""

    a = Driver(default=10.0)
    b = Driver(default=5.0)
    dial = Arbor()

    (a & b).drives(dial.turn, law=non_affine)


class NonAffine(NonAffineBody):
    time = Time.running()


class CrowdedBody(AssemblyNode):
    """A sawtooth of period one unit."""

    a = Driver(default=0.0)
    dial = Arbor()

    a.drives(dial.turn, law=crowded)


class Crowded(CrowdedBody):
    time = Time.running()


class PhaseCoupling:
    """A coupling whose INVERSE carries the jump.

    `inverse` folds the driven angle into one revolution -- what a phase
    reading is -- and `forward` is that inverse on the principal branch.
    The rest render solves the relation below backward, so the face the
    run compiles and integrates is the one with the `ceil` in it, over
    the DRIVEN end's id.
    """

    invertible = True

    def forward(self, phase):
        return phase

    def inverse(self, driven):
        return wrap(driven, 360.0)


def phase_coupling(source, target):
    return PhaseCoupling()


class BackwardJumpBody(AssemblyNode):
    """A relation the rest render solves BACKWARD, whose inverse jumps."""

    crank = Driver(default=100.0, unit='deg')

    first = Arbor()
    second = Arbor()

    crank.drives(first.turn, ratio=2.0)
    second.turn.drives(first.turn, law=phase_coupling)

    def render(self):
        self.second.translate([30.0, 0.0, 0.0])


class BackwardJump(BackwardJumpBody):
    time = Time.running()


class SmoothBody(AssemblyNode):
    """`Window`'s machine with the periodicity taken out: the same law,
    the same shape, and no jump node at all. It is the control the
    per-tick cost of a jump is measured against
    (`evidence/probe_cost.py`), which needs the two machines identical
    in everything but the `floor`."""

    crank = Driver(default=100.0, unit='deg')
    pinion = Arbor()

    crank.drives(pinion.turn, law=tooth_window)


class Smooth(SmoothBody):
    time = Time.running()


##############################################
# Cycle 3: the stop machines
#
# A range is a physical stop located inside the tick. Each running root
# subclasses its own untimed `...Body`, so the one declaration is read
# both ways: untimed a range still REFUSES a binding outside it, and
# running it stops the coordinate at its bound and blocks the inputs
# that push it.


def summed(sources, target):
    """A multi-source law with separable contributions: the shape of a
    coordinate one stopped input and one free one share."""
    return lambda a, b: 2 * a + 3 * b


def gated(sources, target):
    """The open gate. `crank` reaches the wheel only through a factor
    that is zero while the gate is open, so it is a CANDIDATE of the
    wheel's group and not a member of it: a static group would stop the
    crank, and the contribution test does not."""
    return lambda p, c, g: p + c * (g > 0.5)


def folded(source, target):
    """A `wrap` of period 90, whose fold falls at 135 -- inside the
    stretch a crank at 130 covers before its own stop at 145."""
    return lambda angle: 2 * wrap(angle, 90.0)


def curved(source, target):
    """A law that is NOT affine in its source, so the stop on the
    coordinate it drives is sampled and bisected rather than solved."""
    return lambda x: 40 * sin(x)


class RatchetBody(AssemblyNode):
    """The Pascaline module's ratchet, as the framework states it: the
    lower bound is the LAST SEATED TOOTH, an expression over the joint's
    own coordinate, and there is no upper bound because forward rotation
    is free.

    Untimed it poses at any angle, because `36 * floor(v / 36) <= v` for
    every `v`: the bound is evaluated at the value being bound.
    """

    arbor = Driver(default=40.0, unit='deg')
    wheel = Arbor(turn=Revolute(
        axis=(1, 0, 0), range=(lambda turn: 36 * floor(turn / 36), None),
        unit='deg'))

    arbor.drives(wheel.turn, ratio=1.0)


class Ratchet(RatchetBody):
    time = Time.running()


class ImpossibleBoundBody(AssemblyNode):
    """A bound no value satisfies: `turn + 1` is above every `turn`, so
    the declaration forbids every value and says so at the first
    binding."""

    arbor = Driver(default=40.0, unit='deg')
    wheel = Arbor(turn=Revolute(axis=(1, 0, 0),
                                range=(lambda turn: turn + 1, None),
                                unit='deg'))

    arbor.drives(wheel.turn, ratio=1.0)


class OpenLowBody(AssemblyNode):
    """One open bound: `(0, None)` accepts anything above zero."""

    arbor = Driver(default=10.0, unit='deg')
    wheel = Arbor(turn=Revolute(axis=(1, 0, 0), range=(0, None), unit='deg'))

    arbor.drives(wheel.turn, ratio=1.0)


class SweptBody(AssemblyNode):
    """The spike's swept stop: a rack that stops at its own limit while
    an unrelated motor runs its full tick. Two inputs, two groups,
    nothing shared."""

    steer = Driver(default=45.0, unit='mm')
    motor = Driver(default=0.0, unit='deg')

    rack = Slide(travel=Prismatic(axis=(1, 0, 0), range=(None, 50.0),
                                  unit='mm'))
    wheel = Arbor()

    steer.drives(rack.travel, ratio=1.0)
    motor.drives(wheel.turn, ratio=3.0)

    instructions = {
        'Sweep': Instruction(by={'steer': 10.0, 'motor': 9.0}, duration=0.1),
    }

    def render(self):
        self.wheel.translate([0.0, -40.0, 0.0])


class Swept(SweptBody):
    time = Time.running()


class SweptWideBody(SweptBody):
    """The same machine with the rack's bound MOVED and nothing else, so
    a snapshot of one cannot restore into the other."""

    rack = Slide(travel=Prismatic(axis=(1, 0, 0), range=(None, 80.0),
                                  unit='mm'))


class SweptWide(SweptWideBody):
    time = Time.running()


class StepperBody(AssemblyNode):
    """An INTEGER input: a rate's cumulative travel is truncated toward
    zero, so a negative rate rounds like a positive one."""

    step = Driver(default=0, dtype=int, unit='step')
    carriage = Slide()

    step.drives(carriage.travel, ratio=1.0)


class Stepper(StepperBody):
    time = Time.running()


class StoppedDifferentialBody(AssemblyNode):
    """`Differential`'s rigid group with a BOUND on `wrist`.

    Over the whole tick the two inputs agree, so nothing is refused and
    the stop is located; after it `wrist_in` is stopped while `sum_in`
    goes on prescribing `left`, and the check edge catches the
    disagreement. The tick is atomic, so the whole of it commits
    nothing.
    """

    wrist_in = Driver(default=0.0, unit='deg')
    sum_in = Driver(default=0.0, unit='deg')

    wrist = Revolute(axis=(0, 0, 1), range=(None, 5.0), unit='deg')
    tool = Revolute(axis=(0, 1, 0), unit='deg')

    left = wrist + 2 * tool

    wrist_in.drives(wrist)
    wrist.drives(tool, ratio=1.0)
    sum_in.drives(left)

    block = Block()


class StoppedDifferential(StoppedDifferentialBody):
    time = Time.running()


class SharedBody(AssemblyNode):
    """A coordinate two inputs determine, one of which stops: `d.turn`
    goes on moving on what `b_in` contributes after `a_in` is stopped by
    `c.turn`'s bound."""

    a_in = Driver(default=8.0, unit='deg')
    b_in = Driver(default=0.0, unit='deg')

    c = Arbor(turn=Revolute(axis=(0, 0, 1), range=(None, 10.0), unit='deg'))
    d = Arbor()

    a_in.drives(c.turn, ratio=1.0)
    (a_in & b_in).drives(d.turn, law=summed)

    def render(self):
        self.d.translate([30.0, 0.0, 0.0])


class Shared(SharedBody):
    time = Time.running()


class TwoStopsBody(AssemblyNode):
    """Two independent groups reaching two bounds at two fractions of
    one tick."""

    lever_in = Driver(default=18.0, unit='deg')
    steer = Driver(default=45.0, unit='mm')

    lever = Arbor(turn=Revolute(axis=(0, 0, 1), range=(None, 20.0),
                                unit='deg'))
    rack = Slide(travel=Prismatic(axis=(1, 0, 0), range=(None, 50.0),
                                  unit='mm'))

    lever_in.drives(lever.turn, ratio=1.0)
    steer.drives(rack.travel, ratio=1.0)

    def render(self):
        self.rack.translate([0.0, 40.0, 0.0])


class TwoStops(TwoStopsBody):
    time = Time.running()


class OpenGateBody(AssemblyNode):
    """The group is who PUSHES, not who is wired.

    `crank` reaches `wheel.turn` through the compiled program -- it is a
    source of the law -- but while the gate stands open its motion
    changes nothing there, so the wheel's stop does not stop it and the
    flywheel it also drives runs the full tick. Close the gate and the
    same tick stops both.
    """

    push = Driver(default=15.0, unit='deg')
    crank = Driver(default=0.0, unit='deg')
    gate = Driver(default=0.0)

    wheel = Arbor(turn=Revolute(axis=(0, 0, 1), range=(None, 20.0),
                                unit='deg'))
    flywheel = Arbor()

    (push & crank & gate).drives(wheel.turn, law=gated)
    crank.drives(flywheel.turn, ratio=1.0)

    def render(self):
        self.flywheel.translate([30.0, 0.0, 0.0])


class OpenGate(OpenGateBody):
    time = Time.running()


class StopAndJumpBody(AssemblyNode):
    """A stop and a jump crossing in one tick: the crank's own stop at
    `145` falls after the `wrap` fold at `135`, so the crossing is
    located inside segment A and recorded at its fraction OF THE TICK."""

    crank = Driver(default=130.0, unit='deg')

    first = Arbor(turn=Revolute(axis=(0, 0, 1), range=(None, 145.0),
                                unit='deg'))
    folder = Arbor()

    crank.drives(first.turn, ratio=1.0)
    crank.drives(folder.turn, law=folded)

    def render(self):
        self.folder.translate([30.0, 0.0, 0.0])


class StopAndJump(StopAndJumpBody):
    time = Time.running()


class CurvedBody(AssemblyNode):
    """A bound reached through a law that is not affine in its source:
    `40 * sin(x)` reaches `20` at `x == 30`, and the run has to SEARCH
    for that fraction rather than solve for it."""

    crank = Driver(default=0.0, unit='deg')
    dial = Arbor(turn=Revolute(axis=(0, 0, 1), range=(None, 20.0),
                               unit='deg'))

    crank.drives(dial.turn, law=curved)


class Curved(CurvedBody):
    time = Time.running()


# Design.md section 10: a bound naming a SECOND coordinate is deferred.
# The spike's ratchet fixture carries a `lift` that releases the pawl,
# and the shape the general form would take is
#
#     class InputArbor(AssemblyNode):
#         lift = Revolute(axis=(0, 1, 0), unit='deg')
#         turn = Revolute(
#             axis=(1, 0, 0),
#             range=(Bound(lambda turn, lift: -inf if lift > 1 else
#                          36 * floor(turn / 36), reads=('turn', 'lift')),
#                    None))
#
# resolved against the declarer's subtree at `Sim` construction, where
# the ids exist. There is no `Bound` in this cycle and a one-argument
# callable keeps meaning what it means here; the deferral is pinned by a
# skipped test in `tests/test_running_stops.py` rather than only by this
# comment.


##############################################
# Cycle 4: the machines the PUBLISHED document is answerable to
#
# Three shapes the document has to be able to say, and one the tick
# already says and the document must not: a clock read in `simulate()`,
# three jumping laws in one tree, and a machine whose bank is the whole
# of what poses it.


class ClockedBody(AssemblyNode):
    """A machine whose `simulate()` reads the clock: untimed, that read
    is the bare animation variable it always was."""

    crank = Driver(default=0.0, unit='deg')

    first = Arbor()
    flag = Block()

    crank.drives(first.turn, ratio=2.0)

    def simulate(self):
        self.flag.rotate(30.0 * self.time, [0, 0, 1])

    def render(self):
        self.flag.translate([0.0, 25.0, 0.0])


class Clocked(ClockedBody):
    """The same machine, running: elapsed seconds, published under the
    program's own clock name."""

    time = Time.running()


class ThreeCarriesBody(AssemblyNode):
    """The Pascaline's shape in the fixture's own constants: three laws
    in one tree, each carrying exactly one `floor`.

    The collision `evidence/probe_placeholders.py` found needs three
    plans in ONE document to show itself, and the acceptance project
    lives in another repository. This is that machine, here.
    """

    units_entry = Driver(default=0.0, unit='digit')
    tens_entry = Driver(default=0.0, unit='digit')
    hundreds_entry = Driver(default=0.0, unit='digit')

    units = Arbor()
    tens = Arbor()
    hundreds = Arbor()
    trail = Arbor()

    units_entry.drives(units.turn, ratio=DIGIT_STEP)
    (tens_entry & units.turn).drives(tens.turn, law=carried_column_lead)
    (hundreds_entry & tens.turn).drives(hundreds.turn,
                                        law=carried_column_lead)
    hundreds.turn.drives(trail.turn, law=periodic_window)

    def render(self):
        self.tens.translate([30.0, 0.0, 0.0])
        self.hundreds.translate([60.0, 0.0, 0.0])
        self.trail.translate([90.0, 0.0, 0.0])


class ThreeCarries(ThreeCarriesBody):
    time = Time.running()


class WiredBody(AssemblyNode):
    """A WIRING into a joint coordinate the run owns: the declaration
    site hands the child's own coordinate the parent's plain port, and
    the relation driving that port reaches the bank through it."""

    crank = Driver(default=0.0, unit='deg')
    relay = RotationalPort(unit='deg')

    first = Arbor(turn=relay)

    crank.drives(relay, ratio=2.0)


class Wired(WiredBody):
    time = Time.running()


class DerivedBody(AssemblyNode):
    """A DERIVED COORDINATE the rest render solves FORWARD, whose value
    then drives a joint the run owns: the formula edge, with the
    coefficients a consumer evaluates it by."""

    wrist_in = Driver(default=0.0, unit='deg')
    tool_in = Driver(default=0.0, unit='deg')

    wrist = Revolute(axis=(0, 0, 1), unit='deg')
    tool = Revolute(axis=(0, 1, 0), unit='deg')

    left = wrist + 2 * tool

    arm = Arbor()

    wrist_in.drives(wrist)
    tool_in.drives(tool)
    left.drives(arm.turn, ratio=1.0)

    block = Block()

    def render(self):
        self.arm.translate([30.0, 0.0, 0.0])


class Derived(DerivedBody):
    time = Time.running()


class SixboundBody(AssemblyNode):
    """A `Free` joint every one of whose six coordinates a relation
    drives, so the whole floating placement publishes."""

    lift = Driver(default=0.0, unit='mm')
    surge = Driver(default=0.0, unit='mm')
    sway = Driver(default=0.0, unit='mm')
    heading = Driver(default=0.0, unit='deg')
    pitching = Driver(default=0.0, unit='deg')
    rolling = Driver(default=0.0, unit='deg')

    chassis = Chassis()

    lift.drives(chassis.pose.z)
    surge.drives(chassis.pose.x)
    sway.drives(chassis.pose.y)
    heading.drives(chassis.pose.yaw)
    pitching.drives(chassis.pose.pitch)
    rolling.drives(chassis.pose.roll)


class Sixbound(SixboundBody):
    time = Time.running()


class Needle(AssemblyNode):
    """A part posed by a PLAIN PORT its parent drives: the module's
    readout idiom, where the register's angle turns something no joint
    carries."""

    angle = RotationalPort(unit='deg')

    hand = Block()

    def render(self):
        self.hand.translate([0.0, 12.0, 0.0])

    def simulate(self):
        self.hand.rotate(self.angle.value, [0, 0, 1])


class GaugedBody(AssemblyNode):
    """A running root whose readout poses geometry from an
    INTERMEDIATE."""

    crank = Driver(default=0.0, unit='deg')

    first = Arbor()
    gauge = Needle()

    crank.drives(first.turn, ratio=2.0)
    first.turn.drives(gauge.angle, ratio=-1)

    def render(self):
        self.gauge.translate([0.0, 60.0, 0.0])


class Gauged(GaugedBody):
    time = Time.running()


##############################################
# The CONTROL machines: OpenSpec change `declare-controls-on-parts`.
#
# `Columns` is the Pascaline module's own tree shape -- a dial at depth
# under the arbor that turns it, a second column two inputs reach -- and
# is what the whole cycle is answerable to. `ColumnsBare` is its
# control-free twin, so the identity a snapshot is checked against can
# be shown not to have moved. The rest is one machine per refusal, per
# geometry case, and per rule the design states.


class DialArbor(AssemblyNode):
    """The Pascaline's own shape: the joint at depth, the touchable leaf
    beneath it.

    `Arbor` is a LEAF and can hold nothing, so no existing fixture has
    the shape every control in the module has -- a body a hand touches,
    hanging under the node whose joint poses it.
    """

    turn = Revolute(axis=(1, 0, 0), unit='deg')

    dial = Dial()


class Columns(AssemblyNode):
    """Two Pascaline columns: `units.turn` is reached by one input and
    `tens.turn` by BOTH, which is the ambiguity a viewer cannot resolve
    and the author therefore declares.

    Time, the children and the controls are declared on ONE class on
    purpose: a control names a class-body declaration, and splitting the
    body off into a base would only make every reference read
    `ColumnsBody.units.dial`.
    """

    time = Time.running()

    units_entry = Driver(default=0.0, unit='digit')
    tens_entry = Driver(default=0.0, unit='digit')

    units = DialArbor()
    tens = DialArbor()
    frame = Block()

    units_entry.drives(units.turn, ratio=-36.0)
    (tens_entry & units.turn).drives(tens.turn, law=carried_column)

    instructions = {
        'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0),
        'Add ten': Instruction(by={'tens_entry': 1.0}, duration=1.0),
    }
    controls = {
        'units dial': Button(units.dial, 'Add one'),
        'tens dial': Button(tens.dial, 'Add ten'),
        'turn units': Turn(units.dial, units_entry),
        'turn tens': Turn(tens.dial, tens_entry),
    }

    def render(self):
        self.tens.translate([60.0, 0.0, 0.0])
        self.frame.translate([0.0, -60.0, 0.0])


class ColumnsBare(AssemblyNode):
    """`Columns` to the last character, minus the controls: what the
    compiled program, the bank and the identity must be unchanged
    against."""

    time = Time.running()

    units_entry = Driver(default=0.0, unit='digit')
    tens_entry = Driver(default=0.0, unit='digit')

    units = DialArbor()
    tens = DialArbor()
    frame = Block()

    units_entry.drives(units.turn, ratio=-36.0)
    (tens_entry & units.turn).drives(tens.turn, law=carried_column)

    instructions = {
        'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0),
        'Add ten': Instruction(by={'tens_entry': 1.0}, duration=1.0),
    }

    def render(self):
        self.tens.translate([60.0, 0.0, 0.0])
        self.frame.translate([0.0, -60.0, 0.0])


class OffCentreArbor(AssemblyNode):
    """A dial on a joint whose line does NOT run through the node's own
    placed origin."""

    turn = Revolute(axis=(1, 0, 0), at=(0, 3, 0), unit='deg')

    dial = Dial()


class OffCentre(AssemblyNode):
    """Design section 8: the point the joint turns about reaches the
    document only as two translations, so the entry publishes it."""

    time = Time.running()

    units_entry = Driver(default=0.0, unit='digit')

    units = OffCentreArbor()

    units_entry.drives(units.turn, ratio=-36.0)

    instructions = {
        'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0),
    }
    controls = {
        'units dial': Button(units.dial, 'Add one'),
        'turn units': Turn(units.dial, units_entry),
    }


class PlainDial(AssemblyNode):
    """A body carrying a dial and declaring no joint of its own: the
    declaration SITE gives it one."""

    dial = Dial()


class SiteTurned(AssemblyNode):
    """The joint stated by the PARENT at the declaration site.

    `place` carries a site joint's axis and anchor into the child's own
    frame by inverting the child's rest placement, so the published
    `axis` and `origin` are the CARRIED values and not the ones written
    here -- the case a naive implementation gets wrong.
    """

    time = Time.running()

    entry = Driver(default=0.0, unit='digit')

    holder = PlainDial(turn=Revolute(axis=(0, 0, 1), at=(0, 6, 0),
                                     unit='deg'))

    entry.drives(holder.turn, ratio=-36.0)

    instructions = {
        'Add one': Instruction(by={'entry': 1.0}, duration=1.0),
    }
    controls = {
        'turn holder': Turn(holder.dial, entry),
    }

    def render(self):
        self.holder.rotate(90, [1, 0, 0])
        self.holder.translate([0.0, 20.0, 0.0])


class DialHolder(AssemblyNode):
    """An assembly between the joint and the part that declares nothing
    at all: the walk up passes straight through it."""

    dial = Dial()


class DeepArbor(AssemblyNode):
    turn = Revolute(axis=(1, 0, 0), unit='deg')

    holder = DialHolder()


class DeepColumn(AssemblyNode):
    """Three deep: root, the arbor that declares the joint, the holder
    that declares nothing, the dial."""

    time = Time.running()

    entry = Driver(default=0.0, unit='digit')

    deep = DeepArbor()

    entry.drives(deep.turn, ratio=-36.0)

    instructions = {
        'Add one': Instruction(by={'entry': 1.0}, duration=1.0),
    }
    controls = {
        'deep dial': Button(deep.holder.dial, 'Add one'),
        'turn deep': Turn(deep.holder.dial, entry),
    }


class Column(AssemblyNode):
    """A CHILD that declares its own driver, instruction and controls:
    everything about it qualifies through its instance path."""

    entry = Driver(default=0.0, unit='digit')

    arbor = DialArbor()

    entry.drives(arbor.turn, ratio=-36.0)

    instructions = {
        'Add one': Instruction(by={'entry': 1.0}, duration=1.0),
    }
    controls = {
        'dial': Button(arbor.dial, 'Add one'),
        'turn': Turn(arbor.dial, entry),
    }


class ColumnStack(AssemblyNode):
    """A running root that declares no control of its own and holds one
    that does."""

    time = Time.running()

    column = Column()


class Unposed(AssemblyNode):
    """A control on a leaf no run-owned coordinate poses."""

    time = Time.running()

    units_entry = Driver(default=0.0, unit='digit')

    units = DialArbor()
    frame = Block()

    units_entry.drives(units.turn, ratio=-36.0)

    instructions = {
        'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0),
    }
    controls = {
        'press frame': Button(frame, 'Add one'),
    }

    def render(self):
        self.frame.translate([0.0, -60.0, 0.0])


class SlideDial(AssemblyNode):
    travel = Prismatic(axis=(1, 0, 0), unit='mm')

    plate = Dial()


class Sliding(AssemblyNode):
    """A `Turn` over a TRANSLATIONAL coordinate: `Slide` is not in this
    release."""

    time = Time.running()

    feed = Driver(default=0.0, unit='mm')

    carriage = SlideDial()

    feed.drives(carriage.travel, ratio=1.0)

    instructions = {
        'Feed': Instruction(by={'feed': 1.0}, duration=1.0),
    }
    controls = {
        'turn carriage': Turn(carriage.plate, feed),
    }


class Unreached(AssemblyNode):
    """`Columns`' shape with the WRONG input named: `tens_entry` does
    not reach `units.turn` at all."""

    time = Time.running()

    units_entry = Driver(default=0.0, unit='digit')
    tens_entry = Driver(default=0.0, unit='digit')

    units = DialArbor()
    tens = DialArbor()

    units_entry.drives(units.turn, ratio=-36.0)
    (tens_entry & units.turn).drives(tens.turn, law=carried_column)

    instructions = {
        'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0),
    }
    controls = {
        'turn units': Turn(units.dial, tens_entry),
    }

    def render(self):
        self.tens.translate([60.0, 0.0, 0.0])


class Unmoved(AssemblyNode):
    """`Columns`' shape with an input that REACHES the coordinate and
    moves it by nothing at rest: `units_entry`'s partial in `tens.turn`
    is zero where the carry cam is between its ramps."""

    time = Time.running()

    units_entry = Driver(default=0.0, unit='digit')
    tens_entry = Driver(default=0.0, unit='digit')

    units = DialArbor()
    tens = DialArbor()

    units_entry.drives(units.turn, ratio=-36.0)
    (tens_entry & units.turn).drives(tens.turn, law=carried_column)

    instructions = {
        'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0),
    }
    controls = {
        'turn tens': Turn(tens.dial, units_entry),
    }

    def render(self):
        self.tens.translate([60.0, 0.0, 0.0])


class Unnamed(AssemblyNode):
    """A `Button` naming an instruction nothing declares."""

    time = Time.running()

    units_entry = Driver(default=0.0, unit='digit')

    units = DialArbor()

    units_entry.drives(units.turn, ratio=-36.0)

    instructions = {
        'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0),
    }
    controls = {
        'units dial': Button(units.dial, 'Add two'),
    }


class TwoJointed(AssemblyNode):
    """A body two joints compose one motion for."""

    swing = Revolute(axis=(1, 0, 0), unit='deg')
    lift = Revolute(axis=(0, 1, 0), unit='deg')

    dial = Dial()


class TwoJoints(AssemblyNode):
    """A control on a part whose nearest posing node declares TWO
    joints: neither is "the" coordinate."""

    time = Time.running()

    entry = Driver(default=0.0, unit='digit')
    elevation = Driver(default=0.0, unit='deg')

    stack = TwoJointed()

    entry.drives(stack.swing, ratio=-36.0)
    elevation.drives(stack.lift, ratio=1.0)

    instructions = {
        'Add one': Instruction(by={'entry': 1.0}, duration=1.0),
    }
    controls = {
        'turn stack': Turn(stack.dial, entry),
    }


class FreeDial(AssemblyNode):
    """A dial on a body floating against the world."""

    pose = Free(at=(0, 0, 0))

    dial = Dial()


class FreePosed(AssemblyNode):
    """A control on a part posed by a joint owning SIX coordinates."""

    time = Time.running()

    lift = Driver(default=0.0, unit='mm')
    surge = Driver(default=0.0, unit='mm')
    sway = Driver(default=0.0, unit='mm')
    heading = Driver(default=0.0, unit='deg')
    pitching = Driver(default=0.0, unit='deg')
    rolling = Driver(default=0.0, unit='deg')

    floating = FreeDial()

    lift.drives(floating.pose.z)
    surge.drives(floating.pose.x)
    sway.drives(floating.pose.y)
    heading.drives(floating.pose.yaw)
    pitching.drives(floating.pose.pitch)
    rolling.drives(floating.pose.roll)

    instructions = {
        'Turn about': Instruction(by={'heading': 1.0}, duration=1.0),
    }
    controls = {
        'turn floating': Turn(floating.dial, heading),
    }


class NotRunning(AssemblyNode):
    """The same controls under NO time base."""

    units_entry = Driver(default=0.0, unit='digit')

    units = DialArbor()

    units_entry.drives(units.turn, ratio=-36.0)

    instructions = {
        'Park': Instruction({'units_entry': 0.0}, duration=0.5),
    }
    controls = {
        'units dial': Button(units.dial, 'Park'),
    }


class LoopingControls(NotRunning):
    """The same controls under a LOOPING base, inheriting the table and
    the flag from its own base."""

    time = Time(loop=2.0)


class OmittableArbor(AssemblyNode):
    """An arbor whose dial a parameter may leave off the machine.

    The PART goes and the joint stays, which is the shape design section
    10 is about: a machine whose lid carries a control still builds with
    `--set covers=false`.
    """

    fitted = Flag(True)

    turn = Revolute(axis=(1, 0, 0), unit='deg')

    dial = Dial()

    def render(self):
        if not self.fitted:
            self.dial.omit()


class OmittedControl(AssemblyNode):
    """Design section 10: a part THIS render omits drops its control
    rather than refusing the build."""

    time = Time.running()

    fitted = Flag(True)

    units_entry = Driver(default=0.0, unit='digit')

    units = DialArbor()
    spare = OmittableArbor(fitted=fitted)

    units_entry.drives(units.turn, ratio=-36.0)
    units_entry.drives(spare.turn, ratio=-36.0)

    instructions = {
        'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0),
    }
    controls = {
        'spare dial': Button(spare.dial, 'Add one'),
        'units dial': Button(units.dial, 'Add one'),
        'turn units': Turn(units.dial, units_entry),
    }

    def render(self):
        self.spare.translate([60.0, 0.0, 0.0])


class Stepping(AssemblyNode):
    """An INTEGER input: the measurement displaces by one NATIVE unit,
    because `Driver.native` rounds a design-unit displacement to whole
    native units once and anything below half a step is no step at
    all."""

    time = Time.running()

    feed = Driver(default=0, dtype=int, scale=0.0125, unit='mm')

    units = DialArbor()

    feed.drives(units.turn, ratio=-36.0)

    instructions = {
        'Step': Instruction(by={'feed': 0.0125}, duration=1.0),
    }
    controls = {
        'turn units': Turn(units.dial, feed),
    }


class KinkedControl(AssemblyNode):
    """A `Turn` over a law with a KINK exactly at the rest value.

    `kinked` is `5 * abs(x - 50)` and the crank rests at 50, so the
    forward reading is `+5` and the backward `-5`: no single number
    scales the gesture, and a drag scaled by one of them would be wrong
    in the other direction.
    """

    time = Time.running()

    crank = Driver(default=50.0, unit='deg')

    units = DialArbor()

    crank.drives(units.turn, law=kinked)

    instructions = {
        'Nudge': Instruction(by={'crank': 1.0}, duration=1.0),
    }
    controls = {
        'turn units': Turn(units.dial, crank),
    }


class SmoothControl(AssemblyNode):
    """The same shape over a SMOOTH non-affine law, at a state where its
    curvature is at its most awkward: admitted, because a law that
    curves still moves the part exactly what the run commits."""

    time = Time.running()

    crank = Driver(default=89.0, unit='deg')

    units = DialArbor()

    crank.drives(units.turn, law=swinging)

    instructions = {
        'Nudge': Instruction(by={'crank': 1.0}, duration=1.0),
    }
    controls = {
        'turn units': Turn(units.dial, crank),
    }
# The CONSTRAINT machines: a bound that reads other coordinates
#
# The pin tumbler lock's shape, reduced to two pins: a key whose travel
# lifts them over its cuts, and a plug that may only turn while every
# lift stands inside the shear-line window. Every joint here is
# SITE-declared, as most of this module's are, so the declarer is the
# root -- except `ClassGateBody`'s, whose `Plug` declares its own
# children and its own joint and is therefore the other resolution path.


def pin_lift(knot):
    """A key pin's lift as a LAW FACTORY, the two-argument shape `law=`
    takes: `5` mm of lift until the key's travel reaches `knot`, none
    from `knot + 5` on, so the `[-0.05, 0.05]` window opens at
    `knot + 4.95`."""
    def law(source_owner, target_owner):
        return lambda travel: 5 - 5 * clamp01((travel - knot) / 5)

    return law


def cleared(value, window=0.05):
    """Whether a pin's lift stands inside the shear-line window --
    written over `solid_node.math`, so it reads a number and a symbol
    alike."""
    return abs(value) <= window


class GateBody(AssemblyNode):
    """Two pins, a plug that may only turn while both are cleared, and
    the key that lifts them. No time base of its own: the untimed
    control, where the bound is judged when the enumeration closes.

    The children are declared in the order a `Bound` needs them: a body
    can only read what it has already named.
    """

    feed = Driver(default=10.0, unit='mm')
    twist = Driver(default=0.0, unit='deg')

    p1 = Pin()
    p2 = Pin()
    plug = Arbor(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(0, Bound(lambda turn, a, b: 90 * cleared(a) * cleared(b),
                        reads=(p1.lift, p2.lift)))))
    key = Slide()

    feed.drives(key.travel, ratio=1.0)
    key.travel.drives(p1.lift, law=pin_lift(10))
    key.travel.drives(p2.lift, law=pin_lift(13))
    twist.drives(plug.turn, ratio=1.0)

    def render(self):
        self.p2.translate([7.2, 0.0, 0.0])
        self.plug.translate([0.0, -20.0, 0.0])
        self.key.translate([0.0, 20.0, 0.0])


class Gate(GateBody):
    time = Time.running()


class GateWideBody(AssemblyNode):
    """`GateBody` with the window at `0.5` and nothing else changed: the
    identity control, so a snapshot of one cannot restore into the
    other."""

    feed = Driver(default=10.0, unit='mm')
    twist = Driver(default=0.0, unit='deg')

    p1 = Pin()
    p2 = Pin()
    plug = Arbor(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(0, Bound(lambda turn, a, b: (90 * cleared(a, 0.5)
                                            * cleared(b, 0.5)),
                        reads=(p1.lift, p2.lift)))))
    key = Slide()

    feed.drives(key.travel, ratio=1.0)
    key.travel.drives(p1.lift, law=pin_lift(10))
    key.travel.drives(p2.lift, law=pin_lift(13))
    twist.drives(plug.turn, ratio=1.0)

    def render(self):
        self.p2.translate([7.2, 0.0, 0.0])
        self.plug.translate([0.0, -20.0, 0.0])
        self.key.translate([0.0, 20.0, 0.0])


class GateWide(GateWideBody):
    time = Time.running()


class CapturedBody(AssemblyNode):
    """`GateBody` resting SEATED -- the key at `20`, both pins cleared --
    with the CAPTURE stated a second time on the key's own travel: while
    the plug stands turned, the key may not come back out.

    A sibling rather than a subclass: the declaration order is
    load-bearing, and a subclass redeclaring the key would state it
    after the plug that reads it.
    """

    feed = Driver(default=20.0, unit='mm')
    twist = Driver(default=0.0, unit='deg')

    p1 = Pin()
    p2 = Pin()
    plug = Arbor(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(0, Bound(lambda turn, a, b: 90 * cleared(a) * cleared(b),
                        reads=(p1.lift, p2.lift)))))
    key = Slide(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(Bound(lambda travel, turn: 20 * (turn > 0),
                     reads=(plug.turn,)), 20)))

    feed.drives(key.travel, ratio=1.0)
    key.travel.drives(p1.lift, law=pin_lift(10))
    key.travel.drives(p2.lift, law=pin_lift(13))
    twist.drives(plug.turn, ratio=1.0)

    def render(self):
        self.p2.translate([7.2, 0.0, 0.0])
        self.plug.translate([0.0, -20.0, 0.0])
        self.key.translate([0.0, 20.0, 0.0])


class Captured(CapturedBody):
    time = Time.running()


class PawlRatchetBody(AssemblyNode):
    """`RatchetBody`'s own bound with a PAWL in it: the last seated
    tooth, lifted out of the way by a second coordinate.

    The tooth is the COMMITTED arbor's -- that is what makes a ratchet a
    ratchet -- and the pawl's lift is read along the tick's path, so a
    pawl that clears before the wheel meets its tooth releases the
    reverse and one that clears after it does not.
    """

    arbor = Driver(default=40.0, unit='deg')
    hoist = Driver(default=0.0, unit='mm')

    pawl = Pin()
    wheel = Arbor(turn=Revolute(
        axis=(1, 0, 0), unit='deg',
        range=(Bound(lambda turn, lift: (36 * floor(turn / 36)
                                         - 1000 * (lift >= 1)),
                     reads=(pawl.lift,)), None)))

    arbor.drives(wheel.turn, ratio=1.0)
    hoist.drives(pawl.lift, ratio=1.0)

    def render(self):
        self.pawl.translate([0.0, 20.0, 0.0])


class PawlRatchet(PawlRatchetBody):
    time = Time.running()


class Plug(AssemblyNode):
    """The other resolution path: a body declaring its own children AND
    its own class joint, whose bound reads them. The declarer is this
    node, not the root, so the ids the reads qualify to carry the plug's
    own segment."""

    p1 = Pin()
    p2 = Pin()
    turn = Revolute(axis=(0, 0, 1), unit='deg',
                    range=(0, Bound(lambda turn, a, b:
                                    90 * cleared(a) * cleared(b),
                                    reads=(p1.lift, p2.lift))))

    def render(self):
        self.p2.translate([7.2, 0.0, 0.0])


class ClassGateBody(AssemblyNode):
    """`GateBody` with the constraint declared inside the plug."""

    feed = Driver(default=10.0, unit='mm')
    twist = Driver(default=0.0, unit='deg')

    plug = Plug()
    key = Slide()

    feed.drives(key.travel, ratio=1.0)
    key.travel.drives(plug.p1.lift, law=pin_lift(10))
    key.travel.drives(plug.p2.lift, law=pin_lift(13))
    twist.drives(plug.turn, ratio=1.0)

    def render(self):
        self.plug.translate([0.0, -20.0, 0.0])
        self.key.translate([0.0, 20.0, 0.0])


class ClassGate(ClassGateBody):
    time = Time.running()


class PortReadBody(AssemblyNode):
    """A bound reading a PLAIN PORT: legal to declare, and refused at
    `Sim` construction, because a bound reads the state and a port is a
    calculation the enumeration recomputes from it."""

    feed = Driver(default=0.0, unit='deg')
    twist = Driver(default=0.0, unit='deg')

    dial = Wheel()
    plug = Arbor(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(0, Bound(lambda turn, angle: 90 * (angle >= 1),
                        reads=(dial.turn,)))))

    feed.drives(dial.turn, ratio=1.0)
    twist.drives(plug.turn, ratio=1.0)

    def render(self):
        self.plug.translate([0.0, -20.0, 0.0])


class PortRead(PortReadBody):
    time = Time.running()


class ConstantBoundBody(AssemblyNode):
    """A `Bound` whose expression returns a NUMBER: it declares a read
    and reads nothing, so it is refused at `Sim` construction rather
    than carried as a constraint with no expression to evaluate."""

    feed = Driver(default=0.0, unit='mm')
    twist = Driver(default=0.0, unit='deg')

    key = Slide()
    p1 = Pin()
    plug = Arbor(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(0, Bound(lambda turn, a: 45, reads=(p1.lift,)))))

    feed.drives(key.travel, ratio=1.0)
    key.travel.drives(p1.lift, ratio=1.0)
    twist.drives(plug.turn, ratio=1.0)

    def render(self):
        self.p1.translate([0.0, -20.0, 0.0])
        self.plug.translate([0.0, -40.0, 0.0])


class ConstantBound(ConstantBoundBody):
    time = Time.running()


class UnusedReadBody(AssemblyNode):
    """A `Bound` declaring two reads whose expression uses only one: the
    declaration says it reads what it does not, and is refused at `Sim`
    construction naming the read it never uses."""

    feed = Driver(default=0.0, unit='mm')
    twist = Driver(default=0.0, unit='deg')

    key = Slide()
    p1 = Pin()
    p2 = Pin()
    plug = Arbor(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(0, Bound(lambda turn, a, b: 90 * (a <= 0.05),
                        reads=(p1.lift, p2.lift)))))

    feed.drives(key.travel, ratio=1.0)
    key.travel.drives(p1.lift, ratio=1.0)
    key.travel.drives(p2.lift, ratio=1.0)
    twist.drives(plug.turn, ratio=1.0)

    def render(self):
        self.p1.translate([0.0, -20.0, 0.0])
        self.p2.translate([0.0, -30.0, 0.0])
        self.plug.translate([0.0, -40.0, 0.0])


class UnusedRead(UnusedReadBody):
    time = Time.running()


class UnreadGateBody(AssemblyNode):
    """`GateBody` with nothing driving the pins: at the close of the
    enumeration the reads hold NO value, so the bound is not judged."""

    twist = Driver(default=0.0, unit='deg')

    p1 = Pin()
    p2 = Pin()
    plug = Arbor(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(0, Bound(lambda turn, a, b: 90 * cleared(a) * cleared(b),
                        reads=(p1.lift, p2.lift)))))

    twist.drives(plug.turn, ratio=1.0)

    def render(self):
        self.p2.translate([7.2, 0.0, 0.0])
        self.plug.translate([0.0, -20.0, 0.0])


class DriverGateBody(AssemblyNode):
    """A `Bound` reading a DRIVER of the same class, on a CLASS-declared
    joint of the root.

    The gate stands open at `2`; the tick that closes it past `1` while
    the push turns the spindle stops both -- the push because its own
    motion carries the constraint outward, the gate because closing it
    does.
    """

    push = Driver(default=0.0, unit='deg')
    gate = Driver(default=2.0)

    spin = Revolute(axis=(0, 0, 1), unit='deg',
                    range=(None, Bound(lambda spin, gate: 90 * (gate >= 1),
                                       reads=(gate,))))

    block = Block()

    push.drives(spin, ratio=1.0)

    def render(self):
        self.block.translate([0.0, 0.0, 10.0])


class DriverGate(DriverGateBody):
    time = Time.running()
