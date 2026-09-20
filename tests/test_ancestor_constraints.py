# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""An installed obstacle does not reparent the joint it restrains."""

from machinome.motion.joints import Bound, JointRangeError, Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.parameters import Angle
from machinome.simulation import Driver, Sim, State, UnsupportedLaw
from .base import BaseNodeTest
from .constraint_project import (Drive, Flat, Machine, NativeDrive, SeveralScopes,
                                 TwoCopies, TwoTimeDrives, limited_machine,
                                 nested_machine)
from .running_project.parts import Arbor, Block, Floater, Wheel


class NestedStopTest(BaseNodeTest):
    def test_installed_own_bound_freezes_the_committed_coordinate(self):
        from machinome.math import floor
        class Ratchet(Machine):
            time = Time.running()
            Machine.drive.disc.turn.constrain(
                range=(lambda own: 30*floor(own/30), None))
        sim = Sim(Ratchet(), dt=.1)
        sim.move('crank', to=75)
        self.assertEqual(sim.move('crank', to=0).status, 'blocked')
        self.assertEqual(sim.state['crank'], 60)

    def test_repeated_read_across_contributions_is_a_single_dependency(self):
        base = nested_machine()
        class Twice(base):
            Machine.drive.disc.turn.constrain(range=(None, Bound(
                lambda own, phase: 100+phase, reads=(Machine.bank.ones.turn,))))
        sim = Sim(Twice(), dt=.1)
        sim.move('crank', to=150)
        self.assertEqual(sim.state['drive.disc.turn'], 104)
        sim.move('phase', to=20)
        self.assertEqual(sim.move('crank', to=150).status, 'blocked')
        self.assertEqual(sim.state['drive.disc.turn'], 120)

    def test_existing_flat_positive_control(self):
        sim = Sim(Flat(), dt=.1)
        command = sim.move('crank', to=150)
        self.assertEqual(command.status, 'blocked')
        self.assertEqual(sim.state['disc.turn'], 124)

    def test_the_same_stop_on_existing_nested_joints(self):
        sim = Sim(nested_machine()(), dt=.1)
        command = sim.move('crank', to=150)
        self.assertEqual(command.status, 'blocked')
        self.assertEqual(command.admitted, 124)
        self.assertEqual(sim.state['drive.disc.turn'], 124)
        self.assertEqual(sim.state['bank.ones.turn'], 4)
        self.assertEqual(set(sim.state), {
            'crank', 'phase', 'drive.disc.turn', 'bank.ones.turn'})
        self.assertIs(type(sim.node.drive), Machine.drive.node_class)

    def test_moving_read_stops_before_invalidating_a_standing_target(self):
        sim = Sim(nested_machine()(), dt=.1)
        sim.move('crank', to=124)
        command = sim.move('phase', to=-10)
        self.assertEqual(command.status, 'blocked')
        self.assertAlmostEqual(sim.state['phase'], 4)
        self.assertEqual(sim.state['drive.disc.turn'], 124)

    def test_relief_has_no_backlog_and_replay_is_exact(self):
        sim = Sim(nested_machine()(), dt=.1)
        sim.move('crank', to=150)
        saved = sim.snapshot()

        def resume():
            sim.move('phase', to=20)
            self.assertEqual(sim.state['drive.disc.turn'], 124)
            self.assertEqual(sim.move('crank', to=150).status, 'blocked')
            self.assertEqual(sim.state['drive.disc.turn'], 140)
        resume()
        expected = sim.snapshot()
        sim.restore(saved)
        resume()
        self.assertEqual(sim.snapshot(), expected)

    def test_reverse_is_free_and_does_not_move_the_stationary_support(self):
        node = nested_machine()()
        sim = Sim(node, dt=.1)
        before = tuple(node.drive.fixed.operations)
        sim.move('crank', to=150)
        self.assertEqual(sim.move('crank', to=100).status, 'completed')
        self.assertEqual(tuple(node.drive.fixed.operations), before)
        self.assertEqual(sim.state['drive.disc.turn'], 100)

    def test_native_stop_is_never_relaxed(self):
        class Native(Machine):
            time = Time.running()
            drive = NativeDrive()
            drive.disc.turn.constrain(range=(-10, 120))
        sim = Sim(Native(), dt=.1)
        self.assertEqual(sim.move('crank', to=150).status, 'blocked')
        self.assertEqual(sim.state['drive.disc.turn'], 90)
        self.assertEqual(sim.move('crank', to=-10).status, 'blocked')
        self.assertEqual(sim.state['drive.disc.turn'], 0)

    def test_original_and_installed_reads_retain_their_scopes(self):
        sim = Sim(SeveralScopes(), dt=.1)
        sim.move('crank', to=150)
        self.assertEqual(sim.state['drive.disc.turn'], 100)
        sim.move('local', to=50)
        sim.move('crank', to=150)
        self.assertEqual(sim.state['drive.disc.turn'], 124)

    def test_two_copies_and_multiple_ancestors_stay_independent(self):
        node = TwoCopies()
        sim = Sim(node, dt=.1)
        sim.move('left.request', to=40)
        sim.move('right.request', to=40)
        self.assertEqual(sim.state['left.disc.turn'], 12)
        self.assertEqual(sim.state['right.disc.turn'], 15)
        sim.move('right.phase', to=20)
        sim.move('right.request', to=40)
        self.assertEqual(sim.state['right.disc.turn'], 30)
        self.assertEqual(sim.state['left.disc.turn'], 12)
        self.assertIs(type(node.left.disc), type(node.right.disc))

    def test_inherited_constraints_are_additive(self):
        base = limited_machine(90)
        class Narrower(base):
            Machine.drive.disc.turn.constrain(range=(None, 70))
        sim = Sim(Narrower(), dt=.1)
        sim.move('crank', to=100)
        self.assertEqual(sim.state['drive.disc.turn'], 70)

    def test_parameter_bound_resolves_in_its_declaring_ancestor(self):
        class Adjustable(Machine):
            time = Time.running()
            stop = Angle(30)
            Machine.drive.disc.turn.constrain(range=(0, stop))
        for limit in (30, 60):
            sim = Sim(Adjustable(stop=limit), dt=.1)
            sim.move('crank', to=100)
            self.assertEqual(sim.state['drive.disc.turn'], limit)

    def test_reenumeration_does_not_duplicate_limits_or_placement(self):
        sim = Sim(nested_machine()(), dt=.1)
        sim.move('crank', to=124)
        node = sim.node
        before = len(node.drive.disc.operations)
        for _ in range(3):
            node.render()
        self.assertEqual(len(node.drive.disc.operations), before)
        self.assertEqual(len(node.drive.disc._range_constraints['turn']), 1)
        sim.reset()
        self.assertEqual(sim.state['drive.disc.turn'], 0)

    def test_only_the_pushing_time_drive_stops(self):
        sim = Sim(TwoTimeDrives(), dt=1, record=10)
        sim.run(3)
        self.assertEqual(sim.time, 3)
        self.assertEqual(sim.state['drive.disc.turn'], 2.5)
        self.assertEqual(sim.state['other.turn'], 6)
        self.assertEqual(sim.stops[-1].inputs, ())
        self.assertEqual(len(sim.stops[-1].time_drives), 1)
        sim.move('release', to=10)
        self.assertEqual(sim.state['drive.disc.turn'], 2.5)
        sim.run(1)
        self.assertEqual(sim.state['drive.disc.turn'], 3.5)
        self.assertEqual(sim.state['other.turn'], 8)


class PosingTest(BaseNodeTest):
    def test_clocked_scoped_read_stops_its_own_request(self):
        base = limited_machine(200, running=False, clocked=True)
        class Clocked(base):
            Machine.drive.disc.turn.constrain(range=(None, Bound(
                lambda own, phase: 120+phase, reads=(Machine.bank.ones.turn,))))
        sim = Sim(Clocked())
        self.assertEqual(sim.move('crank', to=150).admitted, 124)
        self.assertEqual(sim.move('phase', to=-10).admitted, 0)
        self.assertEqual(sim.state['phase'], 4)
        sim.move('phase', to=20)
        self.assertEqual(sim.move('crank', to=150).admitted, 16)
        self.assertEqual(sim.state['crank'], 140)

    def test_clocked_curved_level_remains_unsupported(self):
        from machinome.math import sin
        from machinome.simulation.clocked import ClockedError
        base = limited_machine(200, running=False, clocked=True)
        class Curved(base):
            Machine.drive.disc.turn.constrain(range=(None, Bound(
                lambda own, phase: 120+sin(phase), reads=(Machine.bank.ones.turn,))))
        with self.assertRaisesRegex(ClockedError, 'CURVES'):
            Sim(Curved())

    def test_failed_request_preserves_committed_bank_time_and_records(self):
        class InvalidEndpoint(Machine):
            time = Time.running()
            Machine.drive.disc.turn.constrain(range=(None, Bound(
                lambda own, phase: 100+1/(phase-5), reads=(Machine.bank.ones.turn,))))
        sim = Sim(InvalidEndpoint(), dt=.1, record=4)
        sim.move('crank', to=20)
        state, time, stops, crossings = sim.state, sim.time, sim.stops, sim.crossings
        with self.assertRaises(Exception):
            sim.move('phase', to=5)
        self.assertEqual((sim.state, sim.time, sim.stops, sim.crossings),
                         (state, time, stops, crossings))

    def test_added_numeric_limit_refuses_an_untimed_pose(self):
        node = limited_machine(90, running=False)()
        node.set_state(crank=90, phase=4)
        with self.assertRaisesRegex(JointRangeError, 'drive.disc.turn.*90'):
            node.set_state(crank=100, phase=4)

    def test_scoped_reads_are_judged_after_sibling_relations(self):
        class Posed(Machine):
            Machine.drive.disc.turn.constrain(range=(None, Bound(
                lambda own, phase: 120+phase, reads=(Machine.bank.ones.turn,))))
        node = Posed()
        node.set_state(crank=124, phase=4)
        with self.assertRaisesRegex(JointRangeError, 'bank.ones.turn.*4'):
            node.set_state(crank=130, phase=4)
        node.set_state(crank=130, phase=20)

    def test_unknown_read_does_not_disable_a_known_installed_limit(self):
        class Unknown(AssemblyNode):
            crank = Driver(default=0)
            drive = Drive()
            other = Arbor()
            crank.drives(drive.disc.turn)
            drive.disc.turn.constrain(range=(0, 90))
            drive.disc.turn.constrain(range=(None, Bound(
                lambda own, phase: 120+phase, reads=(other.turn,))))
        with self.assertRaisesRegex(JointRangeError, '90'):
            Unknown().set_state(crank=100)

    def test_clocked_request_stops_and_restores(self):
        sim = Sim(limited_machine(90, running=False, clocked=True)())
        saved = sim.snapshot()
        result = sim.move('crank', to=150)
        self.assertEqual(result.admitted, 90)
        self.assertTrue(result.stops)
        expected = sim.state
        sim.restore(saved)
        sim.move('crank', to=150)
        self.assertEqual(sim.state, expected)


class RefusalTest(BaseNodeTest):
    def test_omitted_target_is_not_an_inert_constraint(self):
        base = limited_machine(90, running=False)
        class Omitted(base):
            def render(self):
                self.drive.omit()
        with self.assertRaisesRegex(Exception, '(descendant|reach|omit|linked|tree)'):
            Omitted().set_state(crank=0, phase=4)

    def test_incompatible_inherited_unit(self):
        class ChangedDrive(Drive):
            disc = Arbor(turn=Revolute(axis=(0, 0, 1), unit='rad'))
        base = limited_machine()
        with self.assertRaisesRegex(TypeError, 'incompatible joint type or unit'):
            class Bad(base):
                drive = ChangedDrive()

    def test_statement_outside_class_body(self):
        with self.assertRaisesRegex(TypeError, 'class body'):
            Machine.drive.disc.turn.constrain(range=(0, 90))

    def test_plain_port_target(self):
        with self.assertRaisesRegex(TypeError, 'scalar descendant joint'):
            class Bad(AssemblyNode):
                wheel = Wheel()
                wheel.turn.constrain(range=(0, 90))

    def test_repeated_target(self):
        with self.assertRaisesRegex(TypeError, 'broadcast'):
            class Bad(AssemblyNode):
                wheels = Arbor().repeat(2)
                wheels.turn.constrain(range=(0, 90))

    def test_free_component_target(self):
        with self.assertRaisesRegex(TypeError, 'scalar descendant joint'):
            class Bad(AssemblyNode):
                body = Floater()
                body.pose.roll.constrain(range=(0, 90))

    def test_self_read_and_duplicate_read(self):
        with self.assertRaisesRegex(TypeError, 'OWN'):
            class SelfRead(Machine):
                Machine.drive.disc.turn.constrain(range=(None, Bound(
                    lambda own, again: again, reads=(Machine.drive.disc.turn,))))
        with self.assertRaisesRegex(TypeError, 'twice'):
            class Duplicate(Machine):
                Machine.drive.disc.turn.constrain(range=(None, Bound(
                    lambda own, a, b: a+b,
                    reads=(Machine.bank.ones.turn, Machine.bank.ones.turn))))

    def test_foreign_scope(self):
        with self.assertRaisesRegex(TypeError, 'not a child'):
            class Bad(AssemblyNode):
                Machine.drive.disc.turn.constrain(range=(0, 90))

    def test_malformed_or_empty_range(self):
        for span in (None, (None, None), (1,), '12', lambda node: (0, 1)):
            with self.subTest(span=span), self.assertRaisesRegex(TypeError, 'pair'):
                class Bad(Machine):
                    Machine.drive.disc.turn.constrain(range=span)

    def test_incompatible_inherited_target(self):
        base = limited_machine()
        class Missing(AssemblyNode):
            disc = Wheel()
        with self.assertRaisesRegex(TypeError, 'scalar descendant joint'):
            class Bad(base):
                drive = Missing()

    def test_unused_read_cannot_hide_behind_a_tighter_stop(self):
        class Bad(Machine):
            time = Time.running()
            Machine.drive.disc.turn.constrain(range=(0, 10))
            Machine.drive.disc.turn.constrain(range=(None, Bound(
                lambda own, phase: own+200, reads=(Machine.bank.ones.turn,))))
        with self.assertRaisesRegex(UnsupportedLaw, 'never reads'):
            Sim(Bad(), dt=.1)

    def test_numeric_intersection_cannot_be_empty(self):
        with self.assertRaisesRegex(JointRangeError, 'empty'):
            class Bad(Machine):
                Machine.drive.disc.turn.constrain(range=(0, 10))
                Machine.drive.disc.turn.constrain(range=(20, 30))
            Bad()

    def test_new_limit_changes_identity_and_restore_is_atomic(self):
        first = Sim(limited_machine(90)(), dt=.1)
        second = Sim(limited_machine(80)(), dt=.1)
        saved = second.snapshot()
        with self.assertRaises(Exception):
            second.restore(first.snapshot())
        self.assertEqual(second.snapshot(), saved)

    def test_plain_port_read_is_not_silently_banked(self):
        class Bad(Machine):
            time = Time.running()
            wheel = Wheel()
            Machine.phase.drives(wheel.turn)
            Machine.drive.disc.turn.constrain(range=(None, Bound(
                lambda own, phase: 120+phase, reads=(wheel.turn,))))
        with self.assertRaisesRegex(UnsupportedLaw, 'does not bank'):
            Sim(Bad(), dt=.1)


class PublicationTest(BaseNodeTest):
    def test_an_equivalent_native_span_publishes_the_same_document(self):
        from .test_running_document import bound, document
        class Running(Machine):
            time = Time.running()
            drive = NativeDrive()
        added_class = limited_machine(90)
        # Compare two declarations of the same named model. Root class
        # identity is deliberately part of a program's snapshot identity.
        Running.__module__ = added_class.__module__
        Running.__qualname__ = added_class.__qualname__
        native = document(bound(Running()))
        added = document(bound(added_class()))
        # Source mtimes differ; the model name and all mechanical data agree.
        native['root']['mtime'] = added['root']['mtime']
        self.assertEqual(native, added)
