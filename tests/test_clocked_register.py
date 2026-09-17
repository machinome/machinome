# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A register of identical wheels, each written at TWO events.

Closure 1 of the change `declare-the-state` (2026-09-17), findings C1 and
C2. The originating project `projects/Calculators/Curta-Type-I-3x` has
seventeen result wheels of one class; each is written by the stroke that
adds to the register and by the clearing ring that sweeps past its own
rack. Those are two events on two inputs, and one committing relation
states one `at`, so the machine needs:

- two states of two children of ONE class to be TWO states, told apart by
  their PATHS and not by the local name they share (C1); and
- a state to admit SEVERAL committing relations, refusing only two
  answers for one value at ONE landing (C2).

Every expected value below is computed BY HAND from `register.threshold`
and from plain arithmetic; no law of the fixture is called to produce
one.
"""

from unittest import TestCase

from solid_node.simulation import Sim
from solid_node.simulation.clocked import ClockedError

from .base import BaseNodeTest
from .clocked_project import unsupported
from .clocked_project.register import Register, threshold


class PathsNotNamesTest(TestCase):
    """C1: two children of one class are two states."""

    def test_one_relation_writes_three_wheels_of_one_class(self):
        # The class body alone: it is `Register` that names
        # `w0.digit`, `w1.digit` and `w2.digit` among one relation's
        # targets, and the refusal that keyed on the local name
        # `digit` made the class uncreatable.
        self.assertEqual(len(Register._declared_commitments), 4)

    def test_three_wheels_of_one_class_enumerate_apart(self):
        sim = Sim(Register())
        self.assertEqual(
            sorted(name for name in sim.state if name.startswith('w')),
            ['w0.digit', 'w1.digit', 'w2.digit'])

    def test_two_children_written_by_two_different_relations(self):
        # The same shape across two relations rather than inside one:
        # the clearing relations write `w0.digit` and `w1.digit`
        # separately, and neither is the other's second writer.
        sim = Sim(Register(), state={'w0.digit': 3, 'w1.digit': 4})
        sim.move('ring', to=threshold(1, 4))
        self.assertEqual(sim.state['w0.digit'], 0)
        self.assertEqual(sim.state['w1.digit'], 0)


class RegisterTest(BaseNodeTest):
    """C2: a wheel written by the stroke AND by its clearing reach."""

    def test_strokes_add_with_carry(self):
        sim = Sim(Register())
        # operand defaults to 1, so twelve strokes count to twelve: the
        # carry out of the units wheel happens at the tenth.
        request = sim.move('crank', by=360.0 * 12)
        self.assertEqual(len(request.commits), 12)
        self.assertEqual(sim.state['w0.digit'], 2)
        self.assertEqual(sim.state['w1.digit'], 1)
        self.assertEqual(sim.state['w2.digit'], 0)

    def test_a_bigger_operand_adds_and_carries(self):
        sim = Sim(Register(), state={'operand': 9})
        # Nine, eight times: 72.
        sim.move('crank', by=360.0 * 8)
        self.assertEqual(sim.state['w0.digit'], 2)
        self.assertEqual(sim.state['w1.digit'], 7)
        self.assertEqual(sim.state['w2.digit'], 0)

    def test_a_partial_sweep_clears_only_the_wheels_it_reaches(self):
        sim = Sim(Register(),
                  state={'w0.digit': 2, 'w1.digit': 5, 'w2.digit': 1})
        # By hand: w0 is reached at 10 + 4*2 = 18, w1 at 110 + 4*5 = 130,
        # w2 at 210 + 4*1 = 214. A sweep to 200 reaches the first two.
        self.assertEqual(threshold(0, 2), 18.0)
        self.assertEqual(threshold(1, 5), 130.0)
        self.assertEqual(threshold(2, 1), 214.0)
        request = sim.move('ring', to=200.0)
        self.assertEqual(len(request.commits), 2)
        self.assertEqual(sim.state['w0.digit'], 0)
        self.assertEqual(sim.state['w1.digit'], 0)
        self.assertEqual(sim.state['w2.digit'], 1)

    def test_a_reversed_sweep_unclears_nothing(self):
        sim = Sim(Register(),
                  state={'w0.digit': 2, 'w1.digit': 5, 'w2.digit': 1})
        sim.move('ring', to=200.0)
        request = sim.move('ring', to=0.0)
        self.assertEqual(request.commits, ())
        self.assertEqual(sim.state['w0.digit'], 0)
        self.assertEqual(sim.state['w1.digit'], 0)
        self.assertEqual(sim.state['w2.digit'], 1)

    def test_a_second_sweep_fires_nothing_on_a_cleared_wheel(self):
        sim = Sim(Register(),
                  state={'w0.digit': 2, 'w1.digit': 5, 'w2.digit': 1})
        sim.move('ring', to=200.0)
        # Sweeping on: the two cleared wheels' levels stand already
        # risen and cannot rise again, and only w2, whose threshold is
        # 214, is reached.
        request = sim.move('ring', to=300.0)
        self.assertEqual(len(request.commits), 1)
        self.assertEqual(request.commits[0].targets, {'w2.digit': 0})
        self.assertEqual(sim.state['w2.digit'], 0)

    def test_strokes_after_clearing_continue_from_zero(self):
        sim = Sim(Register(),
                  state={'w0.digit': 2, 'w1.digit': 5, 'w2.digit': 1})
        sim.move('ring', to=300.0)
        self.assertEqual(sim.state['w0.digit'], 0)
        self.assertEqual(sim.state['w1.digit'], 0)
        self.assertEqual(sim.state['w2.digit'], 0)
        sim.move('ring', to=0.0)
        sim.move('crank', by=360.0 * 3)
        self.assertEqual(sim.state['w0.digit'], 3)
        self.assertEqual(sim.state['w1.digit'], 0)
        self.assertEqual(sim.state['w2.digit'], 0)

    def test_the_pose_follows_the_committed_digits(self):
        sim = Sim(Register())
        sim.move('crank', by=360.0 * 12)
        # 36 design degrees per digit, by the fixture's own ratio.
        self.assertEqual(sim.node.w0.face.turn.value, 72.0)
        self.assertEqual(sim.node.w1.face.turn.value, 36.0)
        self.assertEqual(sim.node.w2.face.turn.value, 0.0)


class SeveralWritersTest(BaseNodeTest):
    """C2 in its smallest form: two writers apart, and two together."""

    def test_two_writers_on_two_inputs_are_admitted(self):
        sim = Sim(unsupported.Apart())
        sim.move('crank', by=360.0 * 3)
        self.assertEqual(sim.state['value'], 3)
        # The ring's own event writes the same state, at its own event.
        sim.move('ring', by=100.0)
        self.assertEqual(sim.state['value'], 0)

    def test_two_writers_at_one_event_refuse_the_request(self):
        sim = Sim(unsupported.Conflicting())
        before = sim.state
        with self.assertRaises(ClockedError) as caught:
            sim.move('crank', by=360.0)
        message = str(caught.exception)
        self.assertIn('value', message)
        self.assertIn('360.0', message)
        # Both relations named, by what each was written as.
        self.assertEqual(message.count('commits'), 2)
        # And nothing committed.
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.node.face.turn.value, 0.0)
