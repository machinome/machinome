# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A project reached through a symbolic link builds in its own build root.

OpenSpec change ``sim-through-a-symlink``. Videomaker filmed the clocked
Curta by recording a take through the public `Sim`; in the workspace
`projects/` is a symbolic link to `/mnt/data/machinome-projects`, and
`Sim(ClockedCurta())` run from the symlinked path, with that path on
`PYTHONPATH`, raised ``PermissionError: [Errno 13] Permission denied:
'/mnt/home'``. The project root is discovered as a resolved path; the
node's source file was the module's ``__file__`` as imported, through the
link; the build directory was measured from one to the other and climbed
out of the build root.

The fixture is a real project in a directory each test owns, a symbolic
link to it beside it, and a class imported through each spelling. With
the link beside the project, the wrong directory is writable -- it lands
inside the project, outside its build root -- so the proof is where the
build directory is, not whether construction raised.
"""

import importlib
import itertools
import os
import shutil
import sys
import tempfile
from contextlib import chdir
from unittest import TestCase
from unittest.mock import patch

from machinome.core.builder import unanchor_build_dir
from machinome.simulation import Sim


PACKAGES = itertools.count()

ARBOR = '''\
from solid2 import cylinder

from machinome.motion.joints import Revolute
from machinome.node import Solid2Node


class Arbor(Solid2Node):

    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cylinder(r=10, h=4)
'''

MACHINE = '''\
from machinome.node import AssemblyNode
from machinome.simulation import Driver

from .parts.arbor import Arbor


class Machine(AssemblyNode):
    crank = Driver(default=0)
    arbor = Arbor()
    crank.drives(arbor.turn)
'''


class ProjectThroughASymlinkTest(TestCase):
    """One project, two spellings: `<base>/real` and `<base>/link`."""

    def setUp(self):
        # The build root a Python caller gets in a project: the default
        # `_build` under the discovered root, with no command's selection
        # anchored and no suite-wide absolute SOLID_BUILD_DIR.
        environment = patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop('SOLID_BUILD_DIR', None)
        unanchor_build_dir()
        self.addCleanup(unanchor_build_dir)

        self.base = os.path.realpath(
            tempfile.mkdtemp(prefix='machinome-symlinked-'))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.real = os.path.join(self.base, 'real')
        self.link = os.path.join(self.base, 'link')
        self.build_root = os.path.join(self.real, '_build')

        self.package = f'symlinked_fixture_{next(PACKAGES)}'
        self.addCleanup(self.forget_package)
        package_dir = os.path.join(self.real, self.package)
        os.makedirs(os.path.join(package_dir, 'parts'))
        for relative, content in (
                ('__init__.py', ''),
                ('machine.py', MACHINE),
                (os.path.join('parts', '__init__.py'), ''),
                (os.path.join('parts', 'arbor.py'), ARBOR)):
            with open(os.path.join(package_dir, relative), 'w') as source:
                source.write(content)
        with open(os.path.join(self.real, 'pyproject.toml'), 'w') as manifest:
            manifest.write('[tool.machinome]\n'
                           f'model = "{self.package}.machine:Machine"\n')
        os.symlink(self.real, self.link)

        saved_path = list(sys.path)
        self.addCleanup(sys.path.__setitem__, slice(None), saved_path)

    def forget_package(self):
        for name in list(sys.modules):
            if name == self.package or name.startswith(self.package + '.'):
                del sys.modules[name]

    def machine_through(self, spelling):
        """The fixture's `Machine` class, imported with `spelling` -- the
        link or the real path -- on `sys.path`, as `PYTHONPATH=<spelling>`
        puts it there."""
        self.forget_package()
        sys.path[:] = [entry for entry in sys.path
                       if entry not in (self.real, self.link)]
        sys.path.insert(0, spelling)
        importlib.invalidate_caches()
        module = importlib.import_module(f'{self.package}.machine')
        # The precondition of the finding: the module really was imported
        # through this spelling, not resolved by the import system.
        self.assertTrue(
            module.__file__.startswith(spelling + os.sep),
            f'{module.__file__} was not imported through {spelling}')
        return module.Machine

    def assertUnderBuildRoot(self, node):
        self.assertEqual(
            os.path.commonpath((node.build_dir, self.build_root)),
            self.build_root,
            f'{type(node).__name__} builds in {node.build_dir}, outside the '
            f'project build root {self.build_root}')

    def test_sim_through_the_link_builds_under_the_build_root(self):
        Machine = self.machine_through(self.link)
        with chdir(self.link):
            node = Machine()
            sim = Sim(node, 0.1)
        self.assertEqual(sorted(sim.state), ['crank'])
        for built in (node, node.arbor):
            self.assertUnderBuildRoot(built)
        self.assertEqual(
            node.build_dir, os.path.join(self.build_root, self.package))
        self.assertEqual(
            node.arbor.build_dir,
            os.path.join(self.build_root, self.package, 'parts'))
        # Nothing appeared beside the project's sources but its build root,
        # and nothing beside the project and its link.
        self.assertEqual(sorted(os.listdir(self.real)),
                         sorted(['_build', 'pyproject.toml', self.package]))
        self.assertEqual(sorted(os.listdir(self.base)), ['link', 'real'])

    def test_both_spellings_share_one_build_directory(self):
        Linked = self.machine_through(self.link)
        with chdir(self.link):
            linked = Linked()
        Real = self.machine_through(self.real)
        with chdir(self.real):
            real = Real()
        self.assertIsNot(Linked, Real)
        for through_link, through_real in ((linked, real),
                                           (linked.arbor, real.arbor)):
            self.assertEqual(through_link.build_dir, through_real.build_dir)
            self.assertEqual(through_link.stl_file, through_real.stl_file)
            self.assertEqual(through_link.scad_file, through_real.scad_file)
            self.assertEqual(through_link.src, through_real.src)
