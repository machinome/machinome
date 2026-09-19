# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The REGISTER fixture: the Curta's own shape, in three wheels.

Added by closure 1 of the change `declare-the-state` (2026-09-17), for
the finding that made it necessary: the originating project
`projects/Calculators/Curta-Type-I-3x` has SEVENTEEN result wheels of one
class, and every one of them is written TWICE --

- at the STROKE END, by the arithmetic of one crank revolution, which
  writes the whole register at once; and
- at the CLEARING REACH, by the clearing ring sweeping past that wheel's
  own rack, which zeroes it.

Two events, two inputs, one `at` each. Under the first draft of this
design -- "a state has ONE committing relation" -- that machine could not
be written down at all, and a register of identical wheels could not even
be written as ONE relation, because the refusal compared the LOCAL NAME
`digit` rather than the path `w0.digit`. This fixture is the smallest
thing that has both shapes.

Nothing here is the Curta: the arithmetic is a plain three-digit add with
carry, and the clearing geometry is three evenly spaced thresholds. Every
expected value in the tests is computed BY HAND; the laws below are never
called to produce one.
"""

from machinome.math import floor
from machinome.node import AssemblyNode
from machinome.simulation import Driver, State

from .parts import Dial


#: Design degrees of dial rotation per digit.
DIGIT = 36.0

#: Where the first wheel's rack starts, how far apart its teeth are, and
#: how far the ring travels between one wheel and the next -- all in ring
#: degrees, all exactly representable, so a test can name a threshold as
#: a float and mean it.
START = 10.0
PITCH = 4.0
SPAN = 100.0


def threshold(place, digit):
    """Where the ring reaches the wheel at `place` standing at `digit`.

    Written here so a test computes its expectation by hand instead of
    asking the law. The threshold READS the digit -- which is the whole
    point of a source group naming its own target -- and reads it so
    that clearing moves the threshold BEHIND the ring: a wheel standing
    high is reached late, and a wheel already at zero is behind the
    sweep and cannot be reached again.

    That is the mirror of the clearing fixture's `START + PITCH * (10 -
    digit)`, which is the form the project spike MEASURED on the Curta
    and which `clearing.py` keeps. A register swept across several
    wheels needs the other one: under the measured form, zeroing a wheel
    pushes its threshold AHEAD of the ring, so a sweep long enough to
    reach the third wheel reaches the first one a second time, and the
    real machine's ring carries the zeroed rack along with it rather
    than reaching it twice. This fixture states the one-way sweep
    directly instead of modelling that carry.
    """
    return START + SPAN * place + PITCH * digit


def strokes(sources, targets):
    """The event: which completed revolution of the crank we stand in."""
    return lambda crank, operand, d0, d1, d2: floor(crank / 360)


def add(sources, targets):
    """The commit at a stroke end: the whole register, plus the operand,
    read from the register as it stood BEFORE the stroke.

    The carry is inside the arithmetic, where a real machine's is inside
    its gearing; the tests compute it by hand.
    """
    def law(crank, operand, d0, d1, d2):
        total = d0 + 10 * d1 + 100 * d2 + operand
        return (total % 10,
                floor(total / 10) % 10,
                floor(total / 100) % 10)

    return law


def reach(place):
    """The clearing event for ONE wheel: the ring has swept far enough to
    reach it, which depends on the digit it is standing at."""
    def factory(sources, targets):
        return lambda ring, digit: ring >= START + SPAN * place \
            + PITCH * digit

    return factory


def clear(place):
    """The clearing commit for ONE wheel: zero once the rack is reached,
    and what it held before until then."""
    def factory(sources, targets):
        return lambda ring, digit: digit * (
            ring < START + SPAN * place + PITCH * digit)

    return factory


class Wheel(AssemblyNode):
    """One register wheel: the part that HOLDS the value, and therefore
    the class that declares it. Three instances of THIS ONE CLASS is the
    whole point of the fixture."""

    digit = State(default=0, range=(0, 9), dtype=int)

    face = Dial()

    digit.drives(face.turn, ratio=DIGIT)


class Register(AssemblyNode):
    """A crank, a clearing ring, an operand, and three wheels of one
    class -- each digit written by the stroke AND by its own clearing
    reach."""

    crank = Driver(default=0, unit='deg')
    ring = Driver(default=0.0, unit='deg')
    operand = Driver(default=1, range=(0, 9), dtype=int)

    w0 = Wheel()
    w1 = Wheel()
    w2 = Wheel()

    # ONE relation writing three states of three children of ONE class:
    # the targets are told apart by their PATHS and by nothing else.
    (crank & operand & w0.digit & w1.digit & w2.digit).commits(
        (w0.digit, w1.digit, w2.digit), at=strokes, law=add)

    # And one clearing relation per wheel, each reading the digit it
    # writes -- the second writer of each of those three states.
    (ring & w0.digit).commits(w0.digit, at=reach(0), law=clear(0))
    (ring & w1.digit).commits(w1.digit, at=reach(1), law=clear(1))
    (ring & w2.digit).commits(w2.digit, at=reach(2), law=clear(2))
