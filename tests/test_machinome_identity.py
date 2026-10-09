# Machinome - Source code for machines
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Executable contract for the 0.7 Machinome identity."""

import os
from pathlib import Path
import tomllib
from unittest import TestCase

from packaging.requirements import Requirement


ROOT = Path(__file__).resolve().parents[1]


class MachinomeIdentityTest(TestCase):
    def setUp(self):
        self.metadata = tomllib.loads((ROOT / 'pyproject.toml').read_text())

    def test_distribution_import_command_and_extras_share_the_name(self):
        project = self.metadata['project']
        self.assertEqual(project['name'], 'machinome')
        self.assertEqual(project['version'], '0.8.0')
        self.assertEqual(project['scripts'], {'machinome': 'machinome.cli:manage'})
        self.assertEqual(project['urls']['Homepage'],
                         'https://github.com/machinome/machinome')
        # Each extra selects one product by name; a floor such as the
        # viewer's is held by tests/test_release_records.py, not here.
        for extra, name in (('viewer', 'machinome-viewer'),
                            ('mechanics', 'machinome-mechanics'),
                            ('studio', 'machinome-studio')):
            with self.subTest(extra=extra):
                (requirement,) = project['optional-dependencies'][extra]
                self.assertEqual(Requirement(requirement).name, name)

    def test_only_the_machinome_import_package_is_shipped(self):
        self.assertTrue((ROOT / 'machinome' / '__init__.py').is_file())
        self.assertFalse((ROOT / 'solid_node').exists())

    def test_runtime_environment_uses_the_machinome_prefix(self):
        current = set()
        former = set()
        for path in (ROOT / 'machinome').rglob('*.py'):
            source = path.read_text()
            if 'MACHINOME_' in source:
                current.add(os.fspath(path.relative_to(ROOT)))
            if 'SOLID_NODE_' in source:
                former.add(os.fspath(path.relative_to(ROOT)))
        self.assertTrue(current)
        self.assertEqual(former, {'machinome/cli.py'})

    def test_new_documents_and_viewer_lookup_use_machinome(self):
        from machinome.core.serializer import DOCUMENT_FORMAT
        from machinome.viewers.bundle import ENTRY_POINT_GROUP

        self.assertEqual(DOCUMENT_FORMAT, 'machinome-export')
        self.assertEqual(ENTRY_POINT_GROUP, 'machinome.viewer')
