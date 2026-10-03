# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""The runtime contract preserves the ratified narrow Frame precision rule."""
from pathlib import Path
import unittest


class FramePrecisionContractTest(unittest.TestCase):
    def test_frame_and_readout_describe_precise_and_default_paths(self):
        text = (Path(__file__).resolve().parents[1] /
                'shop-skills/machinome-api/SKILL.md').read_text()
        declaration = text.split('`Frame(at=(0,0,0)', 1)[1].split(
            'Arguments follow the joint argument rule', 1)[0]
        readout = text.split('**Reading them back.**', 1)[1].split('**Relations**', 1)[0]
        for passage in (declaration, readout):
            with self.subTest(passage=passage[:30]):
                for phrase in ('both', 'explicitly', 'omitted', 'snap'):
                    self.assertIn(phrase, passage)
        self.assertIn('Final mate angle/axis snap', declaration)
        self.assertIn('Joint axis snapping', declaration)
        self.assertIn('explicitly writing default `z=(0,0,1)`', declaration)
        self.assertIn('with z omitted keeps the snapped path', declaration)
        self.assertIn('y=z×x', declaration)
        self.assertIn('same cached basis', readout)
