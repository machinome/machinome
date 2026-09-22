# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Version-10 producer evidence for the independently maintained viewer."""

import copy
import json
from pathlib import Path

from .base import BaseNodeTest


class TimeDriveCorpusTest(BaseNodeTest):
    def test_committed_documents_and_every_tick_replay(self):
        from tools.generate_time_drive_corpus import build
        expected = json.loads(Path(__file__).with_name(
            'time-drive-corpus.json').read_text())
        actual = build()
        from .source_timing_compatibility import without_semantic_upgrade
        for current, old in zip(actual['machines'], expected['machines']):
            current['document'] = without_semantic_upgrade(
                self, current['document'], old['document'])
        self.assertEqual(actual, expected)

    def test_guard_requires_time_drives_and_their_motion(self):
        from tools.generate_time_drive_corpus import build, uncovered_features
        corpus = build()['machines']
        self.assertEqual(uncovered_features(corpus), [])
        missing = copy.deepcopy(corpus)
        for entry in missing:
            entry['document']['program'].pop('time_drives', None)
        self.assertIn('explicit time drives', uncovered_features(missing))
        missing = copy.deepcopy(corpus)
        for entry in missing:
            for tick in entry['ticks']:
                tick['bank'] = {key: value['initial'] for key, value in
                               entry['document']['program']['coordinates'].items()}
        self.assertIn('uncommanded motion', uncovered_features(missing))

    def test_guard_requires_stop_provenance_and_replay(self):
        from tools.generate_time_drive_corpus import build, uncovered_features
        corpus = build()['machines']
        missing = copy.deepcopy(corpus)
        for entry in missing:
            for tick in entry['ticks']:
                tick['stops'] = []
        self.assertIn('independent time-drive stop', uncovered_features(missing))
        missing = copy.deepcopy(corpus)
        for entry in missing:
            entry['script'] = [action for action in entry['script']
                               if not any(name in action for name in
                                          ('snapshot', 'restore', 'reset'))]
        self.assertIn('snapshot restore and reset', uncovered_features(missing))
