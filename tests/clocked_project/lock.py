# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The LOCK fixture: the requirement note's interlock sketch, AS
WRITTEN.

`workflow/docs/clocked-machine.md` sketches a selector interlock as

    setting = Prismatic(..., range=(0, Bound(
        lambda setting, crank: 54 * (phase(crank) < 1), reads=(crank_turn,))))

which says a selector may be anywhere between 0 and 54 while the crank
rests and must be at ZERO the moment it leaves rest. That is not what
the Curta does: a Curta with a selector set to 18 and the crank half way
through a stroke is every mid-stroke pose there is. The sketch is kept
here DELIBERATELY, because it is the fixture that demonstrates the
correction -- with the knob set it stops the CRANK at phase 1, which is
the behaviour the machine must not have (OpenSpec change
``a-bound-stops-the-request``, design section 4).

`freeze.py` is the same machine with the correction. Every expected
value in the tests is computed BY HAND.
"""

from solid_node.math import floor, max as sym_max
from solid_node.motion.joints import Bound, Prismatic
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, State

from .parts import Dial, Slide


#: Design millimetres of knob travel per digit of the selector.
STEP = 6.0

#: The selector's whole travel, in millimetres: nine digits of `STEP`.
SPAN = 54.0

#: Where the kinked fixture's `max` turns over, in crank degrees.
KINK = 30.0


def strokes(sources, targets):
    """The event: which completed revolution of the crank we stand in.
    Cycle 1's own level, so the fixture's events are not new."""
    return lambda crank, count: floor(crank / 360)


def counted(sources, targets):
    """The commit: one more completed stroke."""
    return lambda crank, count: count + 1


class Lock(AssemblyNode):
    """The note's sketch. The crank dial is declared BEFORE the knob,
    because a body can only read what it has already named."""

    crank = Driver(default=0.0, unit='deg')
    selector = Driver(default=0.0, unit='digit')
    count = State(default=0, dtype=int)

    crank_dial = Dial()
    knob = Slide(travel=Prismatic(
        axis=(0, 1, 0), unit='mm',
        range=(0, Bound(
            lambda travel, turn: SPAN * (turn - 360 * floor(turn / 360) < 1),
            reads=(crank_dial.turn,)))))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(crank_dial.turn)
    selector.drives(knob.travel, ratio=STEP)


class Kinked(AssemblyNode):
    """A level KINKED by `max` in the driver that moves it: the crank
    carries the knob's bound down only once it is past the kink, so the
    stop lies on the far sub-piece and is solved at one division there
    rather than searched (design section 5).

    With the knob at 18 mm the bound is `SPAN - max(turn, KINK)`, which
    stands at 24 mm until the crank reaches 30 degrees and then falls
    with it: the knob's 18 mm is reached at exactly 36 degrees.
    """

    crank = Driver(default=0.0, unit='deg')
    selector = Driver(default=0.0, unit='digit')
    count = State(default=0, dtype=int)

    crank_dial = Dial()
    knob = Slide(travel=Prismatic(
        axis=(0, 1, 0), unit='mm',
        range=(None, Bound(lambda travel, turn: SPAN - sym_max(turn, KINK),
                           reads=(crank_dial.turn,)))))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(crank_dial.turn)
    selector.drives(knob.travel, ratio=STEP)
