# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The FREEZE fixture: what the Curta's off-rest interlocks actually
say.

`lock.py` keeps the requirement note's sketch, which forbids a selector
to STAND anywhere but zero while the crank is off rest. The mechanism
forbids something else: the selector may not MOVE while the crank is off
rest. A freeze is stated by letting BOTH bounds read the coordinate's own
committed value --

    low  = travel * (1 - rest(turn))
    high = travel + (SPAN - travel) * rest(turn)

-- so at rest the pair is `(0, SPAN)` and the knob is free, and off rest
both bounds evaluate to the value the coordinate HELD when the request
started, so the knob may not move in either direction while the crank,
whose own motion leaves the level flat, runs free.

This is the ACCEPTANCE fixture of the change
``a-bound-stops-the-request`` (design section 4). Every expected value in
the tests is computed BY HAND.
"""

from solid_node.math import floor
from solid_node.motion.joints import Bound, Prismatic
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, State

from .lock import SPAN, STEP, counted, strokes
from .parts import Dial, Slide


def rest(turn):
    """Whether the crank stands at rest: less than one degree into its
    own revolution. Written over `solid_node.math`, so it reads a number
    and a symbol alike."""
    return turn - 360 * floor(turn / 360) < 1


class Freeze(AssemblyNode):
    """`Lock`'s machine with the correction: the same crank, the same
    selector, the same state and the same commit, and a knob that is
    FROZEN off rest rather than forbidden to stand anywhere but zero."""

    crank = Driver(default=0.0, unit='deg')
    selector = Driver(default=0.0, unit='digit')
    count = State(default=0, dtype=int)

    crank_dial = Dial()
    knob = Slide(travel=Prismatic(
        axis=(0, 1, 0), unit='mm',
        range=(Bound(lambda travel, turn: travel * (1 - rest(turn)),
                     reads=(crank_dial.turn,)),
               Bound(lambda travel, turn: travel + (SPAN - travel) * rest(turn),
                     reads=(crank_dial.turn,)))))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(crank_dial.turn)
    selector.drives(knob.travel, ratio=STEP)
