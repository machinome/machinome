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
from solid_node.node import AssemblyNode
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
    # `trigger` is not here either, since `play-the-instruction`: an
    # instruction under a clocked root is ONE REQUEST, which is the one
    # verb of this list with a meaning here.
    REFUSED = ('run', 'at', 'every', 'time', 'tick', 'rate',
               'commands', 'program', 'crossings')

    #: How each refused name is reached: a property is read, and a
    #: method is called with arguments it would otherwise accept.
    CALLS = {'run': (0.0,), 'at': (0.0,), 'every': (1.0, print),
             'rate': ('crank', 1.0)}

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
        for name in ('move', 'trigger', 'snapshot', 'restore', 'reset',
                     'initial', 'state', 'commits', 'stops'):
            with self.subTest(name=name):
                self.assertTrue(hasattr(sim, name))

    def test_trigger_is_not_refused_as_a_cadence(self):
        """Task 3.7: `trigger` LEFT this list. A root declaring no
        instruction refuses the NAME it was given, by the instruction
        resolver -- never by the cadence refusal."""
        sim = Sim(Counter())
        with self.assertRaises(KeyError) as caught:
            sim.trigger('Home')
        message = str(caught.exception)
        self.assertIn('Home', message)
        self.assertIn('no instruction', message)
        self.assertNotIn('CLOCKED', message)


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


class NonFiniteCommitTest(BaseNodeTest):
    """A commit value that is not a finite number refuses the request.

    Follow-up of 2026-09-17 to the change ``publish-the-clocked-machine``
    (ADR-128). The export requirement "A published commit says what it
    reads, writes and fires on" states that a CONSUMER computing a
    non-finite commit value refuses the request rather than banking it,
    because a document cannot express a raise. The framework is the
    other runtime of that same contract, and was banking one: the
    Curta's registers would then hold a value no pose, no bound and no
    later event can read.
    """

    def refusal(self, node, expected):
        sim = Sim(node)
        before = dict(sim.state)
        posed = sim.node.face.turn.value
        with self.assertRaises(ClockedError) as caught:
            sim.move('crank', by=360.0)
        message = str(caught.exception)
        # By NAME: the relation as written, the state, and the value.
        self.assertIn('commits', message)
        self.assertIn('value', message)
        self.assertIn(expected, message)
        # ADR-125's atomicity: bank, pose and record stand.
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.node.face.turn.value, posed)
        self.assertEqual(sim.commits, ())

    def test_an_infinite_commit_refuses_the_request(self):
        self.refusal(unsupported.Infinite(), 'inf')

    def test_a_nan_commit_refuses_the_request(self):
        self.refusal(unsupported.NotANumber(), 'nan')

    def test_an_integer_state_is_judged_before_it_is_rounded(self):
        """`round(float('inf'))` raises `OverflowError`, which names
        neither the relation nor the state: the finiteness judgement
        runs first, so an integer state refuses exactly as a float one
        does."""
        self.refusal(unsupported.InfiniteCount(), 'inf')

    def test_a_finite_commit_is_untouched(self):
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


class TriggerTest(BaseNodeTest):
    """Tasks 3 and 4 of `play-the-instruction`: an instruction under a
    clocked root is ONE REQUEST, and `trigger` makes it.

    The originating project is
    `projects/Calculators/Curta-Type-I-3x`, whose `ClockedCurta`
    declares `'Turn crank': Instruction(by={'crank_rotation': 360},
    duration=2)` and could not play it. `Calculator` carries that
    instruction on its own crank, and its ABSOLUTE twin over an
    integer driver.
    """

    def fixture(self):
        from .clocked_project.calculator import Calculator

        return Sim(Calculator())

    def same(self, found, want, where):
        """Field for field, and EXACTLY: a request is a value object and
        two equal requests differ in no float."""
        for name in ('input', 'by', 'to', 'admitted', 'origin', 'end'):
            self.assertEqual(getattr(found, name), getattr(want, name),
                             f'{where} {name}')
            self.assertEqual(type(getattr(found, name)),
                             type(getattr(want, name)), f'{where} {name}')
        self.assertEqual(len(found.commits), len(want.commits), where)
        for one, other in zip(found.commits, want.commits):
            self.assertEqual(one, other, where)
        self.assertEqual(len(found.stops), len(want.stops), where)

    def test_a_relative_instruction_is_the_move_it_states(self):
        """Task 3.1: `by={'crank': 360.0}` IS `move('crank', by=360.0)`,
        made from the same bank."""
        pressed = self.fixture()
        moved = self.fixture()
        found = pressed.trigger('Stroke')
        want = moved.move('crank', by=360.0)
        self.same(found, want, 'Stroke')
        self.assertEqual(pressed.state, moved.state)
        # And it really fired the stroke: one commit, the register at 1.
        self.assertEqual(len(found.commits), 1)
        self.assertEqual(pressed.state['w0.digit'], 1)

    def test_an_absolute_instruction_is_the_move_it_states(self):
        """Task 3.2: the `targets=` branch, over an `int` driver."""
        pressed = self.fixture()
        moved = self.fixture()
        found = pressed.trigger('Set four')
        want = moved.move('operand', to=4)
        self.same(found, want, 'Set four')
        self.assertEqual(pressed.state, moved.state)
        self.assertEqual(pressed.state['operand'], 4)

    def test_the_declared_duration_does_not_reach_the_machine(self):
        """Task 3.3: a request is a PATH and not an interval, so two
        roots differing ONLY in the declared duration make equal
        requests and equal banks."""
        from solid_node.simulation import Driver, Instruction, State

        from .clocked_project.counter import advance, strokes
        from .clocked_project.parts import Dial

        def root(duration):
            class Timed(AssemblyNode):
                crank = Driver(default=0, unit='deg')
                units = State(default=0, range=(0, 9), dtype=int)
                tens = State(default=0, range=(0, 9), dtype=int)

                units_dial = Dial()
                tens_dial = Dial()

                instructions = {'Stroke': Instruction(by={'crank': 720.0},
                                                      duration=duration)}

                (crank & units & tens).commits((units, tens), at=strokes,
                                               law=advance)

                units.drives(units_dial.turn, ratio=36.0)
                tens.drives(tens_dial.turn, ratio=36.0)

            return Sim(Timed())

        slow, instant = root(2.0), root(0.0)
        self.same(slow.trigger('Stroke'), instant.trigger('Stroke'),
                  'duration')
        self.assertEqual(slow.state, instant.state)

    def test_an_unknown_instruction_is_refused_by_name(self):
        """Task 3.4: the running path's own `KeyError`, by construction
        and not by imitation -- and the bank and the pose stand."""
        sim = self.fixture()
        before = dict(sim.state)
        posed = sim.node.crank_dial.turn.value
        with self.assertRaises(KeyError) as caught:
            sim.trigger('nothing')
        message = str(caught.exception)
        self.assertIn('nothing', message)
        self.assertIn('Stroke', message)
        self.assertIn('Set four', message)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.node.crank_dial.turn.value, posed)

    def test_a_child_declared_instruction_keeps_its_qualified_name(self):
        """The resolution is the EXISTING one: an instruction declared
        on a child is `child.Name` and its class-local target resolves
        against the declaring node's own path."""
        from solid_node.simulation import Driver, Instruction, State

        from .clocked_project.counter import advance, strokes
        from .clocked_project.parts import Dial

        class Wheel(AssemblyNode):
            crank = Driver(default=0, unit='deg')
            units = State(default=0, range=(0, 9), dtype=int)
            tens = State(default=0, range=(0, 9), dtype=int)

            units_dial = Dial()
            tens_dial = Dial()

            instructions = {'Stroke': Instruction(by={'crank': 360.0},
                                                  duration=1.0)}

            (crank & units & tens).commits((units, tens), at=strokes,
                                           law=advance)

            units.drives(units_dial.turn, ratio=36.0)
            tens.drives(tens_dial.turn, ratio=36.0)

        class Pair(AssemblyNode):
            left = Wheel()
            right = Wheel()

        sim = Sim(Pair())
        request = sim.trigger('left.Stroke')
        self.assertEqual(request.input, 'left.crank')
        self.assertEqual(sim.state['left.units'], 1)
        self.assertEqual(sim.state['right.units'], 0)
        self.assertEqual(sim.state['right.crank'], 0)


class PathEndsTest(BaseNodeTest):
    """Task 4 of `play-the-instruction`: a request reports BOTH ENDS of
    the path it travelled, verbatim from the bank and therefore in the
    input's own NATIVE units -- the units every commit's `value`
    speaks."""

    def test_a_request_from_a_non_zero_start_reports_both_ends(self):
        """Task 4.2: `origin` is the bank before it, `end` the bank
        after it, and every commit's value lies between them."""
        from .clocked_project.calculator import Calculator

        sim = Sim(Calculator())
        sim.move('crank', by=100.0)
        before = sim.state['crank']
        self.assertEqual(before, 100.0)
        request = sim.move('crank', by=740.0)
        after = sim.state['crank']
        self.assertEqual(request.origin, before)
        self.assertEqual(request.end, after)
        self.assertEqual(request.end, 840.0)
        self.assertTrue(request.commits)
        for commit in request.commits:
            self.assertGreaterEqual(commit.value, request.origin)
            self.assertLessEqual(commit.value, request.end)

    def test_a_clipped_request_ends_at_the_stop_and_not_at_the_ask(self):
        """Task 4.3: the lift is asked for 12 mm and stopped at 9."""
        from .clocked_project.pawl import Stroke

        sim = Sim(Stroke())
        request = sim.move('lift', by=12.0)
        self.assertTrue(request.stops)
        self.assertEqual(request.by, 12.0)
        self.assertEqual(request.origin, 0.0)
        self.assertEqual(request.end, 9.0)
        self.assertEqual(request.end, sim.state['lift'])

    def test_a_request_admitted_at_zero_travel_reports_one_value_twice(self):
        """Task 4.3: nothing moved, so the two ends are the same
        value."""
        from .clocked_project.calculator import Standing

        sim = Sim(Standing())
        request = sim.move('feed', by=-1.0)
        self.assertEqual(request.admitted, 0.0)
        self.assertTrue(request.stops)
        self.assertEqual(request.origin, request.end)
        self.assertEqual(request.origin, sim.state['feed'])

    def test_an_absolute_request_over_an_int_driver_ends_native(self):
        """Task 4.3: `end` is the CONVERTED native value, not the design
        one the caller asked for."""
        from .clocked_project.calculator import Calculator

        sim = Sim(Calculator())
        request = sim.move('operand', to=4)
        self.assertEqual(request.to, 4)
        self.assertEqual(request.origin, 1)
        self.assertEqual(request.end, 4)
        self.assertEqual(request.end, sim.state['operand'])

    def test_a_scaled_request_ends_in_native_units_while_admitted_is_design(
            self):
        """The documented asymmetry, PROVED: `admitted` speaks the units
        `by=` speaks and the two ends speak the bank's."""
        from .clocked_project.pawl import ScaledStroke

        sim = Sim(ScaledStroke())
        request = sim.move('lift', by=3.0)
        self.assertEqual(request.admitted, 3.0)
        self.assertEqual(request.origin, 0.0)
        self.assertEqual(request.end, 6.0)
        self.assertEqual(request.end, sim.state['lift'])
