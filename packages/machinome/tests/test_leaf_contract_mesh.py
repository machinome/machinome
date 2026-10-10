# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A faceted leaf written outside the core, and the one call a leaf
publishes an artifact through (OpenSpec change `leaf-contract`, capability
`leaf-contract`).

`tests/contract_package/faceted_stand_in.py` produces its own STL from a
committed mesh using only declared members: `require_source_file`,
`get_source_file()`, the public `ExternalSourceIdentity` and
`publish_artifact`. Its project builds and tests with no CAD tool on the
PATH, and a second build in a fresh process does not produce the artifact
again.
"""

import glob
import os
import shutil
import subprocess
import sys
import tempfile
from unittest import TestCase
from unittest.mock import patch

from machinome import currency
from machinome._artifact import observe_artifact

BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)
CLI = 'from machinome.cli import manage; manage()'


def run_machinome(arguments, environment):
    """A `machinome` command in a fresh interpreter, under `environment`
    over this one's."""
    env = dict(os.environ, PYTHONPATH=REPO_DIR, **environment)
    return subprocess.run([sys.executable, '-c', CLI, *arguments],
                          cwd=REPO_DIR, env=env, capture_output=True,
                          text=True, timeout=600)


class FacetedStandInProjectTest(TestCase):

    def setUp(self):
        self.build_dir = tempfile.mkdtemp(prefix='leaf-contract-faceted-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)
        self.no_tools = tempfile.mkdtemp(prefix='leaf-contract-no-tools-')
        self.addCleanup(shutil.rmtree, self.no_tools, ignore_errors=True)
        self.log = os.path.join(self.build_dir, 'writes.log')

    def run_project(self):
        run = run_machinome(
            ['test', 'tests/contract_package/faceted_project.py'],
            {'SOLID_BUILD_DIR': self.build_dir, 'PATH': self.no_tools,
             'LEAF_CONTRACT_WRITE_LOG': self.log})
        self.assertIn('1 passed, 0 failed', run.stdout,
                      run.stdout + run.stderr)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        return run

    def writes(self):
        with open(self.log) as handle:
            return len(handle.readlines())

    def test_builds_without_a_cad_tool_and_reuses_its_artifact(self):
        self.run_project()
        stls = glob.glob(os.path.join(self.build_dir, '**', 'cube-*.stl'),
                         recursive=True)
        self.assertEqual(len(stls), 1)
        self.assertTrue(os.path.exists(currency.sidecar(stls[0])))
        self.assertIsNotNone(currency.recorded_digest(stls[0]))
        self.assertEqual(self.writes(), 1)

        self.run_project()
        self.assertEqual(self.writes(), 1)


class PublishArtifactTest(TestCase):
    """The four scenarios of "A leaf publishes an artifact through one
    call", on the faceted stand-in."""

    def setUp(self):
        self.build_dir = tempfile.mkdtemp(prefix='leaf-contract-publish-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)
        environment = patch.dict(os.environ,
                                 {'SOLID_BUILD_DIR': self.build_dir})
        environment.start()
        self.addCleanup(environment.stop)
        from tests.contract_package.faceted_project import Cube
        self.node = Cube()
        self.calls = []

    def write(self, content=b'solid cube\nendsolid cube\n'):
        def writer(temporary):
            self.calls.append(temporary)
            with open(temporary, 'wb') as handle:
                handle.write(content)
        return writer

    def leftovers(self):
        return [name for name in os.listdir(self.node.build_dir)
                if name.endswith('.tmp')]

    def test_a_stale_artifact_is_written_and_recorded(self):
        path = self.node.stl_file
        self.assertFalse(os.path.exists(path))

        published = self.node.publish_artifact(path, self.write())

        self.assertIs(published, True)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(os.path.dirname(self.calls[0]),
                         os.path.dirname(path))
        self.assertNotEqual(self.calls[0], path)
        self.assertEqual(os.stat(path).st_mtime_ns, self.node.mtime_ns)
        self.assertEqual(currency.recorded_digest(path),
                         self.node.source_digest)
        self.assertEqual(currency.recorded_fingerprint(path),
                         self.node.source_fingerprint)
        self.assertEqual(self.leftovers(), [])

    def test_a_current_artifact_is_not_rewritten(self):
        path = self.node.stl_file
        self.node.publish_artifact(path, self.write())
        before = observe_artifact(path)
        self.calls.clear()

        published = self.node.publish_artifact(path, self.write(b'other'))

        self.assertIs(published, False)
        self.assertEqual(self.calls, [])
        self.assertEqual(observe_artifact(path), before)

    def test_a_failing_writer_publishes_nothing(self):
        path = self.node.stl_file
        self.node.publish_artifact(path, self.write())
        with open(path, 'rb') as handle:
            artifact = handle.read()
        with open(currency.sidecar(path), 'rb') as handle:
            record = handle.read()
        # A recipe the artifact was not built under makes it stale, so the
        # writer is reached.
        self.node.source_recipe = 'a different native recipe'

        def failing(temporary):
            with open(temporary, 'wb') as handle:
                handle.write(b'half a mesh')
            raise RuntimeError('the writer failed')

        with self.assertRaisesRegex(RuntimeError, 'the writer failed'):
            self.node.publish_artifact(path, failing)

        with open(path, 'rb') as handle:
            self.assertEqual(handle.read(), artifact)
        with open(currency.sidecar(path), 'rb') as handle:
            self.assertEqual(handle.read(), record)
        self.assertEqual(self.leftovers(), [])

    def test_a_path_that_is_not_the_nodes_is_refused(self):
        elsewhere = os.path.join(self.build_dir, 'elsewhere.stl')

        with self.assertRaises(ValueError) as refused:
            self.node.publish_artifact(elsewhere, self.write())

        self.assertIn(self.node.name, str(refused.exception))
        self.assertIn(elsewhere, str(refused.exception))
        self.assertEqual(self.calls, [])
        self.assertFalse(os.path.exists(elsewhere))

    def test_assemble_presents_the_published_artifact(self):
        assembled = self.node.assemble()

        self.assertTrue(os.path.exists(self.node.stl_file))
        self.assertTrue(self.node._up_to_date(self.node.stl_file))
        self.assertIn(self.node.local_stl, str(assembled))
