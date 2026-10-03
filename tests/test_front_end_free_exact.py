# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Exact geometry needs no CAD front end (OpenSpec change `exact-engine`,
capability `exact-geometry`).

`tests/meta_project/occt_only.py` stands in for machinome-freecad's exact
leaf: its leaves render a bare `TopoDS_Shape`, one read from BREP bytes
with `BRepTools.Read_s` exactly as that adapter reads its transfer. The
project is built, fused exactly and tested in a fresh interpreter, which
must never import cadquery or build123d.
"""

import glob
import os
import shutil
import tempfile
from unittest import TestCase

from .exact_engine_absent import run_machinome


class FrontEndFreeProjectTest(TestCase):

    def setUp(self):
        self.build_dir = tempfile.mkdtemp(prefix='occt-only-build-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)

    def artifacts(self, node, suffix):
        return glob.glob(os.path.join(
            self.build_dir, '**', f'occt_only-{node}-*{suffix}'),
            recursive=True)

    def test_a_kernel_only_project_builds_fuses_and_tests_exactly(self):
        run = run_machinome('test', 'tests/meta_project/occt_only.py',
                            blocked=False, build_dir=self.build_dir)

        self.assertIn('2 passed, 0 failed', run.stdout, run.output)
        self.assertEqual(run.returncode, 0, run.output)
        for node in ('PinnedBlock', 'Probe', 'Far'):
            for suffix in ('.brep', '.stl'):
                with self.subTest(node=node, suffix=suffix):
                    self.assertEqual(len(self.artifacts(node, suffix)), 1)
        for node in ('Block', 'Pin'):
            with self.subTest(node=node):
                self.assertEqual(len(self.artifacts(node, '.brep')), 1)
        self.assertEqual(run.exact_stack & {'cadquery', 'build123d'}, set())
        self.assertIn('machinome.occt.engine', run.exact_stack)
