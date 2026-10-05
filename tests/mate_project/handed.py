# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A handed joint stated once, as a mate whose freedom is a function of
the assembly that states it, and its hand-placed twin.

One class per joint, instantiated once per side, a `left` flag handed
down the declaration: the joint's origin, its axis and its range each
differ by side. The numbers are a seven-joint arm's first joint as its
URDF states it (`openspec/changes/state-the-freedom-per-instance/
evidence/finding.md`, section 3): the origin `(0, +-62.5, 0)`, the axis
`(0, +-1, 0)` and the limits `(-200, 80)` left, `(-80, 200)` right.

`HandedLink` declares NO `left`, so a function called with the moving
child instead of the assembly fails on it; `ContraryLink` declares its
own `left = Flag(True)`, never passed from the mount, so a function
called with the child reads the wrong side silently. The two tell
"called with the assembly" from "called with the child"
(`tests/test_mates.py`, `HandedFreedomTest`).

`TwinPair` is the same machine as the project wrote it before mates: a
link class whose own `turn` reads its own `left`, placed by its mount's
`render()`.
"""

from solid2 import cube

from machinome.motion.joints import Revolute
from machinome.node import AssemblyNode, Solid2Node
from machinome.node.frames import Frame
from machinome.parameters import Flag
from machinome.simulation import Driver


ORIGIN = {True: (0, 62.5, 0), False: (0, -62.5, 0)}
AXIS = {True: (0, 1, 0), False: (0, -1, 0)}
LIMITS = {True: (-200, 80), False: (-80, 200)}


def side_origin(node):
    """The joint's origin on `node`'s side."""
    return ORIGIN[bool(node.left)]


def side_axis(node):
    """The joint's axis on `node`'s side."""
    return AXIS[bool(node.left)]


def side_range(node):
    """The joint's limits on `node`'s side, in degrees."""
    return LIMITS[bool(node.left)]


class HandedLink(Solid2Node):
    """A link with a connector at its own origin and no `left`."""

    origin = Frame()

    def render(self):
        return cube([4, 6, 2], center=True)


class HandedMount(AssemblyNode):
    """The joint, stated once: the fixed frame, the axis and the range
    are functions of the mount's side."""

    left = Flag(False)

    pin = Frame(at=side_origin)

    link = HandedLink()

    turn = link.origin.on(pin, Revolute(axis=side_axis, range=side_range,
                                        unit='deg'))


#: Every node `ContraryMount`'s axis function has been called with.
CONTRARY_CALLS = []


def contrary_axis(node):
    CONTRARY_CALLS.append(node)
    return side_axis(node)


class ContraryLink(Solid2Node):
    """A link whose own `left` says the opposite of its mount's."""

    left = Flag(True)

    origin = Frame()

    def render(self):
        return cube([4, 6, 2], center=True)


class ContraryMount(AssemblyNode):
    """`HandedMount` over a `ContraryLink`, whose `left` is NOT passed."""

    left = Flag(False)

    pin = Frame(at=side_origin)

    link = ContraryLink()

    turn = link.origin.on(pin, Revolute(axis=contrary_axis,
                                        range=side_range, unit='deg'))


class HandedPair(AssemblyNode):
    """Both sides, one driver."""

    angle = Driver(default=30, unit='deg')

    left = HandedMount(left=True)
    right = HandedMount(left=False)

    angle.drives(left.turn)
    angle.drives(right.turn)


##############################################
# The hand-placed twin

class TwinLink(Solid2Node):
    """The link as the project wrote it before mates: its own `turn`,
    read off its own `left`."""

    left = Flag(False)

    turn = Revolute(axis=side_axis, range=side_range, unit='deg')

    def render(self):
        return cube([4, 6, 2], center=True)


class TwinMount(AssemblyNode):
    """The mount placing its link by hand, on its side."""

    left = Flag(False)

    link = TwinLink(left=left)

    def render(self):
        self.link.translate(list(ORIGIN[bool(self.left)]))


class TwinPair(AssemblyNode):
    angle = Driver(default=30, unit='deg')

    left = TwinMount(left=True)
    right = TwinMount(left=False)

    angle.drives(left.link.turn)
    angle.drives(right.link.turn)
