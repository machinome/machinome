# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Two committing relations on one path: when they are ONE event and
when they are TWO.

Two relations fire at one event exactly when their far-side landings are
the SAME float. No tolerance decides it -- a tolerance stated as a
fraction of the request's travel would make one long request merge what
several short requests keep apart, which is the assertion these fixtures
exist to make.

Each pair's second law READS the state the first writes, so the two
readings are told apart by the value that lands: synchronous reads see
what stood BEFORE the event, and two events in path order see what the
earlier one committed.
"""

import math

from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, State

from .parts import Dial


#: A threshold that is exactly representable, and the next float above
#: it. One ulp apart is as close as two surfaces can be without being
#: one.
T = 100.0
UP = math.nextafter(T, math.inf)


def reach_t(sources, targets):
    return lambda crank, a, b: crank >= T


def reach_up(sources, targets):
    return lambda crank, a, b: crank >= UP


def strictly_past_t(sources, targets):
    return lambda crank, a: crank > T


def reach_t_alone(sources, targets):
    return lambda crank, a: crank >= T


def bump_a_alone(sources, targets):
    return lambda crank, a: a + 1


def bump_a(sources, targets):
    """Writes `a`, reading nothing else."""
    return lambda crank, a, b: a + 1


def read_a(sources, targets):
    """Writes `b` from whatever `a` reads AT THIS EVENT: `0` where the
    two are synchronous, `1` where this event follows the one that wrote
    `a`."""
    return lambda crank, a, b: a * 10 + 1


class Pair(AssemblyNode):
    """The shared body: a crank, two states, two dials."""

    crank = Driver(default=0.0, unit='deg')
    a = State(default=0, dtype=int)
    b = State(default=0, dtype=int)

    a_dial = Dial()
    b_dial = Dial()

    a.drives(a_dial.turn, ratio=1.0)
    b.drives(b_dial.turn, ratio=1.0)


class UlpPair(Pair):
    """Surfaces ONE ULP apart: two events, in path order, the second
    reading what the first committed."""

    (Pair.crank & Pair.a & Pair.b).commits(Pair.a, at=reach_t, law=bump_a)
    (Pair.crank & Pair.a & Pair.b).commits(Pair.b, at=reach_up, law=read_a)


class SamePair(Pair):
    """Surfaces landing on ONE float: one synchronous event, both laws
    reading the bank as it stood before it."""

    (Pair.crank & Pair.a & Pair.b).commits(Pair.a, at=reach_t, law=bump_a)
    (Pair.crank & Pair.a & Pair.b).commits(Pair.b, at=reach_t, law=read_a)


class SwappedPair(Pair):
    """`SamePair` with the two lines swapped: declaration order is not
    observable at one event."""

    (Pair.crank & Pair.a & Pair.b).commits(Pair.b, at=reach_t, law=read_a)
    (Pair.crank & Pair.a & Pair.b).commits(Pair.a, at=reach_t, law=bump_a)


class Strict(AssemblyNode):
    """A STRICT comparison: the landing is the next float ABOVE the
    threshold, because the branch at the threshold is still false."""

    crank = Driver(default=0.0, unit='deg')
    a = State(default=0, dtype=int)

    a_dial = Dial()

    a.drives(a_dial.turn, ratio=1.0)

    (crank & a).commits(a, at=strictly_past_t, law=bump_a_alone)


class NonStrict(AssemblyNode):
    """A NON-STRICT comparison against the same threshold: the branch at
    the threshold is already true, so the threshold IS the landing."""

    crank = Driver(default=0.0, unit='deg')
    a = State(default=0, dtype=int)

    a_dial = Dial()

    a.drives(a_dial.turn, ratio=1.0)

    (crank & a).commits(a, at=reach_t_alone, law=bump_a_alone)
