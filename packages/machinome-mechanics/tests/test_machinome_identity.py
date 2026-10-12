# Machinome Mechanics - Mechanical formula helpers for Machinome projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Executable contract for the mechanics package identity.

The package is the repository's distribution `machinome-mechanics`, its
helpers the portion `machinome.mechanics` of the `machinome` package
(change `join-mechanics`).
"""

from pathlib import Path
import tomllib
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]


class MachinomeMechanicsIdentityTest(TestCase):
    def test_distribution_dependency_and_import_package(self):
        manifest = tomllib.loads((ROOT / 'pyproject.toml').read_text())
        project = manifest['project']
        self.assertEqual(project['name'], 'machinome-mechanics')
        self.assertEqual(project['dependencies'], ['machinome>=0.8.0'])
        self.assertEqual(project['license'],
                         'GPL-2.0-or-later OR CERN-OHL-S-2.0+')
        self.assertEqual(project['license-files'],
                         ['LICENSE', 'LICENSES/*.txt'])
        self.assertEqual(project['urls']['Homepage'],
                         'https://github.com/machinome/machinome')
        self.assertEqual(manifest['tool']['setuptools']['packages']['find'],
                         {'include': ['machinome.mechanics'],
                          'namespaces': True})
        self.assertTrue(
            (ROOT / 'machinome' / 'mechanics' / '__init__.py').is_file())
        self.assertFalse((ROOT / 'machinome' / '__init__.py').exists())
        self.assertFalse((ROOT / 'machinome_mechanics').exists())
        self.assertFalse((ROOT / 'solid_node_mechanics').exists())

    def test_formulas_use_machinome_math(self):
        imports = []
        for path in (ROOT / 'machinome' / 'mechanics').glob('*.py'):
            imports.extend(line for line in path.read_text().splitlines()
                           if line.startswith('from ') or line.startswith('import '))
        self.assertTrue(any('machinome' in line for line in imports))
        self.assertFalse(any('machinome_mechanics' in line for line in imports))
        self.assertFalse(any('solid_node' in line for line in imports))

    def test_the_package_resolves_from_its_directory(self):
        import machinome.mechanics as mechanics
        self.assertEqual(Path(mechanics.__file__).resolve(),
                         ROOT / 'machinome' / 'mechanics' / '__init__.py')
