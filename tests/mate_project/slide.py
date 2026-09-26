# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A gripper's two fingers mated by sliding freedoms, and the hand-placed
twin they must reproduce.

The numbers are a four-joint arm's two-finger gripper as its URDF states
it (`openspec/changes/slide-by-mate/evidence/finding.md`, sections 2 and
3): each finger's joint origin `(81.7, +-21.0, 0.0)` on the palm, its
axis `(0, +-1, 0)` in the finger's own frame, its travel `(-11, 20)` mm,
the right finger a mimic of the left with multiplier 1 -- the mirrored
axes make equal travel opposite motion.

`Gripper` states each finger once, as a mate whose freedom is a
`Prismatic`, the mimic a relation between the two mates' coordinates,
and drives the left one by path from two levels up. `TwinGripper` is the
same machine as the project wrote it before mates: a `Prismatic` on each
finger class and a palm whose `render()` translates each finger to its
seat.

`SidePalm` states its slide's axis as a function of the palm's side
(ADR-150's path, on the new kind); `SlotMount` states an axis across the
moving frame's `z`, with no unit; `AnchoredPalm` writes an `at` that
moves nothing.
"""

from solid2 import cube

from machinome.motion.joints import Prismatic
from machinome.node import AssemblyNode, Solid2Node
from machinome.node.frames import Frame
from machinome.parameters import Flag
from machinome.simulation import Driver


SEAT = {True: (81.7, 21.0, 0.0), False: (81.7, -21.0, 0.0)}
AXIS = {True: (0, 1, 0), False: (0, -1, 0)}
TRAVEL = (-11, 20)


class Finger(Solid2Node):
    """A finger with a connector at its own origin."""

    origin = Frame()

    def render(self):
        return cube([4, 2, 6], center=True)


class Palm(AssemblyNode):
    """Both fingers, each one statement, the right a mimic of the left."""

    left_seat = Frame(at=SEAT[True])
    right_seat = Frame(at=SEAT[False])

    left_finger = Finger()
    right_finger = Finger()

    left_grip = left_finger.origin.on(
        left_seat, Prismatic(axis=AXIS[True], range=TRAVEL, unit='mm'))
    right_grip = right_finger.origin.on(
        right_seat, Prismatic(axis=AXIS[False], range=TRAVEL, unit='mm'))

    left_grip.drives(right_grip)


class Wrist(AssemblyNode):
    palm = Palm()


class Gripper(AssemblyNode):
    """The mimic's source driven by path from two levels up."""

    grip = Driver(default=0.0, range=(-11.0, 20.0), unit='mm')

    wrist = Wrist()

    grip.drives(wrist.palm.left_grip)


def side_seat(node):
    """The finger's seat on `node`'s side."""
    return SEAT[bool(node.left)]


def side_axis(node):
    """The finger's axis on `node`'s side."""
    return AXIS[bool(node.left)]


class SidePalm(AssemblyNode):
    """One finger whose seat and axis are functions of the palm's side."""

    left = Flag(True)

    seat = Frame(at=side_seat)

    finger = Finger()

    grip = finger.origin.on(seat, Prismatic(axis=side_axis, range=TRAVEL,
                                            unit='mm'))


class SlotPart(Solid2Node):
    """A part whose connector's `z` stands across its slide."""

    slot = Frame(z=(0, 1, 0), x=(1, 0, 0))

    def render(self):
        return cube(2, center=True)


class SlotMount(AssemblyNode):
    """A slide along `(1, 0, 0)`, stated, not the moving frame's `z`;
    no unit written."""

    seat = Frame(at=(0, 0, 5), z=(0, 1, 0), x=(1, 0, 0))

    part = SlotPart()

    slide = part.slot.on(seat, Prismatic(axis=(1, 0, 0), range=(0, 10)))


class AnchoredPalm(AssemblyNode):
    """`Palm`'s left half, its freedom writing an anchor."""

    left_seat = Frame(at=SEAT[True])

    left_finger = Finger()

    left_grip = left_finger.origin.on(
        left_seat, Prismatic(axis=AXIS[True], at=(0, 0, 5), range=TRAVEL,
                             unit='mm'))


##############################################
# The hand-placed twin

class TwinLeftFinger(Solid2Node):
    travel = Prismatic(axis=AXIS[True], range=TRAVEL, unit='mm')

    def render(self):
        return cube([4, 2, 6], center=True)


class TwinRightFinger(Solid2Node):
    travel = Prismatic(axis=AXIS[False], range=TRAVEL, unit='mm')

    def render(self):
        return cube([4, 2, 6], center=True)


class TwinPalm(AssemblyNode):
    """The palm placing each finger by hand, the mimic between the
    fingers' own joints."""

    left_finger = TwinLeftFinger()
    right_finger = TwinRightFinger()

    left_finger.travel.drives(right_finger.travel)

    def render(self):
        self.left_finger.translate(list(SEAT[True]))
        self.right_finger.translate(list(SEAT[False]))


class TwinWrist(AssemblyNode):
    palm = TwinPalm()


class TwinGripper(AssemblyNode):
    grip = Driver(default=0.0, range=(-11.0, 20.0), unit='mm')

    wrist = TwinWrist()

    grip.drives(wrist.palm.left_finger.travel)
