# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The engine package, `machinome.engine` (OpenSpec change `brep-mesh`,
capability `kernel-extras`, design.md Decisions 2, 3 and 5).

The package's `__init__` holds both seams, the B-rep engine's and the mesh
engine's, under names that are not its providers' module names: resolving
`machinome.engine.brep` binds the provider module as the package's
attribute `brep`, and a seam function of that name would be replaced by it
at its first use. The providers are `machinome.engine.brep` and
`machinome.engine.mesh`; the package imports neither, exports no
operation, and extends its path with portions as `machinome.node` does.
The four former addresses are gone, with no alias. The memos and the
artifact publication are `machinome.brep_cache` and
`machinome.brep_artifacts`.
"""

import importlib
import os
import tempfile
from unittest import TestCase

from .import_probe import probe
from .test_leaf_addresses import import_after, write

#: The B-rep seam's names, design.md Decision 2's table.
BREP_SEAM = ('brep_engine', 'require_brep_engine', 'BrepEngineUnavailable',
             'BrepEngineIncompatible', 'BrepCommonInconsistency',
             'BrepCommonVerificationError', 'BREP_CONTRACT', 'BREP_PROVIDER',
             'BrepShape', 'BrepCurrency', 'BrepComposition', 'BrepComparison',
             'BrepEngine')

#: The mesh seam's names.
MESH_SEAM = ('mesh_engine', 'require_mesh_engine', 'MeshEngineUnavailable',
             'MeshEngineIncompatible', 'MESH_CONTRACT', 'MESH_PROVIDER',
             'MeshSolid', 'MeshSolids', 'MeshComposition', 'MeshComparison',
             'MeshIdentity', 'MeshEngine')

#: The former addresses, which import nothing.
FORMER = ('machinome.exact_engine', 'machinome.mesh_engine',
          'machinome.occt', 'machinome.manifold')


class TheSeamsTest(TestCase):

    def test_the_package_defines_both_seams(self):
        engine = importlib.import_module('machinome.engine')

        for name in BREP_SEAM + MESH_SEAM:
            with self.subTest(name=name):
                self.assertTrue(hasattr(engine, name), name)

    def test_the_contracts_and_the_providers(self):
        import machinome.engine as engine

        self.assertEqual(engine.BREP_CONTRACT, 2)
        self.assertEqual(engine.MESH_CONTRACT, 1)
        self.assertEqual(engine.BREP_PROVIDER, 'machinome.engine.brep')
        self.assertEqual(engine.MESH_PROVIDER, 'machinome.engine.mesh')

    def test_the_seams_survive_their_providers_resolution(self):
        import machinome.engine as engine
        engine.brep_engine.cache_clear()
        engine.mesh_engine.cache_clear()
        self.addCleanup(engine.brep_engine.cache_clear)
        self.addCleanup(engine.mesh_engine.cache_clear)

        brep = engine.brep_engine()
        mesh = engine.mesh_engine()

        self.assertEqual(brep.__name__, 'machinome.engine.brep')
        self.assertEqual(mesh.__name__, 'machinome.engine.mesh')
        self.assertTrue(callable(engine.brep_engine))
        self.assertTrue(callable(engine.mesh_engine))
        self.assertIs(engine.brep_engine(), brep)
        self.assertIs(engine.mesh_engine(), mesh)
        self.assertIs(engine.brep, brep)
        self.assertIs(engine.mesh, mesh)
        self.assertEqual(brep.CONTRACT, engine.BREP_CONTRACT)
        self.assertEqual(mesh.CONTRACT, engine.MESH_CONTRACT)

    def test_the_package_holds_no_operation(self):
        import machinome.engine as engine

        for name in ('intersect_shapes', 'intersect_solids', 'fuse_shapes',
                     'unite_solids', 'read_brep', 'solid_from_mesh'):
            with self.subTest(name=name):
                self.assertFalse(hasattr(engine, name), name)

    def test_importing_the_package_imports_no_provider_or_kernel(self):
        result = probe('import machinome.engine\n').check()

        for name in ('machinome.engine.brep', 'machinome.engine.mesh', 'OCP',
                     'manifold3d'):
            with self.subTest(name=name):
                self.assertFalse(result.imported(name), name)


class TheFormerAddressesTest(TestCase):

    def test_each_former_address_is_not_found(self):
        for name in FORMER + ('machinome.occt.engine',
                              'machinome.manifold.engine'):
            with self.subTest(name=name):
                with self.assertRaises(ModuleNotFoundError):
                    importlib.import_module(name)


class PortionTest(TestCase):
    """A distribution cut from the core installs a provider module under
    `machinome/engine/` without the package's `__init__.py`; a second copy
    of the core never resolves."""

    def setUp(self):
        scratch = tempfile.TemporaryDirectory(prefix='engine-portion-')
        self.addCleanup(scratch.cleanup)
        self.scratch = scratch.name

    def test_a_portion_resolves(self):
        write(self.scratch, 'machinome/engine/probe.py')

        imported = import_after(self.scratch, 'machinome.engine.probe')

        self.assertEqual(
            imported['machinome.engine.probe'],
            'OK ' + os.path.join(self.scratch, 'machinome/engine/probe.py'))

    def test_a_second_copy_of_the_core_is_refused(self):
        write(self.scratch, 'machinome/__init__.py')
        write(self.scratch, 'machinome/engine/__init__.py')
        write(self.scratch, 'machinome/engine/probe.py')

        imported = import_after(self.scratch, 'machinome.engine.probe')

        self.assertTrue(imported['machinome.engine.probe'].startswith(
            'FAILED'), imported['machinome.engine.probe'])


class TheMemosAndPublicationTest(TestCase):
    """design.md Decision 5: the memos and the publication are renamed in
    place, their functions unchanged."""

    def test_the_new_modules_import(self):
        cache = importlib.import_module('machinome.brep_cache')
        artifacts = importlib.import_module('machinome.brep_artifacts')

        for name in ('cached_shape', 'cached_bounding_box',
                     'cached_face_boxes', 'cached_placement',
                     'shape_identity', 'shape_load_observation',
                     '_reset_placement_cache'):
            with self.subTest(name=name):
                self.assertTrue(callable(getattr(cache, name)))
        for name in ('write_brep', 'write_stl', 'deflections',
                     '_atomic_export'):
            with self.subTest(name=name):
                self.assertTrue(callable(getattr(artifacts, name)))

    def test_the_former_modules_are_not_found(self):
        for name in ('machinome.exact_cache', 'machinome.exact_artifacts'):
            with self.subTest(name=name):
                with self.assertRaises(ModuleNotFoundError):
                    importlib.import_module(name)
