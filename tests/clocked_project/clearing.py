# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The CLEARING fixture: an event surface that reads the state it
commits.

The Curta's clearing threshold is `start + pitch * (10 - digit)`: how
far the ring must sweep before this dial's rack reaches it depends on
the digit the dial is STANDING at. The requirement note's sketch wrote a
constant there; the project spike measured that the geometry does not
admit one (`simulation/docs/clocked-spike-2026-09-16.md`, finding 2), and
that measurement is why a source group may name its own target.

The fixture keeps that shape and nothing else of the machine: the state
is declared on the DIAL, the relation on the ROOT that can see both ends,
and the target is named through the path `dial.digit`.
"""

from machinome.node import AssemblyNode
from machinome.simulation import Driver, State

from .parts import Dial


#: Where the first tooth stands, and how far apart the teeth are, in
#: ring degrees. Both exactly representable, so a test can name the
#: threshold as a float and mean it.
START = 10.0
PITCH = 4.0

#: Design degrees of dial rotation per digit.
DIGIT = 36.0


def threshold(digit):
    """Where the rack reaches a dial standing at `digit`, in ring
    degrees. Written here so a test can compute the expectation by hand
    instead of asking the law."""
    return START + PITCH * (10 - digit)


def reach(sources, targets):
    """The event: the ring has swept far enough to reach THIS dial,
    which depends on the digit the dial is standing at."""
    return lambda ring, digit: ring >= START + PITCH * (10 - digit)


def clear(sources, targets):
    """The commit: the dial is left at zero once the rack has reached
    it, and holds what it held before."""
    return lambda ring, digit: digit * (ring < START + PITCH * (10 - digit))


class Wheel(AssemblyNode):
    """One register dial: the part that HOLDS the value, and therefore
    the class that declares it."""

    digit = State(default=0, range=(0, 9), dtype=int)

    face = Dial()

    digit.drives(face.turn, ratio=DIGIT)


class Clearer(AssemblyNode):
    """The ring and one dial: the relation belongs to the assembly that
    can see both ends, and names its target through a path."""

    ring = Driver(default=0.0, unit='deg')

    dial = Wheel()

    (ring & dial.digit).commits(dial.digit, at=reach, law=clear)
