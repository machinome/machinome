# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A machine whose dependencies are SELECTED by where one of its own
parts stands.

The originating project is `projects/Calculators/Curta-Type-I-3x`,
branch `direct-operation`, checkpoint `6a00abe`, and the requirement is
recorded whole in `workflow/docs/curta-shifted-carry-association.md`.
The Curta's carry levers belong to the FIXED frame and its number dials
ride on the CARRIAGE, so the same lever is tripped by dial `s` and
advances dial `s + 1`, where `s` is the carriage position the maker
chose. At any one position the active dependencies are a chain; their
UNION over the positions is cyclic, and the union is what a running
program orders.

`ShiftedCarry` is the note's own reduced fixture, copied from that
project's `simulation/tools/shifted_carry_probe.py`: two wheels, one
fixed lever and a live `shift`, every association written as a mutually
exclusive comparison factor. `FixedZero` and `FixedOne` are its GROUND
TRUTH twins -- the same three laws with `shift` replaced by the literal
`0` and the literal `1` -- which compile as ordinary acyclic programs
and which the selected machine must agree with, coordinate for
coordinate.

The rest of the module is one machine per refusal the change states, and
the Curta-shaped fixture `Carriage` with four dials, three levers, a
carriage joint driven through a ratio, a lift that disengages every
association, and an interlock that refuses a shift unless lifted.
"""

from machinome.math import floor, sign
from machinome.motion.joints import Bound, Prismatic, Revolute
from machinome.motion.ports import RotationalPort, Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver

from ..running_project.parts import Arbor, Block, Carriage as Slide


#: Where the lever counts as SET, in its own travel units, and where it
#: has travelled far enough to stop being pushed.
SET = 0.5
FULL = 1.0

#: Where the clearing rack counts as engaged on a wheel's own retained
#: angle -- the ADR-121 self-read every relation of the reduced fixture
#: carries.
CLEARED = 0.5

#: Degrees of carriage travel per working position of the Curta-shaped
#: fixture, and how many positions it has.
CARRIAGE = 20.0
POSITIONS = 4


##############################################
# 1.1 The reduced fixture, and its frozen twins


def lower_law(sources, target):
    """The lower wheel: turned by the crank only while the carriage is
    at position 0, and returned by its own clearing rack through an
    ADR-121 read of its own angle."""
    return lambda crank, shift, clearing, own: \
        crank * (shift < 0.5) + clearing * (own > CLEARED)


def higher_law(sources, target):
    """The higher wheel: turned by the crank directly at position 1, by
    the crank THROUGH THE LEVER at position 0, and returned by its own
    rack."""
    return lambda crank, shift, clearing, latch, own: \
        crank * (shift >= 0.5) + crank * (shift < 0.5) * (latch >= SET) \
        + clearing * (own > CLEARED)


def carry_law(sources, target):
    """The fixed lever: tripped by whichever wheel the carriage has
    brought under it, and pushed no further once it is home."""
    return lambda lower, higher, shift, own: \
        (lower * (shift < 0.5) + higher * (shift >= 0.5)) * (own < FULL)


class ShiftedCarryBody(AssemblyNode):
    """The note's reduced fixture, with no time base of its own."""

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)
    clearing = Driver(default=0.0, unit='deg')

    lower = Arbor()
    higher = Arbor()
    carry = Slide()

    (crank & shift & clearing & lower.turn).drives(lower.turn,
                                                   law=lower_law)
    (crank & shift & clearing & carry.travel & higher.turn).drives(
        higher.turn, law=higher_law)
    (lower.turn & higher.turn & shift & carry.travel).drives(carry.travel,
                                                            law=carry_law)

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])
        self.carry.translate([0.0, 30.0, 0.0])

    def simulate(self):
        if self.lower.turn.value is None:
            self.lower.turn = 0.0
        if self.higher.turn.value is None:
            self.higher.turn = 0.0
        if self.carry.travel.value is None:
            self.carry.travel = 0.0


class ShiftedCarry(ShiftedCarryBody):
    """The same machine, running: the union the compiler refuses
    today."""

    time = Time.running()


class LoopingShiftedCarry(ShiftedCarryBody):
    """The same machine under a LOOPING base: nothing this change does
    may reach it."""

    time = Time(loop=4.0)


class FrozenBody(AssemblyNode):
    """What `ShiftedCarryBody` is with the carriage nailed down, minus
    the laws, so the two frozen twins share their parts."""

    crank = Driver(default=0.0, unit='deg')
    clearing = Driver(default=0.0, unit='deg')

    lower = Arbor()
    higher = Arbor()
    carry = Slide()

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])
        self.carry.translate([0.0, 30.0, 0.0])

    def simulate(self):
        if self.lower.turn.value is None:
            self.lower.turn = 0.0
        if self.higher.turn.value is None:
            self.higher.turn = 0.0
        if self.carry.travel.value is None:
            self.carry.travel = 0.0


class FixedZero(FrozenBody):
    """The GROUND TRUTH at `shift == 0`: the same three laws with the
    comparison factors replaced by the literals they read there, which
    the framework orders correctly today."""

    time = Time.running()

    (FrozenBody.crank & FrozenBody.clearing & FrozenBody.lower.turn).drives(
        FrozenBody.lower.turn,
        law=lambda sources, target: lambda crank, clearing, own:
        crank + clearing * (own > CLEARED))
    (FrozenBody.crank & FrozenBody.clearing & FrozenBody.carry.travel
     & FrozenBody.higher.turn).drives(
        FrozenBody.higher.turn,
        law=lambda sources, target: lambda crank, clearing, latch, own:
        crank * (latch >= SET) + clearing * (own > CLEARED))
    (FrozenBody.lower.turn & FrozenBody.carry.travel).drives(
        FrozenBody.carry.travel,
        law=lambda sources, target: lambda lower, own: lower * (own < FULL))


class FixedOne(FrozenBody):
    """The GROUND TRUTH at `shift == 1`."""

    time = Time.running()

    (FrozenBody.crank & FrozenBody.clearing & FrozenBody.lower.turn).drives(
        FrozenBody.lower.turn,
        law=lambda sources, target: lambda crank, clearing, own:
        clearing * (own > CLEARED))
    (FrozenBody.crank & FrozenBody.clearing
     & FrozenBody.higher.turn).drives(
        FrozenBody.higher.turn,
        law=lambda sources, target: lambda crank, clearing, own:
        crank + clearing * (own > CLEARED))
    (FrozenBody.higher.turn & FrozenBody.carry.travel).drives(
        FrozenBody.carry.travel,
        law=lambda sources, target: lambda higher, own:
        higher * (own < FULL))


##############################################
# 1.3 The refusal fixtures


class Unconditional(AssemblyNode):
    """The reduced fixture with its SELECTIONS removed and its ADR-121
    self-reads KEPT: an unconditional cycle, which reaches `_ordered`
    today and prints today's cycle message verbatim."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    clearing = Driver(default=0.0, unit='deg')

    lower = Arbor()
    higher = Arbor()
    carry = Slide()

    (crank & clearing & carry.travel & higher.turn).drives(
        higher.turn,
        law=lambda sources, target: lambda crank, clearing, latch, own:
        crank * (latch >= SET) + clearing * (own > CLEARED))
    (lower.turn & higher.turn & carry.travel).drives(
        carry.travel,
        law=lambda sources, target: lambda lower, higher, own:
        (lower + higher) * (own < FULL))

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.lower.turn.value is None:
            self.lower.turn = 0.0
        if self.higher.turn.value is None:
            self.higher.turn = 0.0
        if self.carry.travel.value is None:
            self.carry.travel = 0.0


class UnconditionalBare(AssemblyNode):
    """The same unconditional cycle with the SELF-READS also removed:
    `DoublyBound` from the rest render today, refused by the COMPILE
    after this change."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')

    lower = Arbor()
    higher = Arbor()
    carry = Slide()

    (crank & carry.travel).drives(
        higher.turn,
        law=lambda sources, target: lambda crank, latch: crank + latch)
    (lower.turn & higher.turn).drives(
        carry.travel,
        law=lambda sources, target: lambda lower, higher: lower + higher)

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.lower.turn.value is None:
            self.lower.turn = 0.0
        if self.higher.turn.value is None:
            self.higher.turn = 0.0
        if self.carry.travel.value is None:
            self.carry.travel = 0.0


class SelectedBareBody(AssemblyNode):
    """The reduced fixture's SELECTED cycle with every self-read
    removed, and NO time base of its own: under any base but the running
    one the same relations are what they are today, `DoublyBound` from
    the rest render.

    `lower.turn` is determined at rest by a relation OUTSIDE the block,
    so it carries no rest guard; the block's own two driven ends do."""

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)

    lower = Arbor()
    higher = Arbor()
    carry = Slide()

    (crank & shift).drives(
        lower.turn,
        law=lambda sources, target: lambda crank, shift: crank * (shift < 0.5))
    (crank & shift & carry.travel).drives(
        higher.turn,
        law=lambda sources, target: lambda crank, shift, latch:
        crank * (shift >= 0.5) + crank * (shift < 0.5) * (latch >= SET))
    (lower.turn & higher.turn & shift).drives(
        carry.travel,
        law=lambda sources, target: lambda lower, higher, shift:
        lower * (shift < 0.5) + higher * (shift >= 0.5))

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.higher.turn.value is None:
            self.higher.turn = 0.0
        if self.carry.travel.value is None:
            self.carry.travel = 0.0


class SelectedBare(SelectedBareBody):
    """The same machine, running: `DoublyBound` today, ADMITTED after
    this change."""

    time = Time.running()


class SelectedUnguarded(AssemblyNode):
    """`SelectedBare` with no rest default anywhere: a block relation
    binds nothing at rest, so the run refuses by name."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)

    lower = Arbor()
    higher = Arbor()
    carry = Slide()

    (crank & shift).drives(
        lower.turn,
        law=lambda sources, target: lambda crank, shift: crank * (shift < 0.5))
    (crank & shift & carry.travel).drives(
        higher.turn,
        law=lambda sources, target: lambda crank, shift, latch:
        crank * (shift >= 0.5) + crank * (shift < 0.5) * (latch >= SET))
    (lower.turn & higher.turn & shift).drives(
        carry.travel,
        law=lambda sources, target: lambda lower, higher, shift:
        lower * (shift < 0.5) + higher * (shift >= 0.5))

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])

    def simulate(self):
        return


class SignGated(AssemblyNode):
    """A cycle whose only gate is a `sign`, whose zero branch is ONE
    POINT and not an interval: no source is switched and the
    unconditional cycle stands."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)

    lower = Arbor()
    higher = Arbor()

    (crank & shift & higher.turn).drives(
        lower.turn,
        law=lambda sources, target: lambda crank, shift, higher:
        crank + higher * sign(shift))
    (crank & shift & lower.turn).drives(
        higher.turn,
        law=lambda sources, target: lambda crank, shift, lower:
        crank + lower * sign(0.0 - shift))

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.lower.turn.value is None:
            self.lower.turn = 0.0
        if self.higher.turn.value is None:
            self.higher.turn = 0.0


class BothActive(AssemblyNode):
    """A block whose two selections are BOTH ACTIVE at a reachable value
    of the selecting input: orderable at `shift < 0.5`, cyclic at
    `shift >= 0.5`, so the tick over that piece is refused."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)

    lower = Arbor()
    higher = Arbor()

    (crank & shift & higher.turn).drives(
        lower.turn,
        law=lambda sources, target: lambda crank, shift, higher:
        crank + higher * (shift >= 0.5))
    (crank & shift & lower.turn).drives(
        higher.turn,
        law=lambda sources, target: lambda crank, shift, lower:
        crank + lower * (shift >= 0.5))

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.lower.turn.value is None:
            self.lower.turn = 0.0
        if self.higher.turn.value is None:
            self.higher.turn = 0.0


class PortInBlock(AssemblyNode):
    """A block one of whose driven ends is a PLAIN PORT, which the run
    does not bank and which therefore keeps no history."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)

    link = RotationalPort(unit='deg')

    wheel = Arbor()

    (crank & wheel.turn).drives(
        link, law=lambda sources, target: lambda crank, wheel:
        crank + wheel * 0.5)
    (crank & shift & link).drives(
        wheel.turn, law=lambda sources, target: lambda crank, shift, link:
        crank * (shift >= 0.5) + link * (shift < 0.5))

    block = Block()

    def render(self):
        self.block.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.wheel.turn.value is None:
            self.wheel.turn = 0.0


class GroupInBlock(AssemblyNode):
    """A block member whose driven end is a GROUP: the fold that decides
    an active dependency is computed per driven end, and a group's ends
    are claimed together."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)

    lower = Arbor()
    higher = Arbor()
    carry = Slide()

    (crank & shift & carry.travel).drives(
        lower.turn & higher.turn,
        law=lambda sources, target: lambda crank, shift, latch: (
            crank * (shift < 0.5) + latch * (shift >= 0.5),
            crank * (shift >= 0.5) + latch * (shift < 0.5)))
    (lower.turn & shift).drives(
        carry.travel, law=lambda sources, target: lambda lower, shift:
        lower * (shift < 0.5))

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.lower.turn.value is None:
            self.lower.turn = 0.0
        if self.higher.turn.value is None:
            self.higher.turn = 0.0
        if self.carry.travel.value is None:
            self.carry.travel = 0.0


class WiringInBlock(AssemblyNode):
    """A cycle one of whose steps is a WIRING: the parent's own joint,
    which a relation determines, wired into a child's joint coordinate
    and carried back. A wiring carries no jump node, so no selection can
    break it."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)

    spindle = Revolute(axis=(0, 0, 1), unit='deg')

    relay = Arbor(turn=spindle)
    wheel = Arbor()

    (crank & shift & wheel.turn).drives(
        spindle, law=lambda sources, target: lambda crank, shift, wheel:
        crank + wheel * (shift < 0.5))
    (crank & shift & relay.turn).drives(
        wheel.turn, law=lambda sources, target: lambda crank, shift, relay:
        crank * (shift >= 0.5) + relay * (shift < 0.5))

    def render(self):
        self.wheel.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.spindle.value is None:
            self.spindle = 0.0
        if self.wheel.turn.value is None:
            self.wheel.turn = 0.0


class DerivedInBlock(AssemblyNode):
    """A cycle one of whose steps is a DERIVED COORDINATE, which carries
    no jump node either."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)

    hub = Revolute(axis=(0, 0, 1), unit='deg')
    tool = Revolute(axis=(0, 1, 0), unit='deg')

    reach = hub + 2 * tool

    wheel = Arbor()

    (crank & shift & wheel.turn).drives(
        hub, law=lambda sources, target: lambda crank, shift, wheel:
        crank + wheel * (shift < 0.5))
    (crank & shift & reach).drives(
        wheel.turn, law=lambda sources, target: lambda crank, shift, reach:
        crank * (shift >= 0.5) + reach * (shift < 0.5))

    body = Block()

    def render(self):
        self.wheel.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.hub.value is None:
            self.hub = 0.0
        if self.tool.value is None:
            self.tool = 0.0
        if self.wheel.turn.value is None:
            self.wheel.turn = 0.0


class UnbankedCycle(AssemblyNode):
    """A DECLARED-direction cycle that determines NO banked coordinate.

    `reach.drives(arm)` is read BACKWARD by the rest render, and the
    derived coordinate `reach = hub + 2 * arm` is then solved for `hub`,
    so the tree poses -- while the graph taken FORWARD AS DECLARED holds
    the cycle `arm -> reach -> arm`. Every coordinate on it is a plain
    port, so `_reaching_the_bank` drops both edges before the compile
    orders anything, and nothing about this change may touch the
    machine.
    """

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')

    hub = RotationalPort(unit='deg')
    arm = RotationalPort(unit='deg')

    reach = hub + 2 * arm

    wheel = Arbor()

    crank.drives(wheel.turn, ratio=2.0)
    crank.drives(arm, ratio=1.0)
    reach.drives(arm, ratio=1.0)

    body = Block()

    def render(self):
        self.body.translate([30.0, 0.0, 0.0])


##############################################
# 1.2 The Curta-shaped fixture


#: Where a lever counts as LIFTED out of engagement, in the hoist's own
#: travel units.
LIFTED = 0.5

#: Where a lever counts as RETURNED by the reset cam.
RETURNED = 0.0

#: How far a lever advances the dial beyond it, in dial degrees, and the
#: half-width of a dial's missing-tooth gap.
STEP = 36.0
GAP = 0.5

#: The dials the carriage carries and the fixed levers between them.
DIALS = 4
LEVERS = 3


def aligned(here, place, lever):
    """Whether the carriage has brought dial `place` under lever
    `lever`: a PAIR OF COMPARISONS on the carriage's own joint
    coordinate, which is what makes it a selector the compiler can see
    (design.md section 12 -- the pose model's `clamp01` hat is a CALL
    and is not a jump node at all)."""
    offset = place - lever
    return (here >= offset - 0.5) * (here < offset + 0.5)


def lever_law(index):
    """One fixed lever: tripped by whichever dial the carriage has
    brought under it, held at its stop, and returned by the reset cam --
    the last two through ADR-121 reads of its own travel."""
    def factory(sources, target):
        def law(seat, hoist, reset, d0, d1, d2, d3, own):
            here = seat / CARRIAGE
            pushed = 0.0
            for place, dial in enumerate((d0, d1, d2, d3)):
                pushed = pushed + dial * aligned(here, place, index)
            # The reset cam reaches the levers only while the carriage
            # is LIFTED, which is where a Curta clears them: with the
            # carriage down the same motion would drive the dial the
            # lever faces backwards through its own rack.
            return (pushed * (hoist < LIFTED) * (own < FULL)
                    - reset * (own > RETURNED) * (hoist >= LIFTED))
        return law
    return factory


def dial_law(place):
    """One number dial: advanced by the crank, by whichever lever the
    carriage has brought under the dial BELOW it, and returned by its own
    clearing rack through its missing-tooth gap."""
    def factory(sources, target):
        def law(crank, seat, hoist, clearing, l0, l1, l2, own):
            here = seat / CARRIAGE
            total = crank
            for index, lever in enumerate((l0, l1, l2)):
                # The lever's own TRAVEL turns the dial, through a rack:
                # a term that carries SLOPE, because a jump never moves a
                # part (ADR-107) and a carry that were only a step would
                # be subtracted away.
                total = total + STEP * lever \
                    * aligned(here, place - 1, index) * (hoist < LIFTED)
            free = own - 360.0 * floor(own / 360.0) >= 2 * GAP
            return total + clearing * free
        return law
    return factory


class CarriageBody(AssemblyNode):
    """Four dials on a carriage and three levers in the fixed frame.

    Which dial a lever reads, and which lever a dial is advanced by,
    follow the carriage's OWN joint coordinate -- not the `position`
    driver -- so the selection follows the part rather than the request.
    The `lift` disengages every association at once, and the carriage's
    declared range is an interlock: no shift unless lifted.
    """

    crank = Driver(default=0.0, unit='deg')
    position = Driver(default=0.0, unit=None)
    lift = Driver(default=0.0, unit=None)
    clearing = Driver(default=0.0, unit='deg')
    reset = Driver(default=0.0, unit=None)

    hoist = Prismatic(axis=(0, 0, 1), unit='mm')

    seat = Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(Bound(lambda turn, lift: (CARRIAGE * floor(turn / CARRIAGE)
                                         - CARRIAGE * POSITIONS
                                         * (lift >= LIFTED)),
                     reads=(hoist,)),
               Bound(lambda turn, lift: (CARRIAGE * floor(turn / CARRIAGE)
                                         + CARRIAGE * POSITIONS
                                         * (lift >= LIFTED)),
                     reads=(hoist,))))

    dial0 = Arbor()
    dial1 = Arbor()
    dial2 = Arbor()
    dial3 = Arbor()

    lever0 = Slide()
    lever1 = Slide()
    lever2 = Slide()

    lift.drives(hoist, ratio=1.0)
    position.drives(seat, ratio=CARRIAGE)

    (seat & hoist & reset & dial0.turn & dial1.turn & dial2.turn
     & dial3.turn & lever0.travel).drives(lever0.travel, law=lever_law(0))
    (seat & hoist & reset & dial0.turn & dial1.turn & dial2.turn
     & dial3.turn & lever1.travel).drives(lever1.travel, law=lever_law(1))
    (seat & hoist & reset & dial0.turn & dial1.turn & dial2.turn
     & dial3.turn & lever2.travel).drives(lever2.travel, law=lever_law(2))

    (crank & seat & hoist & clearing & lever0.travel & lever1.travel
     & lever2.travel & dial0.turn).drives(dial0.turn, law=dial_law(0))
    (crank & seat & hoist & clearing & lever0.travel & lever1.travel
     & lever2.travel & dial1.turn).drives(dial1.turn, law=dial_law(1))
    (crank & seat & hoist & clearing & lever0.travel & lever1.travel
     & lever2.travel & dial2.turn).drives(dial2.turn, law=dial_law(2))
    (crank & seat & hoist & clearing & lever0.travel & lever1.travel
     & lever2.travel & dial3.turn).drives(dial3.turn, law=dial_law(3))

    def dials(self):
        return (self.dial0, self.dial1, self.dial2, self.dial3)

    def levers(self):
        return (self.lever0, self.lever1, self.lever2)

    def render(self):
        for index, dial in enumerate(self.dials()):
            dial.translate([25.0 * index, 0.0, 0.0])
        for index, lever in enumerate(self.levers()):
            lever.translate([25.0 * index + 12.5, 20.0, 0.0])

    def simulate(self):
        for dial in self.dials():
            if dial.turn.value is None:
                dial.turn = 0.0
        for lever in self.levers():
            if lever.travel.value is None:
                lever.travel = 0.0


class CurtaCarriage(CarriageBody):
    """The same machine, running."""

    time = Time.running()


##############################################
# A landing in one piece and motion in a later one


class LandedCarry(AssemblyNode):
    """A block that LANDS a coordinate at its gate in one piece and
    drives it FURTHER in the next.

    The lever is pushed by the lower wheel only while the carriage is at
    position 0, and only until it is home -- an ADR-121 read of its own
    travel, which CUTS the path and lands it. Past the detent the higher
    wheel pushes it with no gate at all, so the tick's second piece moves
    it on. What the block reports for it is the absolute value it was
    advanced to by the stretch's END, and reporting the landing alone
    would discard the second piece's motion.
    """

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)

    lower = Arbor()
    higher = Arbor()
    carry = Slide()

    crank.drives(lower.turn, ratio=1.0)

    (crank & shift & carry.travel).drives(
        higher.turn,
        law=lambda sources, target: lambda crank, shift, latch:
        crank * (shift < 0.5) * (latch >= SET) + crank * (shift >= 0.5))
    (lower.turn & higher.turn & shift & carry.travel).drives(
        carry.travel,
        law=lambda sources, target: lambda lower, higher, shift, own:
        lower * (shift < 0.5) * (own < FULL) + higher * (shift >= 0.5))

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.higher.turn.value is None:
            self.higher.turn = 0.0
        if self.carry.travel.value is None:
            self.carry.travel = 0.0


##############################################
# Stops on a block coordinate


class RangedBlock(AssemblyNode):
    """A block one of whose coordinates declares a RANGE, and an input
    that reaches it only through a selection that may be inactive.

    `spin` turns the lower wheel and `crank` the higher one, and the
    lever is tripped by whichever the carriage has brought under it. At
    `shift == 1` the lever reads the HIGHER wheel, so `spin` is coupled
    to the stopped lever only through a term the selection has switched
    out: it is not stopped by it and admits its whole travel.
    """

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    spin = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)

    lower = Arbor()
    higher = Arbor()
    carry = Slide(travel=Prismatic(axis=(1, 0, 0), unit='mm',
                                   range=(None, 0.6)))

    spin.drives(lower.turn, ratio=1.0)

    (crank & shift & carry.travel).drives(
        higher.turn,
        law=lambda sources, target: lambda crank, shift, latch:
        crank * (shift >= 0.5) + crank * (shift < 0.5) * (latch >= SET))
    (lower.turn & higher.turn & shift).drives(
        carry.travel,
        law=lambda sources, target: lambda lower, higher, shift:
        lower * (shift < 0.5) + higher * (shift >= 0.5))

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.higher.turn.value is None:
            self.higher.turn = 0.0
        if self.carry.travel.value is None:
            self.carry.travel = 0.0


class StoppedLanding(AssemblyNode):
    """A block coordinate that a piece LANDS at its own gate and a
    setter then drives past its declared range, in one segment: the
    bound wins, as `Run._landed` running before the stops already
    decides."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    shift = Driver(default=0.0, unit=None)
    setter = Driver(default=0.0, unit='mm')

    lower = Arbor()
    higher = Arbor()
    carry = Slide(travel=Prismatic(axis=(1, 0, 0), unit='mm',
                                   range=(None, 0.6)))

    crank.drives(lower.turn, ratio=1.0)

    (crank & shift & carry.travel).drives(
        higher.turn,
        law=lambda sources, target: lambda crank, shift, latch:
        crank * (shift >= 0.5) + crank * (shift < 0.5) * (latch >= SET))
    (lower.turn & higher.turn & shift & setter & carry.travel).drives(
        carry.travel,
        law=lambda sources, target: lambda lower, higher, shift, setter, own:
        (lower * (shift < 0.5) + higher * (shift >= 0.5)) * (own < SET)
        + setter)

    def render(self):
        self.higher.translate([30.0, 0.0, 0.0])

    def simulate(self):
        if self.higher.turn.value is None:
            self.higher.turn = 0.0
        if self.carry.travel.value is None:
            self.carry.travel = 0.0
