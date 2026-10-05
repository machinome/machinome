# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Thor's elbow and shoulder, stated as frames and mates.

`tests/joint_project/arm.py` pins Thor's elbow as the project writes it
today: `Arm.render()` places the forearm with `rotate(90, X)` and
`translate(0, 160 + 81.5, 68)`, and `Forearm` restates the same pin as
`Revolute(axis=(0, 1, 0), at=(0, 0, 81.5))`. Here the same elbow is one
connector on each side and one sentence in the arm:

    elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))          # on the arm
    hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))   # on the forearm
    elbow = forearm.hinge.on(elbow_pin, Revolute(range=(-135, 135)))

and every test in `tests/test_mates.py` holds the mated arm to the
hand-written one: same rest operations, same joint, same pose at every
binding. The numbers are Thor's, and the spike's
(`openspec/changes/place-parts-by-mate/evidence/spike.md`).

`MatedHousing` is Thor's shoulder, the spike's second pair: the arm's
own `bore` onto the housing's `shoulder_pin`, a 180 degree turn about a
diagonal the hand-written `render()` spells `(0, .7071, .7071)`.
`Pedestal` is the one root-chain case whose fixed end is a SIBLING's
frame: a turret mated onto a still base the assembly places by hand.
`Knuckle` mates a wheel that already spins on a joint of its own.
"""

from solid2 import cube, cylinder

from machinome.motion.joints import Revolute
from machinome.motion.ports import RotationalPort
from machinome.node.assembly import AssemblyNode
from machinome.node.solid2 import Solid2Node
from machinome.node.frames import Frame
from machinome.parameters import Length
from machinome.simulation import Driver

from ..joint_project.parts import Link

# Thor's own constants, as `tests/joint_project/arm.py` quotes them.
ELBOW_ALONG_ARM = 160.0
ELBOW_ACROSS_ARM = 81.5
ELBOW_HEIGHT = 68.0


class MatedForearm(AssemblyNode):
    """`Forearm` minus its `elbow` joint, plus the connector the elbow
    is made through, in the forearm's OWN rest frame: exactly the line
    `Forearm.elbow` states, with its `x` fixing the attitude about it."""

    reach = Length(ELBOW_ALONG_ARM, min=0)

    hinge = Frame(at=(0, 0, ELBOW_ACROSS_ARM), z=(0, 1, 0), x=(1, 0, 0))

    link = Link()


class DefaultXForearm(AssemblyNode):
    """The same connector with its `x` left to the principal default:
    the two `z` lines still meet, and the rest attitude is a different
    one -- the zero of the coordinate is what `x` fixes."""

    reach = Length(ELBOW_ALONG_ARM, min=0)

    hinge = Frame(at=(0, 0, ELBOW_ACROSS_ARM), z=(0, 1, 0))

    link = Link()


class MatedArm(AssemblyNode):
    """Thor's upper arm: the elbow pin is its own connector, the
    forearm root is placed and jointed by one sentence, and nothing is
    written in `render()` at all.

    `bore` is the arm's connector to the housing above it (Thor's
    `LCS_Art1` folded with its offset, the spike's shoulder)."""

    reach = Length(ELBOW_ALONG_ARM, min=0)

    elbow_pin = Frame(at=(0, reach, ELBOW_HEIGHT), z=(0, 0, 1))
    bore = Frame(at=(0, 0, 68), z=(0, 0, 1), x=(0, 1, 0))

    forearm = MatedForearm(reach=reach)

    elbow = forearm.hinge.on(elbow_pin,
                             Revolute(range=(-135, 135), unit='deg'))


class DefaultXArm(AssemblyNode):
    """`MatedArm` over the forearm whose `x` is left out."""

    reach = Length(ELBOW_ALONG_ARM, min=0)

    elbow_pin = Frame(at=(0, reach, ELBOW_HEIGHT), z=(0, 0, 1))

    forearm = DefaultXForearm(reach=reach)

    elbow = forearm.hinge.on(elbow_pin, Revolute(unit='deg'))


class MatedHousing(AssemblyNode):
    """Thor's shoulder: the upper arm's `bore` onto the housing's own
    `shoulder_pin`, and a derived coordinate over the two mates the way
    Thor couples its elbow belt to the shoulder."""

    shoulder_pin = Frame(at=(0, 0, 123), z=(0, 1, 0))

    art2 = MatedArm()

    shoulder = art2.bore.on(shoulder_pin, Revolute(unit='deg'))

    drive = shoulder + 5.85 * art2.elbow


class Seat(Solid2Node):
    """A still base: a connector and no joint."""

    seat = Frame(at=(0, 0, 79))

    def render(self):
        return cylinder(r=40, h=79)


class Turret(Solid2Node):
    """What turns on the base, attached by its own origin."""

    origin = Frame()

    def render(self):
        return cube([30, 30, 40], center=True)


class Pedestal(AssemblyNode):
    """A fixed end on a SIBLING: the turret rests where the base's seat
    is after the base's own hand placement."""

    base = Seat()
    housing = Turret()

    yaw = housing.origin.on(base.seat, Revolute(unit='deg'))

    def render(self):
        self.base.translate([0, 0, 10])


class SpinningWheel(Solid2Node):
    """A wheel spinning on a joint of its own, with a hub connector."""

    spin = Revolute(axis=(0, 1, 0), unit='deg')

    hub = Frame(at=(0, 0, 0), z=(0, 0, 1), x=(1, 0, 0))

    def render(self):
        return cylinder(r=30, h=6)


class Knuckle(AssemblyNode):
    """A steered wheel: the mate's freedom composes OUTSIDE the wheel's
    own spin."""

    knuckle = Frame(at=(10, 0, 0), z=(0, 0, 1))

    wheel = SpinningWheel()

    steer = wheel.hub.on(knuckle, Revolute(unit='deg'))


class Dial(Solid2Node):
    """A part taking an angle on a plain port, for a mate's coordinate
    to be wired into."""

    turn = RotationalPort(unit='deg')

    def render(self):
        return cylinder(r=10, h=2)


class GaugedArm(AssemblyNode):
    """A mate's coordinate wired into a sibling's port, like any
    coordinate the assembly owns."""

    elbow_pin = Frame(at=(0, 160, 68), z=(0, 0, 1))

    forearm = MatedForearm()

    elbow = forearm.hinge.on(elbow_pin, Revolute(unit='deg'))

    gauge = Dial(turn=elbow)


class MatedElbowMachine(AssemblyNode):
    """A root over the mated upper arm, driven the way Thor drives its
    elbow: one driver, stated onto the mate's coordinate."""

    angle = Driver(default=0.0, unit='deg')

    arm = MatedArm()

    angle.drives(arm.elbow)


class MatedShoulderMachine(AssemblyNode):
    """A root over `MatedHousing`, driving both of its mates: the
    shoulder, whose moving frame sits 68 up its line (so its installed
    joint carries a centring pair), and the upper arm's elbow."""

    shoulder_angle = Driver(default=15.0, unit='deg')
    elbow_angle = Driver(default=25.0, unit='deg')

    housing = MatedHousing()

    shoulder_angle.drives(housing.shoulder)
    elbow_angle.drives(housing.art2.elbow)
