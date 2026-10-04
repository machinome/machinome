# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The mesh engine is a conditional dependency of the faceted path, not a
blanket requirement of the assertion module (OpenSpec changes
`conditional-mesh-engine` and `mesh-engine`, capability
`mesh-engine-dependency`).

These tests run the framework in subprocesses where `manifold3d`, the
engine's package `machinome.manifold`, or both are genuinely unimportable,
or where `manifold3d` is found and broken (see tests/mesh_engine_absent.py).
They pin the two halves of the contract -- what keeps working without the
mesh engine, and what fails naming it and the extra that installs it --
and, through every process's exit report, that a path which does not need
the engine never asks for it.

Originating evidence: the browser-engine spike, "Upstream findings for
the framework" item 4 and evidence/fixture-host-verification.md run F; the
pilot's decision of 4 October 2026 making manifold3d the `manifold` extra.
"""

import glob
import os
import shutil
import tempfile
from unittest import TestCase, skipUnless

from .mesh_engine_absent import (TRIMESH_PROBES, mesh_engine_is_installed,
                                 run_machinome, run_python)
from .mesh_engine_fixture import write_fixture


BASEDIR = os.path.dirname(os.path.abspath(__file__))
META_BUILD_DIR = os.path.join(BASEDIR, '_build_meta')
HAVE_ENGINE = mesh_engine_is_installed()
INSTALL = 'pip install "machinome[manifold]"'
NEEDS_ENGINE = ('the absent-engine subprocess is only meaningful when this '
                'interpreter genuinely has the mesh engine to withhold')

#: design.md Decision 8's refusal, written out here.
FACETED_START_REFUSAL = (
    'Error: machinome test on the faceted kernel requires the mesh engine '
    "because every pair the run compares is compared on the parts' meshes; "
    'install it with \'pip install "machinome[manifold]"\'. Exact geometry '
    'does not need it: a model whose every compared part is exact is '
    'decided by the boundary-representation kernel')


class _NoAsksOfTheEngine:

    def assert_engine_never_asked(self, run):
        """No process asked for the engine's package; every ask of its
        kernel was one of trimesh's own probes at its import."""
        self.assertEqual(run.asks('machinome.manifold'), 0, run.output)
        self.assertLessEqual(run.askers('manifold3d'), TRIMESH_PROBES,
                             run.output)


@skipUnless(HAVE_ENGINE, NEEDS_ENGINE)
class AssertionModuleImportTest(_NoAsksOfTheEngine, TestCase):
    """Importing the assertions must not require the mesh engine: an
    all-exact project's assertions live in the same module and are
    decided entirely by the boundary-representation kernel."""

    def test_assertion_module_imports_without_the_mesh_engine(self):
        run = run_python(
            'import machinome.test\n'
            'print("IMPORTED", hasattr(machinome.test, "TestCase"))\n')

        self.assertIn('IMPORTED True', run.stdout, run.stderr)
        self.assertEqual(run.returncode, 0, run.stderr)

    def test_importing_does_not_resolve_the_mesh_engine(self):
        """Import must not merely succeed -- it must not have reached for
        the engine at all, or the dependency is still eager and only the
        error moved."""
        run = run_python('import machinome.test\n')

        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertNotIn('machinome.manifold.engine', run.imported)
        self.assert_engine_never_asked(run)
        self.assertEqual(run.askers('manifold3d'), TRIMESH_PROBES,
                         'trimesh asks for manifold3d at its own import')


@skipUnless(HAVE_ENGINE, NEEDS_ENGINE)
class ExactPathWithoutMeshEngineTest(_NoAsksOfTheEngine, TestCase):
    """An all-exact assembly is verified by the kernel, so it must reach
    the same verdict with no mesh engine installed at all, and never ask
    for it."""

    def test_exact_assembly_asserts_without_the_mesh_engine(self):
        run = run_machinome('test', 'tests/meta_project/exact_tight_fit.py',
                            build_dir=META_BUILD_DIR)

        self.assertIn('Ran 1 tests in', run.stdout, run.stderr)
        self.assertIn('1 passed, 0 failed', run.stdout, run.stderr)
        self.assertNotIn('manifold3d', run.stdout)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assert_engine_never_asked(run)

    def test_connectivity_asserts_without_the_mesh_engine(self):
        """`assertNoDisconnectedSolids` reads connected components from
        the cached base mesh for a faceted solid and from `solid_count`
        for an exact one -- neither needs the mesh engine."""
        run = run_machinome(
            'test', 'tests/meta_project/solid_integrity_green.py',
            build_dir=META_BUILD_DIR)

        self.assertIn('0 failed', run.stdout, run.stderr)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assert_engine_never_asked(run)


@skipUnless(HAVE_ENGINE, NEEDS_ENGINE)
class MissingMeshEngineIsActionableTest(TestCase):
    """A path that genuinely needs the engine fails naming it, the
    operation, and the extra that installs it -- never a bare import error
    and never a silently weaker verdict."""

    def assert_refused(self, fixture, needed_by, **blocking):
        run = run_machinome('test', f'tests/meta_project/{fixture}.py',
                            build_dir=META_BUILD_DIR, **blocking)

        self.assertIn('requires the mesh engine', run.stdout, run.output)
        self.assertIn(needed_by, run.stdout)
        self.assertIn(INSTALL, run.stdout)
        self.assertIn('0 passed, 1 failed', run.stdout)
        self.assertNotEqual(run.returncode, 0)
        self.assertNotIn('ModuleNotFoundError', run.output)
        return run

    def test_faceted_interference_names_the_missing_mesh_engine(self):
        self.assert_refused('assembly_integrity_contact',
                            'assertNoSolidInterference')

    def test_gravity_support_names_the_missing_mesh_engine(self):
        """ADR-049 extracts contact patches from meshed intersections
        for every body, exact solids included, so this assertion is a
        requiring path even for an all-exact assembly. It must say so
        rather than pass or fail obscurely."""
        self.assert_refused('assembly_supported_exact',
                            'assertAssemblySupported')

    def test_an_absent_kernel_under_a_present_engine_is_the_same_refusal(self):
        """The engine's package ships in every install, its kernel only
        with the `manifold` extra: an absent manifold3d is an absent
        engine."""
        self.assert_refused('assembly_integrity_contact',
                            'assertNoSolidInterference',
                            absent=('manifold3d',))

    def test_a_broken_kernel_reports_its_own_failure(self):
        run = run_machinome(
            'test', 'tests/meta_project/assembly_integrity_contact.py',
            build_dir=META_BUILD_DIR, blocked=False, broken=('manifold3d',))

        self.assertIn('broken manifold3d', run.stdout, run.output)
        self.assertNotIn('requires the mesh engine', run.output)
        self.assertNotEqual(run.returncode, 0)


@skipUnless(HAVE_ENGINE, NEEDS_ENGINE)
class FacetedRunRefusesAtItsStartTest(TestCase):
    """Every pair a faceted run compares is compared on meshes, so the run
    refuses before it builds anything, whichever way the kernel was
    chosen."""

    def setUp(self):
        self.build_dir = tempfile.mkdtemp(prefix='mesh-engine-faceted-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)

    def assert_refused_at_start(self, run):
        self.assertEqual(run.returncode, 1, run.output)
        self.assertIn(FACETED_START_REFUSAL, run.stderr.splitlines(),
                      run.output)
        self.assertNotIn('Comparing on the faceted kernel', run.stdout)
        self.assertEqual(glob.glob(os.path.join(self.build_dir, '**', '*.stl'),
                                   recursive=True), [])

    def test_the_faceted_flag_refuses_before_building(self):
        self.assert_refused_at_start(run_machinome(
            'test', '--faceted', 'tests/meta_project/flush.py',
            build_dir=self.build_dir))

    def test_the_faceted_environment_refuses_before_building(self):
        self.assert_refused_at_start(run_machinome(
            'test', 'tests/meta_project/flush.py', build_dir=self.build_dir,
            env={'SOLID_TEST_KERNEL': 'faceted'}))


@skipUnless(HAVE_ENGINE, NEEDS_ENGINE)
class BuildWithoutTheMeshEngineTest(_NoAsksOfTheEngine, TestCase):
    """Building needs the mesh engine only to union a stale faceted
    fusion: a project of imported meshes builds without it, and never
    asks for it."""

    def setUp(self):
        self.project = tempfile.mkdtemp(prefix='mesh-engine-project-')
        self.addCleanup(shutil.rmtree, self.project, ignore_errors=True)
        write_fixture(self.project)
        self.build_dir = os.path.join(self.project, 'build')

    def stls(self):
        return sorted(os.path.basename(path) for path in glob.glob(
            os.path.join(self.build_dir, '**', '*.stl'), recursive=True))

    def test_a_project_of_imported_meshes_builds_without_it(self):
        run = run_machinome('build', 'mfixture/parts.py:Shelf',
                            cwd=self.project, build_dir=self.build_dir)

        self.assertEqual(run.returncode, 0, run.output)
        built = self.stls()
        for part in ('Block', 'Bar'):
            self.assertTrue(any(name.startswith(f'{part.lower()}-')
                                for name in built), (part, built))
        self.assert_engine_never_asked(run)

    def test_a_stale_faceted_fusion_names_the_install(self):
        run = run_machinome('build', 'mfixture/parts.py:Fused',
                            cwd=self.project, build_dir=self.build_dir)

        self.assertNotEqual(run.returncode, 0, run.output)
        self.assertIn('faceted fusion Fused', run.output)
        self.assertIn('requires the mesh engine', run.output)
        self.assertIn(INSTALL, run.output)
