# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A shin holding a servo by a mate with no freedom, and the
hand-placed twin it must reproduce.

The numbers are a quadruped's left knee servo as its project measures
it (`openspec/changes/hold-by-mate/evidence/finding.md`, sections 3 and
6): the seat at the bore midpoint on the shin plate's face,
`(-0.98, -4, -7)`, its `z` along `+X` and its `x` along `+Z`; the servo's
ears 5.5 behind its output shaft. A rigid mate puts the ears on the seat:
a half turn about `(1, 0, 1)/sqrt(2)` and a translation to
`(-0.98, -9.5, -7)`, where the project turned the servo a quarter turn
about `y`, a half turn about `x`, and translated it there.

`Shin` holds the servo by `bolted = servo.ears.on(servo_seat)`;
`PlateShin` onto a still sibling's frame; `OutputShin` a servo with a
joint of its own; `BoltedShin` a servo assembly that itself holds a
screw by a rigid mate. `Leg` turns the shin by a revolute mate and
`Robot` drives it. The `Twin*` classes are the same machines as the
project wrote them before mates: `rotate` and `translate` in `render()`
and a class-body `Revolute` on the shin.
"""

from solid2 import cube

from machinome.motion.joints import Revolute
from machinome.node import AssemblyNode, Solid2Node
from machinome.node.frames import Frame
from machinome.simulation import Driver


SEAT = dict(at=(-0.98, -4, -7), z=(1, 0, 0), x=(0, 0, 1))


class Servo(Solid2Node):
    """A servo whose origin is on its output shaft, its ears behind it."""

    ears = Frame(at=(0, -5.5, 0))
    ear_near = Frame(at=(-14, -5.5, 0))

    def render(self):
        return cube(2, center=True)


class OutputServo(Servo):
    """A servo whose output turns."""

    output = Revolute(axis=(0, 1, 0))


class Screw(Solid2Node):
    """A screw whose origin is under its head."""

    head = Frame()

    def render(self):
        return cube(1, center=True)


class Plate(Solid2Node):
    """A shin plate carrying the seat as its own frame."""

    bores = Frame(**SEAT)

    def render(self):
        return cube(2, center=True)


class Shin(AssemblyNode):
    """The servo held at its measured seat, one statement."""

    servo_seat = Frame(**SEAT)
    knee_bore = Frame(z=(0, 1, 0))

    servo = Servo()

    bolted = servo.ears.on(servo_seat)


class PlateShin(AssemblyNode):
    """The servo held on a still sibling's frame."""

    plate = Plate()
    servo = Servo()

    bolted = servo.ears.on(plate.bores)

    def render(self):
        self.plate.translate([0, 0, 3])


class OutputShin(AssemblyNode):
    """A held servo that keeps its own joint."""

    servo_seat = Frame(**SEAT)

    servo = OutputServo()

    bolted = servo.ears.on(servo_seat)


class BoltedServo(AssemblyNode):
    """A servo with its screw, the screw held by a rigid mate."""

    ears = Frame(at=(0, -5.5, 0))

    servo = Servo()
    screw = Screw()

    screwed = screw.head.on(servo.ear_near)


class BoltedShin(AssemblyNode):
    """A held child that carries a mate of its own."""

    servo_seat = Frame(**SEAT)

    servo = BoltedServo()

    bolted = servo.ears.on(servo_seat)


class Leg(AssemblyNode):
    """The shin turned about the knee by a revolute mate."""

    knee_pin = Frame(at=(0, 8, -30), z=(0, 1, 0))

    shin = Shin()

    knee = shin.knee_bore.on(knee_pin,
                             Revolute(range=(-90, 90), unit='deg'))


class Robot(AssemblyNode):
    angle = Driver(default=0.0, range=(-90.0, 90.0), unit='deg')

    leg = Leg()

    angle.drives(leg.knee)


##############################################
# The hand-placed twin

class TwinShin(AssemblyNode):
    knee = Revolute(axis=(0, 1, 0), range=(-90, 90), unit='deg')

    servo = Servo()

    def render(self):
        self.servo.rotate(90.0, [0, 1, 0])
        self.servo.rotate(180.0, [1, 0, 0])
        self.servo.translate([-0.98, -9.5, -7.0])


class TwinPlateShin(AssemblyNode):
    plate = Plate()
    servo = Servo()

    def render(self):
        self.plate.translate([0, 0, 3])
        self.servo.rotate(90.0, [0, 1, 0])
        self.servo.rotate(180.0, [1, 0, 0])
        self.servo.translate([-0.98, -9.5, -4.0])


class TwinBoltedServo(AssemblyNode):
    servo = Servo()
    screw = Screw()

    def render(self):
        self.screw.translate([-14, -5.5, 0])


class TwinBoltedShin(AssemblyNode):
    servo = TwinBoltedServo()

    def render(self):
        self.servo.rotate(90.0, [0, 1, 0])
        self.servo.rotate(180.0, [1, 0, 0])
        self.servo.translate([-0.98, -9.5, -7.0])


class TwinLeg(AssemblyNode):
    shin = TwinShin()

    def render(self):
        self.shin.translate([0, 8, -30])


class TwinRobot(AssemblyNode):
    angle = Driver(default=0.0, range=(-90.0, 90.0), unit='deg')

    leg = TwinLeg()

    angle.drives(leg.shin.knee)
