# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The Studio skill follows the framework's supported two-color value."""
from pathlib import Path
import unittest


class StateColorContractTest(unittest.TestCase):
    def test_helper_matches_the_shared_source_contract(self):
        text = (Path(__file__).resolve().parents[1] /
                'machinome/studio/shop-skills/machinome-api/SKILL.md').read_text()
        self.assertIn('from machinome.color import color_when', text)
        for phrase in ('color_when(condition, *, on, off)', 'finite zero',
                       'same body', 'document 14', 'API 30',
                       'reset', 'restore', 'replay', 'emitted light'):
            self.assertIn(phrase, text)
