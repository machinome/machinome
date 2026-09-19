# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The REGISTER fixture: a two-digit counter with carry.

One crank, two states, one committing relation and two ordinary
relations posing the dials from the states. It is the shape the Curta's
stroke commit has -- a level built on the crank's own revolutions, an
integer law over the registers as they stood at the start of the stroke
-- with the machine's arithmetic replaced by the smallest thing that
carries.

Every expected value in the tests is computed BY HAND. The law below is
never called to produce one: a test that asked the implementation what
the answer is would pass whatever the implementation did.

The variants beside it are independent classes rather than subclasses on
purpose: a bare committing relation is ADDITIVE under inheritance,
exactly as a bare `drives` is, so a subclass restating one would state
TWO relations on one state and be refused -- which is a refusal of its
own and not a way to write a variant.
"""

from machinome.math import floor, max as sym_max
from machinome.node import AssemblyNode
from machinome.simulation import Driver, State

from .parts import Dial


#: Design degrees of dial rotation per digit.
DIGIT = 36.0


def strokes(sources, targets):
    """The event level: which completed revolution of the crank the
    machine stands in. One jump node, `floor`, which is what makes the
    crossings SOLVED rather than searched."""
    return lambda crank, units, tens: floor(crank / 360)


def backwards(sources, targets):
    """The same level negated: it RISES as the crank falls, which is how
    a mechanism that commits on the other edge states it (design
    section 6)."""
    return lambda crank, units, tens: floor(-crank / 360)


def kinked(sources, targets):
    """A KINKED level: affine on each side of its own breakpoint, and
    solved there rather than searched, `max` being a continuous
    selection and not a jump."""
    return lambda crank, units, tens: floor(sym_max(crank, 0.0) / 360)


def advance(sources, targets):
    """The commit: the two registers after one stroke, read from the two
    registers as they stood BEFORE it.

    Made of jumps and integer arithmetic throughout -- `%` and a
    comparison -- which is exactly the shape a RUNNING law is refused
    for and a commit law is admitted for, because a commit is evaluated
    at one point and never integrated.
    """
    return lambda crank, units, tens: (
        (units + 1) % 10,
        (tens + (units == 9)) % 10,
    )


class Counter(AssemblyNode):
    """A crank, a units register, a tens register, and two dials."""

    crank = Driver(default=0, unit='deg')
    units = State(default=0, range=(0, 9), dtype=int)
    tens = State(default=0, range=(0, 9), dtype=int)

    units_dial = Dial()
    tens_dial = Dial()

    (crank & units & tens).commits((units, tens), at=strokes, law=advance)

    units.drives(units_dial.turn, ratio=DIGIT)
    tens.drives(tens_dial.turn, ratio=DIGIT)


class Reverse(AssemblyNode):
    """The counter whose event is the crank's BACKWARD revolution."""

    crank = Driver(default=0, unit='deg')
    units = State(default=0, range=(0, 9), dtype=int)
    tens = State(default=0, range=(0, 9), dtype=int)

    units_dial = Dial()
    tens_dial = Dial()

    (crank & units & tens).commits((units, tens), at=backwards, law=advance)

    units.drives(units_dial.turn, ratio=DIGIT)
    tens.drives(tens_dial.turn, ratio=DIGIT)


class KinkedCounter(AssemblyNode):
    """The counter whose level is kinked at `crank == 0`."""

    crank = Driver(default=0, unit='deg')
    units = State(default=0, range=(0, 9), dtype=int)
    tens = State(default=0, range=(0, 9), dtype=int)

    units_dial = Dial()
    tens_dial = Dial()

    (crank & units & tens).commits((units, tens), at=kinked, law=advance)

    units.drives(units_dial.turn, ratio=DIGIT)
    tens.drives(tens_dial.turn, ratio=DIGIT)


class Stateless(AssemblyNode):
    """The counter's twin with no state at all: one driver posing one
    dial, and the model every zero-behaviour-change assertion is made
    over."""

    crank = Driver(default=0, unit='deg')

    units_dial = Dial()

    crank.drives(units_dial.turn, ratio=1.0)
