# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A clocked simulation publishes its machine's identity.

The export's manifest carries `clocked.identity`, and a consumer recording a
take through `Sim` compares it with the identity of the machine it
recorded over, so a take made over a machine that differs from the export's
is refused when it is recorded. The originating consumer is Videomaker's
recording of a clocked calculator (OpenSpec change ``sim-identity``).
"""

import json
import os

from machinome.core.export import export_node
from machinome.motion.joints import Revolute
from machinome.motion.ports import Time
from machinome.node.assembly import AssemblyNode
from machinome.simulation import Driver, Sim, State

from .base import BaseNodeTest
from .clocked_project.counter import (Counter, DIGIT, Stateless, advance,
                                      strokes)
from .clocked_project.parts import Dial
from .clocked_project.units import Scaled
from .test_clocked_publication import built


def skipping(sources, targets):
    """The counter's commit law advancing the units by two."""
    return lambda crank, units, tens: ((units + 2) % 10,
                                       (tens + (units >= 8)) % 10)


def restated(stop=324.0, law=advance):
    """The register counter, built here so that every variant has this
    module, one qualified name and one bank: only the units dial's stop
    or the commit law differs."""

    class Counter(AssemblyNode):
        crank = Driver(default=0, unit='deg')
        units = State(default=0, range=(0, 9), dtype=int)
        tens = State(default=0, range=(0, 9), dtype=int)

        units_dial = Dial(turn=Revolute(axis=(0, 0, 1), unit='deg',
                                        range=(0, stop)))
        tens_dial = Dial()

        (crank & units & tens).commits((units, tens), at=strokes, law=law)

        units.drives(units_dial.turn, ratio=DIGIT)
        tens.drives(tens_dial.turn, ratio=DIGIT)

    return Counter


class RunningStateless(AssemblyNode):
    """`Stateless` under a running base: a root whose compiled program
    carries an identity of its own, and which is not clocked."""

    time = Time.running()

    crank = Driver(default=0, unit='deg')

    units_dial = Dial()

    crank.drives(units_dial.turn, ratio=1.0)


class IdentityTest(BaseNodeTest):

    def test_the_identity_is_the_one_the_export_carries(self):
        out_dir = os.path.join(self.build_dir, 'clocked_identity_export')
        export_node(built(Counter()), out_dir, widget=False)
        with open(os.path.join(out_dir, 'manifest.json')) as handle:
            manifest = json.load(handle)
        self.assertEqual(Sim(Counter()).identity,
                         manifest['clocked']['identity'])

    def test_the_identity_does_not_move_with_the_bank(self):
        at_rest = Sim(Counter()).identity
        sim = Sim(Counter(), state={'units': 7})
        self.assertEqual(sim.identity, at_rest)
        saved = sim.snapshot()
        sim.move('crank', by=1080.0)
        self.assertEqual(sim.state['tens'], 1)
        self.assertEqual(sim.identity, at_rest)
        sim.restore(saved)
        self.assertEqual(sim.identity, at_rest)
        sim.reset()
        self.assertEqual(sim.identity, at_rest)

    def test_different_machines_have_different_identities(self):
        self.assertNotEqual(Sim(Counter()).identity, Sim(Scaled()).identity)


class IdentityRefusalTest(BaseNodeTest):

    def test_an_untimed_simulation_refuses_the_identity_by_name(self):
        sim = Sim(Stateless(), 0.1)
        with self.assertRaises(TypeError) as caught:
            sim.identity
        message = str(caught.exception)
        self.assertIn('identity', message)
        self.assertIn('Stateless', message)
        self.assertIn('State', message)
        self.assertNotIn('sim.program.identity', message)

    def test_a_running_simulation_refuses_the_identity_by_name(self):
        sim = Sim(RunningStateless(), 0.1)
        with self.assertRaises(TypeError) as caught:
            sim.identity
        message = str(caught.exception)
        self.assertIn('identity', message)
        self.assertIn('RunningStateless', message)
        self.assertIn('sim.program.identity', message)
        # The member it points at is the running program's own identity.
        self.assertTrue(sim.program.identity)


class SnapshotIdentityTest(BaseNodeTest):
    """A clocked snapshot carries the identity of the machine it was
    taken over, and restores into that machine only."""

    def taken(self):
        """Three strokes of the restated counter, and their snapshot."""
        sim = Sim(restated()())
        sim.move('crank', by=1080.0)
        return sim, sim.snapshot()

    def assertRefused(self, model):
        source, saved = self.taken()
        target = Sim(model())
        # What makes this a test of the identity: the names agree, the
        # machines do not.
        self.assertEqual(target.snapshot().model, saved.model)
        self.assertNotEqual(target.identity, source.identity)
        before = target.state
        posed = target.node.units_dial.turn.value
        with self.assertRaises(ValueError) as caught:
            target.restore(saved)
        message = str(caught.exception)
        self.assertIn(source.identity, message)
        self.assertIn(target.identity, message)
        self.assertIn('Counter(crank,tens,units)', message)
        self.assertEqual(target.state, before)
        self.assertEqual(target.node.units_dial.turn.value, posed)

    def test_a_snapshot_carries_the_machines_identity(self):
        sim = Sim(Counter())
        sim.move('crank', by=360.0)
        self.assertEqual(sim.snapshot().identity, sim.identity)
        self.assertEqual(sim.initial.identity, sim.identity)

    def test_a_snapshot_restores_into_the_same_machine(self):
        _, saved = self.taken()
        target = Sim(restated()())
        target.restore(saved)
        self.assertEqual(target.state, saved.values)
        self.assertEqual(target.state['units'], 3)
        self.assertEqual(target.node.units_dial.turn.value, 108.0)

    def test_a_machine_whose_range_changed_refuses_the_snapshot(self):
        self.assertRefused(restated(stop=360.0))

    def test_a_machine_whose_commit_law_changed_refuses_the_snapshot(self):
        self.assertRefused(restated(law=skipping))
