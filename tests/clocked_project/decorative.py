# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The DECORATIVE fixture: a ranged joint NOTHING binds.

Between "no relation determines this coordinate" and "the author's own
`simulate()` binds it" sits a third case the construction refusals must
not swallow: a decorative range on a part that simply rests. No
relation, no wiring, no derived formula and no author code reaches
`plate.lift`, so the enumeration never records a binding to judge and the
clocked compile takes it as the CONSTANT it is -- examined by no request,
stopping nothing, costing nothing (OpenSpec change
``a-bound-stops-the-request``, design section 3).

`Untouchable` states the same thing from a rest value the declared pair
does NOT contain: an unbound coordinate stands at zero, `(2, 5)` does not
contain zero, and this is still not a refusal, because nothing ever bound
it.
"""

from solid_node.math import floor
from solid_node.motion.joints import Prismatic
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, State

from .parts import Dial, Plate


def strokes(sources, targets):
    return lambda crank, count: floor(crank / 360)


def counted(sources, targets):
    return lambda crank, count: count + 1


class Decorative(AssemblyNode):
    """A clocked machine with a decorative range on a plate that rests."""

    crank = Driver(default=0.0, unit='deg')
    count = State(default=0, dtype=int)

    dial = Dial()
    plate = Plate(lift=Prismatic(axis=(0, 0, 1), unit='mm', range=(0, 5)))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(dial.turn)


class Untouchable(AssemblyNode):
    """The same, with the declared pair placed where the rest value is
    not: still admitted, and still stopping nothing."""

    crank = Driver(default=0.0, unit='deg')
    count = State(default=0, dtype=int)

    dial = Dial()
    plate = Plate(lift=Prismatic(axis=(0, 0, 1), unit='mm', range=(2, 5)))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(dial.turn)
