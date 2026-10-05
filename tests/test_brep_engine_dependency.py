# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The exact engine is resolved only by the paths that use it (OpenSpec
change `exact-engine`, capabilities `exact-engine-dependency` and
`cli-startup-cost`).

Every test here runs the framework in fresh subprocesses, with the engine
genuinely absent where a test says so (see tests/brep_engine_absent.py):
importing the framework loads no engine, a faceted project runs without
it, a stale exact fusion is refused naming the install, and a current one
is reused without asking for the engine at all.
"""

import glob
import os
import re
import shutil
import tempfile
from unittest import TestCase

from .brep_engine_absent import run_machinome, run_python


EXACT_STACK = {'machinome.engine.brep', 'OCP', 'cadquery'}
FUSION = 'tests/meta_project/exact_fusion_current.py:PinnedHub'
FACETED = 'tests/meta_project/separated.py'


def _summary(output):
    """The `machinome test` run's counts: `(ran, passed, failed)`, or None."""
    counts = re.findall(r'Ran (\d+) tests in [0-9.]+ seconds: (\d+) passed, '
                        r'(\d+) failed', output)
    return counts[-1] if counts else None


class _BuildDirectory(TestCase):

    def setUp(self):
        self.build_dir = tempfile.mkdtemp(prefix='exact-engine-build-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)


class ImportLoadsNoEngineTest(TestCase):

    def test_importing_the_exact_path_loads_no_engine_or_kernel(self):
        run = run_python(
            'import machinome.node.fusion, machinome.node.brep_leaf\n'
            'import machinome.brep_cache, machinome.brep_artifacts\n'
            'import machinome.test\n'
            'print("IMPORTED")\n',
            blocked=False)

        self.assertIn('IMPORTED', run.stdout, run.stderr)
        self.assertEqual(run.exact_stack & EXACT_STACK, set(), run.stderr)


class FacetedProjectWithoutEngineTest(_BuildDirectory):

    def test_a_faceted_project_tests_the_same_without_the_engine(self):
        unblocked = run_machinome('test', FACETED, blocked=False,
                                  build_dir=self.build_dir)
        blocked = run_machinome('test', FACETED, build_dir=self.build_dir)

        self.assertIsNotNone(_summary(unblocked.stdout), unblocked.output)
        self.assertEqual(_summary(blocked.stdout), _summary(unblocked.stdout),
                         blocked.output)
        self.assertEqual(blocked.returncode, unblocked.returncode)
        self.assertEqual(blocked.engine_attempts, 0)
        self.assertEqual(blocked.exact_stack & EXACT_STACK, set())


class StaleFusionNamesTheInstallTest(_BuildDirectory):

    def test_building_a_stale_exact_fusion_without_the_engine_fails(self):
        run = run_machinome('build', FUSION, build_dir=self.build_dir)

        self.assertNotEqual(run.returncode, 0, run.output)
        self.assertIn('pip install "machinome[brep]"', run.output)
        self.assertIn('B-rep engine', run.output)
        self.assertGreater(run.engine_attempts, 0)


def _observations(build_dir):
    """`(inode, mtime_ns, ctime_ns)` of every `.brep` and `.stl`."""
    observed = {}
    for pattern in ('*.brep', '*.stl'):
        for path in glob.glob(os.path.join(build_dir, '**', pattern),
                              recursive=True):
            stat = os.stat(path)
            observed[os.path.relpath(path, build_dir)] = (
                stat.st_ino, stat.st_mtime_ns, stat.st_ctime_ns)
    return observed


class CurrentFusionDoesNotResolveTheEngineTest(_BuildDirectory):
    """A current exact fusion does not resolve the engine.

    The fixture's `Pin` declares `optimize = False`, so the builder prepares
    it on every build, current or not (design.md Decision 7). The fixture is
    built unblocked until its artifacts settle -- the first build's sweep
    removes the fused children's STLs, which the second build restores --
    and then once more in a fresh process with the engine absent.
    """

    def test_a_current_exact_fusion_is_reused_without_the_engine(self):
        for _ in range(2):
            settled = run_machinome('build', FUSION, blocked=False,
                                    build_dir=self.build_dir)
            self.assertEqual(settled.returncode, 0, settled.output)
        before = _observations(self.build_dir)
        names = {os.path.basename(path) for path in before}
        for node in ('PinnedHub', 'Hub', 'Pin'):
            for suffix in ('.brep', '.stl'):
                self.assertTrue(any(name.startswith(
                    f'exact_fusion_current-{node}-') and name.endswith(suffix)
                    for name in names), (node, suffix, sorted(names)))

        run = run_machinome('build', FUSION, build_dir=self.build_dir)

        self.assertEqual(run.returncode, 0, run.output)
        self.assertEqual(_observations(self.build_dir), before)
        self.assertEqual(run.engine_attempts, 0)
        self.assertNotIn('machinome.engine.brep', run.exact_stack)
