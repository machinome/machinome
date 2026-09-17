# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""What a clocked stop cannot follow, refused BY NAME at construction.

A stop that can never stop is a mistake in the model, and the temperament
cycle 1 set for a state nothing writes is the one this change takes for a
bound the bank cannot reach (OpenSpec change
``a-bound-stops-the-request``, design section 3). Each class below is one
row of that table, written so its refusal test can quote the offending
declaration.

Two of them are refused by the REQUEST rather than by construction: a
level that steps past the crossing maximum has no fact to refuse until a
request states how far it travels.
"""

import math

from solid_node.math import floor, sin
from solid_node.motion.joints import Bound, Prismatic, Revolute
from solid_node.motion.ports import RotationalPort
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.simulation import Driver, State

from solid2 import cylinder

from .parts import Dial, Plate, Slide


def strokes(sources, targets):
    return lambda crank, count: floor(crank / 360)


def counted(sources, targets):
    return lambda crank, count: count + 1


class Belt(Solid2Node):
    """A part whose angle arrives on a PLAIN port: a calculation the
    enumeration recomputes, and never a coordinate a bound may read."""

    turn = RotationalPort(unit='deg')

    def render(self):
        return cylinder(r=6, h=2)


class HandBound(AssemblyNode):
    """A bounded coordinate the tree's OWN `simulate()` binds: nothing
    can follow it along a path, because its value is whatever that code
    computes from whatever it reads."""

    crank = Driver(default=0.0, unit='deg')
    count = State(default=0, dtype=int)

    dial = Dial()
    plate = Plate(lift=Prismatic(axis=(0, 0, 1), unit='mm', range=(0, 9)))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(dial.turn)

    def simulate(self):
        self.plate.lift = 4.0


class OpaqueChain(AssemblyNode):
    """A bounded coordinate whose chain passes through a law that is not
    an expression: `math.sin` is the standard library's, and cannot be
    applied to a symbol at all."""

    crank = Driver(default=0.0, unit='deg')
    count = State(default=0, dtype=int)

    dial = Dial()
    plate = Plate(lift=Prismatic(axis=(0, 0, 1), unit='mm', range=(0, 9)))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(dial.turn)
    crank.drives(plate.lift, law=lambda driver, driven: math.sin)


class UnreachedRead(AssemblyNode):
    """A `Bound` whose read is a coordinate the author binds by hand: the
    level cannot be evaluated without inventing a value for it."""

    crank = Driver(default=0.0, unit='deg')
    feed = Driver(default=0.0, unit='mm')
    count = State(default=0, dtype=int)

    dial = Dial()
    plate = Plate()
    slide = Slide(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(None, Bound(lambda travel, lift: 9 - lift,
                           reads=(plate.lift,)))))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(dial.turn)
    feed.drives(slide.travel)

    def simulate(self):
        self.plate.lift = 2.0


class PortRead(AssemblyNode):
    """A `Bound` whose read is a plain PORT: ADR-113's own refusal,
    unchanged. A bound reads the state, and a port is a calculation."""

    crank = Driver(default=0.0, unit='deg')
    feed = Driver(default=0.0, unit='mm')
    count = State(default=0, dtype=int)

    belt = Belt()
    slide = Slide(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(None, Bound(lambda travel, turn: 9 - turn,
                           reads=(belt.turn,)))))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(belt.turn)
    feed.drives(slide.travel)


def seated(driver, driven):
    """A law that READS the coordinate it drives: the clearing shape,
    where the rack carries a dial only as far as the next tooth."""
    return lambda clearing, turn: 6 * floor(turn / 6) + clearing


class SelfReadChain(AssemblyNode):
    """A bounded coordinate whose chain READS the coordinate it drives.
    A retained read is a HISTORY, and a clocked pose retains nothing
    between requests: there is no value to read."""

    crank = Driver(default=0.0, unit='deg')
    clearing = Driver(default=0.0, unit=None)
    count = State(default=0, dtype=int)

    dial = Dial()
    wheel = Dial(turn=Revolute(axis=(0, 0, 1), unit='deg', range=(0, 90)))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(dial.turn)
    (clearing & wheel.turn).drives(wheel.turn, law=seated)


class Curved(AssemblyNode):
    """A level that CURVES in a driver that moves it: a clocked stop is
    SOLVED and never searched, so this is refused by name."""

    crank = Driver(default=0.0, unit='deg')
    feed = Driver(default=0.0, unit='mm')
    count = State(default=0, dtype=int)

    dial = Dial()
    slide = Slide(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(None, Bound(lambda travel, turn: sin(turn),
                           reads=(dial.turn,)))))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(dial.turn)
    feed.drives(slide.travel)


class Chattering(AssemblyNode):
    """A level whose jump surfaces a long request crosses past the
    maximum: refused by the REQUEST, which commits nothing."""

    crank = Driver(default=0.0, unit='deg')
    feed = Driver(default=0.0, unit='mm')
    count = State(default=0, dtype=int)

    dial = Dial()
    slide = Slide(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(None, Bound(
            lambda travel, turn: 54 * (turn - 6 * floor(turn / 6) < 1),
            reads=(dial.turn,)))))

    (crank & count).commits(count, at=strokes, law=counted)

    crank.drives(dial.turn)
    feed.drives(slide.travel)
