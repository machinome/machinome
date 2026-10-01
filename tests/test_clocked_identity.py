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
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver, Sim

from .base import BaseNodeTest
from .clocked_project.counter import Counter, Stateless
from .clocked_project.parts import Dial
from .clocked_project.units import Scaled
from .test_clocked_publication import built


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
