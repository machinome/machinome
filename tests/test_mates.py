# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

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
from machinome.motion.ports import RotationalPort, declared_ports
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

    def test_the_rigid_mate_is_deferred(self):
        def build():
            class Rigid(AssemblyNode):
                pin = Frame()
                part = Pin()
                fixed = part.hinge.on(pin)

        self.assertRefused(build, 'Rigid', 'fixed', 'rigid', 'Revolute')

    def test_other_freedoms_are_refused(self):
        for freedom in (lambda: Prismatic(axis=(0, 0, 1)),
                        lambda: Orbit(axis=(0, 0, 1)),
                        lambda: Free()):
            def build():
                class Sliding(AssemblyNode):
                    pin = Frame()
                    part = Pin()
                    slide = part.hinge.on(pin, freedom())

            with self.subTest(freedom=type(freedom()).__name__):
                self.assertRefused(build, 'Sliding', 'slide', 'Revolute',
                                   type(freedom()).__name__)

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

        def callable_axis():
            class Lifted(AssemblyNode):
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(
                    pin, Revolute(axis=lambda node: (0, 0, 1)))

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

        for build, argument in ((token, 'at'), (formula, 'at'),
                                (callable_axis, 'axis'),
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

        def whole():
            class Ranged(AssemblyNode):
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(
                    pin, Revolute(range=lambda node: (0, 90)))

        def reads():
            class Ranged(AssemblyNode):
                gate = RotationalPort(unit='deg')
                pin = Frame()
                part = Pin()
                swing = part.hinge.on(pin, Revolute(
                    range=(Bound(lambda own, gate: gate, reads=gate), None)))

        for build in (token, whole, reads):
            with self.subTest(range=build.__name__):
                self.assertRefused(build, 'Ranged', 'swing', 'range')

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

    def test_the_reference_lists_frames_and_mates(self):
        api = self.page('reference', 'api.rst')

        for entry in ('machinome.node.frames.Frame',
                      'machinome.node.frames.declared_frames',
                      'machinome.motion.mates.declared_mates'):
            with self.subTest(entry=entry):
                self.assertIn(entry, api)

    def test_the_changelog_names_the_mate_above_the_release(self):
        changelog = self.page('project', 'changelog.rst')

        unreleased = changelog.split('Machinome 0.7.0')[0]
        self.assertIn('Unreleased\n----------', unreleased)
        for fragment in ('Frame', '.on(', 'Revolute'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, unreleased)


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
        # The third block builds on the first block's `UpperArm`, as the
        # page's prose says, so the two run in one namespace.
        section = _section(self.page('concepts', 'joints.rst'),
                           'Frames and mates')
        blocks = _code_blocks(section)
        self.assertGreaterEqual(len(blocks), 3)
        namespace = {'__name__': __name__}
        exec(compile(blocks[0], 'joints.rst', 'exec'), namespace)
        exec(compile(blocks[2], 'joints.rst', 'exec'), namespace)

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
