# Machinome Mechanics - Mechanical formula helpers for Machinome projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Executable contract for the mechanics package identity."""

from pathlib import Path
import tomllib
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]


class MachinomeMechanicsIdentityTest(TestCase):
    def test_distribution_dependency_and_import_package(self):
        project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
        self.assertEqual(project['name'], 'machinome-mechanics')
        self.assertEqual(project['dependencies'], ['machinome>=0.7.0'])
        self.assertEqual(project['urls']['Homepage'],
                         'https://github.com/machinome/machinome-mechanics')
        self.assertTrue((ROOT / 'machinome_mechanics' / '__init__.py').is_file())
        self.assertFalse((ROOT / 'solid_node_mechanics').exists())

    def test_formulas_use_machinome_math(self):
        imports = []
        for path in (ROOT / 'machinome_mechanics').glob('*.py'):
            imports.extend(line for line in path.read_text().splitlines()
                           if line.startswith('from ') or line.startswith('import '))
        self.assertTrue(any('machinome' in line for line in imports))
        self.assertFalse(any('solid_node' in line for line in imports))
