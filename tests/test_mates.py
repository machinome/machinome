# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A mate: one sentence that places a part and declares its freedom.

OpenSpec change ``place-parts-by-mate``, tasks sections 4 to 6. Thor's
elbow is one physical pin stated three times -- a rest placement in the
upper arm's `render()`, a joint in the forearm's class, and three module
constants shared only so the two agree. The design Thor is built from
states it once, as a connector on each side, and so does a mate:

    elbow = forearm.hinge.on(elbow_pin, Revolute(range=(-135, 135)))

which compiles, at realization, to three things the framework already
has and nothing else: the forearm's rest operations, a revolute joint of
the forearm's class, and a rotational coordinate of the arm.

The fixture is `tests/mate_project/arm.py`, and every placement test
holds it to the hand-written `tests/joint_project/arm.py`, which pins
Thor as the project writes it today.
"""

import json
import math
import os

from solid2 import cube

from machinome.motion.joints import (Bound, Free, JointRangeError, Orbit,
                                      Prismatic, Revolute, declared_joints)
from machinome.motion.ports import (RotationalPort, TranslationalPort,
                                     declared_ports)
from machinome.node import AssemblyNode, Solid2Node
from machinome.node.declarative import SidewaysReadError
from machinome.node.frames import Frame
from machinome.parameters import Angle, Length

from .base import BaseNodeTest


def fixtures():
    """`tests/mate_project/arm.py`, imported where a test needs it."""
    from .mate_project import arm

    return arm


def mates_module():
    from machinome.motion import mates

    return mates


def slide_fixtures():
    """`tests/mate_project/slide.py`, imported where a test needs it."""
    from .mate_project import slide

    return slide


def serialized(node):
    return [operation.serialized for operation in node.operations]


def numbers(serialized_translation):
    return [float(component) for component in serialized_translation[1]]


class Pin(Solid2Node):
    """A part with two connectors and nothing else."""

    hinge = Frame(at=(0, 0, 5), z=(0, 1, 0), x=(1, 0, 0))
    foot = Frame(at=(0, 0, -5), z=(0, 0, -1))

    def render(self):
        return cube(2, center=True)


class JointedPin(Solid2Node):
    """A part with a connector and a joint of its own."""

    seat = Frame(at=(0, 0, 3))
    spin = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cube(2, center=True)


class Holder(AssemblyNode):
    """An assembly carrying one child that carries a `Pin`, for a
    path two children deep."""

    pin = Pin()


class HeldServo(Solid2Node):
    """A bought part with two connectors and no joint: what a rigid mate
    holds (hold-by-mate). Declared here, beside `Pin`, so a refusal test
    builds its assembly in its own body; `mate_project/hold.py` carries
    the same part for the placement tests."""

    ears = Frame(at=(0, -5.5, 0))
    ear_near = Frame(at=(-14, -5.5, 0))

    def render(self):
        return cube(2, center=True)


class HeldScrew(Solid2Node):
    """A fastener with one connector under its head."""

    head = Frame()

    def render(self):
        return cube(1, center=True)


##############################################
# 4.1 A frame read off a child declaration is a place

class FrameReferenceTest(BaseNodeTest):

    def test_a_childs_frame_is_a_frame_reference(self):
        captured = []

        class Arm(AssemblyNode):
            forearm = Pin()
            captured.append(forearm.hinge)

        reference = captured[0]
        self.assertIsInstance(reference, mates_module().FrameRef)
        self.assertEqual(reference.written, 'forearm.hinge')
        self.assertIs(reference.frame, Pin.hinge)

    def test_a_frame_reference_does_not_drive(self):
        with self.assertRaises(TypeError) as raised:
            class Arm(AssemblyNode):
                forearm = Pin()
                other = Pin()
                forearm.hinge.drives(other)

        message = str(raised.exception)
        for fragment in ('forearm.hinge', 'connector', 'coordinate'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_a_frame_reference_is_not_a_driven_end_either(self):
        with self.assertRaises(TypeError) as raised:
            class Arm(AssemblyNode):
                turn = RotationalPort(unit='deg')
                forearm = Pin()
                turn.drives(forearm.hinge)

        message = str(raised.exception)
        for fragment in ('forearm.hinge', 'connector'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_nothing_is_read_through_a_frame(self):
        with self.assertRaises(AttributeError) as raised:
            class Arm(AssemblyNode):
                forearm = Pin()
                forearm.hinge.anything

        message = str(raised.exception)
        for fragment in ('forearm.hinge', 'anything'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_a_misspelled_frame_is_still_a_misspelling(self):
        with self.assertRaises(SidewaysReadError) as raised:
            class Arm(AssemblyNode):
                forearm = Pin()
                forearm.hnige

        message = str(raised.exception)
        for fragment in ('forearm.hnige', 'hinge', 'foot'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)


##############################################
# 4.2 The class reports its mates

class DeclaredMatesTest(BaseNodeTest):

    def test_the_arm_reports_one_mate(self):
        MatedArm = fixtures().MatedArm

        found = mates_module().declared_mates(MatedArm)

        self.assertEqual(list(found), ['elbow'])
        mate = found['elbow']
        self.assertEqual(mate.name, 'elbow')
        self.assertEqual(mate.moving.written, 'forearm.hinge')
        self.assertIs(mate.moving.frame, fixtures().MatedForearm.hinge)
        self.assertIs(mate.fixed, MatedArm.elbow_pin)

    def test_a_subclass_inherits_the_mate(self):
        MatedArm = fixtures().MatedArm

        class LongerArm(MatedArm):
            pass

        self.assertEqual(list(mates_module().declared_mates(LongerArm)),
                         ['elbow'])

    def test_a_class_without_mates_reports_none(self):
        self.assertEqual(mates_module().declared_mates(Holder), {})


##############################################
# 4.3 Refusals at class creation

class RefusalTest(BaseNodeTest):
    """Each refusal names the class, the mate and the reason, when the
    class is created."""

    def assertRefused(self, build, *expected, kind=TypeError):
        with self.assertRaises(kind) as raised:
            build()
        message = str(raised.exception)
        for fragment in expected:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)
        return message

    def test_a_mate_on_a_leaf(self):
        def build():
            class Leafy(Solid2Node):
                hinge = Frame()
                pin = Frame(at=(0, 0, 1))
                swing = hinge.on(pin, Revolute())

                def render(self):
                    return cube(1)

        self.assertRefused(build, 'Leafy', 'swing', 'assembly')

    def test_the_assemblys_own_frame_as_the_moving_end(self):
        def build():
            class Backwards(AssemblyNode):
                pin = Frame()
                part = Pin()
                swing = pin.on(part.hinge, Revolute())

        self.assertRefused(build, 'Backwards', 'swing', 'moving end',
                           'directly declared child')

    def test_a_moving_frame_two_children_deep(self):
        def build():
            class Deep(AssemblyNode):
                pin = Frame()
                holder = Holder()
                swing = holder.pin.hinge.on(pin, Revolute())

        self.assertRefused(build, 'Deep', 'swing', 'holder.pin.hinge',
                           'more than one child')

    def test_a_fixed_frame_two_children_deep(self):
        def build():
            class Deep(AssemblyNode):
                part = Pin()
                holder = Holder()
                swing = part.hinge.on(holder.pin.foot, Revolute())

        self.assertRefused(build, 'Deep', 'swing', 'holder.pin.foot',
                           'more than one child')

    def test_a_fixed_end_on_a_child_with_a_class_joint(self):
        def build():
            class Loose(AssemblyNode):
                part = Pin()
                base = JointedPin()
                swing = part.hinge.on(base.seat, Revolute())

        self.assertRefused(build, 'Loose', 'swing', 'base', 'rest')

    def test_a_fixed_end_on_a_child_with_a_site_joint(self):
        def build():
            class Loose(AssemblyNode):
                part = Pin()
                base = Pin(turn=Revolute(axis=(0, 0, 1)))
                swing = part.hinge.on(base.foot, Revolute())

        self.assertRefused(build, 'Loose', 'swing', 'base', 'rest')

    def test_a_fixed_end_on_a_child_another_mate_moves(self):
        def build():
            class Chain(AssemblyNode):
                pin = Frame()
                link = Pin()
                cap = Pin()
                knee = link.hinge.on(pin, Revolute())
                lid = cap.hinge.on(link.foot, Revolute())

        self.assertRefused(build, 'Chain', 'lid', 'link', 'rest')

    def test_a_list_held_child_at_either_end(self):
        def moving():
            class Listed(AssemblyNode):
                pin = Frame()
                arms = [Pin(), Pin()]
                swing = arms[0].hinge.on(pin, Revolute())

        def fixed():
            class Listed(AssemblyNode):
                part = Pin()
                arms = [Pin(), Pin()]
                swing = part.hinge.on(arms[0].foot, Revolute())

        for build in (moving, fixed):
            with self.subTest(end=build.__name__):
                self.assertRefused(build, 'Listed', 'swing', 'list',
                                   'one by one')

    def test_a_repeated_child_at_either_end(self):
        def moving():
            class Repeated(AssemblyNode):
                pin = Frame()
                beads = Pin().repeat(3)
                swing = beads.hinge.on(pin, Revolute())

        def fixed():
            class Repeated(AssemblyNode):
                part = Pin()
                beads = Pin().repeat(3)
                swing = part.hinge.on(beads.foot, Revolute())

        for build in (moving, fixed):
            with self.subTest(end=build.__name__):
                self.assertRefused(build, 'Repeated', 'swing', 'beads',
                                   'repeat')

    def test_a_second_mate_on_one_child_names_both(self):
        def build():
            class Looped(AssemblyNode):
                pin = Frame()
                other_pin = Frame(at=(0, 0, 9))
                part = Pin()
                first = part.hinge.on(pin, Revolute())
                second = part.foot.on(other_pin, Revolute())

        self.assertRefused(build, 'Looped', 'first', 'second', 'loop')

    def test_a_bare_mate_with_a_freedom(self):
        def build():
            class Bare(AssemblyNode):
                pin = Frame()
                part = Pin()
                part.hinge.on(pin, Revolute())

        self.assertRefused(build, 'Bare', 'part.hinge', 'named after the mate')

    # hold-by-mate 2.1: a mate may leave its freedom out. Replaces
    # `test_the_rigid_mate_is_deferred` and
    # `test_the_rigid_mate_names_both_freedoms`, which pinned the refusal
    # this change removes.
    def test_a_mate_may_leave_its_freedom_out(self):
        hold = hold_fixtures()
        Shin = hold.Shin
        Shin()

        mate = mates_module().declared_mates(Shin)['bolted']
        self.assertEqual(mate.name, 'bolted')
        self.assertEqual(mate.moving.written, 'servo.ears')
        self.assertIs(mate.fixed, Shin.servo_seat)
        self.assertEqual(mate.fixed.name, 'servo_seat')
        self.assertIsNone(mate.freedom)

        class Explicit(AssemblyNode):
            servo_seat = Frame(**hold.SEAT)
            servo = hold.Servo()
            bolted = servo.ears.on(servo_seat, None)

        explicit = mates_module().declared_mates(Explicit)['bolted']
        self.assertIsNone(explicit.freedom)
        self.assertEqual(explicit.moving.written, 'servo.ears')
        ours, theirs = Explicit(), Shin()
        ours.render()
        theirs.render()
        self.assertEqual(serialized(ours.servo), serialized(theirs.servo))

    # hold-by-mate 2.2: every mate is named, a rigid one included.
    def test_a_rigid_mate_has_a_name(self):
        def build():
            class Bare(AssemblyNode):
                servo_seat = Frame()
                servo = HeldServo()
                servo.ears.on(servo_seat)

        self.assertRefused(build, 'Bare', 'servo.ears', 'by its name')

    # slide-by-mate 2.1: the `Prismatic` case moved out to
    # `test_a_freedom_may_be_a_prismatic`; the refusal names the two
    # kinds a mate accepts.
    def test_other_freedoms_are_refused(self):
        for freedom in (lambda: Orbit(axis=(0, 0, 1)),
                        lambda: Free()):
            def build():
                class Sliding(AssemblyNode):
                    pin = Frame()
                    part = Pin()
                    slide = part.hinge.on(pin, freedom())

            with self.subTest(freedom=type(freedom()).__name__):
                self.assertRefused(build, 'Sliding', 'slide', 'Revolute',
                                   'Prismatic', 'a Revolute or a Prismatic',
                                   type(freedom()).__name__, 'no freedom')

    # slide-by-mate 2.1: a mate's freedom may be a `Prismatic`.
    def test_a_freedom_may_be_a_prismatic(self):
        Palm = slide_fixtures().Palm

        found = mates_module().declared_mates(Palm)
        self.assertEqual(list(found), ['left_grip', 'right_grip'])
        for name, finger, seat in (('left_grip', 'left_finger', 'left_seat'),
                                   ('right_grip', 'right_finger',
                                    'right_seat')):
            with self.subTest(mate=name):
                mate = found[name]
                self.assertEqual(mate.moving.written, f'{finger}.origin')
                self.assertIs(mate.moving.frame, slide_fixtures().Finger.origin)
                self.assertIs(mate.fixed, getattr(Palm, seat))

    # hold-by-mate 2.6: a rigid mate is not a coordinate, so it is
    # refused wherever a coordinate is named.
    def test_a_rigid_mate_is_not_a_relations_end(self):
        from machinome.simulation import Driver

        def body():
            class Bodied(AssemblyNode):
                servo_seat = Frame()
                servo = HeldServo()
                travel = RotationalPort()
                bolted = servo.ears.on(servo_seat)
                bolted.drives(travel)

        def arithmetic():
            class Summed(AssemblyNode):
                servo_seat = Frame()
                servo = HeldServo()
                travel = RotationalPort()
                bolted = servo.ears.on(servo_seat)
                (bolted + 1).drives(travel)

        def wiring():
            class Wired(AssemblyNode):
                servo_seat = Frame()
                servo = HeldServo()
                bolted = servo.ears.on(servo_seat)
                wheel = JointedPin(spin=bolted)

        def path():
            class HeldShin(AssemblyNode):
                servo_seat = Frame()
                servo = HeldServo()
                bolted = servo.ears.on(servo_seat)

            class Root(AssemblyNode):
                angle = Driver(default=0.0, unit='deg')
                shin = HeldShin()
                angle.drives(shin.bolted)

        for build in (body, arithmetic, wiring, path):
            with self.subTest(route=build.__name__):
                self.assertRefused(build, 'bolted', 'owns no coordinate')

    # hold-by-mate 2.7: what stays refused for a rigid mate.
    def test_a_held_part_is_held_once(self):
        def rigid():
            class Twice(AssemblyNode):
                servo_seat = Frame()
                other_seat = Frame(at=(0, 0, 9))
                servo = HeldServo()
                bolted = servo.ears.on(servo_seat)
                again = servo.ear_near.on(other_seat)

        def freed():
            class Twice(AssemblyNode):
                servo_seat = Frame()
                other_seat = Frame(at=(0, 0, 9))
                servo = HeldServo()
                bolted = servo.ears.on(servo_seat)
                swing = servo.ear_near.on(other_seat, Revolute())

        for build, second in ((rigid, 'again'), (freed, 'swing')):
            with self.subTest(second=second):
                self.assertRefused(build, 'Twice', 'bolted', second, 'loop')

    def test_a_fixed_end_on_a_held_sibling_is_refused(self):
        def build():
            class Screwed(AssemblyNode):
                servo_seat = Frame()
                servo = HeldServo()
                screw = HeldScrew()
                bolted = servo.ears.on(servo_seat)
                screwed = screw.head.on(servo.ear_near)

        message = self.assertRefused(build, 'screwed', "'servo'", 'bolted')
        self.assertNotIn('moves it', message)

    def test_a_rigid_mate_on_an_inherited_child_is_refused(self):
        def build():
            class Base(AssemblyNode):
                servo_seat = Frame()
                servo = HeldServo()

            class Mating(Base):
                bolted = Base.servo.ears.on(Base.servo_seat)

        message = self.assertRefused(build, 'Mating', 'bolted', "'servo'",
                                     'Base')
        self.assertNotIn('joint of its own', message)

    # slide-by-mate 2.7: a slide's stated anchor follows the `Revolute`
    # freedom's rules: three numbers, never a function or a parameter.
    def test_a_slides_stated_anchor_is_three_numbers(self):
        def function():
            class Lifted(AssemblyNode):
                pin = Frame()
                part = Pin()
                slide = part.hinge.on(pin, Prismatic(
                    axis=(0, 1, 0), at=lambda node: (0, 0, 0)))

        def token():
            class Lifted(AssemblyNode):
                lift = Length(5)
                pin = Frame()
                part = Pin()
                slide = part.hinge.on(pin, Prismatic(axis=(0, 1, 0),
                                                     at=(0, 0, lift)))

        for build, fragment in (
                (function, 'a stated anchor is three numbers in this version'),
                (token, 'resolve against the moving child')):
            with self.subTest(case=build.__name__):
                self.assertRefused(build, 'Lifted', 'slide', "freedom's at",
                                   fragment)

    # state-the-mate-line 2.1: the refusal of a stated line is gone.
    def test_a_freedom_may_state_its_line(self):
        for label, freedom in (
                ('axis', lambda: Revolute(axis=(0, 0, 1), unit='deg')),
                ('at', lambda: Revolute(at=(0, 0, 0), unit='deg')),
                ('both', lambda: Revolute(axis=(0, 0, 1), at=(0, 0, 0),
                                          unit='deg'))):
            with self.subTest(label=label):
                class Stated(AssemblyNode):
                    pin = Frame()
                    part = Pin()
                    swing = part.hinge.on(pin, freedom())

                self.assertEqual(
                    list(mates_module().declared_mates(Stated)), ['swing'])

    # state-the-mate-line 2.2: a stated line is three numbers.
    STATED_IN_THE_ASSEMBLY = ('written in the assembly and read in the '
                              "moving child's frame")

    def test_a_stated_line_is_numbers(self):
        def token():
            class Lifted(AssemblyNode):
                lift = Length(5)
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(pin, Revolute(at=(0, 0, lift)))

        def formula():
            class Lifted(AssemblyNode):
                lift = Length(5)
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(pin, Revolute(at=(0, 0, lift * 2)))

        def two_components():
            class Lifted(AssemblyNode):
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(pin, Revolute(axis=(0, 1)))

        def a_bool():
            class Lifted(AssemblyNode):
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(pin, Revolute(axis=(0, 0, True)))

        # state-the-freedom-per-instance 2.1: the `callable_axis` case
        # moved out to `test_a_freedom_axis_or_range_may_be_a_function`.
        for build, argument in ((token, 'at'), (formula, 'at'),
                                (two_components, 'axis'), (a_bool, 'axis')):
            with self.subTest(case=build.__name__):
                message = self.assertRefused(
                    build, 'Lifted', 'swing', f"freedom's {argument}",
                    self.STATED_IN_THE_ASSEMBLY)
                self.assertNotIn('two frames supply', message)

    # state-the-mate-line 2.3: a stated axis has a direction.
    def test_a_stated_axis_has_a_direction(self):
        def build():
            class Flat(AssemblyNode):
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(pin, Revolute(axis=(0, 0, 0)))

        self.assertRefused(build, 'Flat', 'swing', "freedom's axis",
                           'an axis of zero length states no line')

    def test_a_freedom_range_that_depends_on_a_declarer(self):
        def token():
            class Ranged(AssemblyNode):
                limit = Angle(90)
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(pin, Revolute(range=(0, limit)))

        # state-the-freedom-per-instance 2.1: the `whole` case moved out
        # to `test_a_freedom_axis_or_range_may_be_a_function`.
        # mates-in-mechanical-contracts admits assembly-scoped Bound reads.
        for build in (token,):
            with self.subTest(range=build.__name__):
                self.assertRefused(build, 'Ranged', 'swing', 'range')

    # state-the-freedom-per-instance 2.1: the refusals of a function
    # `axis` and a whole-range function are gone.
    def test_a_freedom_axis_or_range_may_be_a_function(self):
        for label, freedom in (
                ('axis', lambda: Revolute(axis=lambda node: (0, 0, 1))),
                ('range', lambda: Revolute(range=lambda node: (0, 90)))):
            with self.subTest(label=label):
                class Handed(AssemblyNode):
                    pin = Frame()
                    part = Pin()
                    swing = part.hinge.on(pin, freedom())

                self.assertEqual(
                    list(mates_module().declared_mates(Handed)), ['swing'])

    # state-the-freedom-per-instance 2.2: a function `at` stays refused,
    # with its own reason.
    def test_a_stated_anchor_is_not_a_function(self):
        def build():
            class Anchored(AssemblyNode):
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(
                    pin, Revolute(at=lambda node: (0, 0, 0)))

        message = self.assertRefused(
            build, 'Anchored', 'swing', "freedom's at",
            'a stated anchor is three numbers in this version')
        self.assertNotIn('called with the moving child', message)

    def test_a_range_over_the_coordinate_itself_is_accepted(self):
        class Ranged(AssemblyNode):
            pin = Frame()
            part = Pin()
            swing = part.hinge.on(
                pin, Revolute(range=(-90, lambda own: 90), unit='deg'))

        self.assertEqual(list(mates_module().declared_mates(Ranged)),
                         ['swing'])

    def test_a_freedom_already_declared(self):
        def in_body():
            class Reused(AssemblyNode):
                pin = Frame()
                part = Pin()
                free = Revolute(unit='deg')
                swing = part.hinge.on(pin, free)

        def elsewhere():
            class Reused(AssemblyNode):
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(pin, JointedPin.spin)

        for build in (in_body, elsewhere):
            with self.subTest(where=build.__name__):
                self.assertRefused(build, 'Reused', 'swing', 'freedom',
                                   'already')

    def test_a_mate_name_the_child_already_answers_to(self):
        class WithJoint(Solid2Node):
            hinge = Frame(z=(0, 1, 0))
            elbow = Revolute(axis=(0, 1, 0))

            def render(self):
                return cube(1)

        class WithParameter(Solid2Node):
            hinge = Frame(z=(0, 1, 0))
            elbow = Length(3)

            def render(self):
                return cube(1)

        class WithFrame(Solid2Node):
            hinge = Frame(z=(0, 1, 0))
            elbow = Frame()

            def render(self):
                return cube(1)

        class WithMethod(Solid2Node):
            hinge = Frame(z=(0, 1, 0))

            def elbow(self):
                return None

            def render(self):
                return cube(1)

        for child in (WithJoint, WithParameter, WithFrame, WithMethod):
            def build():
                class UpperArm(AssemblyNode):
                    pin = Frame()
                    forearm = child()
                    elbow = forearm.hinge.on(pin, Revolute())

            with self.subTest(child=child.__name__):
                self.assertRefused(build, 'UpperArm', 'elbow',
                                   child.__name__)

    def test_a_subclass_redeclaring_the_mated_child(self):
        arm = fixtures()

        def build():
            class Reforged(arm.MatedArm):
                forearm = arm.MatedForearm()

        self.assertRefused(build, 'Reforged', 'elbow', 'forearm')

    def test_a_subclass_cannot_mate_a_child_its_base_declares(self):
        def build():
            class Base(AssemblyNode):
                pin = Frame()
                part = Pin()

            class Mating(Base):
                swing = Base.part.hinge.on(Base.pin, Revolute())

        self.assertRefused(build, 'Mating', 'swing', 'part', 'Base')

    def test_a_mate_and_a_parameter_cannot_share_a_name(self):
        def build():
            class Clashing(AssemblyNode):
                pin = Frame()
                part = Pin()
                swing = Length(3)
                swing = part.hinge.on(pin, Revolute())  # noqa: F811

        self.assertRefused(build, 'swing', 'mate')


##############################################
# 4.4 A relation in the declaring body names the mate

class RelationNamesTheMateTest(BaseNodeTest):

    def test_a_relation_in_the_body_names_the_mate(self):
        class Belted(AssemblyNode):
            pin = Frame()
            part = Pin()
            belt = JointedPin()
            swing = part.hinge.on(pin, Revolute(unit='deg'))
            swing.drives(belt.spin, ratio=2)

        self.assertEqual(list(mates_module().declared_mates(Belted)),
                         ['swing'])

    def test_a_mates_coordinate_is_wired_like_any_other(self):
        GaugedArm = fixtures().GaugedArm

        self.assertIn('elbow', declared_ports(GaugedArm))


##############################################
# 5. What a mate compiles to

def hand_written(angle=None, reach=None):
    """Thor's elbow as the project writes it today: `Arm`, placed by
    `render()` and jointed by `Forearm`'s own class."""
    from .joint_project.arm import Arm

    arm = Arm() if reach is None else Arm(reach=reach)
    arm.set_state(angle=0 if angle is None else angle)
    return arm


def rest_of(node):
    """`node`'s operations that are not motion: its rest placement."""
    return [operation.serialized for operation in node.operations
            if not getattr(operation, '_motion', False)]


def matrix_of(serialized_operations):
    """The 4x4 an operation chain composes to, applied in list order."""
    import numpy as np
    import trimesh

    matrix = np.eye(4)
    for operation in serialized_operations:
        if operation[0] == 'r':
            step = trimesh.transformations.rotation_matrix(
                math.radians(float(operation[1])),
                [float(component) for component in operation[2]])
        else:
            step = trimesh.transformations.translation_matrix(
                [float(component) for component in operation[1]])
        matrix = step @ matrix
    return matrix


class RestPlacementTest(BaseNodeTest):
    """5.1 to 5.7: the moving child's rest placement."""

    def assertSameRest(self, mated, hand):
        self.assertEqual([operation[0] for operation in mated],
                         [operation[0] for operation in hand])
        for ours, theirs in zip(mated, hand):
            if ours[0] == 'r':
                self.assertEqual(ours[1], theirs[1])
                self.assertEqual(list(ours[2]), list(theirs[2]))
            else:
                self.assertEqual(numbers(ours), numbers(theirs))

    def test_the_elbow_rests_where_thors_render_puts_it(self):
        arm = fixtures().MatedArm()
        arm.render()

        mated = serialized(arm.forearm)
        self.assertEqual(mated[0], ['r', '90', [1, 0, 0]])
        self.assertEqual(numbers(mated[1]), [0.0, 241.5, 68.0])
        self.assertSameRest(mated, rest_of(hand_written().forearm))

    def test_the_rest_follows_the_arms_reach(self):
        arm = fixtures().MatedArm(reach=150)
        arm.render()

        mated = serialized(arm.forearm)
        self.assertEqual(numbers(mated[1]), [0.0, 231.5, 68.0])
        self.assertSameRest(mated, rest_of(hand_written(reach=150).forearm))

    def test_the_shoulder_rests_where_thors_render_puts_it(self):
        housing = fixtures().MatedHousing()
        housing.render()

        mated = serialized(housing.art2)
        self.assertEqual([operation[0] for operation in mated], ['r', 't'])
        self.assertEqual(mated[0][1], '180')
        root = math.sqrt(0.5)
        for component, expected in zip(mated[0][2], (0, root, root)):
            self.assertAlmostEqual(float(component), expected, delta=1e-9)
        for component, expected in zip(numbers(mated[1]), (0, -68, 123)):
            self.assertAlmostEqual(component, expected, delta=1e-9)

        thor = [['r', '180', [0, 0.7071, 0.7071]], ['t', ['0', '-68', '123']]]
        self.assertTrue(
            (abs(matrix_of(mated) - matrix_of(thor)) < 1e-4).all())

    def test_x_fixes_the_rest_attitude(self):
        arm = fixtures().DefaultXArm()
        arm.render()

        mated = serialized(arm.forearm)
        self.assertEqual(mated[0][1], '120')
        third = 1 / math.sqrt(3)
        for component in mated[0][2]:
            self.assertAlmostEqual(float(component), third, delta=1e-9)
        for component, expected in zip(numbers(mated[1]),
                                       (-81.5, 160.0, 68.0)):
            self.assertAlmostEqual(component, expected, delta=1e-9)

    def test_a_fixed_end_on_a_still_child_uses_its_placement(self):
        pedestal = fixtures().Pedestal()
        pedestal.render()

        self.assertEqual(serialized(pedestal.base), [['t', ['0', '0', '10']]])
        self.assertEqual([numbers(operation)
                          for operation in serialized(pedestal.housing)],
                         [[0.0, 0.0, 89.0]])

    def test_a_fixed_child_placed_by_no_number_refuses_the_mate(self):
        class Stiff(AssemblyNode):
            seat = Frame(at=(0, 0, 79))

        class Floating(AssemblyNode):
            base = Stiff()
            housing = fixtures().Turret()

            yaw = housing.origin.on(base.seat, Revolute(unit='deg'))

            def render(self):
                self.base.translate(['x', 0, 0])

        with self.assertRaises(ValueError) as raised:
            Floating().render()

        message = str(raised.exception)
        for fragment in ('yaw', 'base', 'not a number'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_coinciding_frames_place_nothing(self):
        class Flush(AssemblyNode):
            pin = Frame(at=(0, 0, -5), z=(0, 0, -1))
            part = Pin()
            swing = part.foot.on(pin, Revolute(unit='deg'))

        resting = Flush()
        resting.render()
        self.assertEqual(serialized(resting.part), [])

        # Not because the mate did nothing: bound, it turns the part
        # about the frames' shared line, and still adds no rest
        # operation around it.
        turned = Flush()
        turned.swing = 30
        turned.render()
        self.assertEqual([operation[0] for operation
                          in serialized(turned.part)], ['t', 'r', 't'])
        self.assertEqual(serialized(turned.part)[1], ['r', '30', [0, 0, -1]])
        self.assertEqual(rest_of(turned.part), [])

    def test_a_mated_child_cannot_be_placed_by_hand(self):
        MatedArm = fixtures().MatedArm

        class Handed(MatedArm):
            def render(self):
                self.forearm.translate([0, 0, 1])

        with self.assertRaises(ValueError) as raised:
            Handed().render()

        message = str(raised.exception)
        for fragment in ('Handed', 'forearm', 'elbow'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_an_unmated_sibling_is_still_placed_by_hand(self):
        MatedArm = fixtures().MatedArm

        class Braced(MatedArm):
            brace = Pin()

            def render(self):
                self.brace.translate([0, 0, 7])

        braced = Braced()
        braced.render()

        self.assertEqual(serialized(braced.brace), [['t', ['0', '0', '7']]])
        self.assertEqual(serialized(braced.forearm)[0], ['r', '90', [1, 0, 0]])

    def test_a_rerunning_render_does_not_stack_the_placement(self):
        import warnings

        from machinome.simulation import Driver

        MatedArm = fixtures().MatedArm

        class Legacy(MatedArm):
            lift = Driver(default=0.0, unit='mm')

            def render(self):
                self.lift  # a read: a legacy render, re-run per binding

        legacy = Legacy()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', FutureWarning)
            for lift in (1.0, 2.0, 3.0):
                with self.subTest(lift=lift):
                    legacy.set_state(lift=lift)
                    self.assertTrue(legacy.__dict__.get('_legacy_render'))
                    self.assertEqual(rest_of(legacy.forearm),
                                     [['r', '90', [1, 0, 0]],
                                      ['t', ['0.0', '241.5', '68.0']]])


class InstalledJointTest(BaseNodeTest):
    """5.8 to 5.10: the joint a mate gives the child."""

    def test_the_elbow_joint_is_the_one_thor_writes_by_hand(self):
        arm = fixtures().MatedArm()

        joints = declared_joints(type(arm.forearm))
        self.assertEqual(list(joints), ['elbow'])
        axis, anchor, span = joints['elbow'].arguments(arm.forearm)
        self.assertEqual(axis, (0, 1, 0))
        self.assertEqual(anchor, (0.0, 0.0, 81.5))
        self.assertEqual(span, (-135, 135))

    def test_binding_the_mate_places_the_hand_written_operations(self):
        arm = fixtures().MatedArm()
        arm.elbow = 30
        arm.render()

        mated = serialized(arm.forearm)
        hand = serialized(hand_written(angle=30).forearm)
        self.assertEqual([operation[0] for operation in mated],
                         ['t', 'r', 't', 'r', 't'])
        self.assertEqual(numbers(mated[0]), [0.0, 0.0, -81.5])
        self.assertEqual(mated[1], ['r', '30', [0, 1, 0]])
        self.assertEqual(numbers(mated[2]), [0.0, 0.0, 81.5])
        for ours, theirs in zip(mated, hand):
            self.assertEqual(ours[0], theirs[0])
            if ours[0] == 't':
                self.assertEqual(numbers(ours), numbers(theirs))
            else:
                self.assertEqual(ours[1:], theirs[1:])

    def test_a_mated_wheel_keeps_its_own_spin_inside_the_mate(self):
        knuckle = fixtures().Knuckle()
        knuckle.steer = 20
        knuckle.render()
        knuckle.wheel.spin = 10

        self.assertEqual(list(declared_joints(type(knuckle.wheel))),
                         ['spin', 'steer'])
        operations = serialized(knuckle.wheel)
        self.assertEqual([operation[0] for operation in operations],
                         ['r', 'r', 't'])
        self.assertEqual(operations[0], ['r', '10', [0, 1, 0]])
        self.assertEqual(operations[1], ['r', '20', [0, 0, 1]])
        self.assertEqual(numbers(operations[2]), [10.0, 0.0, 0.0])

    def test_a_mated_child_keeps_its_identity(self):
        arm = fixtures().MatedArm()
        MatedForearm = fixtures().MatedForearm

        self.assertIsNot(type(arm.forearm), MatedForearm)
        self.assertTrue(issubclass(type(arm.forearm), MatedForearm))
        self.assertEqual(type(arm.forearm).__name__, 'MatedForearm')
        self.assertEqual(arm.forearm.uniq_id,
                         MatedForearm(reach=160).uniq_id)


class MateCoordinateTest(BaseNodeTest):
    """5.11 to 5.14: the coordinate a mate owns on the assembly."""

    def root(self):
        from machinome.simulation import Driver

        MatedArm = fixtures().MatedArm

        class Root(AssemblyNode):
            angle = Driver(default=0.0, unit='deg')
            arm = MatedArm()
            angle.drives(arm.elbow)

        return Root()

    def test_the_mates_coordinate_is_a_port_of_the_assembly(self):
        port = declared_ports(fixtures().MatedArm)['elbow']

        self.assertIsInstance(port, RotationalPort)
        self.assertEqual(port.unit, 'deg')
        # ... and the child's joint is a second, WIRED coordinate of the
        # child, as any wired joint is.
        arm = fixtures().MatedArm()
        self.assertIn('elbow', declared_ports(type(arm.forearm)))

    def test_a_driver_turns_the_elbow_through_the_mate(self):
        root = self.root()
        root.set_state(angle=30)

        mated = serialized(root.arm.forearm)
        hand = serialized(hand_written(angle=30).forearm)
        self.assertEqual([operation[0] for operation in mated],
                         [operation[0] for operation in hand])
        self.assertEqual(mated[1], hand[1])
        for ours, theirs in zip(mated, hand):
            if ours[0] == 't':
                self.assertEqual(numbers(ours), numbers(theirs))

    def test_the_range_belongs_to_the_freedom(self):
        root = self.root()

        with self.assertRaises(JointRangeError) as raised:
            root.set_state(angle=150)

        self.assertIn('elbow', str(raised.exception))

    def test_a_mates_coordinate_wires_into_a_port(self):
        gauged = fixtures().GaugedArm()
        gauged.elbow = 25
        gauged.render()

        self.assertEqual(gauged.gauge.turn.value, 25)
        self.assertEqual(gauged.forearm.elbow.value, 25)

    def test_an_unbound_mate_rests(self):
        arm = fixtures().MatedArm()
        arm.render()

        self.assertEqual([operation[0] for operation
                          in serialized(arm.forearm)], ['r', 't'])

    def test_a_mate_bound_then_unbound_clears_its_motion(self):
        MatedArm = fixtures().MatedArm

        class Toggled(MatedArm):
            binding = True

            def simulate(self):
                if type(self).binding:
                    self.elbow = 30

        toggled = Toggled()
        toggled.render()
        self.assertEqual(len(serialized(toggled.forearm)), 5)

        Toggled.binding = False
        toggled.render()

        self.assertEqual([operation[0] for operation
                          in serialized(toggled.forearm)], ['r', 't'])
        self.assertIsNone(toggled.forearm.elbow._value)

    def test_the_installed_joint_is_not_bound_in_simulate(self):
        MatedArm = fixtures().MatedArm

        class Meddling(MatedArm):
            def simulate(self):
                self.forearm.elbow = 10

        with self.assertRaises(ValueError) as raised:
            Meddling().render()

        message = str(raised.exception)
        for fragment in ('elbow', 'mate', 'Meddling'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_the_installed_joint_is_not_driven_by_path(self):
        from machinome.simulation import Driver

        MatedArm = fixtures().MatedArm

        class Root(AssemblyNode):
            angle = Driver(default=0.0, unit='deg')
            arm = MatedArm()
            angle.drives(arm.forearm.elbow)

        with self.assertRaises(ValueError) as raised:
            Root().set_state(angle=10)

        message = str(raised.exception)
        for fragment in ('arm.elbow', 'mate'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_the_installed_joint_may_be_read_as_a_source(self):
        from machinome.simulation import Driver

        MatedArm = fixtures().MatedArm
        Dial = fixtures().Dial

        class Root(AssemblyNode):
            angle = Driver(default=0.0, unit='deg')
            arm = MatedArm()
            dial = Dial()
            angle.drives(arm.elbow)
            arm.forearm.elbow.drives(dial.turn)

        root = Root()
        root.set_state(angle=30)

        self.assertEqual(root.dial.turn.value, 30)

    def test_a_relation_in_the_body_drives_from_the_mate(self):
        class Belted(AssemblyNode):
            pin = Frame()
            part = Pin()
            belt = JointedPin()
            swing = part.hinge.on(pin, Revolute(unit='deg'))
            swing.drives(belt.spin, ratio=2)

        belted = Belted()
        belted.swing = 15
        belted.render()

        self.assertEqual(belted.belt.spin.value, 30)
        self.assertEqual(belted.part.swing.value, 15)

    def test_a_derived_coordinate_reads_two_mates(self):
        housing = fixtures().MatedHousing()
        housing.shoulder = 10
        housing.art2.elbow = 20
        housing.render()

        self.assertAlmostEqual(housing.drive.value, 10 + 5.85 * 20,
                               places=9)
        # Both mates reached their children's joints.
        self.assertEqual(housing.art2.shoulder.value, 10)
        self.assertEqual(housing.art2.forearm.elbow.value, 20)


##############################################
# 6. A mate publishes nothing new

BASE_DOCUMENTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'base_documents')


def published(node):
    """`node`'s document, as `tests/test_running_document.py`'s
    `document()` assembles it, with the declared defaults bound and each
    node's checkout-dependent `mtime` normalized."""
    from machinome.simulation.enumeration import bind_declared_defaults

    from .test_running_document import document

    bind_declared_defaults(node)
    body = document(node)

    def normalized(entry):
        entry['mtime'] = None
        for child in entry.get('children', ()):
            normalized(child)

    normalized(body['root'])
    return body


def entry_of(document, *path):
    entry = document['root']
    for name in path:
        entry = next(child for child in entry['children']
                     if child['name'] == name)
    return entry


def walk(entry):
    yield entry
    for child in entry.get('children', ()):
        yield from walk(child)


class DocumentTest(BaseNodeTest):

    def test_a_machine_without_mates_is_unchanged_in_every_byte(self):
        from .joint_project.arm import Arm

        with open(os.path.join(BASE_DOCUMENTS, 'mate_free_arm.json')) as base:
            expected = base.read()

        self.assertEqual(json.dumps(published(Arm()), indent=2) + '\n',
                         expected)

    def test_a_mated_machine_needs_no_newer_consumer(self):
        from .joint_project.arm import Arm

        mated = published(fixtures().MatedElbowMachine())
        hand = published(Arm())

        self.assertEqual(mated['version'], hand['version'])
        self.assertEqual(mated['format'], hand['format'])
        self.assertEqual(set(mated), set(hand))
        self.assertEqual(mated['drivers'], hand['drivers'])

        ours = entry_of(mated, 'arm', 'forearm')['operations']
        theirs = entry_of(hand, 'forearm')['operations']
        self.assertEqual([operation[0] for operation in ours],
                         [operation[0] for operation in theirs])
        for mine, written in zip(ours, theirs):
            if mine[0] == 'r':
                self.assertEqual(mine[1:], written[1:])
            else:
                self.assertEqual([float(value) for value in mine[1]],
                                 [float(value) for value in written[1]])

        fields = {frozenset(entry) for entry in walk(hand['root'])}
        for entry in walk(mated['root']):
            with self.subTest(node=entry['name']):
                self.assertIn(frozenset(entry), fields)


##############################################
# state-the-mate-line: a freedom may state its own line
#
# A design's connectors are ATTACHMENT frames, and the line a part turns
# about need not be the moving frame's `z` nor pass through its origin.
# The fixtures are Thor's connectors verbatim (`mate_project/verbatim.py`)
# and the mates that state each line (`mate_project/line.py`), every one
# held to a hand-placed twin.

def line_fixtures():
    from .mate_project import line

    return line


def verbatim_fixtures():
    from .mate_project import verbatim

    return verbatim


BINDINGS = (-90, -30, 0, 30, 90, None)


def leaves_of(node, above=None, path=''):
    """Each leaf under `node` with the world matrix its operations and
    every ancestor's compose to, as `(path, matrix)`, the path relative
    to `node`."""
    import numpy as np

    from machinome.node.declarative import declared_children

    matrix = (np.eye(4) if above is None else above) @ matrix_of(
        serialized(node))
    names = (list(declared_children(type(node)))
             if isinstance(node, AssemblyNode) else [])
    if not names:
        yield path, matrix
        return
    for name in names:
        yield from leaves_of(getattr(node, name), matrix, f'{path}/{name}')


class StatedLineTest(BaseNodeTest):
    """2.4 to 2.8: the joint a freedom that states its line installs."""

    def assertSameOperations(self, mated, hand, delta=1e-9):
        self.assertEqual([operation[0] for operation in mated],
                         [operation[0] for operation in hand])
        for ours, theirs in zip(mated, hand):
            if ours[0] == 'r':
                self.assertAlmostEqual(float(ours[1]), float(theirs[1]),
                                       delta=delta)
                for mine, written in zip(ours[2], theirs[2]):
                    self.assertAlmostEqual(float(mine), float(written),
                                           delta=delta)
            else:
                for mine, written in zip(numbers(ours), numbers(theirs)):
                    self.assertAlmostEqual(mine, written, delta=delta)

    def posed(self, cls, child, joint, value, mate=None):
        """`cls` rendered with `joint` of `child` bound to `value` -- or,
        for a mated assembly, the mate's coordinate `mate`."""
        node = cls()
        if value is not None:
            if mate is not None:
                setattr(node, mate, value)
            else:
                setattr(getattr(node, child), joint, value)
        node.render()
        return node

    def test_the_joint_turns_about_the_stated_line(self):
        shoulder = line_fixtures().VerbatimShoulder
        housing = shoulder()

        joints = declared_joints(type(housing.art2))
        self.assertEqual(list(joints), ['shoulder'])
        axis, anchor, _span = joints['shoulder'].arguments(housing.art2)
        self.assertEqual(axis, (0, 0, 1))
        self.assertEqual(anchor, (0.0, 0.0, 0.0))

        # The stated values reach the joint untouched: nothing carried.
        mate = mates_module().declared_mates(shoulder)['shoulder']
        self.assertIs(mate.joint.axis, mate.freedom.axis)
        self.assertIs(mate.joint.at, mate.freedom.at)

        housing.shoulder = 30
        housing.render()
        operations = serialized(housing.art2)
        self.assertEqual([operation[0] for operation in operations],
                         ['r', 'r', 't'])
        self.assertEqual(operations[0], ['r', '30', [0, 0, 1]])

    def test_an_anchor_at_the_childs_origin_drops_the_centring_pair(self):
        by_frame = fixtures().MatedHousing()
        by_frame.shoulder = 30
        by_frame.render()
        stated = line_fixtures().AnchoredHousing()
        stated.shoulder = 30
        stated.render()

        framed = serialized(by_frame.art2)
        self.assertEqual([operation[0] for operation in framed],
                         ['t', 'r', 't', 'r', 't'])
        self.assertEqual(numbers(framed[0]), [0.0, 0.0, -68.0])
        self.assertEqual(framed[1], ['r', '30', [0, 0, 1]])
        self.assertEqual(numbers(framed[2]), [0.0, 0.0, 68.0])

        anchored = serialized(stated.art2)
        self.assertEqual([operation[0] for operation in anchored],
                         ['r', 'r', 't'])
        self.assertEqual(anchored[0], ['r', '30', [0, 0, 1]])
        self.assertEqual(anchored[1:], framed[3:])

        self.assertTrue(
            (abs(matrix_of(anchored) - matrix_of(framed)) < 1e-12).all())

    def test_thors_across_and_reversed_shapes_reproduce_their_twins(self):
        line = line_fixtures()
        verbatim = verbatim_fixtures()
        for mated_cls, hand_cls, child, joint in (
                (line.VerbatimShoulder, verbatim.HandShoulder, 'art2',
                 'shoulder'),
                (line.VerbatimWrist, verbatim.HandWrist, 'art56', 'wrist'),
                (line.VerbatimYaw, verbatim.HandYaw, 'art4', 'yaw')):
            for value in BINDINGS:
                with self.subTest(mate=joint, value=value):
                    mated = self.posed(mated_cls, child, joint, value,
                                       mate=joint)
                    hand = self.posed(hand_cls, child, joint, value)
                    self.assertSameOperations(
                        serialized(getattr(mated, child)),
                        serialized(getattr(hand, child)))
                    ours = dict(leaves_of(mated))
                    theirs = dict(leaves_of(hand))
                    self.assertEqual(sorted(ours), [f'/{child}/plate'])
                    self.assertEqual(sorted(theirs), [f'/{child}/plate'])
                    for path in ours:
                        self.assertTrue(
                            (abs(ours[path] - theirs[path]) < 1e-9).all(),
                            path)

        shoulder = rest_of(self.posed(line.VerbatimShoulder, 'art2',
                                      'shoulder', None).art2)
        self.assertEqual(shoulder[0][1], '180')
        root = math.sqrt(0.5)
        for component, expected in zip(shoulder[0][2], (0, root, root)):
            self.assertAlmostEqual(float(component), expected, delta=1e-9)
        for component, expected in zip(numbers(shoulder[1]), (0, -68, 123)):
            self.assertAlmostEqual(component, expected, delta=1e-9)

        wrist = rest_of(self.posed(line.VerbatimWrist, 'art56', 'wrist',
                                   None).art56)
        self.assertEqual(wrist[0], ['r', '90', [0, 0, 1]])

    def test_a_stated_axis_keeps_the_sign_a_reversed_frame_would_flip(self):
        stated = self.posed(line_fixtures().VerbatimYaw, 'art4', 'yaw', 30,
                            mate='yaw')
        by_frame = self.posed(verbatim_fixtures().ReversedYawByFrame,
                              'art4', 'yaw', 30, mate='yaw')

        self.assertEqual(serialized(stated.art4)[0], ['r', '30', [0, 0, 1]])
        self.assertEqual(serialized(by_frame.art4)[0],
                         ['r', '30', [0, 0, -1]])

    def test_a_freedom_stating_no_line_takes_the_frames(self):
        for owner, name, frame in (
                (fixtures().MatedArm, 'elbow', fixtures().MatedForearm.hinge),
                (fixtures().MatedHousing, 'shoulder', fixtures().MatedArm.bore),
                (verbatim_fixtures().ReversedYawByFrame, 'yaw',
                 verbatim_fixtures().Art4.bore)):
            with self.subTest(mate=name):
                joint = mates_module().declared_mates(owner)[name].joint
                self.assertIs(joint.axis, frame.z)
                self.assertIs(joint.at, frame.at)


class StatedLineDocumentTest(BaseNodeTest):
    """2.9: a mate stating no line publishes the bytes it published
    before; one that states its line publishes it as operations."""

    def test_a_mate_that_states_no_line_is_unchanged_in_every_byte(self):
        arm = fixtures()
        for filename, cls in (
                ('mated_elbow_machine.json', arm.MatedElbowMachine),
                ('mated_shoulder_machine.json', arm.MatedShoulderMachine)):
            with self.subTest(document=filename):
                with open(os.path.join(BASE_DOCUMENTS, filename)) as base:
                    expected = base.read()
                self.assertEqual(
                    json.dumps(published(cls()), indent=2) + '\n', expected)

    def test_a_stated_line_needs_no_newer_consumer(self):
        mated = published(line_fixtures().VerbatimShoulderMachine())
        hand = published(verbatim_fixtures().HandShoulderMachine())

        self.assertEqual(mated['version'], hand['version'])
        self.assertEqual(set(mated), set(hand))
        self.assertEqual(mated['drivers'], hand['drivers'])

        ours = entry_of(mated, 'housing', 'art2')['operations']
        theirs = entry_of(hand, 'housing', 'art2')['operations']
        self.assertEqual([operation[0] for operation in ours],
                         [operation[0] for operation in theirs])
        for mine, written in zip(ours, theirs):
            if mine[0] == 'r':
                if mine[1] == 'angle':
                    self.assertEqual(written[1], 'angle')
                else:
                    self.assertAlmostEqual(float(mine[1]), float(written[1]),
                                           delta=1e-9)
                for component, other in zip(mine[2], written[2]):
                    self.assertAlmostEqual(float(component), float(other),
                                           delta=1e-9)
            else:
                for component, other in zip(mine[1], written[1]):
                    self.assertAlmostEqual(float(component), float(other),
                                           delta=1e-9)

        fields = {frozenset(entry) for entry in walk(hand['root'])}
        for entry in walk(mated['root']):
            with self.subTest(node=entry['name']):
                self.assertIn(frozenset(entry), fields)


##############################################
# 8.1 The manual teaches the mate on the public contract

DOCS = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'docs')


def _section(text, heading):
    """The text of the `heading` section of an .rst page, up to the next
    heading of the same level."""
    lines = text.splitlines()
    start = lines.index(heading)
    underline = lines[start + 1]
    end = len(lines)
    for index in range(start + 2, len(lines) - 1):
        if (lines[index + 1] and set(lines[index + 1]) == set(underline)
                and len(lines[index + 1]) == len(lines[index])):
            end = index
            break
    return '\n'.join(lines[start:end])


def _code_blocks(text):
    """Every `.. code-block:: python` body in `text`, dedented."""
    import textwrap

    blocks = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != '.. code-block:: python':
            continue
        body = []
        for following in lines[index + 1:]:
            if following and not following.startswith(' '):
                break
            body.append(following)
        blocks.append(textwrap.dedent('\n'.join(body)).strip('\n'))
    return blocks


def _code_block_named(text, marker):
    """Select exactly one example by content, not its page ordinal."""
    matches = [block for block in _code_blocks(text) if marker in block]
    if len(matches) != 1:
        raise AssertionError(
            f'Expected one manual codeblock containing {marker!r}; '
            f'found {len(matches)}')
    return matches[0]


class ManualTest(BaseNodeTest):
    """The joints page teaches frames and mates with an example that
    runs, and the changelog names the feature above the release."""

    def page(self, *path):
        with open(os.path.join(DOCS, *path)) as handle:
            return handle.read()

    def test_the_joints_page_example_runs_as_it_says(self):
        section = _section(self.page('concepts', 'joints.rst'),
                           'Frames and mates')
        example = _code_blocks(section)[0]
        namespace = {'__name__': __name__}
        exec(compile(example, 'joints.rst', 'exec'), namespace)

        arm = namespace['UpperArm']()
        arm.render()

        operations = serialized(arm.forearm)
        self.assertEqual(operations[0], ['r', '90', [1, 0, 0]])
        self.assertEqual(numbers(operations[1]), [0.0, 241.5, 68.0])
        self.assertIn('(0, 241.5, 68)', section)
        self.assertEqual(
            list(mates_module().declared_mates(namespace['UpperArm'])),
            ['elbow'])

    def test_the_joints_page_states_a_line_across_a_connector(self):
        """state-the-mate-line 4.1: the second example, a connector whose
        `z` stands across the joint line, runs and turns about the line
        its freedom states."""
        section = _section(self.page('concepts', 'joints.rst'),
                           'Frames and mates')
        example = _code_blocks(section)[1]
        namespace = {'__name__': __name__}
        exec(compile(example, 'joints.rst', 'exec'), namespace)

        shoulder = namespace['Shoulder']()
        joint = declared_joints(type(shoulder.link))['shoulder']
        axis, anchor, _span = joint.arguments(shoulder.link)
        self.assertEqual(axis, (0, 0, 1))
        self.assertEqual(anchor, (0, 0, 0))

        shoulder.shoulder = 30
        shoulder.render()
        operations = serialized(shoulder.link)
        self.assertEqual(operations[0], ['r', '30', [0, 0, 1]])
        self.assertEqual(operations[1][1], '180')
        for component, expected in zip(numbers(operations[2]),
                                       (0, -68, 123)):
            self.assertAlmostEqual(component, expected, delta=1e-9)
        self.assertIn('(0, -68, 123)', section)

    def test_the_joints_page_states_a_handed_freedom(self):
        """state-the-freedom-per-instance 4.1: the handed example
        runs, and each side's installed joint turns about its
        side's axis within its side's range."""
        section = _section(self.page('concepts', 'joints.rst'),
                           'Frames and mates')
        example = _code_block_named(section, 'class Mount(AssemblyNode):')
        namespace = {'__name__': __name__}
        exec(compile(example, 'joints.rst', 'exec'), namespace)

        Mount = namespace['Mount']
        for left, axis, span, origin in (
                (True, (0, 1, 0), (-200, 80), [0.0, 62.5, 0.0]),
                (False, (0, -1, 0), (-80, 200), [0.0, -62.5, 0.0])):
            with self.subTest(left=left):
                mount = Mount(left=left)
                joint = declared_joints(type(mount.link))['turn']
                found_axis, _anchor, found_span = joint.arguments(mount.link)
                self.assertEqual(found_axis, axis)
                self.assertEqual(found_span, span)
                mount.render()
                self.assertEqual(numbers(serialized(mount.link)[0]), origin)
        self.assertNotIn('left', vars(namespace['Link']))
        for fragment in ('once', 'at=', 'the assembly'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)

    def test_the_joints_page_states_a_sliding_freedom(self):
        """slide-by-mate 4.1: the sliding example
        runs; binding one finger's mate slides both fingers,
        equally and oppositely, and the coordinate is a length."""
        section = _section(self.page('concepts', 'joints.rst'),
                           'Frames and mates')
        example = _code_block_named(section, 'class Palm(AssemblyNode):')
        namespace = {'__name__': __name__}
        exec(compile(example, 'joints.rst', 'exec'), namespace)

        Palm = namespace['Palm']
        port = declared_ports(Palm)['left_grip']
        self.assertIsInstance(port, TranslationalPort)
        self.assertEqual(port.unit, 'mm')
        palm = Palm()
        palm.left_grip = 10
        palm.render()
        for finger, axis in (('left_finger', (0, 1, 0)),
                             ('right_finger', (0, -1, 0))):
            with self.subTest(finger=finger):
                operations = serialized(getattr(palm, finger))
                self.assertEqual(operations[0][0], 't')
                self.assertEqual(numbers(operations[0]),
                                 [10.0 * component for component in axis])
        for fragment in ('``Prismatic``', 'slides', 'always states its',
                         'moves nothing', 'a length', "``'mm'``",
                         'neither a fresh ``Revolute`` nor a fresh '
                         '``Prismatic``'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, ' '.join(section.split()))

        reference = _section(self.page('reference', 'api.rst'),
                             'Frames and mates')
        self.assertIn('Prismatic(...))', reference)

    def test_the_joints_page_states_a_held_part(self):
        """hold-by-mate 4.1: the held-part example
        runs; the servo is placed by one rotation and one translation and
        the shin gains no port."""
        section = _section(self.page('concepts', 'joints.rst'),
                           'Frames and mates')
        example = _code_block_named(section, 'class Shin(AssemblyNode):')
        namespace = {'__name__': __name__}
        exec(compile(example, 'joints.rst', 'exec'), namespace)

        Shin = namespace['Shin']
        shin = Shin()
        shin.render()
        operations = serialized(shin.servo)
        self.assertEqual(operations[0], HELD_ROTATION)
        for found, expected in zip(numbers(operations[1]),
                                   (-0.98, -9.5, -7.0)):
            self.assertAlmostEqual(found, expected, delta=1e-9)
        self.assertEqual(declared_ports(Shin), {})
        self.assertIs(type(shin.servo), namespace['Servo'])
        self.assertIsNone(
            mates_module().declared_mates(Shin)['bolted'].freedom)
        text = ' '.join(section.split())
        for fragment in ('may leave its freedom out', 'connector onto '
                         'connector', 'no joint and no coordinate',
                         'the class of the part that holds it',
                         '``freedom`` is ``None``', 'one rotation where',
                         'a fixed end on a child that can move or that '
                         'another mate places'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, text)
        self.assertNotIn('a mate with no freedom at all', text)

        reference = _section(self.page('reference', 'api.rst'),
                             'Frames and mates')
        self.assertIn('``<child>.<frame>.on(<frame>)``',
                      ' '.join(reference.split()))

    def test_the_reference_lists_frames_and_mates(self):
        api = self.page('reference', 'api.rst')

        for entry in ('machinome.node.frames.Frame',
                      'machinome.node.frames.declared_frames',
                      'machinome.motion.mates.declared_mates'):
            with self.subTest(entry=entry):
                self.assertIn(entry, api)

    def test_the_changelog_names_the_mate_in_the_release_that_ships_it(self):
        changelog = self.page('project', 'changelog.rst')

        heading = 'Machinome 0.7.1\n---------------'
        self.assertIn(heading, changelog)
        release = changelog.split(heading, 1)[1].split('Machinome 0.7.0')[0]
        for fragment in ('Frame', '.on(', 'Revolute'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, release)


##############################################
# read-frames-and-mates, tasks 2.9 to 2.13: a mate's ends and freedom
# read off the class, and the line it turns about read from them and
# the moving child's resolved frames alone.

def resolved_frames(node):
    """`machinome.node.frames.resolved_frames`, imported where a test
    needs it, so each test names its own failure."""
    from machinome.node.frames import resolved_frames as read

    return read(node)


class Swung(Solid2Node):
    """A part whose connector sits 5 up its own `z`."""

    hinge = Frame(at=(0, 0, 5))

    def render(self):
        return cube(2, center=True)


class Swinging(AssemblyNode):
    """A freedom stating an axis, unnormalized, and leaving `at` out:
    the anchor is then the moving frame's origin, `(0, 0, 5)` in the
    part's own frame, not the `(0, 0, 0)` `freedom.at` reads."""

    pin = Frame()

    part = Swung()

    swing = part.hinge.on(pin, Revolute(axis=(0, 0, 2), unit='deg'))


class MateReadTest(BaseNodeTest):
    """The documented reads of a mate, off the class. 2.9 and 2.10 are
    GREEN GUARDS: the attributes exist at the base; this change
    documents them."""

    def mate(self, cls, name):
        return mates_module().declared_mates(cls)[name]

    def test_the_ends_and_freedom_of_a_mate_stating_no_line(self):
        arm = fixtures().MatedArm
        mate = self.mate(arm, 'elbow')

        self.assertEqual(mate.name, 'elbow')
        self.assertEqual(mate.moving.written, 'forearm.hinge')
        self.assertIsInstance(mate.fixed, Frame)
        self.assertIs(mate.fixed, arm.elbow_pin)
        self.assertEqual(mate.fixed.name, 'elbow_pin')
        self.assertIsNone(mate.freedom.axis)
        self.assertIs(mate.freedom.anchor_written, False)
        self.assertEqual(mate.freedom.range, (-135, 135))
        self.assertEqual(mate.freedom.unit, 'deg')

    def test_a_fixed_end_on_a_child_is_read_as_written(self):
        mate = self.mate(fixtures().Pedestal, 'yaw')

        self.assertEqual(mate.moving.written, 'housing.origin')
        self.assertNotIsInstance(mate.fixed, Frame)
        self.assertEqual(mate.fixed.written, 'base.seat')

    def test_a_stated_line_is_read_as_written(self):
        line = line_fixtures()

        shoulder = self.mate(line.VerbatimShoulder, 'shoulder').freedom
        self.assertEqual(shoulder.axis, (0, 0, 1))
        self.assertIs(shoulder.anchor_written, True)
        self.assertEqual(shoulder.at, (0, 0, 0))

        anchored = self.mate(line.AnchoredHousing, 'shoulder').freedom
        self.assertIsNone(anchored.axis)
        self.assertIs(anchored.anchor_written, True)

        wrist = self.mate(line.VerbatimWrist, 'wrist').freedom
        self.assertEqual(wrist.axis, (1, 0, 0))
        self.assertIs(wrist.anchor_written, False)

    def test_a_left_out_anchor_is_read_as_not_written(self):
        freedom = self.mate(Swinging, 'swing').freedom

        self.assertEqual(freedom.axis, (0, 0, 2))
        self.assertIs(freedom.anchor_written, False)

    def test_a_left_out_anchor_is_the_moving_frames_resolved_origin(self):
        node = Swinging()
        freedom = self.mate(Swinging, 'swing').freedom

        joint = declared_joints(type(node.part))['swing']
        _axis, anchor, _span = joint.arguments(node.part)
        self.assertEqual(anchor, (0.0, 0.0, 5.0))
        self.assertEqual(anchor, resolved_frames(node.part)['hinge'].at)
        self.assertNotEqual(anchor, tuple(freedom.at))

    def test_the_mates_line_from_the_documented_reads_alone(self):
        arm, line = fixtures(), line_fixtures()
        for cls, name in ((arm.MatedArm, 'elbow'),
                          (arm.Pedestal, 'yaw'),
                          (line.VerbatimShoulder, 'shoulder'),
                          (line.AnchoredHousing, 'shoulder'),
                          (line.VerbatimWrist, 'wrist'),
                          (Swinging, 'swing')):
            with self.subTest(mate=f'{cls.__name__}.{name}'):
                mate = self.mate(cls, name)
                node = cls()
                child_name, frame_name = mate.moving.written.split('.')
                child = getattr(node, child_name)
                moving = resolved_frames(child)[frame_name]
                freedom = mate.freedom

                # The rule the documentation states, in its own terms.
                axis = (freedom.axis if freedom.axis is not None
                        else moving.z)
                at = freedom.at if freedom.anchor_written else moving.at
                length = math.sqrt(sum(component * component
                                       for component in axis))
                axis = tuple(component / length for component in axis)

                joint = declared_joints(type(child))[name]
                installed_axis, installed_at, _span = joint.arguments(child)
                for ours, theirs in zip(axis + tuple(at),
                                        tuple(installed_axis)
                                        + tuple(installed_at)):
                    self.assertAlmostEqual(float(ours), float(theirs),
                                           delta=1e-12)


class ManualReadTest(BaseNodeTest):
    """The reference and the joints page teach the reads."""

    def page(self, *path):
        with open(os.path.join(DOCS, *path)) as handle:
            return handle.read()

    def test_the_reference_lists_the_reads(self):
        api = self.page('reference', 'api.rst')

        for entry in ('.. autofunction:: machinome.node.frames.resolved_frames',
                      '.. autoclass:: machinome.node.frames.ResolvedFrame',
                      '.. autoclass:: machinome.motion.mates.Mate'):
            with self.subTest(entry=entry):
                self.assertIn(entry, api)
        after = api.split(
            '.. autoclass:: machinome.node.frames.ResolvedFrame', 1)[-1]
        self.assertEqual(after.splitlines()[1].strip(), ':members: rotation')

    def test_the_docstrings_state_the_reads(self):
        from machinome.motion.mates import FrameRef, Mate
        from machinome.node.frames import ResolvedFrame

        for where, doc, fragments in (
                ('ResolvedFrame', ResolvedFrame.__doc__,
                 ('columns', 'int', 'float', 'rotation()')),
                ('Mate', Mate.__doc__,
                 ('declared_mates', 'name', 'moving', 'fixed', 'freedom',
                  'anchor_written', "moving frame's origin")),
                ('FrameRef.written', FrameRef.written.__doc__,
                 ("'<child>.<frame>'",)),
                ('Frame.name', Frame.name.__doc__, ('mate.fixed.name',)),
                ('Revolute.anchor_written', Revolute.anchor_written.__doc__,
                 ("moving frame's origin",))):
            for fragment in fragments:
                with self.subTest(where=where, fragment=fragment):
                    self.assertIn(fragment, doc or '')

    def test_the_joints_page_reads_frames_and_mates(self):
        # The frame-read block builds on the first block's `UpperArm`, as the
        # page's prose says, so the two run in one namespace.
        section = _section(self.page('concepts', 'joints.rst'),
                           'Frames and mates')
        blocks = _code_blocks(section)
        self.assertGreaterEqual(len(blocks), 3)
        namespace = {'__name__': __name__}
        exec(compile(blocks[0], 'joints.rst', 'exec'), namespace)
        reads = _code_block_named(section, 'pin = resolved_frames(arm)')
        exec(compile(reads, 'joints.rst', 'exec'), namespace)

        pin, hinge, elbow = (namespace['pin'], namespace['hinge'],
                             namespace['elbow'])
        self.assertEqual(pin.at, (0.0, 150.0, 68.0))
        self.assertEqual((hinge.x, hinge.y, hinge.z),
                         ((1, 0, 0), (0, 0, -1), (0, 1, 0)))
        self.assertEqual(elbow.moving.written, 'forearm.hinge')
        self.assertEqual(elbow.fixed.name, 'elbow_pin')
        self.assertEqual(elbow.freedom.range, (-135, 135))
        self.assertIs(elbow.freedom.anchor_written, False)
        for fragment in ('(0.0, 150.0, 68.0)', 'resolved_frames',
                         'anchor_written', "'forearm.hinge'"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)


##############################################
# state-the-freedom-per-instance, tasks 2.3 to 2.10: a mate's freedom
# may state its `axis` and its `range` as a function of the ASSEMBLY
# that states the mate, called once as the assembly realizes the moving
# child, its result taken as the numbers are. The fixtures are a handed
# joint and its hand-placed twin (`mate_project/handed.py`).

def handed_fixtures():
    from .mate_project import handed

    return handed


def installed(mount, name='turn'):
    """The resolved `(axis, at, range)` of the joint the mate `name`
    gives `mount.link`."""
    return declared_joints(type(mount.link))[name].arguments(mount.link)


class HandedFreedomTest(BaseNodeTest):
    """2.3 to 2.8: the function, the node it receives, when, and how its
    result is taken."""

    def assertRefused(self, build, *expected, absent=(), kind=None):
        from machinome.parameters import ParameterError

        with self.assertRaises(kind or ParameterError) as raised:
            build()
        message = str(raised.exception)
        for fragment in expected:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)
        for fragment in absent:
            with self.subTest(absent=fragment):
                self.assertNotIn(fragment, message)
        return message

    # 2.3 OpenArm's joint on both sides.
    def test_the_handed_joint_resolves_per_side(self):
        HandedMount = handed_fixtures().HandedMount

        for left, axis, span, origin in (
                (True, (0, 1, 0), (-200, 80), [0.0, 62.5, 0.0]),
                (False, (0, -1, 0), (-80, 200), [0.0, -62.5, 0.0])):
            with self.subTest(left=left):
                mount = HandedMount(left=left)
                self.assertEqual(installed(mount),
                                 (axis, (0.0, 0.0, 0.0), span))

                mount.render()
                operations = serialized(mount.link)
                self.assertEqual([operation[0] for operation in operations],
                                 ['t'])
                self.assertEqual(numbers(operations[0]), origin)

    def test_the_handed_range_belongs_to_each_side(self):
        from machinome.simulation import Driver

        HandedMount = handed_fixtures().HandedMount

        class LeftRoot(AssemblyNode):
            angle = Driver(default=0.0, unit='deg')
            mount = HandedMount(left=True)
            angle.drives(mount.turn)

        class RightRoot(AssemblyNode):
            angle = Driver(default=0.0, unit='deg')
            mount = HandedMount(left=False)
            angle.drives(mount.turn)

        with self.assertRaises(JointRangeError) as raised:
            LeftRoot().set_state(angle=150)
        self.assertIn('turn', str(raised.exception))

        right = RightRoot()
        right.set_state(angle=150)
        self.assertEqual(right.mount.turn.value, 150)

    # 2.4 The function receives the assembly.
    def test_the_function_receives_the_assembly_not_the_child(self):
        # (a) The child has no `left`: called with it, the function
        # would raise AttributeError.
        mount = handed_fixtures().HandedMount(left=True)
        self.assertFalse(hasattr(mount.link, 'left'))
        self.assertEqual(installed(mount)[0], (0, 1, 0))

    def test_the_childs_own_flag_is_not_read(self):
        # (b) The child's own `left` says the opposite of the mount's:
        # called with the child, the function would read it silently.
        handed = handed_fixtures()
        del handed.CONTRARY_CALLS[:]
        contrary = handed.ContraryMount(left=False)
        self.assertIs(contrary.link.left, True)
        self.assertEqual(len(handed.CONTRARY_CALLS), 1)
        self.assertIs(handed.CONTRARY_CALLS[0], contrary)
        self.assertIsInstance(handed.CONTRARY_CALLS[0], handed.ContraryMount)
        self.assertEqual(installed(contrary)[0], (0, -1, 0))

    # 3.4, pinned: the joint is never resolved against the child.
    def test_a_handed_link_built_outside_its_mount_is_refused(self):
        from machinome.parameters import ParameterError

        mount = handed_fixtures().HandedMount(left=True)
        stray = type(mount.link)()

        with self.assertRaises(ParameterError) as raised:
            declared_joints(type(stray))['turn'].arguments(stray)
        message = str(raised.exception)
        for fragment in ('HandedMount.turn', 'HandedMount'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)
        self.assertNotIn('AttributeError', message)

    # 2.5 Called once per realized assembly.
    def test_the_function_is_called_once_per_realized_assembly(self):
        from machinome.simulation import Driver

        counts = {'axis': 0, 'range': 0}

        def axis(node):
            counts['axis'] += 1
            return (0, 0, 1)

        def span(node):
            counts['range'] += 1
            return (-90, 90)

        class Counted(AssemblyNode):
            angle = Driver(default=10.0, unit='deg')
            pin = Frame()
            part = Pin()
            swing = part.hinge.on(pin, Revolute(axis=axis, range=span,
                                                unit='deg'))
            angle.drives(swing)

        mounts = [Counted(), Counted()]
        self.assertEqual(counts, {'axis': 2, 'range': 2})

        for mount in mounts:
            for value in (10, 20, 30):
                mount.set_state(angle=value)
            mount.render()
            published(mount)
        self.assertEqual(counts, {'axis': 2, 'range': 2})

    # 2.6 The state it sees.
    def test_the_function_sees_the_assembly_as_a_sites_function_does(self):
        seen = []

        def axis(node):
            seen.append((node.base, resolved_frames(node)['pin'].at))
            return (1, 0, 0) if isinstance(node.base, Swung) else (0, 0, 1)

        class Based(AssemblyNode):
            pin = Frame(at=(0, 0, 9))
            base = Swung()
            part = Pin()
            swing = part.hinge.on(pin, Revolute(axis=axis, unit='deg'))

        based = Based()

        self.assertEqual(len(seen), 1)
        self.assertIs(seen[0][0], based.base)
        self.assertEqual(seen[0][1], (0.0, 0.0, 9.0))
        axis_found = declared_joints(type(based.part))['swing'].arguments(
            based.part)[0]
        self.assertEqual(axis_found, (1, 0, 0))

        based.swing = 30
        based.render()
        self.assertIn(['r', '30', [1, 0, 0]], serialized(based.part))

    # 2.7 The result is taken as the numbers are.
    def refusing(self, argument, returned):
        """A mount whose freedom's `argument` function returns
        `returned()` -- or raises, when `returned` does."""
        HandedLink = handed_fixtures().HandedLink

        def function(node):
            return returned()

        class Refusing(AssemblyNode):
            pin = Frame()
            link = HandedLink()
            turn = link.origin.on(pin, Revolute(unit='deg',
                                                **{argument: function}))

        return Refusing

    def test_a_functions_result_is_taken_as_the_numbers_are(self):
        held = []

        class Gated(AssemblyNode):
            gate = RotationalPort(unit='deg')
            held.append(Bound(lambda own, gate: gate, reads=gate))

        def raising():
            raise KeyError('no such side')

        def a_function():
            return lambda node: (0, 0, 1)

        for argument, label, returned, quoted in (
                ('axis', 'two', lambda: (0, 1), '(0, 1)'),
                ('axis', 'zero', lambda: (0, 0, 0), '(0, 0, 0)'),
                ('axis', 'bool', lambda: (0, 0, True), '(0, 0, True)'),
                ('axis', 'string', lambda: 'xyz', "'xyz'"),
                ('axis', 'function', a_function, 'lambda'),
                ('axis', 'raising', raising, 'KeyError'),
                ('range', 'one', lambda: (0,), '(0,)'),
                ('range', 'bool', lambda: (True, 90), '(True, 90)'),
                ('range', 'reads', lambda: (held[0], None), 'gate'),
                ('range', 'raising', raising, 'KeyError')):
            with self.subTest(argument=argument, returned=label):
                Refusing = self.refusing(argument, returned)
                self.assertRefused(
                    Refusing, 'Refusing.turn', f"freedom's {argument}",
                    quoted, absent=('HandedLink',))

    def test_a_returned_axis_is_normalized_as_a_written_one(self):
        Scaled = self.refusing('axis', lambda: (0, 3, 0))

        self.assertEqual(installed(Scaled())[0], (0, 1, 0))

    # 2.8 The class reads return the function.
    def test_a_function_is_read_as_written(self):
        handed = handed_fixtures()
        counts = {'axis': 0, 'range': 0}

        def axis(node):
            counts['axis'] += 1
            return (0, 0, 1)

        def span(node):
            counts['range'] += 1
            return (-90, 90)

        class Counted(AssemblyNode):
            pin = Frame()
            part = Pin()
            swing = part.hinge.on(pin, Revolute(axis=axis, range=span,
                                                unit='deg'))

        freedom = mates_module().declared_mates(Counted)['swing'].freedom
        self.assertIs(freedom.axis, axis)
        self.assertIs(freedom.range, span)
        self.assertIs(freedom.anchor_written, False)
        self.assertEqual(counts, {'axis': 0, 'range': 0})

        written = mates_module().declared_mates(
            handed.HandedMount)['turn'].freedom
        self.assertIs(written.axis, handed.side_axis)
        self.assertIs(written.range, handed.side_range)
        self.assertIs(written.anchor_written, False)


class HandedTwinTest(BaseNodeTest):
    """2.9 and 2.10: the handed machine against its hand-placed twin, and
    nothing else moves."""

    def assertSameOperations(self, mated, hand, delta=1e-9):
        self.assertEqual([operation[0] for operation in mated],
                         [operation[0] for operation in hand])
        for ours, theirs in zip(mated, hand):
            if ours[0] == 'r':
                self.assertAlmostEqual(float(ours[1]), float(theirs[1]),
                                       delta=delta)
                for mine, written in zip(ours[2], theirs[2]):
                    self.assertAlmostEqual(float(mine), float(written),
                                           delta=delta)
            else:
                for mine, written in zip(numbers(ours), numbers(theirs)):
                    self.assertAlmostEqual(mine, written, delta=delta)

    def posed(self, cls, value):
        from machinome.simulation.enumeration import bind_declared_defaults

        node = cls()
        if value == 'default':
            bind_declared_defaults(node)
        elif value is not None:
            node.set_state(angle=value)
        node.render()
        return node

    def assertSameLeaves(self, mated, hand, expected):
        ours = dict(leaves_of(mated))
        theirs = dict(leaves_of(hand))
        self.assertEqual(sorted(ours), expected)
        self.assertEqual(sorted(theirs), sorted(ours))
        for path in ours:
            self.assertTrue((abs(ours[path] - theirs[path]) < 1e-9).all(),
                            path)

    def test_the_handed_pair_reproduces_its_twin(self):
        handed = handed_fixtures()
        for value in ('default', -80, 0, 80):
            with self.subTest(value=value):
                mated = self.posed(handed.HandedPair, value)
                hand = self.posed(handed.TwinPair, value)
                for side in ('left', 'right'):
                    ours = serialized(getattr(mated, side).link)
                    theirs = serialized(getattr(hand, side).link)
                    self.assertEqual([operation[0] for operation in ours],
                                     ['r', 't'])
                    self.assertSameOperations(ours, theirs)
                self.assertSameLeaves(mated, hand,
                                      ['/left/link', '/right/link'])

    def test_each_unbound_side_rests_as_its_twin(self):
        # A pair whose driver is unbound does not render, so "unbound"
        # is each side's mount on its own, its mate left unbound.
        handed = handed_fixtures()
        for left in (True, False):
            with self.subTest(left=left):
                mated = handed.HandedMount(left=left)
                hand = handed.TwinMount(left=left)
                mated.render()
                hand.render()
                ours = serialized(mated.link)
                self.assertEqual([operation[0] for operation in ours], ['t'])
                self.assertSameOperations(ours, serialized(hand.link))
                self.assertSameLeaves(mated, hand, ['/link'])

    def test_a_handed_machine_needs_no_newer_consumer(self):
        handed = handed_fixtures()
        mated = published(handed.HandedPair())
        hand = published(handed.TwinPair())

        self.assertEqual(mated['version'], hand['version'])
        self.assertEqual(set(mated), set(hand))
        self.assertEqual(mated['drivers'], hand['drivers'])

        for side in ('left', 'right'):
            ours = entry_of(mated, side, 'link')['operations']
            theirs = entry_of(hand, side, 'link')['operations']
            with self.subTest(side=side):
                self.assertEqual([operation[0] for operation in ours],
                                 [operation[0] for operation in theirs])
                for mine, written in zip(ours, theirs):
                    if mine[0] == 'r':
                        self.assertEqual(mine[1], written[1])
                        for component, other in zip(mine[2], written[2]):
                            self.assertAlmostEqual(float(component),
                                                   float(other), delta=1e-9)
                    else:
                        for component, other in zip(mine[1], written[1]):
                            self.assertAlmostEqual(float(component),
                                                   float(other), delta=1e-9)

        fields = {frozenset(entry) for entry in walk(hand['root'])}
        for entry in walk(mated['root']):
            with self.subTest(node=entry['name']):
                self.assertIn(frozenset(entry), fields)


##############################################
# slide-by-mate: a mate's freedom may be a `Prismatic`.
#
# A gripper's finger is placed and freed by a slide, stated once as a
# mate whose freedom is a `Prismatic` with the axis its URDF states, the
# mimic a relation between the two mates' coordinates. The fixtures are
# the gripper and its hand-placed twin (`mate_project/slide.py`).

#: (finger, mate, axis, seat) of `Palm`.
FINGERS = (('left_finger', 'left_grip', (0, 1, 0), [81.7, 21.0, 0.0]),
           ('right_finger', 'right_grip', (0, -1, 0), [81.7, -21.0, 0.0]))

GRIPS = ('default', -11, 0, 10, 20)


class SlidingMateTest(BaseNodeTest):
    """2.3 and 2.5 to 2.8: the joint a sliding freedom installs, its
    coordinate, the mimic, the range, a function axis, the stated axis
    and anchor, and the class reads."""

    def posed(self, cls, value):
        from machinome.simulation.enumeration import bind_declared_defaults

        node = cls()
        if value == 'default':
            bind_declared_defaults(node)
        elif value is not None:
            node.set_state(grip=value)
        node.render()
        return node

    # 2.3 The installed joint and the coordinate.
    def test_the_installed_joint_is_a_prismatic(self):
        palm = slide_fixtures().Palm()

        for finger, mate, axis, _seat in FINGERS:
            with self.subTest(mate=mate):
                child = getattr(palm, finger)
                joint = declared_joints(type(child))[mate]
                self.assertIsInstance(joint, Prismatic)
                self.assertEqual(joint.arguments(child),
                                 (axis, (0.0, 0.0, 0.0), (-11, 20)))
                self.assertEqual(joint.unit, 'mm')

    def test_the_mates_coordinate_is_a_translational_port(self):
        ports = declared_ports(slide_fixtures().Palm)

        for _finger, mate, _axis, _seat in FINGERS:
            with self.subTest(mate=mate):
                self.assertIsInstance(ports[mate], TranslationalPort)
                self.assertNotIsInstance(ports[mate], RotationalPort)
                self.assertEqual(ports[mate].domain, 'translational')
                self.assertEqual(ports[mate].unit, 'mm')

    # 2.5 The mimic and the range.
    def test_the_mimic_moves_the_fingers_equally_and_oppositely(self):
        gripper = self.posed(slide_fixtures().Gripper, 10)
        palm = gripper.wrist.palm

        for finger, _mate, axis, _seat in FINGERS:
            with self.subTest(finger=finger):
                first = serialized(getattr(palm, finger))[0]
                self.assertEqual(first[0], 't')
                self.assertEqual(numbers(first),
                                 [10.0 * component for component in axis])

    def test_the_range_belongs_to_the_freedom(self):
        for value in (25, -12):
            with self.subTest(grip=value):
                with self.assertRaises(JointRangeError) as raised:
                    self.posed(slide_fixtures().Gripper, value)
                self.assertIn('left_grip', str(raised.exception))

    # 2.6 A function axis on a slide.
    def test_a_slides_axis_may_be_a_function_of_the_assembly(self):
        SidePalm = slide_fixtures().SidePalm

        for left, axis, seat in ((True, (0, 1, 0), [81.7, 21.0, 0.0]),
                                 (False, (0, -1, 0), [81.7, -21.0, 0.0])):
            with self.subTest(left=left):
                palm = SidePalm(left=left)
                joint = declared_joints(type(palm.finger))['grip']
                self.assertIsInstance(joint, Prismatic)
                self.assertEqual(joint.arguments(palm.finger)[0], axis)

                palm.grip = 10
                palm.render()
                operations = serialized(palm.finger)
                self.assertEqual([operation[0] for operation in operations],
                                 ['t', 't'])
                self.assertEqual(numbers(operations[0]),
                                 [10.0 * component for component in axis])
                for found, expected in zip(numbers(operations[1]), seat):
                    self.assertAlmostEqual(found, expected, delta=1e-9)

    # 2.7 The stated axis, the unit default and `at`.
    def test_a_slide_takes_its_stated_axis_not_the_frames_z(self):
        SlotMount = slide_fixtures().SlotMount
        mount = SlotMount()

        joint = declared_joints(type(mount.part))['slide']
        self.assertIsInstance(joint, Prismatic)
        self.assertEqual(joint.arguments(mount.part)[0], (1, 0, 0))
        self.assertEqual(joint.unit, 'mm')
        port = declared_ports(SlotMount)['slide']
        self.assertIsInstance(port, TranslationalPort)
        self.assertEqual(port.unit, 'mm')

        mount.slide = 4
        mount.render()
        operations = serialized(mount.part)
        self.assertEqual([operation[0] for operation in operations],
                         ['t', 't'])
        self.assertEqual(numbers(operations[0]), [4.0, 0.0, 0.0])
        self.assertEqual(numbers(operations[1]), [0.0, 0.0, 5.0])

    def test_a_prismatic_without_an_axis_is_refused_by_its_constructor(self):
        # A guard: green at the base and after. The mate adds no refusal
        # of its own; the constructor refuses before any mate is stated.
        with self.assertRaises(TypeError) as raised:
            Prismatic(range=(0, 10))
        self.assertIn('axis', str(raised.exception))

    def test_a_slides_stated_anchor_moves_nothing(self):
        slide = slide_fixtures()
        anchored = slide.AnchoredPalm()

        joint = declared_joints(type(anchored.left_finger))['left_grip']
        self.assertEqual(joint.arguments(anchored.left_finger)[1],
                         (0.0, 0.0, 5.0))

        anchored.left_grip = 10
        anchored.render()
        palm = slide.Palm()
        palm.left_grip = 10
        palm.render()
        self.assertEqual(serialized(anchored.left_finger),
                         serialized(palm.left_finger))

    # 2.8 The class reads.
    def test_a_sliding_freedom_is_read_as_written(self):
        slide = slide_fixtures()

        freedom = mates_module().declared_mates(slide.Palm)[
            'left_grip'].freedom
        self.assertIsInstance(freedom, Prismatic)
        self.assertEqual(freedom.axis, (0, 1, 0))
        self.assertIs(freedom.anchor_written, False)
        self.assertEqual(freedom.range, (-11, 20))
        self.assertEqual(freedom.unit, 'mm')

        stated = mates_module().declared_mates(slide.SlotMount)[
            'slide'].freedom
        self.assertEqual(stated.axis, (1, 0, 0))
        self.assertEqual(stated.unit, 'mm')
        self.assertIs(stated.anchor_written, False)


class SlidingTwinTest(BaseNodeTest):
    """2.4 and 2.9: the gripper against its hand-placed twin, and nothing
    else moves."""

    posed = SlidingMateTest.posed

    def assertSameOperations(self, mated, hand, delta=1e-9):
        self.assertEqual([operation[0] for operation in mated],
                         [operation[0] for operation in hand])
        for ours, theirs in zip(mated, hand):
            for mine, written in zip(numbers(ours), numbers(theirs)):
                self.assertAlmostEqual(mine, written, delta=delta)

    def assertSameLeaves(self, mated, hand, expected):
        ours = dict(leaves_of(mated))
        theirs = dict(leaves_of(hand))
        self.assertEqual(sorted(ours), expected)
        self.assertEqual(sorted(theirs), sorted(ours))
        for path in ours:
            self.assertTrue((abs(ours[path] - theirs[path]) < 1e-9).all(),
                            path)

    # 2.4 The finger rests and slides as the twin's.
    def test_each_unbound_finger_rests_on_its_seat(self):
        # A palm whose mimic has nothing bound at either end does not
        # render, and neither does its twin, so "unbound" is each side's
        # finger on its own, its mate left unbound (`SidePalm`).
        slide = slide_fixtures()
        for left, (finger, _mate, _axis, seat) in zip((True, False),
                                                       FINGERS):
            with self.subTest(finger=finger):
                palm = slide.SidePalm(left=left)
                palm.render()
                ours = serialized(palm.finger)
                self.assertEqual([operation[0] for operation in ours], ['t'])
                for found, expected in zip(numbers(ours[0]), seat):
                    self.assertAlmostEqual(found, expected, delta=1e-9)

    def test_an_unbound_mimic_is_refused_as_the_twins_is(self):
        from machinome.motion.couplings import UnreachedCoordinate

        slide = slide_fixtures()
        for cls in (slide.Palm, slide.TwinPalm):
            with self.subTest(palm=cls.__name__):
                with self.assertRaises(UnreachedCoordinate) as raised:
                    cls().render()
                self.assertIn('nothing bound either end',
                              str(raised.exception))

    def test_the_gripper_reproduces_its_twin(self):
        slide = slide_fixtures()
        for value in GRIPS:
            with self.subTest(grip=value):
                mated = self.posed(slide.Gripper, value)
                hand = self.posed(slide.TwinGripper, value)
                for finger, _mate, axis, seat in FINGERS:
                    ours = serialized(getattr(mated.wrist.palm, finger))
                    theirs = serialized(getattr(hand.wrist.palm, finger))
                    self.assertEqual([operation[0] for operation in ours],
                                     ['t', 't'])
                    travel = 0.0 if value == 'default' else float(value)
                    self.assertEqual(numbers(ours[0]),
                                     [travel * component
                                      for component in axis])
                    for found, expected in zip(numbers(ours[1]), seat):
                        self.assertAlmostEqual(found, expected, delta=1e-9)
                    self.assertSameOperations(ours, theirs)
                self.assertSameLeaves(
                    mated, hand, ['/wrist/palm/left_finger',
                                  '/wrist/palm/right_finger'])

    # 2.9 Nothing else moves.
    def test_a_sliding_machine_needs_no_newer_consumer(self):
        slide = slide_fixtures()
        mated = published(slide.Gripper())
        hand = published(slide.TwinGripper())

        self.assertEqual(mated['version'], hand['version'])
        self.assertEqual(set(mated), set(hand))
        self.assertEqual(mated['drivers'], hand['drivers'])

        for finger, _mate, _axis, _seat in FINGERS:
            ours = entry_of(mated, 'wrist', 'palm', finger)['operations']
            theirs = entry_of(hand, 'wrist', 'palm', finger)['operations']
            with self.subTest(finger=finger):
                self.assertEqual([operation[0] for operation in ours],
                                 [operation[0] for operation in theirs])
                for mine, written in zip(ours, theirs):
                    for component, other in zip(mine[1], written[1]):
                        try:
                            expected = float(other)
                        except ValueError:
                            # The slide driven by `grip`: symbolic, and
                            # the same string on both sides.
                            self.assertEqual(component, other)
                            continue
                        self.assertAlmostEqual(float(component), expected,
                                               delta=1e-9)
        left = entry_of(mated, 'wrist', 'palm', 'left_finger')['operations']
        right = entry_of(mated, 'wrist', 'palm', 'right_finger')['operations']
        self.assertIn('grip', left[0][1])
        self.assertIn('(grip * -1)', right[0][1])

        fields = {frozenset(entry) for entry in walk(hand['root'])}
        for entry in walk(mated['root']):
            with self.subTest(node=entry['name']):
                self.assertIn(frozenset(entry), fields)

    def test_a_class_body_prismatic_places_what_it_placed(self):
        # A guard of 3.1's anchor default: a `Prismatic` stating its axis
        # positionally on a class, bound to 10, places exactly the
        # operations it placed at the base.
        class Carriage(Solid2Node):
            travel = Prismatic((0, 1, 0), range=(-11, 20), unit='mm')

            def render(self):
                return cube(2, center=True)

        carriage = Carriage()
        self.assertEqual(declared_joints(Carriage)['travel'].arguments(
            carriage), ((0, 1, 0), (0.0, 0.0, 0.0), (-11, 20)))
        carriage.travel = 10
        carriage.render()
        self.assertEqual(serialized(carriage), [['t', ['0', '10', '0']]])

    def test_a_revolute_mate_still_installs_a_revolute(self):
        # A guard: the `Revolute` path takes exactly today's objects.
        mate = mates_module().declared_mates(fixtures().MatedArm)['elbow']
        self.assertIs(type(mate.joint), Revolute)
        self.assertIs(type(mate.coordinate), RotationalPort)
        self.assertEqual(mate.coordinate.unit, 'deg')
        self.assertIs(mate.joint.axis, fixtures().MatedForearm.hinge.z)
        self.assertIs(mate.joint.at, fixtures().MatedForearm.hinge.at)


##############################################
# hold-by-mate: a mate with no freedom holds a child where two frames
# meet. The fixtures are a quadruped's left knee servo held in its shin
# (`mate_project/hold.py`), every one held to a hand-placed twin.

def hold_fixtures():
    """`tests/mate_project/hold.py`, imported where a test needs it."""
    from .mate_project import hold

    return hold


HELD_ROTATION = ['r', '180', [0.7071067811865476, 0, 0.7071067811865476]]


class HeldPartTest(BaseNodeTest):
    """2.3, 2.4, 2.6 and 2.7: what a rigid mate compiles to, and what it
    is not."""

    # 2.3 The rest placement.
    def test_the_servo_is_held_at_its_measured_seat(self):
        shin = hold_fixtures().Shin()
        shin.render()

        operations = serialized(shin.servo)
        self.assertEqual([operation[0] for operation in operations],
                         ['r', 't'])
        self.assertEqual(operations[0], HELD_ROTATION)
        for found, expected in zip(numbers(operations[1]),
                                   (-0.98, -9.5, -7.0)):
            self.assertAlmostEqual(found, expected, delta=1e-9)

    # 2.4 Nothing on the child, nothing on the assembly.
    def test_the_held_servo_is_its_declared_class(self):
        hold = hold_fixtures()
        shin = hold.Shin()

        self.assertIs(type(shin.servo), hold.Servo)
        self.assertEqual(declared_joints(type(shin.servo)),
                         declared_joints(hold.Servo))
        self.assertEqual(shin.servo.uniq_id, hold.Servo().uniq_id)

    def test_a_rigid_mate_installs_no_joint_and_no_wiring(self):
        hold = hold_fixtures()
        mate = mates_module().declared_mates(hold.Shin)['bolted']

        self.assertIsNone(mate.joint)
        self.assertEqual(hold.Shin.servo.wiring, {})
        self.assertIs(hold.Shin.servo.node_class, hold.Servo)

    def test_a_rigid_mate_is_not_a_port(self):
        hold = hold_fixtures()

        self.assertEqual(declared_ports(hold.Shin), {})
        self.assertEqual(list(declared_ports(hold.Leg)), ['knee'])

    def test_a_rigid_mate_may_share_a_name_with_the_childs_attribute(self):
        hold = hold_fixtures()

        class Eared(AssemblyNode):
            servo_seat = Frame(**hold.SEAT)
            servo = hold.Servo()
            ears = servo.ears.on(servo_seat)

        eared = Eared()
        eared.render()
        self.assertEqual(serialized(eared.servo)[0], HELD_ROTATION)
        self.assertIs(type(eared.servo), hold.Servo)

    # 2.5 A held part keeps its own joints inside the placement.
    def test_a_held_part_keeps_its_own_joints_inside_the_placement(self):
        shin = hold_fixtures().OutputShin()
        shin.render()
        shin.servo.output = 20

        operations = serialized(shin.servo)
        self.assertEqual([operation[0] for operation in operations],
                         ['r', 'r', 't'])
        self.assertEqual(operations[0], ['r', '20', [0, 1, 0]])
        self.assertEqual(operations[1], HELD_ROTATION)
        for found, expected in zip(numbers(operations[2]),
                                   (-0.98, -9.5, -7.0)):
            self.assertAlmostEqual(found, expected, delta=1e-9)

    # 2.6 A rigid mate is read, not bound.
    def test_a_rigid_mate_is_read_not_bound(self):
        hold = hold_fixtures()
        shin = hold.Shin()

        self.assertIs(shin.bolted,
                      mates_module().declared_mates(hold.Shin)['bolted'])
        with self.assertRaises(AttributeError) as raised:
            shin.bolted = 10
        message = str(raised.exception)
        for fragment in ('Shin', 'bolted', 'owns no coordinate'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    # 2.7 A held part is not placed by hand.
    def test_a_held_part_is_not_placed_by_hand(self):
        Shin = hold_fixtures().Shin

        class Handed(Shin):
            def render(self):
                self.servo.translate([0, 0, 1])

        with self.assertRaises(ValueError) as raised:
            Handed().render()

        message = str(raised.exception)
        for fragment in ('Handed', 'servo', 'bolted'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)


class HeldTwinTest(BaseNodeTest):
    """2.3, 2.5 and 2.8: the held servo against its hand-placed twin, and
    nothing else moves."""

    def assertSameLeaves(self, mated, hand, expected):
        ours = dict(leaves_of(mated))
        theirs = dict(leaves_of(hand))
        self.assertEqual(sorted(ours), expected)
        self.assertEqual(sorted(theirs), sorted(ours))
        for path in ours:
            self.assertTrue((abs(ours[path] - theirs[path]) < 1e-9).all(),
                            path)

    def rendered(self, cls):
        node = cls()
        node.render()
        return node

    # 2.3 The rest placement against the twin.
    def test_the_held_servo_reproduces_its_twin(self):
        hold = hold_fixtures()
        for mated, hand, leaves in (
                (hold.Shin, hold.TwinShin, ['/servo']),
                (hold.PlateShin, hold.TwinPlateShin, ['/plate', '/servo'])):
            with self.subTest(shin=mated.__name__):
                self.assertSameLeaves(self.rendered(mated),
                                      self.rendered(hand), leaves)

    def test_a_held_servo_is_held_on_a_still_siblings_frame(self):
        shin = self.rendered(hold_fixtures().PlateShin)

        self.assertEqual(serialized(shin.plate), [['t', ['0', '0', '3']]])
        operations = serialized(shin.servo)
        self.assertEqual(operations[0], HELD_ROTATION)
        for found, expected in zip(numbers(operations[1]),
                                   (-0.98, -9.5, -4.0)):
            self.assertAlmostEqual(found, expected, delta=1e-9)

    # 2.5 The held part rides, and keeps what it carries.
    def test_a_held_part_rides_with_the_part_that_holds_it(self):
        from machinome.simulation.enumeration import bind_declared_defaults

        hold = hold_fixtures()
        for value in (-90, -30, 0, 30, 90, 'default'):
            with self.subTest(angle=value):
                nodes = []
                for cls in (hold.Robot, hold.TwinRobot):
                    node = cls()
                    if value == 'default':
                        bind_declared_defaults(node)
                    else:
                        node.set_state(angle=value)
                    node.render()
                    nodes.append(node)
                self.assertSameLeaves(*nodes, ['/leg/shin/servo'])

    def test_a_held_assembly_keeps_its_own_mates(self):
        hold = hold_fixtures()
        mated = self.rendered(hold.BoltedShin)
        hand = self.rendered(hold.TwinBoltedShin)

        self.assertSameLeaves(mated, hand,
                              ['/servo/screw', '/servo/servo'])
        self.assertIs(type(mated.servo.screw), hold.Screw)

    # 2.8 Nothing else moves.
    def test_a_held_machine_needs_no_newer_consumer(self):
        hold = hold_fixtures()
        mated = published(hold.Robot())
        hand = published(hold.TwinRobot())

        self.assertEqual(mated['version'], hand['version'])
        self.assertEqual(set(mated), set(hand))
        self.assertEqual(mated['drivers'], hand['drivers'])

        ours = entry_of(mated, 'leg', 'shin', 'servo')['operations']
        theirs = entry_of(hand, 'leg', 'shin', 'servo')['operations']
        self.assertEqual([operation[0] for operation in ours], ['r', 't'])
        self.assertEqual([operation[0] for operation in theirs],
                         ['r', 'r', 't'])
        self.assertEqual(ours[0], HELD_ROTATION)
        self.assertTrue((abs(matrix_of(ours) - matrix_of(theirs))
                         < 1e-9).all())

        fields = {frozenset(entry) for entry in walk(hand['root'])}
        for entry in walk(mated['root']):
            with self.subTest(node=entry['name']):
                self.assertIn(frozenset(entry), fields)
