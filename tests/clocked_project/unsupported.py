# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The clocked models a SIMULATION refuses, and the two it admits with a
consequence.

Each class here is legal at class definition -- the classes alone cannot
say what shape an `at` expression has, nor what the whole tree writes --
and refused when a simulation is constructed over it, which is the first
moment those facts exist.
"""

from solid_node.math import floor, sin
from solid_node.motion.joints import Revolute
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.simulation import Driver, Instruction, State

from .parts import Dial


def stroke(sources, targets):
    return lambda crank, value: floor(crank / 360)


def bump(sources, targets):
    return lambda crank, value: value + 1


def curved(sources, targets):
    """A CURVED level: the crank's motion bends it, so no crossing of it
    is solved by a division."""
    return lambda crank, value: floor(sin(crank))


def compound(sources, targets):
    """TWO jump nodes: one event is one surface family, and two are two
    committing relations."""
    return lambda crank, value: floor(crank / 360) + floor(crank / 180)


def remainder(sources, targets):
    """`a % b` is not integer valued, so it is not an event level."""
    return lambda crank, value: crank % 360


def arithmetic(sources, targets):
    """No jump node at all."""
    return lambda crank, value: crank / 360


def textual(sources, targets):
    """An expression carrying raw text the framework cannot evaluate: a
    SolidPython constant whose text is not an expression this framework
    parses."""
    from solid2.core.object_base import OpenSCADConstant

    return lambda crank, value: floor(
        crank / 360 + OpenSCADConstant('$mystery ? 1 : 2'))


def two_values(sources, targets):
    return lambda crank, value: (value + 1, value + 2)


class Textual(AssemblyNode):
    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=textual, law=bump)
    value.drives(face.turn, ratio=1.0)


class Curved(AssemblyNode):
    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=curved, law=bump)
    value.drives(face.turn, ratio=1.0)


class Compound(AssemblyNode):
    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=compound, law=bump)
    value.drives(face.turn, ratio=1.0)


class Remainder(AssemblyNode):
    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=remainder, law=bump)
    value.drives(face.turn, ratio=1.0)


class Arithmetic(AssemblyNode):
    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=arithmetic, law=bump)
    value.drives(face.turn, ratio=1.0)


class WrongShape(AssemblyNode):
    """One target, a law returning two values."""

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=stroke, law=two_values)
    value.drives(face.turn, ratio=1.0)


class Unwritten(AssemblyNode):
    """A state no committing relation targets."""

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    spare = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=stroke, law=bump)
    value.drives(face.turn, ratio=1.0)


class Writable(AssemblyNode):
    """A child that writes its own state."""

    digit = State(default=0, dtype=int)
    crank = Driver(default=0.0, unit='deg')
    face = Dial()

    (crank & digit).commits(digit, at=stroke, law=bump)
    digit.drives(face.turn, ratio=1.0)


class TwoWriters(AssemblyNode):
    """The root writes the child's state too: two writers for one value,
    which no single class body can see."""

    ring = Driver(default=0.0, unit='deg')
    child = Writable()

    (ring & child.digit).commits(child.digit, at=stroke, law=bump)


class Instructed(AssemblyNode):
    """An instruction naming a state among its targets."""

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    instructions = {'Reset': Instruction({'value': 0}, duration=0.0)}

    (crank & value).commits(value, at=stroke, law=bump)
    value.drives(face.turn, ratio=1.0)


class Stop(Solid2Node):
    """A dial that cannot turn past a quarter."""

    turn = Revolute(axis=(0, 0, 1), unit='deg', range=(0.0, 90.0))

    def render(self):
        from solid2 import cylinder

        return cylinder(r=10, h=3)


class Bounded(AssemblyNode):
    """A clocked model whose final pose can violate a joint range.

    Cycle 2 is what clips a request path at a bound; until then a
    violated bound is the impossible pose it has always been, raised on
    the pose the request ends at -- with every event on the WHOLE path
    already fired. This fixture RECORDS that gap rather than hiding it.
    """

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Stop()

    (crank & value).commits(value, at=stroke, law=bump)
    value.drives(face.turn, ratio=36.0)


def explode(sources, targets):
    """A law that raises once the state has reached two -- on the THIRD
    event of a request, which is where atomicity is asserted.

    It is an ordinary expression under the symbolic inspection: the
    guard tests for a NUMBER, and a symbolic token is not one.
    """
    def law(crank, value):
        if isinstance(value, (int, float)) and not isinstance(value, bool) \
                and value >= 2:
            raise RuntimeError('the third event refuses')
        return value + 1

    return law


class Exploding(AssemblyNode):
    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=stroke, law=explode)
    value.drives(face.turn, ratio=1.0)


def shadowed(sources, targets):
    """An event level over a STATE alone: nothing a request moves enters
    it, so it can never cross anything."""
    return lambda value, shadow: floor(value / 2)


def follow(sources, targets):
    return lambda value, shadow: shadow + 1


class Unreachable(AssemblyNode):
    """A committing relation NO declared driver can reach.

    Its sources are both states, so its event level is constant between
    events and no request can ever move it: it would compile with an
    empty table of levels and sit there silently, never firing. Closure 1
    (C4) refuses it at simulation construction instead.
    """

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    shadow = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=stroke, law=bump)
    (value & shadow).commits(shadow, at=shadowed, law=follow)
    value.drives(face.turn, ratio=1.0)


def bump_by_ten(sources, targets):
    return lambda crank, value: value + 10


class Conflicting(AssemblyNode):
    """Two relations writing ONE state at ONE event.

    Both levels are `floor(crank / 360)`, so both land on the same float
    on any request: two answers for one value at one event, which is the
    one thing the several-writers rule of closure 1 (C2) still refuses --
    and it refuses the REQUEST, because a class body cannot see a
    landing.
    """

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=stroke, law=bump)
    (crank & value).commits(value, at=stroke, law=bump_by_ten)
    value.drives(face.turn, ratio=1.0)


def swept(sources, targets):
    """A clearing-shaped event on a SECOND input: one event per hundred
    degrees of the ring."""
    return lambda ring, value: floor(ring / 100)


def wipe(sources, targets):
    """The clearing commit's shape: zero once the ring has reached, which
    it has by construction at the landing."""
    return lambda ring, value: value * (ring < 0)


class Apart(AssemblyNode):
    """The same two writers on two DIFFERENT inputs and two different
    events -- the Curta's own shape, and admitted."""

    crank = Driver(default=0.0, unit='deg')
    ring = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)
    face = Dial()

    (crank & value).commits(value, at=stroke, law=bump)
    (ring & value).commits(value, at=swept, law=wipe)
    value.drives(face.turn, ratio=1.0)
