# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The OUTSIDE fixture: a bank standing OUTSIDE a bound.

A `Bound` whose reads hold no value at the pose that made the bank is not
judged by the enumeration at all -- the joints capability's own rule,
older than this change -- so a `state=` may stand a bounded coordinate
beyond its bound. The clocked chain gives the unbound read its rest
CONSTANT, so the clocked level is a real one, and the direction test is
what keeps the machine operable there: it may move freely as long as it
does not go FURTHER outside, and it may return (OpenSpec change
``a-bound-stops-the-request``, design sections 3 and 7).

Nothing is ever clamped and nothing is silently repaired.
"""

from solid_node.math import floor
from solid_node.motion.joints import Bound, Prismatic
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, State

from .parts import Dial, Plate, Slide


#: Where the slide's bound stands when the plate rests at zero.
LIMIT = 9.0


def strokes(sources, targets):
    return lambda crank, count: floor(crank / 360)


def counted(sources, targets):
    return lambda crank, count: count + 1


class Outside(AssemblyNode):
    """A feed driving a slide whose upper bound reads a plate NOTHING
    binds. The plate is declared first, because a body can only read
    what it has already named."""

    crank = Driver(default=0.0, unit='deg')
    feed = Driver(default=0.0, unit='mm')
    count = State(default=0, dtype=int)

    dial = Dial()
    plate = Plate()
    slide = Slide(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(None, Bound(lambda travel, lift: LIMIT - lift,
                           reads=(plate.lift,)))))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(dial.turn)
    feed.drives(slide.travel)
