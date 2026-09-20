# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The tutorial's machine is real source, built and tested by the suite.

`docs/tutorial/` is a Machinome project whose manifest declares one named
model per chapter of the tutorial. Every chapter must build, and every
companion test a chapter writes must pass under `machinome test`, so a page
cannot describe a machine that no longer exists.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TUTORIAL = REPO / 'docs' / 'tutorial'


def machinome(*args, build_dir):
    env = dict(os.environ, SOLID_BUILD_DIR=str(build_dir),
               PYTHONPATH=str(REPO))
    env.pop('SOLID_TEST_KERNEL', None)
    return subprocess.run(
        [sys.executable, '-c', 'from machinome.cli import manage; manage()',
         *args],
        cwd=TUTORIAL, env=env, capture_output=True, text=True)


class TutorialCounterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.build_dir = Path(cls.tmp.name) / '_build'

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_project_is_there(self):
        self.assertTrue((TUTORIAL / 'pyproject.toml').is_file())
        self.assertTrue((TUTORIAL / 'counter' / 'digits.svg').is_file())

    def test_every_chapter_builds(self):
        result = machinome('build', '--all', build_dir=self.build_dir)
        self.assertEqual(result.returncode, 0,
                         result.stdout[-3000:] + result.stderr[-3000:])

    def test_every_companion_test_passes(self):
        result = machinome('test', '--all', build_dir=self.build_dir)
        self.assertEqual(result.returncode, 0,
                         result.stdout[-3000:] + result.stderr[-3000:])
        self.assertIn('0 failed', result.stdout)


if __name__ == '__main__':
    unittest.main()
