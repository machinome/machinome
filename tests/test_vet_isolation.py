# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""What vetting costs, and what it never touches.

OpenSpec change ``vet-the-project`` (design D2, D9). Vet reads a
project's bytes and the universe declaration, and nothing else: it
imports no kernel, no node module, no loader and no other command, it
never imports or runs a file of the project it vets, and it reads no
environment variable. What was imported is only observable in a process
that has not already imported it, so each run is a fresh interpreter
(`tests/import_probe.py`).
"""

import json
import os
import shutil
from unittest import TestCase
from unittest.mock import patch

from .import_probe import probe
from .vet_support import copy_fixture, fixture_root

DISPATCH = 'from machinome.cli import manage; manage()\n'

#: As in `tests/test_vet_command.py`: the installed script does not put
#: the working directory on `sys.path`, and neither does this probe.
SAFE_PATH = {'PYTHONSAFEPATH': '1'}

OTHER_COMMANDS = (
    'machinome.manager.build', 'machinome.manager.develop',
    'machinome.manager.test', 'machinome.manager.snapshot',
    'machinome.manager.new', 'machinome.manager.export',
    'machinome.manager.viewer', 'machinome.manager.models',
    'machinome.manager.import_step',
)


class CostTest(TestCase):
    """(8.1)"""

    def test_vetting_a_cadquery_model_loads_no_kernel_and_no_node(self):
        result = probe(DISPATCH, argv=['vet', '--tests'], env=SAFE_PATH,
                       cwd=fixture_root('pure_project')).check()

        self.assertTrue(result.imported('machinome.manager.vet'))
        self.assertTrue(result.imported('machinome.manifest'))
        for module in ('OCP', 'cadquery', 'numpy', 'trimesh',
                       'build123d', 'machinome.node', 'machinome.core',
                       'machinome.core.loader', *OTHER_COMMANDS):
            with self.subTest(module=module):
                self.assertFalse(result.imported(module), module)


class IsolationTest(TestCase):
    """(8.2)"""

    def test_a_module_with_a_side_effect_is_not_run(self):
        root = fixture_root('side_effect')
        marker = os.path.join(root, 'side_effect_fixture', 'marker')
        self.addCleanup(lambda: os.path.exists(marker) and os.remove(marker))

        result = probe(DISPATCH, argv=['vet', '--json'], env=SAFE_PATH,
                       cwd=root)

        # The model writes its marker at import time, which vet reports
        # as a finding and never lets happen.
        self.assertEqual(result.status, 1, result.stderr)
        self.assertEqual(
            {finding['kind'] for model in json.loads(result.stdout)['models']
             for finding in model['findings']}, {'file-write'})
        self.assertFalse(os.path.exists(marker))
        self.assertFalse(result.imported('side_effect_fixture'))


class EnvironmentTest(TestCase):
    """(8.3) The same tree gives the same JSON whatever the environment
    says."""

    def vet_json(self, root, env=None):
        result = probe(DISPATCH, argv=['vet', '--json', '--tests'],
                       env={**SAFE_PATH, **(env or {})}, cwd=root)
        self.assertEqual(result.status, 0, result.stderr)
        return result.stdout

    def test_the_build_directory_does_not_matter(self):
        root = fixture_root('pure_project')
        build = os.path.join(root, 'elsewhere-build')
        self.addCleanup(shutil.rmtree, build, ignore_errors=True)

        with patch.dict(os.environ):
            os.environ.pop('SOLID_BUILD_DIR', None)
            unset = self.vet_json(root)
            set_ = self.vet_json(root, {'SOLID_BUILD_DIR': build})

        self.assertEqual(unset, set_)
        self.assertFalse(os.path.exists(build))

    def test_a_dotenv_file_does_not_matter(self):
        _, root = copy_fixture(self, 'pure_project')
        absent = self.vet_json(root)
        with open(os.path.join(root, '.env'), 'w') as stream:
            stream.write('SOLID_BUILD_DIR=/nowhere\nMACHINOME_PORT=1\n')

        present = self.vet_json(root)

        self.assertEqual(absent, present)
