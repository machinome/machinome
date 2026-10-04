# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import os
from .base import BaseNodeTest
from . import flat_project
from machinome.node.openscad.writer import scad_file
from machinome.node.openscad.writer import generate_scad


class TwoPipesTest(BaseNodeTest):
    """Regression for B11: tests/flat_project/two_pipes.py used a bare
    (non-relative) import of its sibling module, and called
    .translate(100, 0, 0) with three arguments even though the API
    takes a single vector. Both bugs meant this example could never
    even be imported, let alone rendered."""

    def test_import(self):
        # Used to raise ModuleNotFoundError: No module named 'simple_pipe'.
        self.assertTrue(hasattr(flat_project, 'TwoPipes'))

    def test_render_returns_two_pipes(self):
        node = flat_project.TwoPipes()

        rendered = node.render()

        self.assertEqual(len(rendered), 2)
        for child in rendered:
            self.assertIsInstance(child, flat_project.SimplePipe)

    def test_translated_pipe_has_one_translation_operation(self):
        node = flat_project.TwoPipes()

        _, translated = node.render()

        self.assertEqual(len(translated.operations), 1)
        self.assertEqual(translated.operations[0].translation, [100, 0, 0])

    def test_assemble(self):
        node = flat_project.TwoPipes()

        assembled = node.assemble()

        self.assertIsNotNone(assembled)
        # assemble() writes no SCAD (`scad-presentation`); generate_scad()
        # writes the assembly's on demand.
        self.assertFalse(os.path.exists(scad_file(node)))
        generate_scad(node)
        self.assertTrue(os.path.exists(scad_file(node)))
