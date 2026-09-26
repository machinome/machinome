# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Thor's connectors as the design states them, and their hand-placed
twins.

A design's connectors are ATTACHMENT frames: folded with their offsets,
the moving connector's `z` is the joint line for Thor's base yaw and
elbow, reversed for the forearm yaw, and ACROSS the line for the
shoulder and the wrist (`openspec/changes/state-the-mate-line/evidence/
finding.md`, section 3). This module holds what a freedom that states
no line can already express -- the moving parts with their verbatim
connectors, and the HAND-PLACED TWIN of each mate: an assembly whose
`render()` writes the rest placement the verbatim pair solves to, over a
child whose class declares the hand-written joint. The mates that state
the line are in `line.py`, beside this module.

Every moving part carries a `Plate` placed off its own origin, so a
composed world matrix sees an anchor or an axis in the wrong place.
"""

import math

from solid2 import cube

from machinome.motion.joints import Revolute
from machinome.node import AssemblyNode, Solid2Node
from machinome.node.frames import Frame
from machinome.simulation import Driver

HALF = math.sqrt(0.5)


class Plate(Solid2Node):
    """A leaf with enough geometry to be a real part."""

    def render(self):
        return cube([4, 6, 2], center=True)


class Link(AssemblyNode):
    """A moving body: one plate, placed off the body's own origin."""

    plate = Plate()

    def render(self):
        self.plate.translate([7, 11, 13])


# The shoulder: the connector stands ACROSS the joint line, 68 up it.

class Art2(Link):
    bore = Frame(at=(0, 0, 68), z=(0, 1, 0), x=(-1, 0, 0))


class HandArt2(Link):
    shoulder = Revolute(axis=(0, 0, 1), unit='deg')


class HandShoulder(AssemblyNode):
    """The shoulder as Thor's `Art1.render()` places it by hand."""

    art2 = HandArt2()

    def render(self):
        self.art2.rotate(180, [0, HALF, HALF])
        self.art2.translate([0, -68, 123])


class HandShoulderMachine(AssemblyNode):
    angle = Driver(default=30.0, unit='deg')

    housing = HandShoulder()

    angle.drives(housing.art2.shoulder)


# The wrist: the connector stands ACROSS the joint line.

class Art56(Link):
    bore = Frame(x=(0, -1, 0))


class HandArt56(Link):
    wrist = Revolute(axis=(1, 0, 0), unit='deg')


class HandWrist(AssemblyNode):
    art56 = HandArt56()

    def render(self):
        self.art56.rotate(90, [0, 0, 1])
        self.art56.translate([0, 0, 111.5])


# The forearm yaw: the connector's z points down the joint line.

class Art4(Link):
    bore = Frame(z=(0, 0, -1))


class HandArt4(Link):
    yaw = Revolute(axis=(0, 0, 1), unit='deg')


class HandYaw(AssemblyNode):
    art4 = HandArt4()

    def render(self):
        self.art4.rotate(180, [0, 1, 0])
        self.art4.translate([0, 0, -1])


class ReversedYawByFrame(AssemblyNode):
    """The reversed connector mated with a freedom that states no line:
    the joint turns about the connector's own `(0, 0, -1)`."""

    yaw_pin = Frame(at=(0, 0, -1))

    art4 = Art4()

    yaw = art4.bore.on(yaw_pin, Revolute(unit='deg'))
