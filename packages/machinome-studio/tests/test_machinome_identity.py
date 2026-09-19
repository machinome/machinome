# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Executable contract for Machinome Studio's product identity."""

from pathlib import Path
import tomllib
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]


class MachinomeStudioIdentityTest(TestCase):
    def test_package_and_current_entry_copy_use_machinome(self):
        project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
        self.assertEqual(project['name'], 'machinome-studio')
        self.assertEqual(project['description'],
                         'Machinome Studio mechanical CAD agent harness')
        self.assertIn('# Machinome Studio', (ROOT / 'README.md').read_text())

    def test_workspace_scripts_use_canonical_product_paths(self):
        sources = '\n'.join(path.read_text(errors='ignore')
                            for path in (ROOT / 'scripts').iterdir()
                            if path.is_file())
        for name in ('machinome-framework', 'machinome-viewer',
                     'machinome-mechanics'):
            self.assertIn(name, sources)
        self.assertIn('machinome', sources)

    def test_project_configuration_uses_machinome_studio(self):
        source = '\n'.join(path.read_text(errors='ignore')
                           for path in (ROOT / 'floor').rglob('*.py'))
        self.assertIn('machinome-studio', source)
        self.assertIn('libresolid-studio', source)
        self.assertIn('renamed [tool.libresolid-studio]', source)
