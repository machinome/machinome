# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD engine, the package `machinome.openscad` (OpenSpec changes
`expression-type` and `scad-presentation`, capability `openscad-engine`).

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
                     'openscad_binary', 'OpenScadUnavailable', 'scad_text',
                     'require_binary'):
            with self.subTest(name):
                self.assertFalse(hasattr(package, name))

    def test_the_provider_declares_contract_version_two(self):
        engine = importlib.import_module('machinome.openscad.engine')
        self.assertEqual(engine.CONTRACT, 2)


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


class ScadTextTest(TestCase):
    """(`scad-presentation`) The engine writes the SCAD text of the core's
    presentation description, exactly as SolidPython renders the calls the
    core used to make."""

    def setUp(self):
        self.engine = importlib.import_module('machinome.openscad.engine')
        self.p = importlib.import_module('machinome.node.presentation')

    def test_a_placed_coloured_import_is_solidpythons_rendering(self):
        from solid2 import color, import_stl, rotate, scad_render, translate
        p = self.p
        description = p.Rotate(30.0, [0, 0, 1], p.Translate(
            [1, 2.5, 0], p.Color((1.0, 0.5, 0.0), 1,
                                 p.ArtifactImport('a/b.stl'))))
        expected = scad_render(rotate(30.0, [0, 0, 1])(translate(
            [1, 2.5, 0])(color([1.0, 0.5, 0.0], 1)(import_stl('a/b.stl')))))
        self.assertEqual(self.engine.scad_text(description), expected)
        self.assertEqual(
            expected,
            'rotate(a = 30.0, v = [0, 0, 1]) {\n'
            '\ttranslate(v = [1, 2.5, 0]) {\n'
            '\t\tcolor(alpha = 1, c = [1.0, 0.5, 0.0]) {\n'
            '\t\t\timport(file = "a/b.stl", origin = [0, 0]);\n'
            '\t\t}\n\t}\n}\n')

    def test_a_symbolic_angle_is_written_as_its_closed_text(self):
        from machinome.expression_graph import get_animation_time
        p = self.p
        text = self.engine.scad_text(p.Rotate(
            get_animation_time() * 360, [0, 0, 1], p.ArtifactImport('a.stl')))
        self.assertIn('rotate(a = ($t * 360), v = [0, 0, 1])', text)

    def test_a_union_of_none_is_an_empty_union(self):
        self.assertEqual(self.engine.scad_text(self.p.Union(())),
                         'union();\n')

    def test_a_union_of_two_is_solidpythons(self):
        from solid2 import import_stl, scad_render, union
        p = self.p
        text = self.engine.scad_text(p.Union((p.ArtifactImport('a.stl'),
                                              p.ArtifactImport('b.stl'))))
        self.assertEqual(text, scad_render(union()(
            [import_stl('a.stl'), import_stl('b.stl')])))

    def test_fn_prefixes_the_text(self):
        text = self.engine.scad_text(self.p.ArtifactImport('a.stl'), fn=24)
        self.assertTrue(text.startswith('$fn = 24;\n\nimport(file = "a.stl"'),
                        text)

    def test_authored_geometry_is_written_as_authored(self):
        from solid2 import cube, import_stl, scad_render
        geometry = cube(1) + import_stl('vendor/external.stl')
        self.assertEqual(
            self.engine.scad_text(self.p.Authored(geometry)),
            scad_render(geometry))
        self.assertIn('import(file = "vendor/external.stl"',
                      self.engine.scad_text(self.p.Authored(geometry)))

    def test_require_binary_is_the_binary_contracts(self):
        binary = importlib.import_module('machinome.openscad.binary')
        binary.openscad_binary.cache_clear()
        self.addCleanup(binary.openscad_binary.cache_clear)
        with patch('machinome.openscad.binary.shutil.which',
                   return_value='/opt/openscad'):
            self.assertEqual(self.engine.require_binary('x', 'y'),
                             '/opt/openscad')
        binary.openscad_binary.cache_clear()
        with patch('machinome.openscad.binary.shutil.which',
                   return_value=None):
            with self.assertRaises(binary.OpenScadUnavailable):
                self.engine.require_binary('x', 'y', 'z')
