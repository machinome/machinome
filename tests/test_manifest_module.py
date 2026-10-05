# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`machinome.manifest`: what a manifest declares, without the geometry
stack.

OpenSpec change ``vet-the-project`` (design D1). `machinome vet` and the
source adapters' containment check need a project's root and its models,
and nothing that `machinome.core.loader` drags in with it: the node base,
numpy and its family. So manifest discovery and the validated model
declaration move into a top-level module, and the loader re-exports every
name it moved, so every existing importer keeps receiving the same
objects.
"""

import os
import shutil
import tempfile
from unittest import TestCase

from .import_probe import probe


def write(root, text):
    with open(os.path.join(root, 'pyproject.toml'), 'w') as manifest:
        manifest.write(text)
    return os.path.join(root, 'pyproject.toml')


class TheManifestModuleIsLightTest(TestCase):
    """(2.1) Importing it loads no node module and no kernel."""

    def test_importing_the_manifest_module_loads_no_geometry_stack(self):
        result = probe('import machinome.manifest\n').check()

        self.assertTrue(result.imported('machinome.manifest'))
        for heavy in ('machinome.core', 'machinome.node', 'numpy',
                      'trimesh', 'cadquery', 'OCP'):
            with self.subTest(module=heavy):
                self.assertFalse(result.imported(heavy), heavy)


class TheLoaderReexportsTest(TestCase):
    """(2.2) The loader's names are the manifest module's objects."""

    def test_the_moved_names_are_the_same_objects(self):
        from machinome import manifest
        from machinome.core import loader

        for name in ('ProjectManifestError', 'MODEL_NAME', 'project_root',
                     '_find_manifest'):
            with self.subTest(name=name):
                self.assertIs(getattr(loader, name), getattr(manifest, name))

    def test_a_manifest_module_error_is_caught_as_the_loaders(self):
        from machinome import manifest
        from machinome.core import loader

        root = tempfile.mkdtemp(prefix='machinome-manifest-')
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        write(root, '[tool.machinome]\n')

        try:
            manifest.read_declaration(root)
        except loader.ProjectManifestError as error:
            self.assertIn('no model reference', str(error))
        else:
            self.fail('read_declaration admitted a manifest with no model')


class ReadDeclarationTest(TestCase):
    """(2.3) The declaration, and every refusal `read_project` makes."""

    def setUp(self):
        self.root = os.path.realpath(
            tempfile.mkdtemp(prefix='machinome-manifest-'))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def declaration(self):
        from machinome.manifest import read_declaration
        return read_declaration(self.root)

    def test_a_single_model_manifest(self):
        manifest = write(self.root,
                         '[tool.machinome]\nmodel = "sim.clock:Clock"\n')

        declared = self.declaration()

        self.assertEqual(declared.root, self.root)
        self.assertEqual(declared.manifest, manifest)
        self.assertEqual(declared.models, ((None, 'sim.clock:Clock'),))
        self.assertIsNone(declared.default)
        self.assertFalse(declared.named)

    def test_a_named_models_manifest_keeps_declaration_order(self):
        write(self.root,
              '[tool.machinome]\nmodel = "b_clock"\n'
              '[tool.machinome.models]\n'
              'b_clock = "sim.b:B"\n'
              'a_clock = "sim.a:A"\n')

        declared = self.declaration()

        self.assertEqual(declared.models,
                         (('b_clock', 'sim.b:B'), ('a_clock', 'sim.a:A')))
        self.assertEqual(declared.default, 'b_clock')
        self.assertTrue(declared.named)

    def test_named_models_without_a_default(self):
        write(self.root, '[tool.machinome.models]\nclock = "sim.c:C"\n')

        declared = self.declaration()

        self.assertIsNone(declared.default)
        self.assertTrue(declared.named)

    def test_the_declaration_is_found_from_a_nested_directory(self):
        write(self.root, '[tool.machinome]\nmodel = "sim.clock:Clock"\n')
        nested = os.path.join(self.root, 'sim', 'deep')
        os.makedirs(nested)
        from machinome.manifest import read_declaration

        self.assertEqual(read_declaration(nested).root, self.root)

    def assertRefusedAlike(self, text, expected):
        """The manifest module refuses with exactly the message the
        loader's `read_project` gave before the move, and `read_project`
        still gives it."""
        from machinome.core.loader import read_project
        from machinome.manifest import ProjectManifestError
        manifest = write(self.root, text)
        expected = expected.format(manifest=manifest, root=self.root)

        with self.assertRaises(ProjectManifestError) as declared:
            self.declaration()
        with self.assertRaises(ProjectManifestError) as project:
            read_project(self.root)

        self.assertEqual(str(declared.exception), expected)
        self.assertEqual(str(project.exception), expected)

    def test_a_bad_name_is_refused(self):
        self.assertRefusedAlike(
            '[tool.machinome.models]\n"design.c" = "sim.c:C"\n',
            "{manifest} declares the model name 'design.c'; a name is one "
            "word of letters, digits, underscores and hyphens")

    def test_a_reference_without_a_colon_is_refused(self):
        self.assertRefusedAlike(
            '[tool.machinome.models]\nclock = "sim.c"\n',
            "{manifest} declares model 'clock' as 'sim.c'; a model is a "
            "reference of the form package.module:Class")

    def test_a_name_colliding_with_a_root_directory_is_refused(self):
        os.makedirs(os.path.join(self.root, 'docs'))
        self.assertRefusedAlike(
            '[tool.machinome.models]\ndocs = "sim.c:C"\n',
            "{manifest} declares a model named 'docs', but docs/ is a "
            "directory at the project root and its artifacts would mirror "
            "into the model's build directory; rename the model")

    def test_an_unknown_default_is_refused(self):
        self.assertRefusedAlike(
            '[tool.machinome]\nmodel = "c_clock"\n'
            '[tool.machinome.models]\na_clock = "sim.a:A"\n'
            'b_clock = "sim.b:B"\n',
            "{manifest} sets model = 'c_clock', which must name one of the "
            "declared models: a_clock, b_clock")

    def test_an_empty_table_is_refused(self):
        self.assertRefusedAlike(
            '[tool.machinome]\n[tool.machinome.models]\n',
            "{manifest} declares [tool.machinome.models] with no models")

    def test_a_missing_model_is_refused(self):
        self.assertRefusedAlike(
            '[tool.machinome]\n',
            "{manifest} has [tool.machinome] but no model reference")

    def test_the_old_tool_table_is_refused(self):
        self.assertRefusedAlike(
            '[tool.solid-node]\nmodel = "sim.c:C"\n',
            "{manifest} uses [tool.solid-node]; Machinome 0.7 uses "
            "[tool.machinome] (and [tool.machinome.models])")
