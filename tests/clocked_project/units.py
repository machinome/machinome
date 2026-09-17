# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""What a commit law speaks, and where rounding happens.

The bank holds NATIVE values, which is what a declaration means by
`default` and what every law in the framework already reads. A commit
law therefore reads native values and returns native values, and its
return is deliberately NOT passed through the design-unit conversion a
driver applies to a move target -- doing that would divide a scaled
state by its scale a SECOND time.

The one thing that happens to a committed value is the integer rounding:
a state declaring `dtype=int` counts whole native units, so its value is
rounded ONCE, at the commit, to the nearest one.
"""

from solid_node.math import floor
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, State

from .parts import Dial


#: A value that is a whole number only after rounding, and that a
#: float state must keep exactly.
NEARLY_NINE = 9 - 1e-12


def stroke(sources, targets):
    return lambda crank, value: floor(crank / 360)


def four(sources, targets):
    """A law returning a NATIVE four: a scaled state holds four, and
    poses at four times its scale."""
    return lambda crank, value: 4.0


def nearly_nine(sources, targets):
    return lambda crank, value: NEARLY_NINE


class Scaled(AssemblyNode):
    """A state with a `scale` and no `dtype`: the law's return is held
    unrescaled, and the pose reads it through the scale exactly once."""

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0.0, unit='digit', scale=10.0)

    face = Dial()

    (crank & value).commits(value, at=stroke, law=four)

    value.drives(face.turn, ratio=10.0)


class Rounded(AssemblyNode):
    """An INTEGER state whose law returns a value a hair below nine."""

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)

    face = Dial()

    (crank & value).commits(value, at=stroke, law=nearly_nine)

    value.drives(face.turn, ratio=1.0)


class Unrounded(AssemblyNode):
    """The same law over a FLOAT state: nothing is rounded."""

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0.0)

    face = Dial()

    (crank & value).commits(value, at=stroke, law=nearly_nine)

    value.drives(face.turn, ratio=1.0)


def jumps_only(sources, targets):
    """A commit law made ENTIRELY of jumps: a digit. Refused as a
    RUNNING law, because under a run every jump is subtracted and such a
    law could never move anything; admitted here, because a commit is
    evaluated at ONE POINT and never integrated."""
    return lambda crank, value: floor(crank / 360) % 10


class JumpsOnly(AssemblyNode):
    """The asymmetry between a commit law and a running law, in one
    class."""

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)

    face = Dial()

    (crank & value).commits(value, at=stroke, law=jumps_only)

    value.drives(face.turn, ratio=1.0)


class Timed(AssemblyNode):
    """A clocked model whose geometry reads `self.time`.

    A clocked root declares no time base, so `time` is not in the bank
    and the pose leaves it the untimed symbolic animation variable --
    which is what it is for an untimed model today.
    """

    crank = Driver(default=0.0, unit='deg')
    value = State(default=0, dtype=int)

    face = Dial()

    (crank & value).commits(value, at=stroke, law=jumps_only)

    def simulate(self):
        self.face.turn = self.value * 10.0 + self.time * 360.0


class TimedTwin(AssemblyNode):
    """`Timed` with its state replaced by a driver of the same value:
    the pose the clocked one must render identically."""

    crank = Driver(default=0.0, unit='deg')
    value = Driver(default=0, dtype=int)

    face = Dial()

    def simulate(self):
        self.face.turn = self.value * 10.0 + self.time * 360.0
