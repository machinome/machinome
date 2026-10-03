# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD engine, the package `machinome.openscad` (OpenSpec change
`expression-type`, capability `openscad-engine`).

The package exports nothing. Its provider module adopts a value SolidPython
built as the core's expression graph, reading the value's text with the
core's own parser; its binary module is the OpenSCAD binary contract,
moved here unchanged from `machinome/openscad.py`.
"""

import ast
import importlib
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class PackageTest(TestCase):

    def test_the_package_itself_exports_nothing(self):
        package = importlib.import_module('machinome.openscad')
        for name in ('adopt', 'CONTRACT', 'require_openscad',
                     'openscad_binary', 'OpenScadUnavailable'):
            with self.subTest(name):
                self.assertFalse(hasattr(package, name))

    def test_the_provider_declares_contract_version_one(self):
        engine = importlib.import_module('machinome.openscad.engine')
        self.assertEqual(engine.CONTRACT, 1)


class AdoptTest(TestCase):

    def setUp(self):
        self.engine = importlib.import_module('machinome.openscad.engine')

    def test_solidpythons_animation_time_is_the_name_t(self):
        import solid2
        node = self.engine.adopt(solid2.get_animation_time())
        self.assertEqual((node.kind, node.text), ('name', '$t'))

    def test_text_in_the_language_is_parsed(self):
        from solid2.core.object_base import scad_inline
        node = self.engine.adopt(scad_inline('(other + 2)'))
        self.assertEqual((node.kind, node.op), ('binop', '+'))
        self.assertEqual([(child.kind, child.text) for child in node.children],
                         [('name', 'other'), ('num', '2')])

    def test_text_outside_the_language_is_carried_raw(self):
        from solid2.core.object_base import scad_inline
        node = self.engine.adopt(scad_inline('$mystery ? 1 : 2'))
        self.assertEqual((node.kind, node.text), ('raw', '$mystery ? 1 : 2'))

    def test_anything_else_is_not_adopted(self):
        from machinome.expression_graph import ExpressionNode, symbol
        for value in (1.0, 'x', symbol('$t'), ExpressionNode('name', text='a')):
            with self.subTest(type(value).__name__):
                self.assertIsNone(self.engine.adopt(value))


class BinaryTest(TestCase):

    def test_the_binary_module_imports_no_solidpython(self):
        tree = ast.parse((ROOT / 'machinome/openscad/binary.py').read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split('.')[0]
                                for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split('.')[0])
        self.assertNotIn('solid2', imported)

    def test_the_binary_contract_refuses_unchanged(self):
        binary = importlib.import_module('machinome.openscad.binary')
        binary.openscad_binary.cache_clear()
        self.addCleanup(binary.openscad_binary.cache_clear)
        with patch('machinome.openscad.binary.shutil.which',
                   return_value=None):
            with self.assertRaises(binary.OpenScadUnavailable) as raised:
                binary.require_openscad(
                    'node housing (FacetedBox)',
                    'its STL is rendered from SCAD by OpenSCAD')
        self.assertEqual(
            str(raised.exception),
            'node housing (FacetedBox) requires the OpenSCAD binary because '
            'its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and '
            "ensure 'openscad' is on PATH")
