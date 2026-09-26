# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Mates whose freedom states the line the part turns about.

The connectors are the design's, verbatim (`verbatim.py`); the frames
place the part, and the freedom states the joint line in the moving
part's OWN frame -- the axis Thor's `ROOT_CHAIN` names for each link,
and, for the shoulder, the anchor at the part's own origin, where the
hand-written joint had it. Each is held to its hand-placed twin in
`verbatim.py` by `tests/test_mates.py`.
"""

from machinome.motion.joints import Revolute
from machinome.node import AssemblyNode
from machinome.node.frames import Frame
from machinome.simulation import Driver

from .arm import MatedArm
from .verbatim import Art2, Art4, Art56


class VerbatimShoulder(AssemblyNode):
    shoulder_pin = Frame(at=(0, 0, 123))

    art2 = Art2()

    shoulder = art2.bore.on(
        shoulder_pin, Revolute(axis=(0, 0, 1), at=(0, 0, 0), unit='deg'))


class VerbatimShoulderMachine(AssemblyNode):
    angle = Driver(default=30.0, unit='deg')

    housing = VerbatimShoulder()

    angle.drives(housing.shoulder)


class VerbatimWrist(AssemblyNode):
    wrist_pin = Frame(at=(0, 0, 111.5))

    art56 = Art56()

    wrist = art56.bore.on(wrist_pin, Revolute(axis=(1, 0, 0), unit='deg'))


class VerbatimYaw(AssemblyNode):
    yaw_pin = Frame(at=(0, 0, -1))

    art4 = Art4()

    yaw = art4.bore.on(yaw_pin, Revolute(axis=(0, 0, 1), unit='deg'))


class AnchoredHousing(AssemblyNode):
    """`MatedHousing`'s shoulder -- the upper arm's `bore`, whose `z` IS
    the joint line, 68 up it -- with the anchor stated at the upper
    arm's own origin."""

    shoulder_pin = Frame(at=(0, 0, 123), z=(0, 1, 0))

    art2 = MatedArm()

    shoulder = art2.bore.on(shoulder_pin,
                            Revolute(at=(0, 0, 0), unit='deg'))
