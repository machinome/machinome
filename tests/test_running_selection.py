# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A selection decides which sources a law reads.

OpenSpec change ``select-the-source``. A mechanism's dependencies may be
SELECTED by where one of its own parts stands, so that the union of what
it reads over every selection is cyclic although each selection's own
dependencies are not: the same fixed carry lever of a Curta is tripped by
the dial the carriage has brought under it and advances the dial beyond
that one.

The originating project is ``projects/Calculators/Curta-Type-I-3x``,
branch ``direct-operation``, checkpoint ``6a00abe``, and the requirement
is recorded whole in
``workflow/docs/curta-shifted-carry-association.md``. Its executable
diagnostic is reduced to ``tests/carriage_project/machine.py``.

Such a union is a BLOCK: one entry of the program, ordered once per
PIECE of a tick rather than once per program. Everything here is new
behaviour; a program with no block keeps its order, its document, its
cost and its identity, which the untouched suites pin.
"""

import hashlib
import math

from machinome.motion.couplings import CouplingError, DoublyBound
from machinome.simulation import Sim, UnsupportedLaw
from machinome.simulation.program import (MembershipInvariantError,
                                           _FOLDABLE,
                                           _agree_on_membership,
                                           _block_members, _reads_under,
                                           _units, release_tree)

from .base import BaseNodeTest
from .carriage_project.machine import (BothActive, CurtaCarriage,
                                       DerivedInBlock, FixedOne, FixedZero,
                                       GroupInBlock, LandedCarry,
                                       LoopingShiftedCarry, PortInBlock,
                                       SelectedBare, SelectedBareBody,
                                       SelectedUnguarded,
                                       ShiftedCarry, ShiftedCarryBody,
                                       SignGated, UnbankedCycle,
                                       Unconditional, UnconditionalBare,
                                       WiringInBlock)
from .running_project.machine import Train


#: The run's own agreement window, relative.
def agrees(first, second):
    return abs(first - second) <= 1e-9 * max(1.0, abs(first), abs(second))


def block_of(sim):
    """The one compound block edge of a running simulation's program."""
    found = [edge for edge in sim._run.program.edges if edge.kind == 'block']
    assert len(found) == 1, found
    return found[0]


def cranked(klass, travel, ticks, state=None, dt=None):
    """`klass` cranked by `travel` over one second, in `ticks` steps."""
    step = dt if dt is not None else 1.0 / ticks
    sim = Sim(klass(), dt=step, state=state or {})
    command = sim.move('crank', by=travel, duration=1.0)
    for _step in range(ticks):
        sim.run(step)
    return sim, command


class SelectorFoldTest(BaseNodeTest):
    """Task 2.4: which jump nodes are SELECTORS, and what the fold says
    each member still reads."""

    def setUp(self):
        super().setUp()
        self.sim = Sim(ShiftedCarry(), dt=0.02)
        self.program = self.sim._run.program
        self.block = block_of(self.sim).block

    def named(self, keys):
        return sorted(self.program.nodes[key].name for key in keys)

    def test_a_selector_is_a_jump_whose_level_reads_nothing_the_block_gives(
            self):
        wheel, lever = self.block.members
        self.assertEqual(self.block.names, ('higher.turn', 'carry.travel'))
        self.assertEqual(
            [(jump.primitive, str(jump.argument))
             for jump in self.block.selectors[0]],
            [('>=', '(shift - 0.5)'), ('<', '(shift - 0.5)')])
        self.assertEqual(
            [(jump.primitive, str(jump.argument))
             for jump in self.block.selectors[1]],
            [('<', '(shift - 0.5)'), ('>=', '(shift - 0.5)')])
        # The gates whose level reads a coordinate the block determines
        # -- the lever's travel and the wheel's own angle -- are NOT
        # selectors and stay where ADR-121 put them.
        forced = {jump.placeholder for jump in self.block.selectors[0]}
        self.assertEqual(
            sorted(jump.placeholder for jump in wheel.plans[0].jumps
                   if jump.placeholder not in forced),
            ['$j2', '$j3'])
        self.assertEqual(
            sorted(jump.placeholder for jump in lever.plans[0].jumps
                   if jump.placeholder not in {
                       one.placeholder for one in self.block.selectors[1]}),
            ['$j2'])

    def test_the_fold_says_what_each_member_reads(self):
        """`spikes/fold.py`'s two measurements, as the compiled block
        computes them."""
        wheel, lever = self.block.members
        self.assertEqual(
            sorted(_reads_under(wheel.plans[0], {})),
            ['carry.travel', 'clearing', 'crank', 'higher.turn', 'shift'])
        self.assertEqual(
            sorted(_reads_under(wheel.plans[0], {'$j1': 0.0})),
            ['clearing', 'crank', 'higher.turn', 'shift'])
        self.assertEqual(
            sorted(_reads_under(lever.plans[0], {})),
            ['carry.travel', 'higher.turn', 'lower.turn', 'shift'])
        self.assertEqual(
            sorted(_reads_under(lever.plans[0], {'$j1': 0.0})),
            ['carry.travel', 'lower.turn', 'shift'])
        # And what that means for the block: at any value of `shift` at
        # most one of the two dependencies is active.
        self.assertEqual(self.named(self.block.unconditional[0]), [])
        self.assertEqual(self.named(self.block.switched[0]), ['carry.travel'])
        self.assertEqual(self.named(self.block.unconditional[1]), [])
        # `lower.turn` is UPSTREAM of the block, not in it: what the
        # fold decides for a member is which of the coordinates the BLOCK
        # determines it still reads.
        self.assertEqual(self.named(self.block.switched[1]), ['higher.turn'])

    def test_the_fold_is_monotone(self):
        """One fold per member decides both questions: the reads under
        EVERY foldable selector at zero are a SUBSET of the reads under
        each one alone."""
        for index, member in enumerate(self.block.members):
            plan = member.plans[0]
            zero = {jump.placeholder: 0.0
                    for jump in self.block.selectors[index]
                    if jump.primitive in _FOLDABLE}
            least = _reads_under(plan, zero)
            for jump in self.block.selectors[index]:
                if jump.primitive not in _FOLDABLE:
                    continue
                alone = _reads_under(plan, {jump.placeholder: 0.0})
                self.assertLessEqual(least, alone,
                                     f'{member.description} {jump}')

    def test_a_sign_gate_switches_nothing(self):
        """`sign`'s zero branch is ONE POINT and not an interval, so a
        source gated on it is never switched and the cycle stands."""
        self.assertNotIn('sign', _FOLDABLE)
        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(SignGated(), dt=0.02)
        message = str(caught.exception)
        self.assertIn('form a cycle the run cannot order', message)
        self.assertIn('not sign, whose zero is a single point', message)


class ConstructionRefusalTest(BaseNodeTest):
    """Task 2.5: what cannot be a block, refused at construction and by
    relation identity."""

    def test_a_wiring_in_a_block_is_refused(self):
        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(WiringInBlock(), dt=0.02)
        message = str(caught.exception)
        self.assertIn('the wiring WiringInBlock.spindle -> turn of relay',
                      message)
        self.assertIn('it carries no jump node, so no selection can switch '
                      'what it reads', message)

    def test_a_derived_coordinate_in_a_block_is_refused(self):
        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(DerivedInBlock(), dt=0.02)
        message = str(caught.exception)
        self.assertIn("the derived coordinate 'reach' (hub + 2 * tool)",
                      message)
        self.assertIn('it carries no jump node', message)

    def test_an_intermediate_among_a_blocks_driven_ends_is_refused(self):
        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(PortInBlock(), dt=0.02)
        message = str(caught.exception)
        self.assertIn('(crank, wheel.turn) drives link', message)
        self.assertIn('which the running simulation does not own', message)
        self.assertIn('State the relation into the joint coordinate and let '
                      'the port follow it.', message)

    def test_a_block_member_driving_a_group_is_refused(self):
        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(GroupInBlock(), dt=0.02)
        message = str(caught.exception)
        self.assertIn('drives (lower.turn, higher.turn)', message)
        self.assertIn('A member of a block drives ONE coordinate', message)

    def test_a_cycle_no_selection_breaks_keeps_todays_message(self):
        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(Unconditional(), dt=0.02)
        self.assertIn(
            'form a cycle the run cannot order: each waits on a coordinate '
            'another determines. A running program is acyclic, because the '
            'rest render solved every relation in one direction.',
            str(caught.exception))


class ProgramListingTest(BaseNodeTest):
    """Task 2.6: the program's own listing, and therefore its
    identity."""

    def test_the_block_line_names_its_members_and_precedes_them(self):
        sim = Sim(ShiftedCarry(), dt=0.02)
        lines = sim._run.program.described().splitlines()
        where = lines.index("block ['higher.turn', 'carry.travel']")
        self.assertIn('drives higher.turn]', lines[where + 1])
        self.assertIn('drives carry.travel]', lines[where + 2])
        # The member lines carry their own expressions, so the identity
        # covers every member's law as it covers any other edge's.
        self.assertIn('(shift >= 0.5)', lines[where + 1])
        self.assertIn('(carry.travel < 1.0)', lines[where + 2])
        # And the edge OUTSIDE the block is listed before it, ordinarily.
        self.assertIn('drives lower.turn]', lines[where - 1])

    def test_the_identity_covers_the_block_line(self):
        sim = Sim(ShiftedCarry(), dt=0.02)
        program = sim._run.program
        described = program.described()
        self.assertEqual(
            program.identity,
            hashlib.sha256(described.encode()).hexdigest())
        without = '\n'.join(line for line in described.splitlines()
                            if not line.startswith('block '))
        self.assertNotEqual(
            program.identity,
            hashlib.sha256(without.encode()).hexdigest())

    def test_a_program_with_no_block_prints_no_block_line(self):
        sim = Sim(Train(), dt=0.05)
        described = sim._run.program.described()
        self.assertNotIn('\nblock ', described)
        self.assertEqual(sim._run.program.listed(),
                         list(sim._run.program.edges))


class RestTest(BaseNodeTest):
    """Tasks 3.1, 3.3 and 3.7: a block relation binds nothing at rest."""

    def test_the_rest_bank_is_each_coordinates_own_guarded_default(self):
        sim = Sim(ShiftedCarry(), dt=0.02)
        self.assertEqual(sim.state, {'carry.travel': 0.0, 'clearing': 0.0,
                                     'crank': 0.0, 'higher.turn': 0.0,
                                     'lower.turn': 0.0, 'shift': 0.0})

    def test_a_selected_cycle_with_no_self_read_is_admitted(self):
        """Task 3.7. Today this fixture is refused
        ``DoublyBound: higher.turn would be bound by the relation
        (crank, shift, carry.travel) drives higher.turn and by the
        author's simulate()`` -- by the REST RENDER, before any compile.
        """
        sim = Sim(SelectedBare(), dt=0.02)
        self.assertEqual(sim.state, {'carry.travel': 0.0, 'crank': 0.0,
                                     'higher.turn': 0.0, 'lower.turn': 0.0,
                                     'shift': 0.0})
        self.assertEqual(block_of(sim).block.names,
                         ('higher.turn', 'carry.travel'))

    def test_an_unconditional_cycle_with_no_self_read_reaches_the_compile(
            self):
        """Task 3.7, the other half: the same verdict, by a better
        message. Today this fixture is refused ``DoublyBound:
        higher.turn would be bound by the relation (crank, carry.travel)
        drives higher.turn and by the author's simulate()``, which names
        ONE coordinate and the author's ``simulate()``."""
        with self.assertRaises(UnsupportedLaw) as caught:
            Sim(UnconditionalBare(), dt=0.02)
        message = str(caught.exception)
        self.assertIn('(crank, carry.travel) drives higher.turn', message)
        self.assertIn('(lower.turn, higher.turn) drives carry.travel',
                      message)
        self.assertIn('form a cycle the run cannot order', message)

    def test_a_block_relation_with_no_rest_default_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            Sim(SelectedUnguarded(), dt=0.02)
        message = str(caught.exception)
        self.assertIn('carry.travel, higher.turn', message)
        self.assertIn('needs a rest value for each', message)


class OtherTimeBaseTest(BaseNodeTest):
    """Task 3.4: under no time base and under a looping one, nothing
    changes."""

    def test_the_same_relations_are_refused_as_they_are_today(self):
        for klass in (ShiftedCarryBody, LoopingShiftedCarry):
            with self.subTest(klass.__name__):
                with self.assertRaises(CouplingError) as caught:
                    klass().set_state(crank=0.0, shift=0.0, clearing=0.0)
                message = str(caught.exception)
                self.assertIn('it reads lower.turn, the coordinate it '
                              'drives, and a relation that reads its own '
                              'driven end states INCREMENTS', message)

    def test_a_selected_cycle_is_still_doubly_bound_untimed(self):
        """Nothing new is DECLARED, so the untimed enumeration refuses
        the same relations it refuses today."""
        with self.assertRaises(DoublyBound) as caught:
            SelectedBareBody().set_state(crank=0.0, shift=0.0)
        self.assertIn('higher.turn would be bound by the relation',
                      str(caught.exception))


class MembershipTest(BaseNodeTest):
    """Tasks 3.5 and 3.6: where membership is decided, and what clears
    it."""

    def marks(self, root):
        return {record.described(): record.block_member
                for _assembly, _path, records, _formulas, _wirings
                in _units(root) for record in records}

    def test_a_cycle_that_reaches_no_bank_coordinate_is_left_alone(self):
        node = UnbankedCycle()
        sim = Sim(node, dt=0.02)
        self.assertEqual(sim.state, {'crank': 0.0, 'wheel.turn': 0.0})
        self.assertEqual(set(self.marks(node).values()), {False})

    def test_the_pre_pass_and_the_compile_must_agree(self):
        sim = Sim(ShiftedCarry(), dt=0.02)
        block = block_of(sim).block
        with self.assertRaises(MembershipInvariantError) as caught:
            _agree_on_membership(set(), (block,), sim._run.program.nodes)
        message = str(caught.exception)
        self.assertIn('marked the relations determining none', message)
        self.assertIn('the compile found carry.travel, higher.turn', message)
        # There is no tick at construction, and this is not a landing.
        self.assertIn('Construction refused the model.', message)
        self.assertNotIn('The tick committed nothing', message)

    def test_the_pre_pass_is_idempotent(self):
        node = ShiftedCarry()
        _block_members(node)
        first = self.marks(node)
        _block_members(node)
        self.assertEqual(first, self.marks(node))
        self.assertEqual(sorted(name for name, mark in first.items() if mark),
                         ['(crank, shift, clearing, carry.travel, '
                          'higher.turn) drives higher.turn',
                          '(lower.turn, higher.turn, shift, carry.travel) '
                          'drives carry.travel'])

    def test_the_marks_survive_a_release_and_are_recomputed(self):
        """The marks are a function of the tree's declared relations and
        not of the run, so `release_tree` leaves them where they are: it
        releases a tree the PRODUCER is about to re-render, and an
        unmarked block would refuse that render `DoublyBound`. What keeps
        a stale mark harmless is `_step_relation`'s running-root guard
        and the pre-pass's own idempotence."""
        node = ShiftedCarry()
        _block_members(node)
        marked = self.marks(node)
        release_tree(node)
        self.assertEqual(self.marks(node), marked)
        _block_members(node)
        self.assertEqual(self.marks(node), marked)

    def test_a_second_simulation_over_one_tree_starts_fresh(self):
        node = ShiftedCarry()
        first = Sim(node, dt=0.02)
        first.move('crank', by=1.0, duration=0.1)
        for _step in range(6):
            first.run(0.02)
        second = Sim(node, dt=0.02)
        self.assertEqual(second.state, {'carry.travel': 0.0, 'clearing': 0.0,
                                        'crank': 0.0, 'higher.turn': 0.0,
                                        'lower.turn': 0.0, 'shift': 0.0})

    def test_a_non_running_tree_is_untouched_by_a_stale_mark(self):
        """The marks live on the RECORDS and no render rewrites them, so
        a mark could in principle survive into a later untimed
        enumeration -- except that `_step_relation`'s marked branch is
        guarded by the root's own time base."""
        node = SelectedBare()
        _block_members(node)
        self.assertTrue(any(self.marks(node).values()))

        other = SelectedBareBody()
        for _assembly, _path, records, _formulas, _wirings in _units(other):
            for record in records:
                record.block_member = True
        with self.assertRaises(DoublyBound) as caught:
            other.set_state(crank=0.0, shift=0.0)
        self.assertIn('higher.turn would be bound by the relation',
                      str(caught.exception))


class PieceTest(BaseNodeTest):
    """Task 4.1: the selected machine equals the machine with the
    selection frozen."""

    def test_the_carry_happens_at_one_position_and_not_the_other(self):
        for shift, twin in ((0.0, FixedZero), (1.0, FixedOne)):
            with self.subTest(shift=shift):
                selected, _command = cranked(ShiftedCarry, 2.0, 12,
                                             state={'shift': shift})
                frozen, _other = cranked(twin, 2.0, 12)
                for identifier, value in frozen.state.items():
                    self.assertTrue(
                        agrees(value, selected.state[identifier]),
                        f'{identifier}: {value!r} != '
                        f'{selected.state[identifier]!r}')
                self.assertEqual(selected.state['shift'], shift)

    def test_the_lever_is_what_advances_the_higher_wheel_at_position_zero(
            self):
        selected, _command = cranked(ShiftedCarry, 2.0, 12,
                                     state={'shift': 0.0})
        self.assertTrue(agrees(selected.state['lower.turn'], 2.0))
        self.assertEqual(selected.state['carry.travel'], 1.0)
        self.assertTrue(agrees(selected.state['higher.turn'], 1.5))


class ForcedSelectorTest(BaseNodeTest):
    """Task 4.3: on a piece a selector is a CONSTANT for every member,
    substituted rather than re-located."""

    def setUp(self):
        super().setUp()
        self.sim = Sim(ShiftedCarry(), dt=0.02)
        self.program = self.sim._run.program
        self.block = block_of(self.sim).block
        self.wheel = self.block.members[0]

    def paths(self, shift_delta):
        keys = self.program.keys
        values = self.program.values_of(dict(self.sim.state))
        deltas = {key: 0.0 for key in self.program.nodes}
        deltas[keys['shift']] = shift_delta
        start = {name: values[key]
                 for name, key in zip(self.wheel.names, self.wheel.needs)}
        delta = {name: deltas[key]
                 for name, key in zip(self.wheel.names, self.wheel.needs)}
        return start, delta

    def test_a_forced_selector_records_no_crossing_of_its_own(self):
        """The wheel's law carries its selector in LAYER ONE and also
        reads the coordinate it drives, so the forced branch has to hold
        through `_Retained.outer`'s partition, through the walk's
        `_decide` and `_tentative`, through its sampling and through the
        far-side landing."""
        start, delta = self.paths(1.0)
        reading = self.wheel.retained[0]
        found = []
        reading.increment(start, delta, self.wheel.description,
                          self.wheel.driven[0], found, 0)
        self.assertEqual(
            [(entry.primitive, entry.t) for entry in found],
            [('>=', 0.5)],
            'the selector surface is located when nothing forces it')

        forced = {jump.placeholder: 1.0
                  for jump in self.block.selectors[0]}
        found = []
        reading.increment(start, delta, self.wheel.description,
                          self.wheel.driven[0], found, 0, forced)
        self.assertEqual(found, [],
                         'a forced node is a constant on the piece and its '
                         'crossings are not located again')

    def test_flipping_the_forced_branch_changes_the_answer(self):
        keys = self.program.keys
        values = self.program.values_of(dict(self.sim.state))
        deltas = {key: 0.0 for key in self.program.nodes}
        deltas[keys['crank']] = 1.0
        start = {name: values[key]
                 for name, key in zip(self.wheel.names, self.wheel.needs)}
        delta = {name: deltas[key]
                 for name, key in zip(self.wheel.names, self.wheel.needs)}
        reading = self.wheel.retained[0]
        high, low = self.block.selectors[0]
        # `shift >= 0.5` reading TRUE drives the wheel from the crank;
        # reading FALSE leaves it to the lever, which stands at zero.
        engaged, _landing = reading.increment(
            start, delta, self.wheel.description, self.wheel.driven[0],
            None, 0, {high.placeholder: 1.0, low.placeholder: 0.0})
        idle, _other = reading.increment(
            start, delta, self.wheel.description, self.wheel.driven[0],
            None, 0, {high.placeholder: 0.0, low.placeholder: 1.0})
        self.assertEqual(engaged, 1.0)
        self.assertEqual(idle, 0.0)

    def test_a_switched_out_source_is_handed_no_motion(self):
        """Task 4.8: every term reading it is multiplied by a branch the
        block forced to zero, so the float handed over cannot reach the
        answer."""
        keys = self.program.keys
        lever = self.block.members[1]
        values = self.program.values_of(dict(self.sim.state))
        low, high = self.block.selectors[1]
        forced = {low.placeholder: 1.0, high.placeholder: 0.0}
        found = []
        for higher in (0.0, 5.0):
            deltas = {key: 0.0 for key in self.program.nodes}
            deltas[keys['lower.turn']] = 0.25
            deltas[keys['higher.turn']] = higher
            start = {name: values[key]
                     for name, key in zip(lever.names, lever.needs)}
            delta = {name: deltas[key]
                     for name, key in zip(lever.names, lever.needs)}
            found.append(lever.plans[0].increment(
                start, delta, lever.description, lever.driven[0], None, 0,
                forced))
        self.assertEqual(found[0], found[1])
        self.assertEqual(found[0], 0.25)
        # And the assertion is not vacuous: under the COMPLEMENTARY
        # selection the same source is active and its motion is the whole
        # of the answer.
        deltas = {key: 0.0 for key in self.program.nodes}
        deltas[keys['lower.turn']] = 0.25
        deltas[keys['higher.turn']] = 5.0
        start = {name: values[key]
                 for name, key in zip(lever.names, lever.needs)}
        delta = {name: deltas[key]
                 for name, key in zip(lever.names, lever.needs)}
        active = lever.plans[0].increment(
            start, delta, lever.description, lever.driven[0], None, 0,
            {low.placeholder: 0.0, high.placeholder: 1.0})
        self.assertEqual(active, 5.0)


class SelectionChangeTest(BaseNodeTest):
    """Task 4.5: a selection change alone moves nothing."""

    def test_a_selection_change_inside_a_tick_moves_nothing(self):
        sim = Sim(ShiftedCarry(), dt=1.0, record=4)
        sim.move('crank', by=3.0, duration=1.0)
        sim.run(1.0)
        held = dict(sim.state)
        sim.move('shift', by=1.0, duration=1.0)
        sim.run(1.0)
        for identifier in ('lower.turn', 'higher.turn', 'carry.travel'):
            self.assertEqual(sim.state[identifier], held[identifier],
                             identifier)
        self.assertEqual(sim.state['shift'], 1.0)
        self.assertTrue(sim.crossings)
        self.assertEqual(sim.stops, [])


class LandingTest(BaseNodeTest):
    """Task 4.7: a landing in one piece and motion in a later one commit
    BOTH."""

    def test_the_block_commits_the_absolute_it_advanced_to(self):
        sim = Sim(LandedCarry(), dt=1.0, record=4)
        sim.move('crank', by=4.0, duration=1.0)
        sim.move('shift', by=1.0, duration=1.0)
        sim.run(1.0)
        # Piece one: the lower wheel pushes the lever to its stop, where
        # its own gate cuts the path and LANDS it at 1.0. Piece two: the
        # detent has passed, the higher wheel drives it with no gate, and
        # the crank's remaining 2.0 reaches it through the higher wheel.
        self.assertEqual(sim.state['lower.turn'], 4.0)
        self.assertEqual(sim.state['higher.turn'], 3.0)
        self.assertEqual(sim.state['carry.travel'], 3.0)
        self.assertNotEqual(sim.state['carry.travel'], 1.0)

    def test_the_landing_alone_would_be_one(self):
        """What the rule rejects, stated as arithmetic rather than as a
        claim: the lever's own gate cuts the path at `1.0`, which is
        what "the last landing" would commit."""
        sim = Sim(LandedCarry(), dt=0.5, record=4)
        sim.move('crank', by=4.0, duration=1.0)
        sim.move('shift', by=1.0, duration=1.0)
        sim.run(0.5)
        self.assertEqual(sim.state['carry.travel'], 1.0)


class AccuracyTest(BaseNodeTest):
    """Task 4.6: one tick, twelve and two hundred and forty agree."""

    #: Chosen so that no committed value at any tick's end stands within
    #: the agreement window of a gate threshold or a selector surface:
    #: `carry.travel >= 0.5` is reached at a crank of `0.5`, and neither
    #: `0.7 * k / 12` nor `0.7 * k / 240` is ever `0.5`.
    TRAVEL = 0.7

    def runs(self):
        found = {}
        for ticks in (1, 12, 240):
            sim, command = cranked(ShiftedCarry, self.TRAVEL, ticks)
            found[ticks] = (dict(sim.state), command)
        return found

    def test_every_coordinate_agrees_within_the_window(self):
        found = self.runs()
        base, _command = found[1]
        for ticks in (12, 240):
            state, _other = found[ticks]
            for identifier, value in base.items():
                self.assertTrue(
                    agrees(value, state[identifier]),
                    f'{ticks} ticks, {identifier}: {value!r} != '
                    f'{state[identifier]!r}')

    def test_every_command_reports_the_same_status_exactly(self):
        found = self.runs()
        statuses = {ticks: entry[1].status for ticks, entry in found.items()}
        self.assertEqual(set(statuses.values()), {'completed'})

    def test_admitted_travel_agrees_within_the_window_and_not_bit_for_bit(
            self):
        """`Command.admits` returns ONE difference per tick and
        `Run.integrate` sums them, so 240 summed differences and one
        difference are ulps apart by construction. That is a fact about
        the command bookkeeping and has nothing to do with blocks; the
        contract is the window, and promising bit-equality would be a
        claim the existing code already falsifies."""
        found = self.runs()
        one = found[1][1].admitted
        many = found[240][1].admitted
        self.assertTrue(agrees(one, many), f'{one!r} vs {many!r}')

    def test_a_discrete_reading_is_exact(self):
        found = self.runs()
        for ticks in (1, 12, 240):
            state, _command = found[ticks]
            self.assertEqual(state['carry.travel'] >= 0.5, True)
            self.assertEqual(state['higher.turn'] > 0.5, False)
            self.assertEqual(math.floor(state['lower.turn']), 0)


class RuntimeRefusalTest(BaseNodeTest):
    """Task 6.1: a piece that cannot be ordered refuses the tick,
    transactionally."""

    def test_a_still_cyclic_piece_refuses_the_tick(self):
        sim = Sim(BothActive(), dt=1.0, record=4)
        sim.move('crank', by=1.0, duration=1.0)
        sim.run(1.0)
        held = dict(sim.state)
        tick = sim.tick
        crossings = list(sim.crossings)
        stops = list(sim.stops)

        command = sim.move('shift', by=1.0, duration=1.0)
        with self.assertRaises(UnsupportedLaw) as caught:
            sim.run(1.0)
        message = str(caught.exception)
        self.assertIn('over the piece [0.5, 1.0] of this tick', message)
        self.assertIn('(crank, shift, higher.turn) drives lower.turn',
                      message)
        self.assertIn('(crank, shift, lower.turn) drives higher.turn',
                      message)
        self.assertIn('>= on (shift - 0.5) reads 1.0', message)
        self.assertIn('The tick committed nothing', message)

        self.assertEqual(sim.state, held)
        self.assertEqual(sim.tick, tick)
        self.assertEqual(list(sim.crossings), crossings)
        self.assertEqual(list(sim.stops), stops)
        self.assertEqual(command.status, 'refused')


class CurtaShapedTest(BaseNodeTest):
    """The Curta-shaped fixture: four dials on a carriage, three levers
    in the fixed frame, and one block."""

    def test_the_whole_carriage_is_one_block(self):
        sim = Sim(CurtaCarriage(), dt=0.02)
        block = block_of(sim).block
        self.assertEqual(sorted(block.names),
                         ['dial0.turn', 'dial1.turn', 'dial2.turn',
                          'dial3.turn', 'lever0.travel', 'lever1.travel',
                          'lever2.travel'])
        # Every selector reads the carriage's own JOINT coordinate or the
        # hoist, never the `position` driver: the selection follows the
        # part rather than the request.
        for index, member in enumerate(block.members):
            for jump in block.selectors[index]:
                names = str(jump.argument)
                self.assertTrue('seat' in names or 'hoist' in names,
                                f'{member.description}: {names}')
                self.assertNotIn('position', names)

    DT = 0.02

    def step(self, sim, name, travel, duration, ticks):
        handle = sim.move(name, by=travel, duration=duration)
        for _tick in range(ticks):
            sim.run(self.DT)
        return handle

    def test_a_shift_away_and_back_preserves_every_part(self):
        """Task 5.6. A selection that goes inactive drives nothing, and a
        coordinate no edge determines HOLDS, so the lever left set at one
        position stands where the mechanism left it until the reset cam
        returns it -- and then acts on the wheel it now faces."""
        sim = Sim(CurtaCarriage(), dt=self.DT, record=256)
        self.step(sim, 'lift', 1.0, 0.1, 5)
        self.step(sim, 'position', 1.0, 0.2, 10)
        self.step(sim, 'lift', -1.0, 0.1, 5)
        self.step(sim, 'crank', 36.0, 0.4, 20)
        # At position one, lever 0 faces dial 1 and advances dial 2;
        # lever 1 faces dial 2 and advances dial 3.
        self.assertTrue(agrees(sim.state['dial0.turn'], 36.0))
        self.assertTrue(agrees(sim.state['dial1.turn'], 36.0))
        self.assertTrue(agrees(sim.state['dial2.turn'], 72.0))
        self.assertTrue(agrees(sim.state['dial3.turn'], 72.0))
        self.assertEqual(sim.state['lever0.travel'], 1.0)
        held = dict(sim.state)

        # Shifting away changes NOTHING but the carriage.
        self.step(sim, 'lift', 1.0, 0.1, 5)
        self.step(sim, 'position', 1.0, 0.2, 10)
        self.step(sim, 'lift', -1.0, 0.1, 5)
        for key, value in held.items():
            if key in ('position', 'seat', 'hoist', 'lift'):
                continue
            # BIT FOR BIT, every dial and every lever: a piece whose
            # substituted law does not move leaves its coordinate at the
            # exact float it held, so twenty ticks of lifting, shifting
            # and dropping add a true zero to each of them.
            self.assertEqual(sim.state[key], value,
                             f'{key}: {sim.state[key]!r} != {value!r}')
        self.assertEqual(sim.state['seat'], 40.0)

        # The levers stay SET until the reset cam reaches them, which it
        # does only with the carriage lifted.
        self.step(sim, 'lift', 1.0, 0.1, 5)
        self.step(sim, 'reset', 1.0, 0.2, 10)
        self.step(sim, 'lift', -1.0, 0.1, 5)
        # The cam drives each lever exactly ONTO its own `travel >
        # RETURNED` surface, and what it rests at is the float sum of the
        # cam's ten increments -- `1.1102230246251565e-16`, the residue
        # of adding a tenth ten times. A reading taken on a coordinate's
        # own surface is what design.md section 4 excludes from the exact
        # promise; the bit-for-bit assertions above are taken away from
        # every surface.
        self.assertTrue(agrees(sim.state['lever0.travel'], 0.0))
        self.assertTrue(agrees(sim.state['lever1.travel'], 0.0))
        self.assertTrue(agrees(sim.state['dial3.turn'], 72.0))

        # And now each lever acts on the wheel it FACES at this position.
        self.step(sim, 'crank', 36.0, 0.4, 20)
        self.assertTrue(agrees(sim.state['dial2.turn'], 108.0))
        self.assertTrue(agrees(sim.state['dial3.turn'], 144.0))
        self.assertTrue(agrees(sim.state['lever2.travel'], 0.0))
