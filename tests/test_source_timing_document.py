# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""The corrected producer must not silently reach an endpoint-era consumer."""
from dataclasses import replace
import hashlib

from machinome.simulation import Sim
from .base import BaseNodeTest
from .carriage_project.machine import FixedZero, ShiftedCarry
from .running_project.machine import Train, TrainBody, PlayCorpus, LoopingTrain
from .running_project.time_drive import affine
from .test_running_document import document


class SourceTimingDocumentTest(BaseNodeTest):
    def test_every_running_shape_declares_corrected_semantics(self):
        for model in (Train, FixedZero, ShiftedCarry, PlayCorpus):
            with self.subTest(model=model.__name__):
                self.assertEqual(document(model())['version'], 11)
        self.assertEqual(document(affine())['version'], 11)

    def test_nonrunning_version_selection_is_unchanged(self):
        for model in (LoopingTrain, TrainBody):
            with self.subTest(model=model.__name__):
                self.assertLess(document(model())['version'], 5)

    def test_endpoint_era_snapshot_refuses_before_mutation(self):
        sim = Sim(FixedZero(), .1, record=16)
        snapshot = sim.snapshot()
        listing = sim._run.program.described()
        self.assertIn('source-timing version=11', listing)
        old_listing = '\n'.join(line for line in listing.split('\n')
                                if line != 'source-timing version=11')
        old = replace(snapshot, program=hashlib.sha256(old_listing.encode()).hexdigest())
        sim.move('crank', to=4)
        before = sim.snapshot()
        with self.assertRaises(ValueError):
            sim.restore(old)
        self.assertEqual(sim.snapshot(), before)
        sim.restore(snapshot)
        self.assertEqual(sim.move('crank', to=4).status, 'completed')
        self.assertAlmostEqual(sim.state['higher.turn'], 3.5)
