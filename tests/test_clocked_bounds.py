# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A bound STOPS a clocked request on its path.

The originating project is `projects/Calculators/Curta-Type-I-3x`, whose
eight interlocks are each a `Bound` on a joint and none of which needs a
framework idea this change does not already have. What the framework
could not do before this cycle was OBEY them: a request that would drive
a mechanism through a stop was refused WHOLE and committed nothing, which
is a machine no maker can operate.

The whole of the change is one step in FRONT of cycle 1's event loop: the
request's travel is CLIPPED to the largest fraction at which every
compiled constraint is still satisfied, and the events are then located
on the clipped path exactly as they are today. The stop is SOLVED, CUT or
PARTITIONED and never searched, and no tolerance is introduced anywhere.

Every expected number here is computed BY HAND. A test that asked the
implementation what the answer is would pass whatever the implementation
did.

OpenSpec change ``a-bound-stops-the-request``.
"""

import math

from solid_node.expression_graph import free_names
from solid_node.scad_expression import as_node
from solid_node.simulation import Sim
from solid_node.simulation.clocked import TooManyEvents

from .base import BaseNodeTest
from .clocked_project.bounds_unsupported import (Chattering, Curved,
                                                 HandBound,
                                                 OpaqueChain, PortRead,
                                                 SelfReadChain,
                                                 UnreachedRead)
from .clocked_project.decorative import Decorative, Untouchable
from .clocked_project.gate import Gate, Shut
from .clocked_project.lock import Kinked, Lock
from .clocked_project.outside import Outside
from .clocked_project.freeze import Freeze
from .clocked_project.pawl import (PITCH, Pawl, ScaledStroke, Stroke,
                                   TwoStops)
from .running_project.machine import PortRead as RunningPortRead


class CompileTest(BaseNodeTest):
    """Task 2.1: what construction compiles, and over what."""

    def test_the_pawl_compiles_one_constraint_over_the_bank(self):
        sim = Sim(Pawl())
        compiled = sim._clocked.bounds
        self.assertEqual([(entry.coordinate, entry.side)
                          for entry in compiled],
                         [('crank_dial.turn', 'low')])
        # The chain is the composition of the relations that determine
        # the coordinate, down to the bank's own ids -- which for a dial
        # the crank drives directly is the crank and nothing else.
        self.assertEqual(free_names(as_node(compiled[0].chain)), {'crank'})

    def test_a_plain_numeric_range_compiles_both_sides(self):
        sim = Sim(Stroke())
        compiled = sim._clocked.bounds
        self.assertEqual([(entry.coordinate, entry.side)
                          for entry in compiled],
                         [('plate.lift', 'low'), ('plate.lift', 'high')])
        self.assertEqual(free_names(as_node(compiled[0].chain)), {'lift'})


class RefusalTest(BaseNodeTest):
    """Task 2.3: what a clocked stop cannot follow, refused BY NAME at
    construction -- and what the framework already refuses earlier."""

    def refusal(self, model):
        with self.assertRaises(Exception) as caught:
            Sim(model())
        return str(caught.exception)

    def test_a_bounded_coordinate_bound_by_hand_is_refused(self):
        message = self.refusal(HandBound)
        self.assertIn("joint 'lift'", message)
        self.assertIn("the coordinate 'plate.lift'", message)
        self.assertIn('low bound', message)
        self.assertIn('bound BY HAND', message)
        self.assertIn('HandBound.simulate()', message)

    def test_a_chain_through_a_law_that_is_not_an_expression_is_refused(self):
        message = self.refusal(OpaqueChain)
        self.assertIn("the coordinate 'plate.lift'", message)
        self.assertIn('cannot be applied to symbols', message)
        self.assertIn('solid_node.math', message)

    def test_a_bound_reading_an_unreached_coordinate_is_refused(self):
        message = self.refusal(UnreachedRead)
        self.assertIn("its read 'plate.lift'", message)
        self.assertIn('bound BY HAND', message)
        self.assertIn('UnreachedRead.simulate()', message)

    def test_a_bound_reading_a_plain_port_is_refused(self):
        message = self.refusal(PortRead)
        self.assertIn("reads 'belt.turn'", message)
        self.assertIn('the clocked simulation does not bank', message)
        self.assertIn('a plain port or a derived coordinate', message)

    def test_a_curved_level_is_refused_by_name(self):
        message = self.refusal(Curved)
        self.assertIn("joint 'travel'", message)
        self.assertIn("the coordinate 'slide.travel'", message)
        self.assertIn('high bound', message)
        self.assertIn("CURVES as 'crank' moves", message)
        self.assertIn('sin', message)

    def test_a_self_read_chain_is_refused_before_the_clocked_compile(self):
        # The row design section 3 states for a chain that reads the
        # coordinate it drives is a BACKSTOP: the relation layer refuses
        # a self-read under every non-running root long before the
        # clocked compile is reached, and this asserts the message a
        # maker actually sees.
        message = self.refusal(SelfReadChain)
        self.assertIn('reads wheel.turn, the coordinate it drives',
                      message)


class AuthorityNameTest(BaseNodeTest):
    """Task 2.5: the shared bound compile says which authority its
    refusal speaks for, and the RUNNING message is unchanged character
    for character."""

    RUNNING = (
        "Arbor.turn: its upper bound -- the range of the coordinate "
        "'plug.turn' -- reads 'dial.turn', which the run does not bank. A "
        "bound reads the STATE -- a joint coordinate or a declared input "
        "-- and a plain port or a derived coordinate is a calculation the "
        "enumeration recomputes from it on every tick. Read the joint the "
        "port follows.")

    def test_the_running_refusal_is_unchanged_character_for_character(self):
        with self.assertRaises(ValueError) as caught:
            Sim(RunningPortRead(), 0.1)
        self.assertEqual(str(caught.exception), self.RUNNING)

    def test_the_clocked_refusal_differs_only_in_the_authority(self):
        with self.assertRaises(ValueError) as caught:
            Sim(PortRead())
        self.assertEqual(
            str(caught.exception),
            "Slide.travel: its upper bound -- the range of the coordinate "
            "'slide.travel' -- reads 'belt.turn', which the clocked "
            "simulation does not bank. A bound reads the STATE -- a joint "
            "coordinate or a declared input -- and a plain port or a "
            "derived coordinate is a calculation the enumeration "
            "recomputes from it on every tick. Read the joint the port "
            "follows.")


def constraint(sim, coordinate, side):
    for entry in sim._clocked.bounds:
        if entry.coordinate == coordinate and entry.side == side:
            return entry
    raise AssertionError(f'no {side} constraint for {coordinate}')


class ClassificationTest(BaseNodeTest):
    """Task 3.1 and 3.3: the level's shape in each driver that moves
    it, decided ONCE and structurally."""

    def test_an_affine_level_is_classified_per_driver(self):
        sim = Sim(Stroke())
        entry = constraint(sim, 'plate.lift', 'high')
        self.assertEqual(entry.shapes, {'lift': 'affine'})
        # The crank moves the registers and the dials, and cannot move
        # this level at all: it is not examined for it.
        self.assertFalse(entry.moves_with('crank'))

    def test_a_kinked_level_is_classified_kinked_and_carries_its_cuts(self):
        sim = Sim(Kinked())
        entry = constraint(sim, 'knob.travel', 'high')
        self.assertEqual(entry.shapes['crank'], 'kinked')
        self.assertTrue(entry.kinks['crank'])
        # The selector enters the same level affinely.
        self.assertEqual(entry.shapes['selector'], 'affine')

    def test_a_jumped_level_classifies_by_its_skeleton(self):
        sim = Sim(Lock())
        entry = constraint(sim, 'knob.travel', 'high')
        # The bound is a comparison against a `floor` of the crank: the
        # skeleton holds one branch per piece and is CONSTANT in the
        # crank there, while the level itself genuinely steps.
        self.assertEqual(entry.shapes['crank'], 'constant')
        self.assertEqual(len(entry.plans['crank'].jumps), 2)
        self.assertEqual(entry.shapes['selector'], 'affine')

    def test_a_level_no_driver_moves_is_examined_for_none_of_them(self):
        sim = Sim(Decorative())
        entries = sim._clocked.bounds
        self.assertEqual([(entry.coordinate, entry.side) for entry in entries],
                         [('plate.lift', 'low'), ('plate.lift', 'high')])
        for entry in entries:
            self.assertEqual(entry.plans, {})
            self.assertFalse(entry.moves_with('crank'))

    def test_too_many_crossings_is_re_raised_as_the_clocked_refusal(self):
        sim = Sim(Chattering(), state={'feed': 20.0})
        with self.assertRaises(TooManyEvents) as caught:
            sim.move('crank', by=100000.0)
        message = str(caught.exception)
        self.assertIn("move('crank', by=100000.0)", message)
        self.assertIn("the high bound of 'slide.travel'", message)
        self.assertIn('1000', message)
        self.assertIn('committed nothing', message)
        self.assertEqual(sim.state['crank'], 0.0)


class ClipTest(BaseNodeTest):
    """Tasks 4.1 to 4.6: where the request stops, and how exactly."""

    def test_the_own_coordinate_is_read_at_the_requests_start(self):
        # A single long backwards request and ten short ones from the
        # same bank end at the SAME value -- the last seated tooth --
        # because the second short request starts ON that tooth, where
        # the bound evaluates to the tooth itself and the request admits
        # ZERO travel. One tooth of backlash either way, which is what a
        # ratchet does.
        seated = PITCH * math.floor(1000.0 / PITCH)
        self.assertEqual(seated, 996.0)

        long = Sim(Pawl(), state={'crank': 1000.0})
        request = long.move('crank', by=-3600.0)
        self.assertEqual(long.state['crank'], seated)
        self.assertEqual(request.admitted, seated - 1000.0)
        self.assertEqual(request.commits, ())

        short = Sim(Pawl(), state={'crank': 1000.0})
        admissions = [short.move('crank', by=-360.0).admitted
                      for _ in range(10)]
        self.assertEqual(short.state['crank'], seated)
        self.assertEqual(admissions, [seated - 1000.0] + [0.0] * 9)

    def test_a_request_from_a_seated_tooth_admits_nothing(self):
        sim = Sim(Pawl(), state={'crank': 996.0})
        request = sim.move('crank', by=-360.0)
        self.assertEqual(request.admitted, 0.0)
        self.assertEqual(sim.state['crank'], 996.0)
        self.assertEqual(len(request.stops), 1)
        self.assertEqual(request.stops[0].coordinate, 'crank_dial.turn')
        self.assertEqual(request.stops[0].side, 'low')

    def test_the_threshold_frees_a_bank_standing_outside_a_bound(self):
        # The plate NOTHING binds gives the read its rest constant, so
        # the level is a real one and the slide stands at 20 where its
        # bound is 9. The threshold is `max(0, g(0))`, read at the start
        # of EACH request: standing outside, the machine may move
        # inward freely and may not go further out; once it has come
        # back inside, the ordinary bound is what holds it.
        sim = Sim(Outside(), state={'feed': 20.0})

        standing = sim.move('feed', to=20.0)
        self.assertEqual(standing.admitted, 0.0)
        self.assertEqual(standing.stops, ())

        further = sim.move('feed', by=5.0)
        self.assertEqual(further.admitted, 0.0)
        self.assertEqual(sim.state['feed'], 20.0)
        self.assertEqual(len(further.stops), 1)
        self.assertEqual(further.stops[0].coordinate, 'slide.travel')
        self.assertEqual(further.stops[0].side, 'high')

        inward = sim.move('feed', by=-15.0)
        self.assertEqual(inward.admitted, -15.0)
        self.assertEqual(sim.state['feed'], 5.0)

        # And back out, from INSIDE, only as far as the bound itself:
        # design section 7's threshold is the level the REQUEST started
        # at, and this request started legal (evidence.md, design
        # question 1).
        back = sim.move('feed', by=15.0)
        self.assertEqual(back.admitted, 4.0)
        self.assertEqual(sim.state['feed'], 9.0)

    def test_a_constant_level_outside_its_pair_stops_nothing(self):
        sim = Sim(Untouchable())
        request = sim.move('crank', by=720.0)
        self.assertEqual(request.admitted, 720.0)
        self.assertEqual(request.stops, ())

    def test_a_bound_met_exactly_at_a_representable_value_lands_on_it(self):
        sim = Sim(Gate())
        request = sim.move('crank', by=1000.0)
        # travel = crank / 100, and the shut gate's bound is 3 mm: the
        # last crank value at which travel <= 3 is exactly 300.
        self.assertEqual(request.admitted, 300.0)
        self.assertEqual(sim.state['crank'], 300.0)

    def test_a_jumped_level_lands_on_the_last_float_before_its_surface(self):
        sim = Sim(Lock(), state={'selector': 3.0})
        request = sim.move('crank', by=360.0)
        # The sketch's bound is 54 while `phase < 1` and 0 from there
        # on, and the knob stands at 18: the last crank value at which
        # the phase is still below one degree.
        self.assertEqual(sim.state['crank'], math.nextafter(1.0, 0.0))
        self.assertEqual(request.admitted, math.nextafter(1.0, 0.0))

    def test_a_kinked_level_is_solved_at_its_breakpoint(self):
        sim = Sim(Kinked(), state={'selector': 3.0})
        request = sim.move('crank', by=100.0)
        # The bound stands at 54 - 30 = 24 until the crank reaches 30
        # and falls with it after that; the knob's 18 mm is reached at
        # exactly 54 - 18 = 36 degrees.
        self.assertEqual(request.admitted, 36.0)
        self.assertEqual(sim.state['crank'], 36.0)


class RequestTest(BaseNodeTest):
    """Tasks 5.1 to 5.8: what a clipped request does, and what it
    reports."""

    def test_the_clip_precedes_the_events(self):
        # The gate's events are at every 200 degrees, so the whole
        # travel of 1000 would cross five surfaces; the clip admits 300,
        # and exactly ONE event fires, at the same landing the short
        # request fires it at.
        long = Sim(Gate())
        request = long.move('crank', by=1000.0)
        self.assertEqual([commit.value for commit in request.commits],
                         [200.0])
        short = Sim(Gate())
        self.assertEqual([commit.value
                          for commit in short.move('crank', by=300.0).commits],
                         [200.0])

    def test_a_request_stopped_at_zero_travel_is_admitted(self):
        sim = Sim(Freeze(), state={'crank': 180.0, 'selector': 3.0})
        before = sim.state
        request = sim.move('selector', by=3.0)
        self.assertEqual(request.admitted, 0.0)
        self.assertEqual(request.commits, ())
        self.assertEqual(sim.state, before)
        self.assertEqual(len(request.stops), 1)
        stop = request.stops[0]
        self.assertEqual(stop.coordinate, 'knob.travel')
        self.assertEqual(stop.side, 'high')
        self.assertEqual(stop.bound, 18.0)
        self.assertEqual(stop.value, 18.0)
        self.assertEqual(stop.input, 3.0)
        self.assertEqual(stop.fraction, 0.0)

    def test_admitted_is_in_design_units_on_a_scaled_driver(self):
        sim = Sim(ScaledStroke())
        request = sim.move('lift', by=20.0)
        # The bank holds native units, where the plate's stop is 9; the
        # driver's scale is 0.5 design units per native unit.
        self.assertEqual(sim.state['lift'], 9.0)
        self.assertEqual(request.by, 20.0)
        self.assertEqual(request.admitted, 4.5)

    def test_two_constraints_at_one_landing_are_two_entries(self):
        sim = Sim(TwoStops())
        request = sim.move('lift', by=20.0)
        self.assertEqual(request.admitted, 9.0)
        self.assertEqual(sorted((stop.coordinate, stop.side)
                                for stop in request.stops),
                         [('back.lift', 'high'), ('front.lift', 'high')])
        self.assertEqual({stop.input for stop in request.stops}, {9.0})

    def test_a_whole_travel_reports_no_stop(self):
        sim = Sim(Stroke())
        request = sim.move('lift', by=5.0)
        self.assertEqual(request.admitted, 5.0)
        self.assertEqual(request.stops, ())

    def test_sim_stops_is_a_bounded_ring_under_record(self):
        sim = Sim(Stroke(), record=2)
        self.assertEqual(sim.stops, ())
        for _ in range(3):
            sim.move('lift', by=20.0)
            sim.move('lift', by=-20.0)
        self.assertEqual(len(sim.stops), 2)
        self.assertEqual({stop.coordinate for stop in sim.stops},
                         {'plate.lift'})

    def test_sim_stops_is_empty_without_record(self):
        sim = Sim(Stroke())
        sim.move('lift', by=20.0)
        self.assertEqual(sim.stops, ())


#: Every fixture the agreement test samples, as
#: `(model, state, input, travel)`.
SAMPLED = (
    (Pawl, {'crank': 1000.0}, 'crank', -120.0),
    (Stroke, None, 'lift', 5.0),
    (ScaledStroke, None, 'lift', 8.0),
    (Lock, {'selector': 3.0}, 'selector', 2.0),
    (Freeze, {'selector': 3.0}, 'crank', 300.0),
    (Kinked, {'selector': 3.0}, 'crank', 20.0),
    (Gate, None, 'crank', 250.0),
    (Outside, {'feed': 20.0}, 'feed', -8.0),
    (Decorative, None, 'crank', 300.0),
)


class AgreementTest(BaseNodeTest):
    """Task 6.1: the compiled chain agrees with the POSE.

    The composition is substitution and never simplification, so the
    chain performs arithmetic equivalent to the enumeration's over the
    identical native values. Compared with `math.isclose` rather than bit
    for bit: bit-for-bit is a claim about evaluation ORDER that neither
    this design nor ADR-113's makes, and the bug this test exists to
    catch -- a composition that simplified -- is orders of magnitude
    wide, not an ulp (design section 10).
    """

    def test_every_chain_agrees_with_the_tree_it_poses(self):
        from solid_node.motion.ports import clocked_marking, get_coordinate

        for model, state, input_id, travel in SAMPLED:
            with self.subTest(model=model.__name__):
                sim = Sim(model(), state=state)
                clocked = sim._clocked
                origin = clocked.bank[input_id]
                for step in range(21):
                    bank = dict(clocked.bank)
                    bank[input_id] = origin + travel * (step / 20.0)
                    with clocked_marking(clocked.marks):
                        clocked.pose(bank)
                    for entry in clocked.bounds:
                        held = {name: bank[name]
                                for name in entry.chain_names}
                        chained = entry.chain.evaluate(held)
                        node, name = (entry.node, entry.joint.name)
                        posed = get_coordinate(node, name)._value
                        posed = 0.0 if posed is None else posed
                        self.assertTrue(
                            math.isclose(chained, posed, rel_tol=1e-12,
                                         abs_tol=1e-12),
                            f'{entry.coordinate}: chain {chained!r} '
                            f'against pose {posed!r}')


class AuthorityTest(BaseNodeTest):
    """Task 6.3 and 6.5: ONE authority judges one binding."""

    def spy(self):
        """Both judgement sites' consultation of the MARK, recorded."""
        from solid_node.motion import couplings as couplings_module
        from solid_node.motion import joints as joints_module

        seen = []
        originals = {}
        for module in (joints_module, couplings_module):
            originals[module] = module.clocked_owned

            def recorded(node, name, _module=module,
                         _original=originals[module]):
                answer = _original(node, name)
                seen.append((_module.__name__.rsplit('.', 1)[-1], name,
                             answer))
                return answer

            module.clocked_owned = recorded
        self.addCleanup(
            lambda: [setattr(module, 'clocked_owned', original)
                     for module, original in originals.items()])
        return seen

    def test_a_request_marks_the_coordinates_it_compiled(self):
        seen = self.spy()
        sim = Sim(Gate())
        # Construction is NOT a request: nothing is marked there.
        self.assertTrue(all(not answer for _site, _name, answer in seen))
        seen.clear()
        request = sim.move('crank', by=1000.0)
        # The clip landed the shutter EXACTLY on its inclusive bound and
        # the pose accepted it, without the enumeration judging it.
        self.assertEqual(request.admitted, 300.0)
        self.assertIn(('joints', 'travel', True), seen)
        self.assertIn(('couplings', 'travel', True), seen)

    def test_a_pose_that_is_not_a_request_is_judged_by_the_enumeration(self):
        sim = Sim(Gate())
        sim.move('crank', by=1000.0)
        taken = sim.snapshot()
        seen = self.spy()
        sim.restore(taken)
        self.assertTrue(seen)
        self.assertTrue(all(not answer for _site, _name, answer in seen))

    def test_the_mark_is_inert_for_an_untimed_and_a_running_root(self):
        from .running_project.machine import Gate as RunningGate
        from .running_project.machine import GateBody

        seen = self.spy()
        GateBody().set_state(**{'feed': 10.0, 'twist': 0.0, 'time': 0.0})
        running = Sim(RunningGate(), 0.1)
        running.move('twist', by=10.0, duration=0.1)
        running.run(0.1)
        self.assertTrue(seen)
        self.assertTrue(all(not answer for _site, _name, answer in seen))

    def test_a_commit_out_of_range_refuses_the_request_by_name(self):
        from solid_node.motion.joints import JointRangeError

        sim = Sim(Shut(), record=8)
        before = sim.state
        posed = sim.node.shutter.travel.value
        with self.assertRaises(JointRangeError) as caught:
            sim.move('crank', by=400.0)
        message = str(caught.exception)
        self.assertIn("joint 'travel'", message)
        self.assertIn("the coordinate 'shutter.travel'", message)
        self.assertIn('high bound of 0.0', message)
        self.assertIn("move('crank', by=400.0)", message)
        self.assertIn('committed nothing', message)
        # The bank, the tree and the record stand exactly as they did.
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.node.shutter.travel.value, posed)
        self.assertEqual(sim.commits, ())
        self.assertEqual(sim.stops, ())


class AcceptanceTest(BaseNodeTest):
    """Task 7: the shapes the Curta's interlocks actually take."""

    def test_the_freeze_frees_the_knob_at_rest_and_holds_it_off_rest(self):
        at_rest = Sim(Freeze(), state={'selector': 3.0})
        free = at_rest.move('selector', by=3.0)
        self.assertEqual(free.admitted, 3.0)
        self.assertEqual(free.stops, ())
        self.assertEqual(at_rest.node.knob.travel.value, 36.0)

        off_rest = Sim(Freeze(), state={'crank': 180.0, 'selector': 3.0})
        held = off_rest.move('selector', by=3.0)
        self.assertEqual(held.admitted, 0.0)
        self.assertEqual(len(held.stops), 1)

    def test_the_freeze_lets_the_crank_run_where_the_sketch_stops_it(self):
        # THIS is the correction of design section 4, as evidence rather
        # than as an opinion: the same request, the same knob setting,
        # the two declarations side by side.
        freeze = Sim(Freeze(), state={'selector': 3.0})
        ran = freeze.move('crank', by=360.0)
        self.assertEqual(ran.admitted, 360.0)
        self.assertEqual(ran.stops, ())
        self.assertEqual([commit.value for commit in ran.commits], [360.0])
        self.assertEqual(freeze.state['count'], 1)

        sketch = Sim(Lock(), state={'selector': 3.0})
        stopped = sketch.move('crank', by=360.0)
        self.assertEqual(stopped.admitted, math.nextafter(1.0, 0.0))
        self.assertEqual(stopped.commits, ())
        self.assertEqual(len(stopped.stops), 1)
        self.assertEqual(sketch.state['count'], 0)

    def test_a_plain_numeric_range_stops_a_request_of_twenty_at_nine(self):
        sim = Sim(Stroke())
        request = sim.move('lift', by=20.0)
        self.assertEqual(request.admitted, 9.0)
        self.assertEqual(sim.state['lift'], 9.0)
        # Inclusive, and the pose accepts it.
        self.assertEqual(sim.node.plate.lift.value, 9.0)

    def test_the_gate_shows_the_coarseness_of_one_clip_per_request(self):
        # The clip is computed ONCE, over the bank the request STARTED
        # from: the long request is clipped against the gate as the maker
        # found it, and the split pair lets the first request's commit
        # open the gate before the second is clipped. Deliberate
        # coarseness (design section 8), not a defect.
        long = Sim(Gate())
        self.assertEqual(long.move('crank', by=1000.0).admitted, 300.0)

        split = Sim(Gate())
        first = split.move('crank', by=200.0)
        second = split.move('crank', by=800.0)
        self.assertEqual(first.admitted, 200.0)
        self.assertEqual(second.admitted, 800.0)
        self.assertEqual(split.state['crank'], 1000.0)
        self.assertEqual(split.state['opened'], 1)

    def test_a_ranged_joint_nothing_binds_admits_every_request(self):
        sim = Sim(Decorative())
        request = sim.move('crank', by=3600.0)
        self.assertEqual(request.admitted, 3600.0)
        self.assertEqual(request.stops, ())
        self.assertEqual(sim.state['count'], 10)


class ZeroBehaviourChangeTest(BaseNodeTest):
    """Task 8: what this cycle must not have moved.

    The whole existing suite is the first assertion (task 8.1) and it is
    not repeated here; these are the three statements design section 15
    makes that deserve naming, and `tests/test_clocked_publication.py`'s
    own `ZeroBehaviourChangeTest` carries task 8.5 -- a stateless tree
    enters no clocked path, and its published document is the recorded
    one, byte for byte.
    """

    def test_a_running_stop_is_unchanged_in_behaviour_and_record(self):
        from .running_project.machine import Gate as RunningGate

        sim = Sim(RunningGate(), 0.1, record=8)
        twist = sim.move('twist', by=90.0, duration=0.1)
        sim.run(0.1)
        # The plug's bound reads two pin lifts and holds it at zero while
        # the key stands unseated: the running stop, its record and its
        # blocked command, exactly as `test_running_stops` asserts them.
        self.assertEqual(twist.status, 'blocked')
        self.assertEqual(sim.stops[0].coordinate, 'plug.turn')
        self.assertEqual(sim.stops[0].bound, 'high')

    def test_an_untimed_binding_outside_a_bound_is_still_refused(self):
        from solid_node.motion.joints import JointRangeError

        from .running_project.machine import GateBody, SweptBody

        # The close-of-enumeration judgement: the pin tumbler's plug may
        # not turn while the pins stand unseated, judged when the pass
        # that bound them closes.
        with self.assertRaises(JointRangeError) as caught:
            GateBody().set_state(feed=10.0, twist=45.0, time=0.0)
        self.assertIn('plug', str(caught.exception))
        # And the bind-time judgement of a plain numeric range.
        with self.assertRaises(JointRangeError) as caught:
            SweptBody().set_state(steer=60.0, motor=0.0)
        self.assertIn('travel', str(caught.exception))
        self.assertIn('60', str(caught.exception))

    def test_a_clocked_fixture_with_no_ranged_joint_is_cycle_ones(self):
        from .clocked_project.counter import Counter

        sim = Sim(Counter(), record=8)
        self.assertEqual(sim._clocked.bounds, ())
        self.assertEqual(sim._clocked.marks, frozenset())
        request = sim.move('crank', by=1080.0)
        self.assertEqual(request.admitted, 1080.0)
        self.assertEqual(request.stops, ())
        self.assertEqual([commit.value for commit in request.commits],
                         [360.0, 720.0, 1080.0])
        self.assertEqual(sim.state, {'crank': 1080.0, 'tens': 0, 'units': 3})
        self.assertEqual(sim.stops, ())
