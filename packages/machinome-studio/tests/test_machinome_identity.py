# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Executable contract for Machinome Studio's product identity."""

from pathlib import Path
import tomllib
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = 'packages/machinome-studio/machinome/studio/frontend'


class MachinomeStudioIdentityTest(TestCase):
    def test_package_and_current_entry_copy_use_machinome(self):
        project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
        self.assertEqual(project['name'], 'machinome-studio')
        self.assertEqual(project['description'],
                         'Machinome Studio: a project hub and workspace in '
                         'the browser where a team of agents builds a '
                         'machinome project with its maker')
        readme = (ROOT / 'README.md').read_text()
        self.assertIn('# machinome-studio', readme)
        self.assertIn('machinome studio --projects-dir PATH', readme)

    def test_studio_scripts_use_canonical_product_paths(self):
        # The browser tests build the frontend from the repository's npm
        # workspace and opt in; the favicon pack is written under the
        # package directory (change `join-studio`).
        e2e = (ROOT / 'scripts' / 'test-e2e').read_text()
        self.assertIn(f'npm run build --workspace {FRONTEND}', e2e)
        self.assertIn('MACHINOME_STUDIO_E2E=1', e2e)
        favicon = (ROOT / 'scripts' / 'build-favicon').read_text()
        self.assertIn('"machinome" / "studio" / "frontend" / "public" / "assets"',
                      favicon)
        for script in (e2e, favicon):
            self.assertNotIn('floor/', script)

    def test_project_configuration_uses_machinome_studio(self):
        source = '\n'.join(path.read_text(errors='ignore')
                           for path in (ROOT / 'machinome' / 'studio').rglob('*.py'))
        self.assertIn('machinome-studio', source)
        self.assertIn('libresolid-studio', source)
        self.assertIn('renamed [tool.libresolid-studio]', source)
