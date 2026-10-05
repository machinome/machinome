# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The manual describes the same mate contract the acceptance fixture runs."""

import unittest
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class MateContractDocumentationTest(unittest.TestCase):
    def test_the_drive_example_executes_and_intersects_its_original_bound(self):
        from machinome.motion.joints import Bound, Revolute
        from machinome.motion.ports import Time
        from machinome.node.assembly import AssemblyNode
        from machinome.node.frames import Frame
        from machinome.simulation import Driver, Sim
        from .test_mate_contracts import Handle, Pawl

        text = (ROOT / 'docs/concepts/joints.rst').read_text()
        example = text.partition('For example, with ``Handle``')[2]
        example = example.partition('.. code-block:: python\n\n')[2]
        example = example.partition('\n\n``travel``')[0]
        self.assertTrue(example.startswith('    class Drive(AssemblyNode):'))
        namespace = dict(AssemblyNode=AssemblyNode, Frame=Frame,
                         Bound=Bound, Revolute=Revolute, Handle=Handle, Pawl=Pawl)
        exec(textwrap.dedent(example), namespace)
        Drive = namespace['Drive']
        class Running(Drive):
            time = Time.running()
            request = Driver(default=0)
            relief = Driver(default=0)
            lifting = Driver(default=0)
            request.drives(Drive.travel)
            relief.drives(Drive.pawl.turn)
            lifting.drives(Drive.handle.lift)
        sim = Sim(Running(), dt=.1)
        self.assertEqual(sim.move('request', to=120).status, 'blocked')
        self.assertEqual(sim.state['handle.travel'], 90)
        sim.move('relief', to=20)
        self.assertEqual(sim.move('request', to=120).status, 'blocked')
        self.assertEqual(sim.state['handle.travel'], 100)

    def test_joints_teaches_mate_read_scope_and_constraint_target(self):
        joints = (ROOT / 'docs/concepts/joints.rst').read_text()
        self.assertIn('reads=(pawl.turn,)', joints)
        self.assertIn('travel.constrain(range=(None, 100))', joints)
        self.assertIn('declaring assembly', joints)
        self.assertNotIn('or reads other coordinates; a mate', joints)

    def test_running_and_reference_admit_explicit_mate_selection(self):
        running = (ROOT / 'docs/concepts/running.rst').read_text()
        reference = (ROOT / 'docs/reference/api.rst').read_text()
        self.assertIn('coordinate=travel', running)
        self.assertIn('generated child joint', reference)
