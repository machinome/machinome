# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The clocked simulation: `Sim(model)`, and a request that solves its
own events.

A clocked simulation has no `dt` and no clock. It holds a BANK of every
driver and every state, poses the tree exactly as the build path poses a
driven model outside a simulation, and moves ONE declared driver along a
straight path per request -- committing every rising event on it, in path
order, each reading what the one before it left.

Task 6 of the change `declare-the-state`, with the construction refusals
of task 4 beside it. The originating project is
`projects/Calculators/Curta-Type-I-3x`.
"""

from solid_node.motion.joints import JointRangeError
from solid_node.scad_expression import GraphValue
from solid_node.simulation import Sim
from solid_node.simulation.clocked import ClockedError

from .base import BaseNodeTest
from .clocked_project.counter import Counter, Stateless
from .clocked_project.units import (JumpsOnly, NEARLY_NINE, Rounded, Scaled,
                                    Timed, TimedTwin, Unrounded)
from .clocked_project import unsupported


class ConstructionTest(BaseNodeTest):
    """Task 6.1: what a clocked `Sim` is constructed with."""

    def test_a_clocked_sim_takes_no_dt_and_holds_the_bank(self):
        sim = Sim(Counter())
        self.assertEqual(sim.state, {'crank': 0, 'tens': 0, 'units': 0})
        self.assertFalse(sim.running)
        self.assertTrue(sim.clocked)
        # Posed once, at the declared defaults.
        self.assertEqual(sim.node.units_dial.turn.value, 0.0)

    def test_a_dt_over_a_clocked_root_is_refused(self):
        node = Counter()
        with self.assertRaises(TypeError) as caught:
            Sim(node, 0.02)
        message = str(caught.exception)
        self.assertIn('dt', message)
        self.assertIn('requests', message)

    def test_a_stateless_root_still_requires_a_dt(self):
        with self.assertRaises(TypeError):
            Sim(Stateless())

    def test_state_binds_declared_drivers_and_states(self):
        sim = Sim(Counter(), state={'crank': 90.0, 'units': 3})
        self.assertEqual(sim.state['crank'], 90.0)
        self.assertEqual(sim.state['units'], 3)
        self.assertEqual(sim.node.units_dial.turn.value, 3 * 36.0)

    def test_an_unknown_state_name_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            Sim(Counter(), state={'nonesuch': 1})
        self.assertIn('nonesuch', str(caught.exception))


class ConstructionRefusalTest(BaseNodeTest):
    """Tasks 4.5 and 6.1: what a simulation refuses about a clocked
    tree, which no class body could have seen."""

    def test_a_curved_at_is_refused_naming_the_driver_and_primitive(self):
        with self.assertRaises(ClockedError) as caught:
            Sim(unsupported.Curved())
        message = str(caught.exception)
        self.assertIn('crank', message)
        self.assertIn('sin', message)
        self.assertIn('SOLVED', message)

    def test_a_compound_at_is_refused(self):
        with self.assertRaises(ClockedError) as caught:
            Sim(unsupported.Compound())
        self.assertIn('one surface family', str(caught.exception))

    def test_a_remainder_at_is_refused(self):
        with self.assertRaises(ClockedError) as caught:
            Sim(unsupported.Remainder())
        self.assertIn('one surface family', str(caught.exception))

    def test_a_bare_arithmetic_at_is_refused(self):
        with self.assertRaises(ClockedError) as caught:
            Sim(unsupported.Arithmetic())
        self.assertIn('one surface family', str(caught.exception))

    def test_raw_text_in_an_at_is_refused(self):
        with self.assertRaises(ClockedError) as caught:
            Sim(unsupported.Textual())
        self.assertIn('$mystery', str(caught.exception))

    def test_a_law_returning_the_wrong_number_of_values_is_refused(self):
        with self.assertRaises(ClockedError) as caught:
            Sim(unsupported.WrongShape())
        message = str(caught.exception)
        self.assertIn('value', message)
        self.assertIn('ONE target', message)

    def test_a_state_nothing_writes_is_refused(self):
        with self.assertRaises(ClockedError) as caught:
            Sim(unsupported.Unwritten())
        message = str(caught.exception)
        self.assertIn('spare', message)
        self.assertIn('nothing writes it', message)

    def test_two_relations_of_the_tree_may_write_one_state(self):
        """Closure 1, C2: the root and the child both write the child's
        digit, at two different events on two different inputs. That is
        the Curta's stroke-and-clearing shape, and it is admitted; the
        one-event conflict is refused by the REQUEST."""
        sim = Sim(unsupported.TwoWriters())
        sim.move('child.crank', by=360.0)
        self.assertEqual(sim.state['child.digit'], 1)
        sim.move('ring', by=360.0)
        self.assertEqual(sim.state['child.digit'], 2)

    def test_a_relation_no_driver_can_reach_is_refused(self):
        """Closure 1, C4: every source a state, so nothing a request
        moves enters its level and it could never fire."""
        with self.assertRaises(ClockedError) as caught:
            Sim(unsupported.Unreachable())
        message = str(caught.exception)
        self.assertIn('shadow', message)
        self.assertIn('no declared driver', message)

    def test_an_instruction_targeting_a_state_is_refused(self):
        with self.assertRaises(ClockedError) as caught:
            Sim(unsupported.Instructed())
        message = str(caught.exception)
        self.assertIn('Reset', message)
        self.assertIn('value', message)

    def test_a_commit_law_made_entirely_of_jumps_is_admitted(self):
        """Task 4.3: the asymmetry with a running law, which refuses that
        shape as arithmetic -- a commit is evaluated at ONE POINT and
        never integrated, so a law of jumps is a perfectly good one."""
        sim = Sim(JumpsOnly())
        sim.move('crank', by=360.0 * 12)
        # floor(4320 / 360) % 10 == 12 % 10 == 2, computed by hand.
        self.assertEqual(sim.state['value'], 2)


class RequestTest(BaseNodeTest):
    """Task 6.3: what a request is and what it moves."""

    def test_one_request_fires_one_event(self):
        sim = Sim(Counter())
        request = sim.move('crank', by=360.0)
        self.assertEqual(request.input, 'crank')
        self.assertEqual(len(request.commits), 1)
        self.assertEqual(sim.state['units'], 1)
        self.assertEqual(sim.state['crank'], 360.0)

    def test_ten_events_in_one_request_equal_ten_requests_of_one(self):
        once = Sim(Counter())
        long_request = once.move('crank', by=3600.0)

        many = Sim(Counter())
        short = [many.move('crank', by=360.0) for _ in range(10)]

        self.assertEqual(len(long_request.commits), 10)
        self.assertEqual(once.state, many.state)
        self.assertEqual([commit.value for commit in long_request.commits],
                         [commit.value
                          for request in short for commit in request.commits])
        # The carry, computed by hand: ten strokes from zero leave the
        # units back at zero and the tens at one.
        self.assertEqual(once.state['units'], 0)
        self.assertEqual(once.state['tens'], 1)

    def test_the_carry_is_the_hand_computed_one(self):
        sim = Sim(Counter(), state={'units': 8, 'tens': 3})
        sim.move('crank', by=360.0)
        self.assertEqual((sim.state['units'], sim.state['tens']), (9, 3))
        sim.move('crank', by=360.0)
        self.assertEqual((sim.state['units'], sim.state['tens']), (0, 4))

    def test_to_moves_to_the_value(self):
        sim = Sim(Counter())
        request = sim.move('crank', to=1080.0)
        self.assertEqual(len(request.commits), 3)
        self.assertEqual(sim.state['crank'], 1080.0)

    def test_a_backwards_request_moves_the_crank_and_fires_nothing(self):
        sim = Sim(Counter(), state={'crank': 3600.0, 'units': 9})
        sim.move('crank', by=-3600.0)
        self.assertEqual(sim.state['crank'], 0.0)
        self.assertEqual(sim.state['units'], 9)
        # The pose follows the crank and the state, which is all a pose
        # is a function of.
        self.assertEqual(sim.node.units_dial.turn.value, 9 * 36.0)

    def test_a_request_naming_a_state_is_refused(self):
        sim = Sim(Counter())
        with self.assertRaises(ValueError) as caught:
            sim.move('units', by=1)
        message = str(caught.exception)
        self.assertIn('units', message)
        self.assertIn('State', message)

    def test_a_request_naming_a_joint_coordinate_is_refused(self):
        sim = Sim(Counter())
        with self.assertRaises(ValueError) as caught:
            sim.move('units_dial.turn', by=1.0)
        self.assertIn('units_dial.turn', str(caught.exception))

    def test_a_request_stating_both_by_and_to_is_refused(self):
        sim = Sim(Counter())
        with self.assertRaises(ValueError):
            sim.move('crank', by=1.0, to=1.0)
        with self.assertRaises(ValueError):
            sim.move('crank')

    def test_the_commit_record_names_the_relation_and_the_targets(self):
        sim = Sim(Counter())
        commit = sim.move('crank', by=360.0).commits[0]
        self.assertIn('commits', commit.relation)
        self.assertEqual(commit.targets, {'units': 1, 'tens': 0})
        self.assertEqual(commit.value, 360.0)
        self.assertEqual(commit.fraction, 1.0)


class AtomicityTest(BaseNodeTest):
    """Task 6.5: a refused request commits nothing."""

    def test_a_law_raising_on_the_third_event_leaves_everything_alone(self):
        sim = Sim(unsupported.Exploding())
        before = dict(sim.state)
        posed = sim.node.face.turn.value
        with self.assertRaises(Exception):
            sim.move('crank', by=360.0 * 5)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.node.face.turn.value, posed)
        self.assertEqual(sim.commits, ())


class SessionSetupTest(BaseNodeTest):
    """Task 6.7: snapshot, restore, initial, reset, record."""

    def test_snapshot_and_restore_carry_the_states(self):
        sim = Sim(Counter())
        sim.move('crank', by=1080.0)
        saved = sim.snapshot()
        sim.move('crank', by=360.0)
        self.assertEqual(sim.state['units'], 4)
        sim.restore(saved)
        self.assertEqual(sim.state['units'], 3)
        self.assertEqual(sim.state['crank'], 1080.0)
        self.assertEqual(sim.node.units_dial.turn.value, 3 * 36.0)

    def test_reset_returns_to_the_initial_snapshot(self):
        sim = Sim(Counter(), state={'units': 2})
        self.assertEqual(sim.initial.values['units'], 2)
        sim.move('crank', by=720.0)
        sim.reset()
        self.assertEqual(sim.state['units'], 2)
        self.assertEqual(sim.state['crank'], 0.0)

    def test_restore_refuses_a_snapshot_from_another_model(self):
        one = Sim(Counter())
        other = Sim(Scaled())
        saved = other.snapshot()
        before = dict(one.state)
        with self.assertRaises(ValueError):
            one.restore(saved)
        self.assertEqual(one.state, before)

    def test_record_keeps_a_bounded_ring(self):
        sim = Sim(Counter(), record=3)
        sim.move('crank', by=3600.0)
        self.assertEqual(len(sim.commits), 3)
        self.assertEqual([commit.value for commit in sim.commits],
                         [2880.0, 3240.0, 3600.0])

    def test_without_record_the_request_is_still_complete(self):
        sim = Sim(Counter())
        request = sim.move('crank', by=1080.0)
        self.assertEqual(sim.commits, ())
        self.assertEqual(len(request.commits), 3)


class CadenceRefusalTest(BaseNodeTest):
    """Task 6.9: a clocked model has no clock."""

    # `stops` is deliberately NOT here: the change
    # ``a-bound-stops-the-request`` LIFTS cycle 1's refusal of that name,
    # because a clocked model has no clock but it does have stops.
    REFUSED = ('run', 'at', 'every', 'time', 'tick', 'rate', 'trigger',
               'commands', 'program', 'crossings')

    #: How each refused name is reached: a property is read, and a
    #: method is called with arguments it would otherwise accept.
    CALLS = {'run': (0.0,), 'at': (0.0,), 'every': (1.0, print),
             'rate': ('crank', 1.0), 'trigger': ('Home',)}

    def test_every_cadence_name_is_refused(self):
        sim = Sim(Counter())
        for name in self.REFUSED:
            with self.subTest(name=name):
                with self.assertRaises(TypeError) as caught:
                    found = getattr(sim, name)
                    if name in self.CALLS:
                        found(*self.CALLS[name])
                message = str(caught.exception)
                self.assertIn(name, message)
                self.assertIn('CLOCKED', message)

    def test_the_clocked_surface_is_admitted(self):
        sim = Sim(Counter())
        for name in ('move', 'snapshot', 'restore', 'reset', 'initial',
                     'state', 'commits', 'stops'):
            with self.subTest(name=name):
                self.assertTrue(hasattr(sim, name))


class BoundTest(BaseNodeTest):
    """Task 6.11: a violated bound is still an impossible POSE.

    This test RECORDS the cycle-2 gap rather than hiding it: a request
    that would drive a mechanism through a stop is refused WHOLE, rather
    than being clipped where the machine stops and keeping what it
    committed on the way. Closure 1 (C3) is the "whole" part: the pose is
    the last step of a request, and a refused pose is a refused request.
    """

    def test_a_violated_range_raises_on_the_pose_the_request_ends_at(self):
        sim = Sim(unsupported.Bounded())
        with self.assertRaises(JointRangeError):
            sim.move('crank', by=360.0 * 3)

    def test_a_request_whose_final_pose_is_refused_commits_nothing(self):
        sim = Sim(unsupported.Bounded(), record=8)
        # Two strokes stand inside the stop: 2 * 36 = 72 of 90 degrees.
        sim.move('crank', by=360.0 * 2)
        before = sim.state
        posed = sim.node.face.turn.value
        with self.assertRaises(JointRangeError):
            sim.move('crank', by=360.0 * 2)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.state['crank'], 720.0)
        self.assertEqual(sim.state['value'], 2)
        # The tree is still posed where it was, and the ring of
        # recorded events did not grow.
        self.assertEqual(sim.node.face.turn.value, posed)
        self.assertEqual(len(sim.commits), 2)

    def test_a_restore_whose_pose_is_refused_changes_nothing(self):
        from solid_node.simulation.clocked import ClockedSnapshot

        sim = Sim(unsupported.Bounded())
        sim.move('crank', by=360.0)
        before = sim.state
        posed = sim.node.face.turn.value
        impossible = ClockedSnapshot(sim.snapshot().model,
                                     {'crank': 0.0, 'value': 3})
        with self.assertRaises(JointRangeError):
            sim.restore(impossible)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.node.face.turn.value, posed)


class UnitsTest(BaseNodeTest):
    """Task 6.13: native in, native out, one rounding."""

    def test_a_scaled_state_is_committed_unrescaled(self):
        sim = Sim(Scaled())
        sim.move('crank', by=360.0)
        self.assertEqual(sim.state['value'], 4.0)
        # The pose reads the design value through the scale exactly
        # once: a second conversion would give 0.4.
        self.assertEqual(sim.node.face.turn.value, 40.0)

    def test_an_integer_state_rounds_once_at_the_commit(self):
        sim = Sim(Rounded())
        sim.move('crank', by=360.0)
        self.assertEqual(sim.state['value'], 9)
        self.assertIsInstance(sim.state['value'], int)

    def test_a_float_state_keeps_what_the_law_returned(self):
        sim = Sim(Unrounded())
        sim.move('crank', by=360.0)
        self.assertEqual(sim.state['value'], NEARLY_NINE)


class TimeTest(BaseNodeTest):
    """Task 6.15: a clocked pose leaves `time` symbolic."""

    def test_time_is_absent_from_the_bank(self):
        sim = Sim(Timed())
        self.assertNotIn('time', sim.state)

    def test_the_pose_reads_the_symbolic_animation_variable(self):
        sim = Sim(Timed())
        before = sim.node.face.turn.value
        self.assertIsInstance(before, GraphValue)
        sim.move('crank', by=360.0 * 3)
        after = sim.node.face.turn.value
        self.assertIsInstance(after, GraphValue)
        self.assertNotEqual(str(before), str(after))

    def test_the_posed_expression_matches_the_driver_twin(self):
        sim = Sim(Timed())
        sim.move('crank', by=360.0 * 3)
        value = sim.state['value']

        twin = TimedTwin()
        twin.set_state(**{'crank': 0.0, 'value': value})
        self.assertEqual(str(sim.node.face.turn.value),
                         str(twin.face.turn.value))
