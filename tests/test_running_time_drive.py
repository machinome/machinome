# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Retained elapsed-time motion: the Astrarium framework finding."""

from machinome.motion.couplings import DoublyBound
from machinome.motion.joints import Bound, Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver, RunConflict, Sim, UnsupportedLaw

from .base import BaseNodeTest
from .running_project.time_drive import (Shaft, affine, astrarium, gated,
                                         curved_stop, mixed, releasable, stopped)
from .test_running_simulation import turned


class TimeDriveTest(BaseNodeTest):
    def test_affine_time_runs_without_commands(self):
        node = affine()
        sim = Sim(node, dt=0.02, meshes=False)
        self.assertEqual(dict(sim.state), {'shaft.turn': 0})
        self.assertEqual(sim.commands, ())
        sim.run(2)
        self.assertAlmostEqual(sim.state['shaft.turn'], 12)
        self.assertAlmostEqual(turned(node.shaft), 12)
        self.assertEqual(sim.time, 2)
        self.assertEqual(sim.commands, ())

    def test_enable_at_nonzero_time_does_not_teleport(self):
        sim = Sim(gated(), dt=0.02, meshes=False)
        sim.run(2)
        sim.move('enabled', to=0)
        self.assertAlmostEqual(sim.state['shaft.turn'], 12)
        sim.run(2)
        sim.move('enabled', to=1)
        self.assertAlmostEqual(sim.state['shaft.turn'], 12)
        sim.run(1)
        self.assertAlmostEqual(sim.state['shaft.turn'], 18)
        self.assertEqual(sim.time, 5)

    def test_nonlinear_law_resumes_at_global_time(self):
        sim = Sim(gated(square=True), dt=0.1, meshes=False)
        sim.run(1)
        sim.move('enabled', to=0)
        sim.run(2)
        sim.move('enabled', to=1)
        self.assertAlmostEqual(sim.state['shaft.turn'], 1)
        sim.run(1)
        self.assertAlmostEqual(sim.state['shaft.turn'], 8)

    def test_astrarium_stop_wind_resume(self):
        sim = Sim(astrarium(), dt=0.02, meshes=False)
        sim.run(2)
        sim.move('enabled', to=0)
        sim.run(2)
        sim.move('wind', by=2)
        self.assertAlmostEqual(sim.state['shaft.turn'], 2)
        self.assertAlmostEqual(sim.state['weight.drop'], 0)
        sim.move('enabled', to=1)
        sim.run(1)
        self.assertAlmostEqual(sim.state['shaft.turn'], 3)
        self.assertAlmostEqual(sim.state['weight.drop'], 1)
        self.assertEqual(sim.time, 5)

    def test_exhaustion_discards_missed_travel(self):
        sim = Sim(astrarium(), dt=0.02, meshes=False)
        sim.run(12)
        self.assertAlmostEqual(sim.state['shaft.turn'], 10)
        self.assertAlmostEqual(sim.state['weight.drop'], 10)
        sim.move('enabled', to=0)
        sim.move('wind', by=5)
        sim.move('enabled', to=1)
        sim.run(1)
        self.assertAlmostEqual(sim.state['shaft.turn'], 11)
        self.assertAlmostEqual(sim.state['weight.drop'], 6)

    def test_a_stop_does_not_stop_an_independent_time_drive(self):
        sim = Sim(stopped(), dt=1, meshes=False, record=16)
        sim.run(4)
        self.assertEqual(sim.state['shaft.turn'], 2.5)
        self.assertEqual(sim.state['weight.drop'], 2.5)
        self.assertEqual(sim.state['other.turn'], 8)
        self.assertEqual(sim.time, 4)
        stop = sim.stops[0]
        self.assertEqual(stop.tick, 3)
        self.assertEqual(stop.t, 0.5)
        self.assertEqual(stop.inputs, ())
        self.assertEqual(len(stop.time_drives), 1)

    def test_release_retries_without_a_new_command(self):
        sim = Sim(releasable(), dt=1, meshes=False)
        sim.run(4)
        self.assertEqual(sim.state['shaft.turn'], 2.5)
        sim.move('release', to=10)
        self.assertEqual(sim.time, 4)
        self.assertEqual(sim.state['shaft.turn'], 2.5)
        sim.run(1)
        self.assertEqual(sim.state['shaft.turn'], 3.5)

    def test_snapshot_replay_and_reset(self):
        sim = Sim(astrarium(), dt=0.1, meshes=False, record=20)
        sim.run(2)
        saved = sim.snapshot()
        def sequence():
            sim.move('enabled', to=0)
            sim.run(1)
            sim.move('wind', by=1)
            sim.move('enabled', to=1)
            sim.run(2)
            return dict(sim.state), sim.time, sim.crossings, sim.stops
        first = sequence()
        sim.restore(saved)
        self.assertEqual(sequence(), first)
        sim.reset()
        self.assertEqual(sim.time, 0)
        self.assertEqual(sim.state['shaft.turn'], 0)
        sim.run(1)
        self.assertAlmostEqual(sim.state['shaft.turn'], 1)


class ExistingControlsTest(BaseNodeTest):
    def test_commanded_rate_still_runs(self):
        class Commanded(AssemblyNode):
            time = Time.running()
            drive = Driver(default=0)
            shaft = Shaft()
            drive.drives(shaft.turn, ratio=6)
        sim = Sim(Commanded(), dt=0.1, meshes=False)
        sim.rate('drive', 1)
        sim.run(2)
        self.assertAlmostEqual(sim.state['shaft.turn'], 12)

    def test_direct_joint_assignment_remains_doubly_bound(self):
        class HandBound(AssemblyNode):
            time = Time.running()
            shaft = Shaft()
            def simulate(self):
                self.shaft.turn = self.time
        with self.assertRaises(DoublyBound):
            Sim(HandBound(), dt=0.1, meshes=False)


class DeclarationTest(BaseNodeTest):
    def test_other_bases_and_every_clock_target_remain_refused(self):
        for base in (Time.elapsed(), Time(loop=4)):
            with self.subTest(base=base):
                with self.assertRaisesRegex(TypeError, 'Time.running'):
                    class WrongSource(AssemblyNode):
                        time = base
                        shaft = Shaft()
                        time.drives(shaft.turn)
        for base in (Time.running(), Time.elapsed(), Time(loop=4)):
            with self.subTest(base=base):
                with self.assertRaisesRegex(TypeError, 'clock'):
                    class WrongTarget(AssemblyNode):
                        time = base
                        drive = Driver(default=0)
                        drive.drives(time)

    def test_foreign_clock_is_refused_by_owner(self):
        class Owner(AssemblyNode):
            time = Time.running()
        with self.assertRaisesRegex(TypeError, 'own time base'):
            class Foreign(AssemblyNode):
                time = Time.running()
                shaft = Shaft()
                Owner.time.drives(shaft.turn)

    def test_a_child_cannot_create_another_clock(self):
        class Child(AssemblyNode):
            time = Time.running()
            shaft = Shaft()
            time.drives(shaft.turn)
        class Root(AssemblyNode):
            time = Time.running()
            child = Child()
        with self.assertRaisesRegex((TypeError, UnsupportedLaw), 'root|ROOT'):
            Sim(Root(), 0.1, meshes=False)

    def test_redeclaring_time_does_not_retarget_an_inherited_relation(self):
        class Original(AssemblyNode):
            time = Time.running()
            shaft = Shaft()
            time.drives(shaft.turn)
        class Replacement(Original):
            time = Time.running()
        with self.assertRaisesRegex(TypeError, 'own time base'):
            Sim(Replacement(), 0.1, meshes=False)

    def test_group_order_and_factory_owners(self):
        called = []
        def law(owners, target):
            called.append((owners, target))
            return lambda enabled, seconds: 3*seconds*(enabled > 0.5)
        class Ordered(AssemblyNode):
            time = Time.running()
            enabled = Driver(default=1)
            shaft = Shaft()
            (enabled & time).drives(shaft.turn, law=law)
        node = Ordered()
        sim = Sim(node, 0.1, meshes=False)
        sim.run(1)
        self.assertAlmostEqual(sim.state['shaft.turn'], 3)
        self.assertEqual(len(called), 1)
        self.assertIs(called[0][0][0], node)
        self.assertIs(called[0][0][1], node)
        self.assertIs(called[0][1], node.shaft)

    def test_clock_is_not_commandable_or_in_the_bank(self):
        sim = Sim(affine(), 0.1, meshes=False)
        for call in (lambda: sim.move('time', by=1),
                     lambda: sim.rate('time', 1)):
            with self.assertRaisesRegex(ValueError, 'declared input'):
                call()
        self.assertNotIn('time', sim.state)
        self.assertFalse(sim.drivers)

    def test_free_captured_clock_explains_the_explicit_source(self):
        def hidden(owners, target):
            elapsed = owners[0].time
            return lambda drive, angle: drive + elapsed*(angle < 100)
        class Hidden(AssemblyNode):
            time = Time.running()
            drive = Driver(default=0)
            shaft = Shaft()
            (drive & shaft.turn).drives(shaft.turn, law=hidden)
            def simulate(self):
                if self.shaft.turn.value is None:
                    self.shaft.turn = 0
        with self.assertRaisesRegex(UnsupportedLaw, 'time.*drives'):
            Sim(Hidden(), 0.1, meshes=False)


class StopAndLifecycleTest(BaseNodeTest):
    def test_curved_upstream_time_path_keeps_train_coherent(self):
        for dt in (2, 0.5, 0.02):
            with self.subTest(dt=dt):
                sim = Sim(curved_stop(), dt, meshes=False, record=100)
                sim.run(2)
                self.assertAlmostEqual(sim.state['shaft.turn'], 2, places=8)
                self.assertEqual(sim.state['follower.turn'], 2)
                self.assertEqual(sim.time, 2)

    def test_grouped_targets_stop_together(self):
        class Grouped(AssemblyNode):
            time = Time.running()
            first = Shaft(turn=Revolute(axis=(0, 0, 1), range=(0, 2.5)))
            second = Shaft()
            time.drives((first.turn, second.turn),
                        law=lambda owner, targets: lambda t: (t, 2*t))
        sim = Sim(Grouped(), 1, meshes=False, record=10)
        sim.run(4)
        self.assertEqual(sim.state['first.turn'], 2.5)
        self.assertEqual(sim.state['second.turn'], 5)
        self.assertEqual(len(sim.stops[0].time_drives), 1)

    def test_mixed_stop_retires_command_but_not_clock(self):
        sim = Sim(mixed(), 1, meshes=False, record=10)
        command = sim.rate('assist', 1)
        sim.run(2)
        self.assertEqual(sim.state['shaft.turn'], 2.5)
        self.assertEqual(command.status, 'blocked')
        self.assertEqual(command.admitted, 1.25)
        self.assertEqual(sim.stops[0].inputs, ('assist',))
        self.assertEqual(len(sim.stops[0].time_drives), 1)
        sim.run(1)
        self.assertEqual(sim.time, 3)
        self.assertEqual(sim.state['shaft.turn'], 2.5)
        self.assertEqual(sim.state['assist'], 1.25)

    def test_a_same_tick_release_waits_until_next_tick(self):
        class ReleasedLater(AssemblyNode):
            time = Time.running()
            hoist = Driver(default=0)
            lift = Shaft()
            shaft = Shaft(turn=Revolute(axis=(0, 0, 1), range=(0, Bound(
                lambda turn, lift: 10*(lift >= 1), reads=(lift.turn,)))))
            hoist.drives(lift.turn)
            time.drives(shaft.turn)
        sim = Sim(ReleasedLater(), 1, meshes=False)
        sim.move('hoist', to=2, duration=1)
        sim.run(1)
        self.assertEqual(sim.state['shaft.turn'], 0)
        self.assertEqual(sim.state['lift.turn'], 2)
        sim.run(1)
        self.assertEqual(sim.state['shaft.turn'], 1)

    def test_conflict_rolls_back_time_bank_and_records(self):
        class Conflicted(AssemblyNode):
            time = Time.running()
            drive = Driver(default=0)
            wrist = Revolute(axis=(0, 0, 1), range=(0, 5))
            tool = Revolute(axis=(0, 1, 0))
            left = wrist + 2*tool
            time.drives(wrist, ratio=10)
            wrist.drives(tool)
            drive.drives(left)
        sim = Sim(Conflicted(), 1, meshes=False, record=10)
        before = dict(sim.state)
        command = sim.move('drive', by=30, duration=1)
        # The first half agrees; after wrist's time drive stops, the
        # independent commanded total continues and the second half fails.
        with self.assertRaises(RunConflict):
            sim.run(1)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.time, 0)
        self.assertEqual(sim.stops, [])
        self.assertEqual(sim.crossings, [])
        self.assertEqual(command.status, 'refused')
        self.assertEqual(command.admitted, 0)

    def test_due_action_reads_committed_state(self):
        sim = Sim(affine(), 0.5, meshes=False)
        seen = []
        sim.every(1, lambda: seen.append((sim.time, sim.state['shaft.turn'])))
        sim.run(1)
        self.assertEqual(seen, [(1, 6)])

    def test_a_new_simulation_takes_exclusive_ownership(self):
        node = affine()
        first = Sim(node, 0.1, meshes=False)
        first.run(1)
        second = Sim(node, 0.1, meshes=False)
        with self.assertRaisesRegex(RuntimeError, 'own|taken'):
            first.run(1)
        second.run(1)
        self.assertAlmostEqual(second.state['shaft.turn'], 6)


class PublicationTest(BaseNodeTest):
    def test_time_drive_document_is_explicit(self):
        from .test_running_document import document
        node = affine()
        sim = Sim(node, 0.1, meshes=False)
        sim.run(1)
        before = dict(sim.state)
        doc = document(node)
        self.assertEqual(doc['version'], 11)
        program = doc['program']
        self.assertEqual(program['time_drives'], [{'id': '@time:0', 'edge': 0}])
        self.assertEqual(program['edges'][0]['needs'], ['time'])
        self.assertEqual(program['sources']['shaft.turn'], ['@time:0'])
        self.assertNotIn('time', program['sources'])
        self.assertEqual(list(program['coordinates']), ['shaft.turn'])
        self.assertEqual(doc['drivers'], {})
        self.assertEqual(document(node), doc)
        self.assertEqual(dict(sim.state), before)
        self.assertEqual(sim.time, 1)
        sim.run(1)
        self.assertAlmostEqual(sim.state['shaft.turn'], 12)

    def test_independent_and_self_read_drives_publish(self):
        from .test_running_document import document
        for factory in (stopped, astrarium):
            with self.subTest(factory=factory):
                node = factory()
                Sim(node, 0.1, meshes=False)
                doc = document(node)
                self.assertEqual(doc['version'], 11)
                drives = doc['program']['time_drives']
                self.assertEqual(len(drives), 2 if factory is stopped else 1)
                for drive in drives:
                    edge = doc['program']['edges'][drive['edge']]
                    self.assertIn('time', edge['needs'])
                    self.assertNotIn('time', edge['gives'])
