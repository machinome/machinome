# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The PENDULUM fixtures: a machine with a CLOCK and memory.

The square `elapsed x memory` of ADR-125's two-axis table (OpenSpec
change ``time-without-running``, design sections 2 and 5). A bob whose
pose is a formula of elapsed seconds, and a count beside it the machine
writes when the pendulum's phase -- an expression of TIME -- crosses its
release. Events on time and events on inputs are the same kind of event.

The originating project of the clocked discipline is
`projects/Calculators/Curta-Type-I-3x`, and it is NOT owed this cycle:
the Curta has no clock. These fixtures are the evidence that the table's
open square is sayable, and nothing here costs the Curta anything.

Every expected value in the tests is computed BY HAND. The levels below
are never called to produce one.

Two spellings differ from `design.md` section 5, both deliberately and
neither a design change:

- the pose is written `A * sin(360 * t / T)` rather than
  `A * sin(2 * pi * t / T)`, because `solid_node.math.sin` takes
  DEGREES. It is the same function of time;
- `A` is the bob's amplitude in degrees and `T` its period in seconds,
  so the release level `floor((t + T / 4) / (T / 2))` rises at
  `t = T/4 + k * T/2` -- the swing's own extremes, TWICE per period,
  where an escapement releases.
"""

from solid2 import cube, cylinder

from solid_node.math import floor, sin
from solid_node.motion.joints import Prismatic, Revolute
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.simulation import Driver, State


#: The pendulum's period, in seconds. Exactly representable, and chosen
#: so every release instant a test names is an exact float.
T = 2.0

#: The bob's amplitude, in degrees.
A = 12.0

#: The first release, in seconds: a quarter period in, where the swing
#: reaches its extreme. Releases follow every `T / 2` from there.
FIRST = T / 4

#: The whole travel of the fixtures that carry a ranged lift, in
#: millimetres.
STROKE = 9.0

#: Degrees of dial rotation per counted release.
DIGIT = 36.0

#: The quarter turn a counted dial is admitted through: two releases
#: stand inside it and three do not.
QUARTER = 90.0


def release(sources, targets):
    """The event level: which half swing the pendulum stands in.

    AFFINE in the clock -- a floor over a linear function of time -- so
    its crossings are SOLVED by one division and this cycle introduces
    no tolerance (design section 5).
    """
    return lambda time, engaged, count: floor((time + T / 4) / (T / 2))


def advance(sources, targets):
    """The commit: the count after one release, read from the count as
    it stood before it. A disengaged escapement counts nothing."""
    return lambda time, engaged, count: count + engaged


def held(sources, targets):
    """The level of a relation NO DRIVER can move: every source but the
    clock is a state."""
    return lambda time, count: floor((time + T / 4) / (T / 2))


def counted(sources, targets):
    """The commit of that relation."""
    return lambda time, count: count + 1


def curved(sources, targets):
    """A CURVED level in the CLOCK: no crossing of it is solved by a
    division, so it is refused at simulation construction."""
    return lambda time, count: floor(sin(time))


def strokes(sources, targets):
    """Cycle 1's own level, on a driver: the clockless twin's event."""
    return lambda crank, count: floor(crank / 360)


def bump(sources, targets):
    return lambda crank, count: count + 1


def wobble(source, driven):
    """A law FACTORY that reads the owner's `time` at realization and
    CLOSES OVER it (design section 7).

    The one route by which a compiled chain can carry the clock: a
    factory is called once, with the realized owners, and an unbound
    read of `time` there is the symbolic animation variable. The chain
    composed for a bound over the coordinate this drives therefore
    carries a free name the bank has not got.
    """
    base = source.time
    return lambda engaged: engaged + A * base


class Bob(Solid2Node):
    """The swinging mass: ONE box on one revolute joint.

    A box and not a cylinder because the document-producer check of
    design section 6 runs `solid build` and `solid export` over `Swing`,
    and a single box is the whole of the geometry that claim needs.
    """

    swing = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cube([2, 2, 40], center=True)


class Quarter(Solid2Node):
    """A counted dial that cannot turn past a quarter."""

    turn = Revolute(axis=(0, 0, 1), unit='deg', range=(0.0, QUARTER))

    def render(self):
        return cylinder(r=10, h=3)


class Plate(Solid2Node):
    """A plate rising in its guide, bounded at the whole stroke."""

    lift = Prismatic(axis=(0, 0, 1), unit='mm', range=(0.0, STROKE))

    def render(self):
        return cube([12, 12, 3], center=True)


class Regulator(AssemblyNode):
    """ELAPSED x MEMORY: a clock, a driver, a state, and one committing
    relation whose event is located on the clock."""

    time = Time.elapsed()
    engaged = Driver(default=1, dtype=int)
    count = State(default=0, dtype=int)

    bob = Bob()

    (time & engaged & count).commits(count, at=release, law=advance)

    def simulate(self):
        self.bob.swing = A * sin(360.0 * self.time / T)


class Swing(AssemblyNode):
    """ELAPSED x NONE: `Regulator` with the state and the relation
    removed.

    Admitted and EQUIVALENT: the ordinary fixed-`dt` stepping loop runs
    over it, and its published document is the document `Untimed`
    publishes, byte for byte (design section 2).
    """

    time = Time.elapsed()
    engaged = Driver(default=1, dtype=int)

    bob = Bob()

    def simulate(self):
        self.bob.swing = A * sin(360.0 * self.time / T)


class Untimed(AssemblyNode):
    """`Swing` with no time base at all: the twin every byte-identity
    assertion is made against."""

    engaged = Driver(default=1, dtype=int)

    bob = Bob()

    def simulate(self):
        self.bob.swing = A * sin(360.0 * self.time / T)


class Clockless(AssemblyNode):
    """`Regulator`'s twin with NO time base: the clocked root of cycle
    1, whose bank has no clock, whose `sim.time` is refused and whose
    request may not name one."""

    crank = Driver(default=0.0, unit='deg')
    count = State(default=0, dtype=int)

    bob = Bob()

    (crank & count).commits(count, at=strokes, law=bump)

    def simulate(self):
        self.bob.swing = A * sin(360.0 * self.time / T)


class ClockAlone(AssemblyNode):
    """A committing relation whose ONLY moving source is the clock.

    Cycle 1 refuses a relation every source of which is a state, because
    no request could reach it. Under an elapsed root the clock is
    something a request moves, so this is ADMITTED (design section 5).
    """

    time = Time.elapsed()
    count = State(default=0, dtype=int)

    bob = Bob()

    (time & count).commits(count, at=held, law=counted)


class Curved(AssemblyNode):
    """An `at` that CURVES as the clock moves."""

    time = Time.elapsed()
    count = State(default=0, dtype=int)

    bob = Bob()

    (time & count).commits(count, at=curved, law=counted)


class Lift(AssemblyNode):
    """An elapsed clocked root carrying a ranged joint a DRIVER moves.

    The driver request is clipped at the bound and reports its stop,
    exactly as ADR-126 says; a TIME request over the same fixture is
    clipped by nothing and makes its whole travel (design section 7).
    """

    time = Time.elapsed()
    engaged = Driver(default=1, dtype=int)
    lift = Driver(default=0.0, unit='mm')
    count = State(default=0, dtype=int)

    bob = Bob()
    plate = Plate()

    (time & engaged & count).commits(count, at=release, law=advance)

    lift.drives(plate.lift)

    def simulate(self):
        self.bob.swing = A * sin(360.0 * self.time / T)


class Ranged(AssemblyNode):
    """An elapsed clocked root whose COUNT poses a bounded dial.

    A time request whose commits carry that dial past the quarter is
    refused WHOLE by the end-of-request judgement: a coordinate outside
    its declared range is an impossible pose, and nothing stopped the
    clock (design section 7).
    """

    time = Time.elapsed()
    engaged = Driver(default=1, dtype=int)
    count = State(default=0, dtype=int)

    face = Quarter()

    (time & engaged & count).commits(count, at=release, law=advance)

    count.drives(face.turn, ratio=DIGIT)


class Captured(AssemblyNode):
    """A RANGED joint driven by a relation whose law factory captured
    the clock at realization (design section 7).

    Refused at simulation construction, by name: the chain composed for
    that bound carries the animation symbol, which is not a bank id.
    """

    time = Time.elapsed()
    engaged = Driver(default=1, dtype=int)
    count = State(default=0, dtype=int)

    arm = Quarter()

    (time & engaged & count).commits(count, at=release, law=advance)

    engaged.drives(arm.turn, law=wobble)


class Swinging(AssemblyNode):
    """An ASSEMBLY below the root, whose pose reads the root's clock.

    A leaf may not read `time` at all -- the framework refuses it by
    name -- so the descendant that proves the clock reaches the whole
    tree is an assembly.
    """

    def __init__(self):
        self.tip = Bob()
        super().__init__()

    def render(self):
        return [self.tip]

    def simulate(self):
        self.tip.swing = A * sin(360.0 * self.time / T)


class Nested(AssemblyNode):
    """`Regulator` with the bob one assembly further down: the clock is
    delivered per visited assembly, so the descendant reads the banked
    seconds and not `$t` (design section 6)."""

    time = Time.elapsed()
    engaged = Driver(default=1, dtype=int)
    count = State(default=0, dtype=int)

    (time & engaged & count).commits(count, at=release, law=advance)

    def __init__(self):
        self.arm = Swinging()
        super().__init__()

    def render(self):
        return [self.arm]
