# machinome-viewer - the browser viewer for Machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Executable contract for the unreleased viewer's final identity."""

from pathlib import Path
import tomllib
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]


class MachinomeViewerIdentityTest(TestCase):
    def setUp(self):
        self.metadata = tomllib.loads((ROOT / 'pyproject.toml').read_text())

    def test_python_distribution_command_and_lookup_are_machinome(self):
        project = self.metadata['project']
        self.assertEqual(project['name'], 'machinome-viewer')
        self.assertEqual(project['scripts'],
                         {'machinome-viewer': 'machinome_viewer.cli:main'})
        self.assertEqual(
            project['entry-points']['machinome.viewer']['bundle'],
            'machinome_viewer.bundle:describe')
        self.assertTrue((ROOT / 'machinome_viewer' / '__init__.py').is_file())
        self.assertFalse((ROOT / 'solid_node_viewer').exists())

    def test_bundle_and_browser_global_are_machinome(self):
        widget = tomllib.loads((ROOT / 'pyproject.toml').read_text())
        self.assertEqual(widget['project']['name'], 'machinome-viewer')
        build = (ROOT / 'machinome_viewer' / 'widget' / 'build.mjs').read_text()
        self.assertIn('MachinomeViewer', build)
        self.assertIn('machinome-viewer.js', build)
        self.assertNotIn('SolidNodeWidget', build)

    def test_loader_accepts_current_and_legacy_formats(self):
        loader = (ROOT / 'machinome_viewer' / 'widget' / 'src' /
                  'viewer.ts').read_text()
        self.assertIn('machinome-export', loader)
        self.assertIn('solid-node-export', loader)
