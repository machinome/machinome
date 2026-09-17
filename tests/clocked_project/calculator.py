# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The CURTA-SHAPED fixture: every interaction the corpus needs, at once.

The originating project is `projects/Calculators/Curta-Type-I-3x`. The
fixtures of cycles 1 to 3 each carry ONE shape -- a stroke, a clearing
reach, a ratchet, a freeze -- and the cases a second runtime gets wrong
are the INTERACTIONS: a clip and a commit in one request, a clearing
surface that moves with the state it writes while an interlock holds, a
chain that has to traverse an intermediate port to reach a bound. This
fixture carries all of them together (OpenSpec change
``publish-the-clocked-machine``, design section 17).

Nothing here is the Curta: the arithmetic is a plain four-digit add with
carry, the clearing geometry is four evenly spaced racks, and the
interlocks are `pawl.py`'s ratchet and `freeze.py`'s off-rest freeze
written over this machine's own crank. FOUR wheels rather than
seventeen is a corpus-size choice: the seventeenth wheel exercises
nothing the fourth does not, and every scenario here is replayed by a
second runtime.

Every expected value in the tests is computed BY HAND; the laws below
are never called to produce one.

The classes BESIDE `Calculator` are the shapes the conformance corpus
must exercise and no fixture of cycles 1 to 3 has: a `ceil` event, a
`sign` event, and two relations writing ONE state at ONE landing. They
are added HERE rather than by editing a fixture whose own cycle's tests
say what it means.
"""

from solid_node.math import ceil, floor, sign
from solid_node.motion.joints import Bound, Prismatic, Revolute
from solid_node.motion.ports import TranslationalPort
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, Instruction, State

from .freeze import rest
from .parts import Dial, Plate, Slide
from .register import DIGIT, Wheel


#: Ring degrees before the first wheel's rack.
START = 10.0

#: Ring degrees per digit a wheel stands at.
PITCH = 4.0

#: Ring degrees between one wheel's rack and the next.
SPAN = 100.0

#: Design millimetres of knob travel per digit of the selector.
STEP = 6.0

#: The knob's whole travel, in millimetres: nine digits of `STEP`.
TRAVEL = 54.0

#: The ratchet's tooth pitch, in degrees of the crank dial. Exactly
#: representable, so a test can name a seated tooth as a float.
TOOTH = 6.0

#: Millimetres of feed per event of the halving relation. A hundred, so
#: the division is exact at every value a test names.
PACE = 100.0


def strokes(sources, targets):
    """The stroke event: which completed revolution of the crank the
    machine stands in. One jump node, `floor`."""
    return lambda crank, operand, d0, d1, d2, d3: floor(crank / 360)


def add(sources, targets):
    """The stroke commit: the whole four-digit register plus the
    operand, read from the register as it stood BEFORE the stroke.

    The carry is inside the arithmetic, where a real machine's is inside
    its gearing; the tests compute it by hand. A `%` over a NEGATIVE
    total is reachable from here -- `operand` declares `range=(0, 9)`,
    which is presentation and clamps nothing -- and that is what makes
    the published law's remainder a question the corpus asks.
    """
    def law(crank, operand, d0, d1, d2, d3):
        total = d0 + 10 * d1 + 100 * d2 + 1000 * d3 + operand
        return (total % 10,
                floor(total / 10) % 10,
                floor(total / 100) % 10,
                floor(total / 1000) % 10)

    return law


def reach(place):
    """The clearing event for ONE wheel: the ring has swept far enough
    to reach its rack, which moves with the digit the wheel stands at.

    `clearing.py`'s shape, one rack per wheel: a wheel standing HIGH is
    reached early, and a wheel already at zero is reached last.
    """
    def factory(sources, targets):
        return lambda ring, digit: ring >= (START + SPAN * place
                                            + PITCH * (10 - digit))

    return factory


def clear(place):
    """The clearing commit for ONE wheel: zero once its rack is reached,
    and what it held before until then."""
    def factory(sources, targets):
        return lambda ring, digit: digit * (ring < (START + SPAN * place
                                                    + PITCH * (10 - digit)))

    return factory


def paces(sources, targets):
    """The halving event: which completed `PACE` of the feed we stand
    in."""
    return lambda feed, halved: floor(feed / PACE)


def halves(sources, targets):
    """The halving commit: an ODD whole number of native units divided
    by two, so the value written lands EXACTLY halfway between two whole
    units every time.

    `State.committed` takes the nearest whole native unit and an exact
    half to the EVEN one, so the banked values walk 2, 2, 4, 4, 6 -- a
    consumer reaching for a rounding that takes a half toward positive
    infinity, or away from zero, fails on the second of each pair.
    """
    return lambda feed, halved: (floor(feed / PACE) * 2 + 1) / 2


def past(sources, targets):
    """A comparison event: the crank has reached half a revolution."""
    return lambda crank, count: crank >= 180


def bump(sources, targets):
    return lambda crank, count: count + 1


def doubled(sources, targets):
    return lambda crank, count: count + 2


def ceilings(sources, targets):
    """A `ceil` event: the revolution the crank is WITHIN, which steps
    up the instant the crank leaves one."""
    return lambda crank, count: ceil(crank / 360)


def signs(sources, targets):
    """A `sign` event: the shuttle crossing its own centre."""
    return lambda shuttle, count: sign(shuttle)


class Calculator(AssemblyNode):
    """Four wheels of one class, two writers per digit, a selector wired
    through an intermediate PORT, an anti-reversal ratchet and an
    off-rest freeze.

    The crank dial is declared BEFORE the knob, because a class body can
    only read what it has already named.
    """

    crank = Driver(default=0, unit='deg')
    ring = Driver(default=0.0, unit='deg')
    operand = Driver(default=1, range=(0, 9), dtype=int)
    setting = Driver(default=0.0, unit='digit')
    feed = Driver(default=0.0, unit='mm')

    halved = State(default=0, dtype=int)

    #: The Curta's own instruction on this fixture's crank, and its
    #: ABSOLUTE twin. Under a clocked root each is ONE REQUEST -- `by`
    #: a `move` BY that travel, `targets` a `move` TO that value -- so
    #: the corpus pins what a BUTTON does and not merely that one
    #: exists (OpenSpec change ``play-the-instruction``, design section
    #: 8). `Stroke` crosses a stroke event on its way, so the recorded
    #: step carries commits; `Set four` lands an `int`-typed driver
    #: through `native()`.
    instructions = {
        'Stroke': Instruction(by={'crank': 360.0}, duration=2.0),
        'Set four': Instruction({'operand': 4}, duration=0.5),
    }

    w0 = Wheel()
    w1 = Wheel()
    w2 = Wheel()
    w3 = Wheel()

    #: The RATCHET: a one-argument bound on the crank dial's own
    #: coordinate, read at the value it HELD when the request started,
    #: so the tooth is the tooth the request began on (`pawl.py`).
    crank_dial = Dial(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(lambda turn: TOOTH * floor(turn / TOOTH), None)))

    #: The selector reaches the knob through a PLAIN PORT, which is how
    #: the Curta's selectors are wired -- and what makes the knob's
    #: chain a composition the published document must have traversed.
    shaft = TranslationalPort(unit='mm')

    #: The FREEZE: both bounds read the coordinate's own committed
    #: value, so at rest the pair is `(0, TRAVEL)` and off rest the knob
    #: may not move in either direction (`freeze.py`).
    knob = Slide(travel=Prismatic(
        axis=(0, 1, 0), unit='mm',
        range=(Bound(lambda travel, turn: travel * (1 - rest(turn)),
                     reads=(crank_dial.turn,)),
               Bound(lambda travel, turn: (travel
                                           + (TRAVEL - travel) * rest(turn)),
                     reads=(crank_dial.turn,)))))

    (crank & operand & w0.digit & w1.digit & w2.digit & w3.digit).commits(
        (w0.digit, w1.digit, w2.digit, w3.digit), at=strokes, law=add)

    (ring & w0.digit).commits(w0.digit, at=reach(0), law=clear(0))
    (ring & w1.digit).commits(w1.digit, at=reach(1), law=clear(1))
    (ring & w2.digit).commits(w2.digit, at=reach(2), law=clear(2))
    (ring & w3.digit).commits(w3.digit, at=reach(3), law=clear(3))

    (feed & halved).commits(halved, at=paces, law=halves)

    crank.drives(crank_dial.turn)
    setting.drives(shaft)
    shaft.drives(knob.travel, ratio=STEP)


#: Where `Standing`'s slide is admitted from, in millimetres. Its rest
#: pose is BELOW it, and the enumeration never judged that: a `Bound`
#: whose reads hold no value at the pose that made the bank is not
#: judged at all (`outside.py`).
FLOOR = 3.0


def strokes_alone(sources, targets):
    return lambda crank, count: floor(crank / 360)


class Standing(AssemblyNode):
    """A bank standing OUTSIDE a bound, which a request moves back
    INSIDE.

    `outside.py` has the shape -- a `Bound` reading a plate NOTHING
    binds, so the chain gives it the rest constant and the clocked level
    is a real one -- with the bound placed so the rest pose is outside
    it rather than inside. The machine may move freely as long as it
    does not go FURTHER outside, and it may RETURN; nothing is ever
    clamped and nothing is silently repaired.

    The plate is declared first, because a body can only read what it
    has already named.
    """

    crank = Driver(default=0.0, unit='deg')
    feed = Driver(default=0.0, unit='mm')
    count = State(default=0, dtype=int)

    dial = Dial()
    plate = Plate()
    slide = Slide(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(Bound(lambda travel, lift: FLOOR + lift,
                     reads=(plate.lift,)), None)))

    (crank & count).commits(count, at=strokes_alone, law=bump)

    crank.drives(dial.turn)
    feed.drives(slide.travel)


class Ceiling(AssemblyNode):
    """A `ceil` event, which no fixture of cycles 1 to 3 states."""

    crank = Driver(default=0.0, unit='deg')
    count = State(default=0, dtype=int)

    dial = Dial()

    (crank & count).commits(count, at=ceilings, law=bump)

    crank.drives(dial.turn)


class Signed(AssemblyNode):
    """A `sign` event, which no fixture of cycles 1 to 3 states: a
    shuttle that starts on one side of its centre and crosses it."""

    shuttle = Driver(default=-5.0, unit='mm')
    count = State(default=0, dtype=int)

    slide = Slide()

    (shuttle & count).commits(count, at=signs, law=bump)

    shuttle.drives(slide.travel)


class Conflict(AssemblyNode):
    """Two committing relations writing ONE state at ONE landing.

    A state may be written at several DIFFERENT events, and has one
    answer at each; two answers at one landing refuse the REQUEST and
    commit nothing.
    """

    crank = Driver(default=0.0, unit='deg')
    count = State(default=0, dtype=int)

    dial = Dial()

    (crank & count).commits(count, at=past, law=bump)
    (crank & count).commits(count, at=past, law=doubled)

    crank.drives(dial.turn)
