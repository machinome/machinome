# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The GATE fixture: a bound that reads a STATE the same request writes.

The clip is computed ONCE, over the bank as it stands when the request
begins (OpenSpec change ``a-bound-stops-the-request``, design section 8),
and this is the fixture that makes that decision VISIBLE. A shutter
travels at one hundredth of the crank; a committing relation opens the
gate at every two hundred degrees; and the shutter's upper bound is `3`
while the gate is shut and `12` once it is open.

From `crank = 0, opened = 0`:

- one `move('crank', by=1000)` is clipped against the SHUT gate and
  admits 300, the event inside it opening a gate the clip has already
  read;
- `move('crank', by=200)` then `move('crank', by=800)` commits that same
  event FIRST, so the second request is clipped against the open gate and
  the pair admits 1000.

Both numbers are computed BY HAND. The pawl cannot discriminate that
decision -- a ratchet gives one tooth of backlash either way -- which is
why this fixture exists.

`Shut` beside it is the other half: a gate whose commit CLOSES it, so the
event inside the request carries a compiled coordinate out of range and
the clocked simulation's own end-of-request judgement refuses the whole
request (design section 10).
"""

from solid_node.math import floor
from solid_node.motion.joints import Bound, Prismatic
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, State

from .parts import Slide


#: Degrees of crank per millimetre of shutter travel. A hundred, so the
#: division is exact at every value a test names.
PER_MM = 100.0

#: Where the gate's own event is: one every two hundred degrees.
REACH = 200.0


def reaches(sources, targets):
    """The event: which completed `REACH` of the crank we stand in."""
    return lambda crank, opened: floor(crank / REACH)


def opens(sources, targets):
    """The commit: the gate is open from here on."""
    return lambda crank, opened: 1


def shuts(sources, targets):
    """The commit of the other half: the gate is shut from here on."""
    return lambda crank, opened: 1


def hundredth(driver, driven):
    """The shutter's law: one hundredth of the crank, written as a
    DIVISION so the value at a named crank angle is exact."""
    return lambda crank: crank / PER_MM


class Gate(AssemblyNode):
    """The shutter may travel 3 mm while the gate is shut and 12 mm once
    it is open."""

    crank = Driver(default=0.0, unit='deg')
    opened = State(default=0, dtype=int)

    shutter = Slide(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(0, Bound(lambda travel, open_: 3 + 9 * open_,
                        reads=(opened,)))))

    (crank & opened).commits(opened, at=reaches, law=opens)

    crank.drives(shutter.travel, law=hundredth)


class Shut(AssemblyNode):
    """The same machine whose commit SHUTS the gate instead: the clip
    reads `3`, the event inside the request writes `1`, and the bound
    the final bank evaluates is `0` -- which the shutter, standing at 3,
    is outside."""

    crank = Driver(default=0.0, unit='deg')
    shutting = State(default=0, dtype=int)

    shutter = Slide(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(0, Bound(lambda travel, shut: 3 - 3 * shut,
                        reads=(shutting,)))))

    (crank & shutting).commits(shutting, at=reaches, law=shuts)

    crank.drives(shutter.travel, law=hundredth)
