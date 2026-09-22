# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The running simulation: the run owns the coordinates.

OpenSpec change ``run-owns-the-coordinates``, cycle 1 of the open-run
campaign. A root declaring ``time = Time.running()`` gets a simulation
that owns a BANK of every driver and every joint coordinate of the
linked tree, initialized from the untimed rest pose, bound by the run on
every tick, and advanced by INCREMENTS: over one tick a continuous law
contributes exactly ``f(end) - f(start)`` to its driven coordinate, from
where it stood.

Originating projects: the Curta ``InputMesh`` bench, whose transmission
pinion could only say where it IS and never where it WAS, and the
Pascaline module, whose dials must accumulate without register re-entry.

Everything here is new behaviour; nothing in it changes what an untimed
or looping root does, which the untouched suites pin.
"""

import gc
import tracemalloc
from unittest import TestCase
from unittest.mock import patch

from machinome.core.serializer import instructions_table
from machinome.motion.couplings import DoublyBound
from machinome.motion.ports import get_coordinate
from machinome.simulation import Instruction, RunConflict, Sim, UnsupportedLaw

from .base import BaseNodeTest
from .running_project.machine import (Backwards, Clearing, ContinuousRead,
                                      Differential, Follower,
                                      Guarded, HandBound, LoopingTrain,
                                      Opaque, PlainClearing, PortSelfRead,
                                      Ranged, RangedExact, RemainderRead,
                                      Sixfree,
                                      SpringBank, SpringBankBody, StatedBelow,
                                      Stdlib, Stepped, SteppedBody, Stepper,
                                      Train, TrainBody, Unbound,
                                      UnrestedClearing)


def reads(node, name):
    """The value a coordinate of `node` holds, by the name the port
    enumeration reports it under."""
    return get_coordinate(node, name)._value


def turned(node):
    """The angle the joint placed `node` at, off its own operations --
    pixels for a kinematic model: the body moved, not only the number."""
    for operation in node.operations:
        if getattr(operation, '_motion', False) and hasattr(operation, 'angle'):
            return operation.angle
    return None


def slid(node):
    for operation in node.operations:
        if (getattr(operation, '_motion', False)
                and hasattr(operation, 'translation')):
            return operation.translation
    return None


class BankTest(BaseNodeTest):
    """(2) The bank is every driver and every joint coordinate of the
    linked tree, by qualified id, and its initial values are the untimed
    rest pose."""

    def test_the_bank_lists_drivers_and_joint_coordinates_only(self):
        sim = Sim(Train(), 0.1)
        self.assertEqual(sorted(sim.state), [
            'crank', 'first.turn', 'lever', 'second.turn', 'slide.travel',
            'spindle'])

    def test_the_initial_bank_is_the_untimed_rest_pose(self):
        sim = Sim(Train(), 0.1, state={'crank': 10.0})
        self.assertEqual(sim.state, {
            'crank': 10.0,
            'lever': 100.0,
            'first.turn': 20.0,
            'second.turn': -30.0,
            'slide.travel': 4.0,
            'spindle': 10.0,
        })
        self.assertEqual(sim.tick, 0)
        self.assertEqual(sim.time, 0.0)
        self.assertTrue(sim.running)

    def test_a_plain_port_is_computed_by_the_enumeration_not_banked(self):
        node = Train()
        sim = Sim(node, 0.1, state={'crank': 10.0})
        self.assertNotIn('wheel.turn', sim.state)
        self.assertEqual(reads(node.wheel, 'turn'), 10.0)

    def test_a_joint_on_a_leaf_is_owned_like_any_other(self):
        node = Train()
        Sim(node, 0.1, state={'crank': 10.0})
        self.assertEqual(reads(node.first, 'turn'), 20.0)
        self.assertEqual(turned(node.first), 20.0)

    def test_state_refuses_a_coordinate_id(self):
        with self.assertRaises(ValueError) as caught:
            Sim(Train(), 0.1, state={'first.turn': 12.0})
        self.assertIn('first.turn', str(caught.exception))

    def test_the_running_surface_is_refused_under_a_looping_root(self):
        sim = Sim(LoopingTrain(), 0.1)
        self.assertFalse(sim.running)
        for call in (lambda: sim.move('crank', by=1.0, duration=1.0),
                     lambda: sim.rate('crank', 1.0),
                     lambda: sim.snapshot(),
                     lambda: sim.restore(None),
                     lambda: sim.reset(),
                     lambda: sim.commands,
                     lambda: sim.program,
                     lambda: sim.initial):
            with self.subTest(call=call):
                with self.assertRaises(TypeError) as caught:
                    call()
                self.assertIn('Time.running()', str(caught.exception))


class IntegrationTest(BaseNodeTest):
    """(3) Moves accumulate; an affine chain follows; a law with a kink
    integrates exactly."""

    def test_two_moves_accumulate_through_the_train(self):
        node = Train()
        sim = Sim(node, 0.1)
        first = sim.move('crank', by=10.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(first.status, 'completed')
        self.assertEqual(first.admitted, 10.0)
        second = sim.move('crank', by=10.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(second.status, 'completed')
        self.assertEqual(second.admitted, 10.0)
        self.assertEqual(sim.state['crank'], 20.0)
        self.assertEqual(sim.state['first.turn'], 40.0)
        self.assertEqual(sim.state['second.turn'], -60.0)
        self.assertEqual(turned(node.first), 40.0)
        self.assertEqual(turned(node.second), -60.0)

    def test_a_law_with_a_kink_integrates_exactly(self):
        sim = Sim(Train(), 0.1)
        sim.move('lever', by=40.0, duration=0.8)
        sim.run(0.3)
        self.assertEqual(sim.state['slide.travel'], 13.6)
        sim.run(0.1)
        # The same arithmetic the law performs: 4 + 72*clamp01(6.5/11.25).
        self.assertEqual(sim.state['slide.travel'], 45.599999999999994)
        sim.run(0.1)
        self.assertEqual(sim.state['slide.travel'], 76.0)
        sim.run(0.3)
        self.assertEqual(sim.state['slide.travel'], 76.0)
        self.assertEqual(sim.state['lever'], 140.0)

    def test_backward_propagation_through_an_invertible_law(self):
        sim = Sim(Backwards(), 0.1)
        sim.move('crank', by=10.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(sim.state['first.turn'], 20.0)
        self.assertEqual(sim.state['second.turn'], 5.0)

    def test_an_undriven_joint_holds_on_every_tick(self):
        sim = Sim(Train(), 0.1)
        seen = []
        sim.every(0.1, lambda: seen.append(
            (sim.state['lever'], sim.state['slide.travel'])))
        sim.move('crank', by=10.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(len(seen), 10)
        self.assertEqual(set(seen), {(100.0, 4.0)})


class ConflictTest(BaseNodeTest):
    """(6) Two inputs prescribing one rigid group."""

    def test_a_disagreeing_tick_is_refused_and_commits_nothing(self):
        node = Differential()
        sim = Sim(node, 0.1)
        before = dict(sim.state)
        handle = sim.move('wrist_in', by=10.0, duration=1.0)
        with self.assertRaises(RunConflict) as caught:
            sim.run(0.1)
        message = str(caught.exception)
        self.assertIn('left', message)
        self.assertIn('wrist', message)
        self.assertIn('tool', message)
        self.assertIn('sum_in', message)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.tick, 0)
        self.assertEqual(reads(node, 'wrist'), before['wrist'])
        self.assertEqual(handle.status, 'refused')
        self.assertEqual(handle.admitted, 0.0)
        self.assertEqual(sim.commands, ())

    def test_the_refused_increments_are_named(self):
        sim = Sim(Differential(), 0.1)
        sim.move('wrist_in', by=10.0, duration=0.1)
        with self.assertRaises(RunConflict) as caught:
            sim.run(0.1)
        message = str(caught.exception)
        self.assertIn('30', message)
        self.assertIn('0', message)

    def test_the_same_group_moved_consistently_is_admitted(self):
        node = Differential()
        sim = Sim(node, 0.1)
        sim.move('wrist_in', by=10.0, duration=1.0)
        sim.move('sum_in', by=30.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(sim.state['wrist'], 10.0)
        self.assertEqual(sim.state['tool'], 10.0)
        self.assertEqual(reads(node, 'left'), 30.0)


class AuthorBindingTest(BaseNodeTest):
    """(7) A law stated imperatively is refused; a guarded rest default
    keeps working."""

    def test_an_unconditional_author_binding_is_refused(self):
        with self.assertRaises(DoublyBound) as caught:
            Sim(HandBound(), 0.1)
        message = str(caught.exception)
        self.assertIn('HandBound', message)
        self.assertIn('first.turn', message)
        self.assertIn('running simulation', message)

    def test_a_guarded_rest_default_keeps_working(self):
        node = Guarded()
        sim = Sim(node, 0.1)
        self.assertEqual(sim.state['slide.travel'], 4.0)
        sim.move('crank', by=10.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(sim.state['slide.travel'], 4.0)
        self.assertEqual(reads(node.slide, 'travel'), 4.0)


class SnapshotTest(BaseNodeTest):
    """(8), (9) Snapshot, restore and reset act on the run's bank."""

    def test_a_snapshot_restores_mid_run(self):
        node = Train()
        sim = Sim(node, 0.1)
        sim.move('crank', by=10.0, duration=1.0)
        sim.run(0.5)
        saved = sim.snapshot()
        self.assertEqual(saved, sim.snapshot())
        sim.run(0.5)
        completed = dict(sim.state)
        sim.restore(saved)
        self.assertEqual(sim.state, dict(saved.bank))
        self.assertEqual(sim.tick, saved.tick)
        self.assertEqual(reads(node.first, 'turn'), sim.state['first.turn'])
        sim.run(0.5)
        self.assertEqual(sim.state, completed)

    def test_a_mismatched_program_is_refused_before_anything_changes(self):
        sim = Sim(Train(), 0.1)
        other = Sim(Backwards(), 0.1)
        alien = other.snapshot()
        before = dict(sim.state)
        with self.assertRaises(ValueError) as caught:
            sim.restore(alien)
        message = str(caught.exception)
        self.assertIn(sim.program.identity, message)
        self.assertIn(alien.program, message)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.tick, 0)

    def test_a_mismatched_dt_is_refused(self):
        fine = Sim(Train(), 0.05)
        coarse = Sim(Train(), 0.1)
        with self.assertRaises(ValueError) as caught:
            coarse.restore(fine.snapshot())
        message = str(caught.exception)
        self.assertIn('0.05', message)
        self.assertIn('0.1', message)

    def test_reset_returns_to_the_initial_snapshot(self):
        sim = Sim(Train(), 0.1, record=8)
        sim.move('crank', by=10.0, duration=1.0)
        sim.run(1.0)
        sim.reset()
        self.assertEqual(sim.snapshot(), sim.initial)
        self.assertEqual(sim.tick, 0)
        self.assertEqual(sim.state['crank'], 0.0)
        self.assertEqual(sim.state['first.turn'], 0.0)
        self.assertEqual(sim.commands, ())
        self.assertEqual(sim.trajectory, [])

    def test_a_handle_issued_before_a_restore_is_cancelled(self):
        sim = Sim(Train(), 0.1)
        saved = sim.snapshot()
        handle = sim.move('crank', by=10.0, duration=1.0)
        sim.run(0.5)
        sim.restore(saved)
        self.assertEqual(handle.status, 'cancelled')
        self.assertEqual(handle.admitted, 5.0)

    def test_a_snapshot_after_a_cancel_carries_no_command(self):
        sim = Sim(Train(), 0.1)
        handle = sim.move('crank', by=10.0, duration=1.0)
        sim.run(0.2)
        handle.cancel()
        snapshot = sim.snapshot()
        self.assertEqual(snapshot.commands, ())
        sim.run(0.3)
        sim.restore(snapshot)
        self.assertEqual(sim.commands, ())
        bank = dict(sim.state)
        sim.run(0.2)
        self.assertEqual(sim.state, bank)

    def test_a_snapshot_before_a_cancel_reissues_the_command(self):
        sim = Sim(Train(), 0.1)
        handle = sim.move('crank', by=10.0, duration=1.0)
        sim.run(0.2)
        saved = sim.snapshot()
        sim.run(0.1)
        handle.cancel()
        sim.restore(saved)
        self.assertEqual(handle.status, 'cancelled')
        self.assertEqual(handle.admitted, 3.0)
        fresh, = sim.commands
        self.assertIsNot(fresh, handle)
        self.assertEqual(fresh.status, 'active')
        sim.run(0.1)
        self.assertEqual(sim.state['crank'], 3.0)


class ProgramReductionRunTest(BaseNodeTest):
    """OpenSpec change ``publish-only-what-runs``: shrinking the
    compiled program's coordinate table to what it computes changes
    nothing about the RUN -- the relation onto a `.repeat()` child's
    port is left to the ordinary enumeration exactly as before, and the
    identity a snapshot is checked against is a digest of the inputs,
    the coordinates, the spans and the edges, never of the node table
    the reduction shrinks."""

    def test_a_repeated_ports_run_follows_the_driver_like_the_untimed_pose(self):
        node = SpringBank()
        sim = Sim(node, 0.1)
        sim.move('lift', by=6.0, duration=0.5)
        for _ in range(6):
            sim.run(0.1)
            lift = sim.state['lift']
            untimed = SpringBankBody()
            untimed.set_state(lift=lift)
            for copy, reference in zip(node.springs, untimed.springs):
                self.assertAlmostEqual(reads(copy, 'height'),
                                       reads(reference, 'height'))

    def test_the_identity_a_repeated_ports_program_compiles_to_is_stable(self):
        """Compiled twice in the same process, over the same tree
        shape, the identity does not move: the second reading is taken
        from a fresh compile, not from a stored digest."""
        first = Sim(SpringBank(), 0.1).program.identity
        second = Sim(SpringBank(), 0.1).program.identity
        self.assertEqual(first, second)

    def test_only_the_source_timing_generation_changes_trains_old_identity(self):
        """The corpus is COMMITTED data, captured from a run of this
        framework. Reading `Train`'s freshly compiled identity against
        it -- rather than against a second in-process reading -- is
        what proves the reduction does not move an identity an existing
        snapshot was already checked against."""
        import json
        import os

        corpus_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'running-corpus.json')
        with open(corpus_path) as handle:
            corpus = json.load(handle)
        identities = {entry['document']['program']['identity']
                     for entry in corpus['machines'] if entry['name'] == 'Train'}
        import hashlib
        program = Sim(Train(), 0.1).program
        self.assertNotIn(program.identity, identities)
        old = '\n'.join(line for line in program.described().split('\n')
                        if line != 'source-timing version=11')
        self.assertEqual(identities, {hashlib.sha256(old.encode()).hexdigest()})


class InstructionTest(BaseNodeTest):
    """(10) Instructions under a running root are moves; `by=` is
    relative everywhere."""

    def test_a_relative_instruction_accumulates(self):
        sim = Sim(Train(), 0.1)
        sim.trigger('Advance')
        sim.run(0.5)
        self.assertEqual(sim.state['crank'], 10.0)
        sim.trigger('Advance')
        sim.run(0.5)
        self.assertEqual(sim.state['crank'], 20.0)

    def test_an_absolute_instruction_moves_to_its_target(self):
        sim = Sim(Train(), 0.1)
        sim.trigger('Advance')
        sim.run(0.5)
        sim.trigger('Advance')
        sim.run(0.5)
        sim.trigger('Park')
        sim.run(0.5)
        self.assertEqual(sim.state['crank'], 40.0)

    def test_a_relative_instruction_ramps_under_a_looping_root(self):
        sim = Sim(LoopingTrain(), 0.1)
        sim.trigger('Advance')
        sim.run(0.5)
        self.assertEqual(sim.state['crank'], 10.0)
        sim.trigger('Advance')
        sim.run(0.5)
        self.assertEqual(sim.state['crank'], 20.0)

    def test_the_declaration_reads_back_one_of_the_two(self):
        relative = Instruction(by={'crank': 10.0}, duration=0.5)
        absolute = Instruction({'crank': 40.0}, duration=0.5)
        self.assertEqual(relative.by, {'crank': 10.0})
        self.assertIsNone(relative.targets)
        self.assertEqual(absolute.targets, {'crank': 40.0})
        self.assertIsNone(absolute.by)

    def test_exactly_one_of_targets_and_by(self):
        with self.assertRaises(TypeError):
            Instruction({'crank': 0.0}, duration=1.0, by={'crank': 1.0})
        with self.assertRaises(TypeError):
            Instruction(duration=1.0)

    def test_an_instruction_whose_input_is_owned_starts_nothing(self):
        sim = Sim(Train(), 0.1)
        rate = sim.rate('crank', 90.0)
        with self.assertRaises(ValueError) as caught:
            sim.trigger('Wind')
        self.assertIn('crank', str(caught.exception))
        # 'Wind' names `lever` too, and nothing was started on it.
        self.assertEqual(sim.commands, (rate,))


class CommandTest(BaseNodeTest):
    """(11) One owner per input, an outcome handle, retirement."""

    def test_a_rate_and_a_move_on_one_input_conflict(self):
        sim = Sim(Train(), 0.1)
        rate = sim.rate('crank', 90.0)
        with self.assertRaises(ValueError) as caught:
            sim.move('crank', by=10.0, duration=1.0)
        message = str(caught.exception)
        self.assertIn('crank', message)
        self.assertIn('rate', message)
        self.assertEqual(rate.status, 'active')

    def test_two_moves_on_one_input_conflict(self):
        sim = Sim(Train(), 0.1)
        sim.move('crank', by=10.0, duration=1.0)
        with self.assertRaises(ValueError) as caught:
            sim.move('crank', by=10.0, duration=1.0)
        self.assertIn('crank', str(caught.exception))

    def test_a_rate_accumulates_until_released(self):
        sim = Sim(Train(), 0.1)
        handle = sim.rate('crank', 90.0)
        sim.run(2.0)
        sim.rate('crank', 0)
        self.assertEqual(sim.state['crank'], 180.0)
        self.assertEqual(sim.state['first.turn'], 360.0)
        self.assertEqual(handle.status, 'completed')
        self.assertEqual(handle.admitted, 180.0)
        self.assertEqual(sim.commands, ())

    def test_releasing_an_unowned_input_is_a_no_op(self):
        sim = Sim(Train(), 0.1)
        self.assertIsNone(sim.rate('crank', 0))
        self.assertEqual(sim.commands, ())

    def test_a_reverse_request_runs(self):
        """Cycle 3: a reverse move meets a stop exactly as a forward one
        does, and a crank that meets none runs backwards through the same
        laws."""
        for kind, call, landed in (
                ('by', lambda sim: sim.move('crank', by=-10.0, duration=1.0),
                 10.0),
                ('to', lambda sim: sim.move('crank', to=5.0, duration=1.0),
                 5.0),
                ('rate', lambda sim: sim.rate('crank', -90.0), -70.0)):
            with self.subTest(kind=kind):
                node = Train()
                sim = Sim(node, 0.1)
                sim.move('crank', by=20.0, duration=1.0)
                sim.run(1.0)
                handle = call(sim)
                sim.run(1.0)
                if kind == 'rate':
                    sim.rate('crank', 0)
                self.assertEqual(sim.state['crank'], landed)
                self.assertEqual(sim.state['first.turn'], landed * 2)
                self.assertEqual(sim.state['second.turn'], landed * -3.0)
                self.assertEqual(reads(node.first, 'turn'), landed * 2)
                self.assertEqual(handle.status, 'completed')
                self.assertEqual(handle.admitted, landed - 20.0)

    def test_a_reverse_rate_on_an_integer_input_truncates_toward_zero(self):
        """A negative rate rounds the way a positive one does: `trunc`,
        not `floor`, so the state neither leads nor lags by a whole
        native unit depending on direction."""
        for rate, expected in ((-1.5, [-1, -3, -4, -6]),
                               (1.5, [1, 3, 4, 6])):
            with self.subTest(rate=rate):
                sim = Sim(Stepper(), 1.0)
                sim.rate('step', rate)
                trace = []
                for _ in range(4):
                    sim.run(1.0)
                    trace.append(sim.state['step'])
                self.assertEqual(trace, expected)
                self.assertEqual(sim.state['carriage.travel'], expected[-1])

    def test_only_a_declared_input_can_be_moved(self):
        sim = Sim(Train(), 0.1)
        with self.assertRaises(ValueError) as caught:
            sim.move('first.turn', by=10.0, duration=1.0)
        message = str(caught.exception)
        self.assertIn('first.turn', message)
        self.assertIn('crank', message)
        self.assertIn('lever', message)

    def test_completed_commands_are_retired(self):
        sim = Sim(Train(), 0.1)
        handles = []
        for _ in range(100):
            handles.append(sim.move('crank', by=1.0, duration=0.1))
            sim.run(0.1)
            self.assertLessEqual(len(sim.commands), 1)
        self.assertEqual(sim.state['crank'], 100.0)
        self.assertTrue(all(handle.status == 'completed'
                            for handle in handles))

    def test_a_zero_duration_move_integrates_now(self):
        node = Train()
        sim = Sim(node, 0.1)
        sim.run(2.0)
        self.assertEqual(sim.tick, 20)
        handle = sim.move('crank', by=10.0, duration=0)
        self.assertEqual(sim.tick, 20)
        self.assertEqual(sim.state['crank'], 10.0)
        self.assertEqual(sim.state['first.turn'], 20.0)
        self.assertEqual(reads(node.first, 'turn'), 20.0)
        self.assertEqual(handle.status, 'completed')
        self.assertEqual(sim.commands, ())


class CancelTest(BaseNodeTest):
    """`cancel()` RETIRES the command: the input is free at once, the
    handle keeps reporting what it admitted, and nothing else moves."""

    def test_cancel_before_the_first_tick_moves_nothing(self):
        sim = Sim(Train(), 0.1)
        before = dict(sim.state)
        handle = sim.move('crank', by=10.0, duration=1.0)
        handle.cancel()
        sim.run(0.1)
        self.assertEqual(handle.status, 'cancelled')
        self.assertEqual(handle.admitted, 0.0)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.commands, ())

    def test_cancel_midway_keeps_the_travel_it_made(self):
        sim = Sim(Train(), 0.1)
        handle = sim.move('crank', by=10.0, duration=1.0)
        sim.run(0.3)
        handle.cancel()
        self.assertEqual(handle.status, 'cancelled')
        self.assertEqual(handle.admitted, 3.0)
        bank = dict(sim.state)
        sim.run(0.7)
        self.assertEqual(sim.state, bank)
        self.assertEqual(handle.admitted, 3.0)
        self.assertEqual(sim.commands, ())

    def test_a_cancelled_rate_stops(self):
        sim = Sim(Train(), 0.1)
        handle = sim.rate('crank', 90.0)
        sim.run(0.3)
        handle.cancel()
        self.assertEqual(handle.status, 'cancelled')
        self.assertEqual(handle.admitted, 27.0)
        self.assertIsNone(handle.remaining)
        bank = dict(sim.state)
        sim.run(0.3)
        self.assertEqual(sim.state, bank)
        self.assertEqual(sim.commands, ())

    def test_a_replacement_is_accepted_at_once(self):
        sim = Sim(Train(), 0.1)
        handle = sim.move('crank', by=10.0, duration=1.0)
        sim.run(0.3)
        handle.cancel()
        replacement = sim.move('crank', by=5.0, duration=0.5)
        self.assertEqual(sim.commands, (replacement,))
        sim.run(0.5)
        self.assertEqual(replacement.status, 'completed')
        self.assertEqual(sim.state['crank'], 8.0)
        self.assertEqual(sim.state['first.turn'], 16.0)

    def test_cancelling_twice_is_cancelling_once(self):
        sim = Sim(Train(), 0.1)
        first = sim.move('crank', by=10.0, duration=1.0)
        sim.run(0.3)
        first.cancel()
        replacement = sim.move('crank', by=5.0, duration=0.5)
        first.cancel()
        self.assertEqual(first.status, 'cancelled')
        self.assertEqual(first.admitted, 3.0)
        self.assertEqual(replacement.status, 'active')
        self.assertEqual(sim.commands, (replacement,))
        sim.run(0.1)
        self.assertEqual(replacement.status, 'active')
        self.assertEqual(replacement.admitted, 1.0)

    def test_cancel_on_a_retired_handle_does_nothing(self):
        completed_sim = Sim(Train(), 0.1)
        completed = completed_sim.move('crank', by=10.0, duration=1.0)
        completed_sim.run(1.0)
        completed.cancel()
        self.assertEqual(completed.status, 'completed')
        self.assertEqual(completed.admitted, 10.0)
        self.assertEqual(completed_sim.commands, ())

        blocked_sim = Sim(Ranged(), 0.1)
        blocked = blocked_sim.move('crank', by=50.0, duration=0.5)
        blocked_sim.run(0.5)
        blocked.cancel()
        self.assertEqual(blocked.status, 'blocked')
        self.assertEqual(blocked.admitted, 45.0)
        self.assertEqual(blocked_sim.commands, ())

        refused_sim = Sim(Differential(), 0.1)
        refused = refused_sim.move('wrist_in', by=10.0, duration=1.0)
        with self.assertRaises(RunConflict):
            refused_sim.run(0.1)
        refused.cancel()
        self.assertEqual(refused.status, 'refused')
        self.assertEqual(refused.admitted, 0.0)
        self.assertEqual(refused_sim.commands, ())

    def test_cancelling_one_command_leaves_the_other_running(self):
        sim = Sim(Train(), 0.1)
        crank_handle, lever_handle = sim.trigger('Wind')
        crank_handle.cancel()
        self.assertEqual(crank_handle.status, 'cancelled')
        self.assertEqual(sim.commands, (lever_handle,))
        sim.run(0.5)
        self.assertEqual(crank_handle.status, 'cancelled')
        self.assertEqual(crank_handle.admitted, 0.0)
        self.assertEqual(lever_handle.status, 'completed')
        self.assertEqual(lever_handle.admitted, 5.0)

    def test_a_cancelled_run_replays_identically(self):
        def script():
            sim = Sim(Train(), 0.1)
            handle = sim.move('crank', by=10.0, duration=1.0)
            sim.run(0.3)
            handle.cancel()
            sim.run(0.4)
            return (sim.state, sim.tick, handle.status, handle.admitted)

        first = script()
        second = script()
        self.assertEqual(first, second)


class PurityTest(BaseNodeTest):
    """(12) Rendering and rebinding advance nothing."""

    def test_rendering_and_rebinding_change_nothing(self):
        node = Train()
        sim = Sim(node, 0.1)
        sim.move('crank', by=10.0, duration=1.0)
        sim.run(1.0)
        before = dict(sim.state)
        tick = sim.tick
        node.render()
        self.assertEqual(reads(node.first, 'turn'), before['first.turn'])
        self.assertEqual(reads(node.second, 'turn'), before['second.turn'])
        node.set_state(**dict(sim.state, time=sim.time))
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.tick, tick)
        self.assertEqual(reads(node.first, 'turn'), before['first.turn'])
        sim.move('crank', by=10.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(sim.state['crank'], 20.0)
        self.assertEqual(sim.state['first.turn'], 40.0)


class CompileRefusalTest(BaseNodeTest):
    """(13) A law is inspected as the expression it builds."""

    def test_a_jump_compiles(self):
        # Cycle 1 refused this law by name; cycle 2 compiles it into a
        # JUMP PLAN and integrates it over the tick's pieces
        # (`test_running_jumps.py`). What has not changed is the untimed
        # reading, which `SteppedBody` still poses absolutely.
        sim = Sim(Stepped(), 0.1)
        edge, = [edge for edge in sim.program.edges if edge.kind == 'law']
        plan, = edge.plans
        jump, = plan.jumps
        self.assertEqual(jump.primitive, 'floor')
        self.assertTrue(jump.affine)
        self.assertEqual(jump.argument.evaluate({'crank': 720.0}), 2.0)
        self.assertNotIn('floor', str(plan.skeleton))
        body = Sim(SteppedBody(), 0.1, state={'crank': 115.0})
        self.assertEqual(reads(body.node.first, 'turn'), 13.6)

    def test_a_stdlib_law_is_refused_as_non_symbolic(self):
        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(Stdlib(), 0.1)
        self.assertIn('symbol', str(caught.exception))

    def test_an_opaque_source_is_refused(self):
        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(Opaque(), 0.1)
        message = str(caught.exception)
        self.assertIn('relay', message)
        self.assertIn('first.turn', message)

    def test_a_law_with_a_kink_compiles(self):
        sim = Sim(Train(), 0.1)
        text = sim.program.described()
        self.assertIn('lever', text)
        self.assertIn('max', text)
        self.assertIn('min', text)
        self.assertNotIn('floor', text)


class RangeTest(BaseNodeTest):
    """A joint's range STOPS the tick's motion rather than failing it
    (cycle 3). Cycle 1 refused the whole tick here and left the bank at
    the last admitted one; the declaration has not changed, only what the
    run reads it as."""

    def test_the_crossing_tick_commits_at_the_bound(self):
        node = Ranged()
        sim = Sim(node, 0.1, record=8)
        handle = sim.move('crank', by=50.0, duration=0.5)
        sim.run(0.5)
        self.assertEqual(sim.state['first.turn'], 90.0)
        self.assertEqual(sim.state['crank'], 45.0)
        self.assertEqual(reads(node.first, 'turn'), 90.0)
        self.assertEqual(sim.tick, 5)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(handle.admitted, 45.0)
        self.assertEqual(handle.requested, 50.0)
        stop, = sim.stops
        self.assertEqual(stop.coordinate, 'first.turn')
        self.assertEqual(stop.bound, 'high')
        self.assertEqual(stop.value, 90.0)
        self.assertEqual(stop.t, 0.5)
        self.assertEqual(stop.inputs, ('crank',))

    def test_a_move_landing_exactly_on_the_bound_completes(self):
        sim = Sim(RangedExact(), 0.1, record=8)
        handle = sim.move('crank', by=5.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['first.turn'], 90.0)
        self.assertEqual(handle.status, 'completed')
        self.assertEqual(handle.admitted, 5.0)
        self.assertEqual(sim.stops, [])
        self.assertEqual(sim.tick, 1)


class UnboundCoordinateTest(BaseNodeTest):
    """An unbound joint coordinate is refused at construction."""

    def test_a_coordinate_nothing_binds_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            Sim(Unbound(), 0.1)
        message = str(caught.exception)
        self.assertIn('idle.turn', message)
        self.assertIn('rest value', message)

    def test_a_partly_bound_free_joint_names_both_coordinates(self):
        with self.assertRaises(ValueError) as caught:
            Sim(Sixfree(), 0.1)
        message = str(caught.exception)
        self.assertIn('chassis.pose.roll', message)
        self.assertIn('chassis.pose.pitch', message)


class RecordingTest(BaseNodeTest):
    """Recording is explicit and bounded."""

    def test_nothing_is_recorded_by_default(self):
        sim = Sim(Train(), 0.1)
        sim.rate('crank', 1.0)
        sim.run(100.0)
        gc.collect()
        tracemalloc.start()
        sim.run(100.0)
        _current, first = tracemalloc.get_traced_memory()
        tracemalloc.reset_peak()
        sim.run(900.0)
        _current, later = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertEqual(sim.trajectory, [])
        self.assertLess(later - first, 64 * 1024)

    def test_a_ring_keeps_the_most_recent_ticks(self):
        sim = Sim(Train(), 0.1, record=64)
        sim.rate('crank', 1.0)
        sim.run(10.0)
        self.assertEqual(len(sim.trajectory), 64)
        self.assertEqual([tick for tick, _bank in sim.trajectory],
                         list(range(37, 101)))

    def test_an_invalid_recording_option_is_refused(self):
        for value in (0, -1, True, 'all'):
            with self.subTest(record=value):
                with self.assertRaises(ValueError) as caught:
                    Sim(Train(), 0.1, record=value)
                self.assertIn('record', str(caught.exception))


class SetStateCoordinateTest(BaseNodeTest):
    """(2.19) `set_state` accepts a qualified joint-coordinate id under a
    running root, and only there."""

    def test_a_coordinate_id_binds_and_places_under_a_running_root(self):
        node = Unbound()
        node.set_state(crank=0.0)
        node.set_state(**{'idle.turn': 12.0})
        self.assertEqual(reads(node.idle, 'turn'), 12.0)
        self.assertEqual(turned(node.idle), 12.0)

    def test_a_coordinate_a_relation_drives_is_still_the_relations(self):
        """A hand binding is not a run: outside one, a coordinate a
        relation drives is cleared and re-solved by the enumeration
        `set_state` runs, exactly as a hand assignment always was. What
        makes the bank stick is the RUN as the binder, and nothing
        else."""
        node = Train()
        node.set_state(crank=0.0, lever=100.0)
        node.set_state(**{'first.turn': 12.0})
        self.assertEqual(reads(node.first, 'turn'), 0.0)

    def test_a_dotted_coordinate_of_a_multi_coordinate_joint_binds(self):
        node = Sixfree()
        node.set_state(lift=0.0, surge=0.0, sway=0.0, heading=0.0)
        node.set_state(**{'chassis.pose.roll': 3.0})
        self.assertEqual(reads(node.chassis, 'pose.roll'), 3.0)
        self.assertNotIn('pose.roll', vars(node.chassis))

    def test_a_coordinate_id_is_refused_under_any_other_root(self):
        for factory in (LoopingTrain, TrainBody):
            with self.subTest(root=factory.__name__):
                node = factory()
                node.set_state(crank=0.0, lever=100.0)
                with self.assertRaises(ValueError) as caught:
                    node.set_state(**{'first.turn': 12.0})
                message = str(caught.exception)
                self.assertIn('first.turn', message)
                self.assertIn('crank', message)

    def test_a_refused_binding_restores_coordinates_too(self):
        node = Unbound()
        node.set_state(crank=0.0)
        node.set_state(**{'idle.turn': 12.0})
        with self.assertRaises(ValueError) as caught:
            node.set_state(**{'idle.turn': 99.0, 'nobody.turn': 1.0})
        self.assertIn('nobody.turn', str(caught.exception))
        self.assertEqual(reads(node.idle, 'turn'), 12.0)
        self.assertEqual(turned(node.idle), 12.0)


class FollowerTest(BaseNodeTest):
    """(2.24) An author-bound plain port follows a run-owned coordinate,
    and is never marked as the run's."""

    def test_the_port_follows_and_keeps_the_author_as_its_binder(self):
        from machinome.motion.ports import RunBinder

        node = Follower()
        sim = Sim(node, 0.1)
        seen = []

        def check():
            slot = get_coordinate(node.gauge, 'readout')
            seen.append((slot._value, sim.state['gauge.turn'],
                         sim.state['first.turn'],
                         isinstance(slot.binder, RunBinder)))

        sim.every(0.1, check)
        sim.move('crank', by=10.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(len(seen), 10)
        for readout, turn, first, run_bound in seen:
            self.assertEqual(readout, turn)
            self.assertEqual(readout, first)
            self.assertFalse(run_bound)
        self.assertEqual(seen[-1][0], 20.0)
        self.assertEqual(seen[0][0], 2.0)


class RelativeInstructionDocumentTest(BaseNodeTest):
    """(2.25) A relative instruction is not yet published."""

    def test_the_table_carries_the_absolute_entry_only(self):
        from machinome.core.serializer import symbolic_document

        node = Train()
        with symbolic_document(node) as (_declarations, instructions):
            table = instructions_table(instructions)
        self.assertEqual(sorted(table), ['Park'])
        self.assertEqual(table['Park']['targets'], {'crank': 40.0})
        self.assertEqual(table['Park']['duration'], 0.5)


class ReservedClockNameTest(BaseNodeTest):
    """(4.4) `time` is the run's own name, and a bank entry under it
    would be silently overwritten every tick."""

    def test_a_driver_qualifying_to_time_is_refused_at_construction(self):
        from machinome.simulation import sim as sim_module
        from machinome.simulation.driver import Driver as Declaration

        real = sim_module.qualified_drivers

        def with_a_clock_named_driver(node):
            return dict(real(node), time=Declaration(default=0.0))

        with patch.object(sim_module, 'qualified_drivers',
                          with_a_clock_named_driver):
            with self.assertRaises(ValueError) as caught:
                Sim(Train(), 0.1)
        message = str(caught.exception)
        self.assertIn("'time'", message)
        self.assertIn('reserved', message)

    def test_the_python_preview_of_an_unbound_clock_is_unchanged(self):
        """(4.2) Cycle 1's preview, which the document producer alone
        leaves behind: everywhere else an unbound `time` under a running
        root still reads the bare animation variable."""
        node = Train()
        node.set_state(crank=0.0, lever=100.0)
        node.assemble()
        self.assertEqual(str(node.time), '$t')


class OneTreeOneOwnerTest(BaseNodeTest):
    """(6) One simulation owns a tree at a time, and the newest takes
    it -- which is what makes `ScenarioTest.simulation()`'s "fresh per
    call" promise true over a node built once per class."""

    def test_a_second_simulation_over_one_tree_starts_fresh(self):
        node = Train()
        first = Sim(node, 0.1)
        first.move('crank', by=20.0, duration=1.0)
        first.run(1.0)
        self.assertEqual(first.state['crank'], 20.0)

        second = Sim(node, 0.1)

        self.assertEqual(second.state, dict(first.initial.bank))
        self.assertEqual(second.tick, 0)

    def test_a_released_simulation_refuses_to_advance(self):
        node = Train()
        first = Sim(node, 0.1)
        first.move('crank', by=20.0, duration=1.0)
        first.run(0.5)
        second = Sim(node, 0.1)

        with self.assertRaises(RuntimeError) as caught:
            first.run(0.1)
        message = str(caught.exception)
        self.assertIn('Train', message)
        self.assertIn('no longer', message)

        second.move('crank', by=10.0, duration=1.0)
        second.run(1.0)
        self.assertEqual(second.state['crank'], 10.0)
        self.assertEqual(second.state['first.turn'], 20.0)

    def test_an_author_binding_is_still_refused(self):
        with self.assertRaises(DoublyBound) as caught:
            Sim(HandBound(), 0.1)
        message = str(caught.exception)
        self.assertIn('HandBound', message)
        self.assertIn('first.turn', message)

    def test_two_scenarios_of_one_class_run_off_one_built_node(self):
        from machinome.simulation.scenario import ScenarioTest

        class Scenario(ScenarioTest):
            node = Train
            dt = 0.1

        banks = []
        for _ in range(2):
            scenario = Scenario()
            simulation = scenario.simulation()
            simulation.move('crank', by=10.0, duration=1.0)
            simulation.run(1.0)
            banks.append(simulation.state)
        self.assertEqual(banks[0], banks[1])


class StatedBelowRunTest(BaseNodeTest):
    """A LIVE run over the shape `a-read-is-not-a-binding` fixes.

    The child states the relation into its own leaf's joint and the root
    only READS it. A run accepted this all along -- the refusal was the
    producer's epilogue over a tree an ENUMERATION posed -- so what these
    pin is that the completed restore leaves a live run exactly where it
    was: the bank after the publication is the bank the run computed, and
    the next tick goes on from it.
    """

    def test_the_run_poses_both_coordinates_from_its_driver(self):
        node = StatedBelow()
        sim = Sim(node, 0.05)
        sim.move('push', to=2.0, duration=0.2)
        sim.run(0.4)

        self.assertAlmostEqual(sim.state['plug.key.travel'], 2.0)
        self.assertAlmostEqual(sim.state['plug.p1.lift'], 1.0)
        self.assertAlmostEqual(sim.state['d1.lift'], -1.0)

    def test_publishing_under_that_run_leaves_the_bank_alone(self):
        from machinome.core.serializer import symbolic_document

        node = StatedBelow()
        sim = Sim(node, 0.05)
        sim.move('push', to=2.0, duration=0.2)
        sim.run(0.4)
        state = sim.state

        with symbolic_document(node) as (_declarations, _instructions):
            pass

        self.assertEqual(sim.state, state)
        sim.run(0.2)
        self.assertEqual(sim.state, state)


class SelfReadRestTest(BaseNodeTest):
    """A law that READS the coordinate it drives, at REST and at
    COMPILE (OpenSpec change `read-the-driven-coordinate`).

    What the run does with the read is `tests/test_running_reads.py`.
    """

    def test_the_relation_binds_nothing_at_rest(self):
        # The REST render itself: no run owns the tree yet, so this is
        # the pose `Sim` reads the initial bank off.
        rest = Clearing()
        rest.set_state(setter=0.0, ring=500.0, time=0.0)
        record = rest.__dict__['_relations'][0]

        self.assertEqual(record.direction, 'forward')
        self.assertEqual(reads(rest.wheel, 'turn'), 108.0)

        node = Clearing()
        sim = Sim(node, 0.1)
        self.assertEqual(sim.state['wheel.turn'], 108.0)

    def test_the_guarded_rest_default_survives(self):
        node = Clearing(digit=252.0)
        sim = Sim(node, 0.1)

        self.assertEqual(sim.state['wheel.turn'], 252.0)
        self.assertEqual(reads(node.wheel, 'turn'), 252.0)

    def test_a_self_read_with_no_rest_default_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            Sim(UnrestedClearing(), 0.1)

        message = str(caught.exception)
        self.assertIn('wheel.turn', message)
        self.assertIn('needs a rest value for each', message)

    def test_the_fixture_compiles(self):
        sim = Sim(Clearing(), 0.1)

        edges = [edge for edge in sim.program.edges if edge.kind == 'law']
        self.assertEqual(len(edges), 1)
        edge = edges[0]
        self.assertIn(edge.gives[0], edge.needs)

    def test_a_law_whose_skeleton_still_names_the_read_is_refused(self):
        for machine in (ContinuousRead, RemainderRead):
            with self.subTest(machine=machine.__name__):
                with self.assertRaises(UnsupportedLaw) as caught:
                    Sim(machine(), 0.1)
                message = str(caught.exception)
                self.assertIn('wheel.turn', message)
                self.assertIn(machine.__name__, message)
                self.assertIn('PIECEWISE CONSTANT', message)
                self.assertIn('remainder', message)

    def test_a_self_read_of_a_coordinate_the_run_does_not_bank_is_refused(self):
        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(PortSelfRead(), 0.1)

        message = str(caught.exception)
        self.assertIn('wheel.turn', message)
        self.assertIn('retained value is a history', message)

    def test_reaching_inputs_ignores_a_self_need(self):
        sim = Sim(Clearing(), 0.1)
        key = sim._run.keys['wheel.turn']

        self.assertEqual(sorted(sim.program.sources[key]),
                         ['ring', 'setter'])

    def test_the_identity_names_what_the_law_reads(self):
        reading = Sim(Clearing(), 0.1)
        plain = Sim(PlainClearing(), 0.1)

        self.assertIn('wheel.turn', reading.program.described())
        self.assertNotEqual(reading.program.identity, plain.program.identity)
        with self.assertRaises(ValueError):
            plain.restore(reading.snapshot())

    def test_the_compiled_read_is_the_relation_s_declared_one(self):
        """ONE definition of the self-read: the compile takes it off the
        record the class definition wrote, not off a second derivation of
        its own."""
        node = Clearing()
        sim = Sim(node, 0.1)
        relation = node.__dict__['_relations'][0].relation

        # `(setter & ring & wheel.turn).drives(wheel.turn, ...)`: the
        # third member of the source group is the read.
        self.assertEqual(relation.self_read, 2)

        edge = [edge for edge in sim.program.edges if edge.kind == 'law'][0]
        self.assertEqual(len(edge.gives), 1)
        self.assertEqual(edge.gives[0], edge.needs[relation.self_read])
        self.assertEqual([reading is not None for reading in edge.retained],
                         [True])

    def test_naming_the_driven_coordinate_two_ways_is_refused(self):
        """The child standing for its one joint on one side and the
        coordinate on the other: two spellings, two declaration keys, one
        slot. The class definition sees no self-read, so the rest rule
        does not apply and the REST render refuses the relation against
        the author's own guard -- which is why a running machine never
        reaches the compile with the two disagreeing. The compile's own
        slot comparison stands behind this as a backstop for the
        invariant."""
        from machinome.node import AssemblyNode
        from machinome.motion.ports import Time
        from machinome.parameters import Angle
        from machinome.simulation import Driver

        from .running_project.machine import missing_tooth_pair
        from .running_project.parts import Arbor

        class Aliased(AssemblyNode):
            time = Time.running()
            digit = Angle(108.0)
            ring = Driver(default=0.0, unit='deg')
            wheel = Arbor()

            (ring & wheel).drives(wheel.turn, law=missing_tooth_pair)

            def simulate(self):
                if self.wheel.turn.value is None:
                    self.wheel.turn = self.digit

        self.assertIsNone(Aliased._declared_relations[0].self_read)

        with self.assertRaises(DoublyBound) as caught:
            Sim(Aliased(), 0.1)

        message = str(caught.exception)
        self.assertIn('wheel.turn', message)
        self.assertIn("the author's simulate()", message)


class SelectionConstructionTest(BaseNodeTest):
    """A cycle every selection breaks is a BLOCK, and the program orders
    it once per piece (OpenSpec change ``select-the-source``).

    The two halves of the change's construction contract live here
    beside the other construction tests: the union the compiler refused
    is admitted, and the union no selection breaks is refused with the
    message it has always had.
    """

    def test_the_selected_union_constructs(self):
        from .carriage_project.machine import ShiftedCarry

        sim = Sim(ShiftedCarry(), dt=0.02)
        self.assertEqual(sim.state, {'carry.travel': 0.0, 'clearing': 0.0,
                                     'crank': 0.0, 'higher.turn': 0.0,
                                     'lower.turn': 0.0, 'shift': 0.0})

    def test_a_cycle_no_selection_breaks_is_refused(self):
        """The fixture that actually reaches ``_ordered`` today -- a
        cycle whose relations keep their self-reads, so
        ``_step_relation`` defers them past the rest render. Nothing in
        the suite pinned this refusal before this change, and the specs
        never stated it."""
        from .carriage_project.machine import Unconditional

        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(Unconditional(), dt=0.02)
        message = str(caught.exception)
        self.assertIn(
            '(crank, clearing, carry.travel, higher.turn) drives higher.turn',
            message)
        self.assertIn(
            '(lower.turn, higher.turn, carry.travel) drives carry.travel',
            message)
        self.assertIn('form a cycle the run cannot order: each waits on a '
                      'coordinate another determines. A running program is '
                      'acyclic, because the rest render solved every '
                      'relation in one direction.', message)

    def test_the_two_moved_refusals(self):
        """Two outcomes MOVE with this change, and the test names the old
        one so the move is visible in the diff.

        A SELECTED cycle with no self-read, refused
        ``DoublyBound: higher.turn would be bound by the relation
        (crank, shift, carry.travel) drives higher.turn and by the
        author's simulate()`` by the REST RENDER today, now constructs.
        An UNCONDITIONAL one, refused the same way today, now reaches the
        COMPILE and gets the message that names every relation on the
        cycle.
        """
        from .carriage_project.machine import SelectedBare, UnconditionalBare

        sim = Sim(SelectedBare(), dt=0.02)
        self.assertEqual(sorted(sim.state),
                         ['carry.travel', 'crank', 'higher.turn',
                          'lower.turn', 'shift'])

        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(UnconditionalBare(), dt=0.02)
        message = str(caught.exception)
        self.assertIn('(crank, carry.travel) drives higher.turn', message)
        self.assertIn('(lower.turn, higher.turn) drives carry.travel',
                      message)
        self.assertNotIn('doubly bound', message.lower())
