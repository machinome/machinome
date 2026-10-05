# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The verdict store across real `machinome test` processes.

The finding is a process boundary: the studio floor starts a fresh
`machinome test` for every run, so the ADR-070 memo was always cold --
1348.9 s for `wall_clock_02` where 18.35 s was the warm floor, 246.9 s for
strandbeest where 11.97 s was (`workflow/warts.md`, 2026-09-29). These
tests therefore run the real CLI in child processes, on a small project of
two exact parts and one faceted STL part swept over three instants, and
prove by COUNT (tests/verdict_probe.py), never by timing: the first run
computes N verdicts, the second computes none and is served N.

The framework suite pins `SOLID_TEST_VERDICT_STORE=off`; every child here
overrides it with `on`, except where the run under test is the one that
switches the store off.
"""

import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from unittest import TestCase

import trimesh
from trimesh.creation import box

from . import mesh_engine_absent
from .verdict_probe import PROBE, counts


BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)

ANSI = re.compile(r'\x1b\[[0-9;]*m')
TIMING = re.compile(r'(Ran \d+ tests in )[\d.]+( seconds)')
RESULT = re.compile(r'^Running \S+?\.(?P<name>test_\w+)', re.MULTILINE)

MANIFEST = '''\
[tool.machinome]
model = "vfixture.machine:Machine"
'''

MACHINE = '''\
import cadquery as cq

from machinome.node import AssemblyNode, CadQueryNode, StlNode


class Block(CadQueryNode):
    """A block bored through: the pin runs in the bore with 1 mm of
    radial clearance, so their boxes overlap and their solids do not."""

    def render(self):
        return cq.Workplane('XY').box(10, 10, 10).faces('>Z').workplane() \\
            .hole(6)


class Pin(CadQueryNode):

    def render(self):
        return cq.Workplane('XY').circle(2).extrude(20)


class Plate(StlNode):
    """The faceted part: a committed mesh, flush under the block."""

    stl_source = 'plate.stl'


class Machine(AssemblyNode):

    def __init__(self):
        self.block = Block()
        self.pin = Pin()
        self.plate = Plate()
        super().__init__()
        self.plate.translate([0, 0, -6])

    def render(self):
        self.pin.translate([0, 0, -4 + 2 * self.time])
        return [self.block, self.pin, self.plate]
'''

COMPANION = '''\
from machinome.test import TestCase, testing_steps

from .machine import Machine


class MachineTest(TestCase):
    node = Machine

    @testing_steps(3)
    def test_no_solid_interference(self):
        self.assertNoSolidInterference(self.node)

    @testing_steps(3)
    def test_the_pin_clears_the_bore(self):
        self.assertNotIntersecting(self.node.pin, self.node.block)

    def test_the_plate_is_clear_of_the_block(self):
        # Flush contact: non-empty at exactly 0.0 mm3, a foul at the
        # strict default. This test fails on purpose.
        self.assertNotIntersecting(self.node.block, self.node.plate)
'''


def write_fixture(project):
    package = os.path.join(project, 'vfixture')
    os.makedirs(package)
    with open(os.path.join(project, 'pyproject.toml'), 'w') as handle:
        handle.write(MANIFEST)
    open(os.path.join(package, '__init__.py'), 'w').close()
    with open(os.path.join(package, 'machine.py'), 'w') as handle:
        handle.write(MACHINE)
    with open(os.path.join(package, 'test_machine.py'), 'w') as handle:
        handle.write(COMPANION)
    box((20, 20, 2)).export(os.path.join(package, 'plate.stl'))


class ChildRun:
    """One probed `machinome test` child: streams, counts, results."""

    def __init__(self, completed):
        self.returncode = completed.returncode
        self.stdout = ANSI.sub('', completed.stdout)
        self.stderr = completed.stderr
        self.counts = (counts(self.stderr)
                       if completed.returncode != -signal.SIGKILL else None)
        self.results = {}
        for line in self.stdout.splitlines():
            match = RESULT.match(line)
            if match:
                self.results[match.group('name')] = (
                    'failed' if 'FAIL!' in line else 'passed')

    @property
    def untimed_stdout(self):
        return TIMING.sub(r'\1<time>\2', self.stdout)

    @property
    def summary(self):
        lines = [line for line in self.stdout.splitlines()
                 if line.startswith('Ran ')]
        assert len(lines) == 1, self.stdout
        return lines[0]

    @property
    def failures(self):
        """Every failing assertion's message, volumes included."""
        return sorted(line for line in self.stdout.splitlines()
                      if line.startswith('AssertionError'))


def run(project, *arguments, store='on', env=None, prefix=''):
    environment = dict(os.environ, PYTHONPATH=REPO_DIR)
    environment.pop('SOLID_BUILD_DIR', None)
    if store is not None:
        environment['SOLID_TEST_VERDICT_STORE'] = store
    environment.update(env or {})
    return ChildRun(subprocess.run(
        [sys.executable, '-c', prefix + PROBE, 'test', *arguments],
        cwd=project, env=environment, capture_output=True, text=True,
        timeout=600))


def listing(directory):
    return {name: os.stat(os.path.join(directory, name)).st_mtime_ns
            for name in os.listdir(directory)}


class AcrossProcesses(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.template_root = tempfile.mkdtemp(prefix='machinome-verdict-cli-')
        cls.template = os.path.join(cls.template_root, 'project')
        write_fixture(cls.template)
        # Build once, with the store off, so every test starts from a
        # current build and a run's stdout is the test run's alone.
        cls.baseline = run(cls.template, store='off')
        assert cls.baseline.results, cls.baseline.stdout + cls.baseline.stderr
        assert not os.path.exists(os.path.join(
            cls.template, '_build', '.verdicts'))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.template_root, ignore_errors=True)

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix='machinome-verdict-cli-')
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self.project = os.path.join(self.scratch, 'project')
        shutil.copytree(self.template, self.project)
        self.store = os.path.join(self.project, '_build', '.verdicts')

    def assertSameVerdicts(self, one, other):
        self.assertEqual(one.results, other.results)
        self.assertEqual(one.failures, other.failures)
        self.assertEqual(one.returncode, other.returncode)

    def test_a_second_process_is_served_every_verdict(self):
        """Task 6.1."""
        first = run(self.project)
        second = run(self.project)

        computed = first.counts['computations']
        self.assertGreater(computed, 0, first.stderr)
        self.assertEqual(first.counts['store_hits'], 0)
        self.assertEqual(second.counts['computations'], 0,
                         'the second process recomputed a kept verdict')
        self.assertEqual(second.counts['store_hits'], computed)
        self.assertEqual(second.untimed_stdout, first.untimed_stdout)
        self.assertSameVerdicts(second, self.baseline)
        self.assertEqual(self.baseline.results[
            'test_the_plate_is_clear_of_the_block'], 'failed',
            'the flush-contact test no longer fails; the fixture changed')

    def test_a_tampered_artifact_recomputes_exactly_its_pairs(self):
        """Task 6.2: new bytes under the old mtime."""
        first = run(self.project)
        plate_pairs = [pair for pair in first.counts['computed_pairs']
                       if any(name and 'Plate' in name for name in pair)]
        self.assertTrue(plate_pairs, first.counts['computed_pairs'])

        artifacts = [os.path.join(folder, name)
                     for folder, _, names in os.walk(
                         os.path.join(self.project, '_build'))
                     for name in names
                     if 'Plate' in name and name.endswith('.stl')]
        self.assertEqual(len(artifacts), 1, artifacts)
        (artifact,) = artifacts
        tampered = trimesh.load(artifact)
        tampered.apply_translation([0, 0, 0.5])
        before = os.stat(artifact)
        replacement = os.path.join(self.scratch, 'tampered.stl')
        tampered.export(replacement)
        self.assertEqual(os.path.getsize(replacement), before.st_size)
        os.replace(replacement, artifact)
        os.utime(artifact, ns=(before.st_atime_ns, before.st_mtime_ns))

        second = run(self.project)
        oracle = run(self.project, '--no-verdict-store')

        self.assertEqual(sorted(sorted(pair)
                                for pair in second.counts['computed_pairs']),
                         sorted(sorted(pair) for pair in plate_pairs),
                         'the run did not recompute exactly the pairs '
                         'involving the tampered artifact')
        self.assertSameVerdicts(second, oracle)
        self.assertNotEqual(second.failures, first.failures,
                            'the tampered geometry changed no verdict; '
                            'this proves nothing')

    def test_a_moved_project_is_served(self):
        """Task 6.3: the project and its build directory move together."""
        first = run(self.project)
        moved = os.path.join(self.scratch, 'moved', 'project')
        os.makedirs(os.path.dirname(moved))
        os.rename(self.project, moved)

        second = run(moved)

        self.assertGreater(first.counts['computations'], 0)
        self.assertEqual(second.counts['computations'], 0,
                         'the moved project recomputed a kept verdict')
        self.assertEqual(second.results, first.results)

    def test_a_run_without_the_store_computes_and_leaves_it_alone(self):
        """Task 6.4."""
        first = run(self.project)
        before = listing(self.store)
        third = run(self.project, '--no-verdict-store')

        self.assertEqual(third.counts['computations'],
                         first.counts['computations'])
        self.assertEqual(third.counts['store_hits'], 0)
        self.assertEqual(listing(self.store), before)
        self.assertTrue(third.summary.endswith('(verdict store off)'),
                        third.summary)
        self.assertFalse(first.summary.endswith(')'), first.summary)
        self.assertSameVerdicts(third, first)

    def test_a_killed_run_leaves_a_readable_store(self):
        """Task 6.5: SIGKILL right after the first segment is published."""
        killed = run(self.project,
                     env={'VERDICT_PROBE_KILL_AFTER_FLUSH': '1'})
        self.assertEqual(killed.returncode, -signal.SIGKILL, killed.stderr)
        self.assertTrue(os.listdir(self.store))

        after = run(self.project)

        self.assertNotIn('Traceback', after.stderr)
        self.assertGreater(after.counts['store_hits'], 0)
        self.assertSameVerdicts(after, self.baseline)


class WithoutTheMeshEngine(TestCase):
    """Task 6.6: an all-exact project keeps its store where neither
    `manifold3d` nor the mesh engine's package `machinome.engine.mesh` can be
    imported (the finder of `tests/mesh_engine_absent.py`, in every
    process of both runs), and neither run asks for the engine."""

    def test_an_all_exact_fixture_is_served_on_its_second_run(self):
        build_dir = tempfile.mkdtemp(prefix='machinome-verdict-exact-')
        self.addCleanup(shutil.rmtree, build_dir, ignore_errors=True)
        reference = 'tests/meta_project/exact_clearance.py'

        with mesh_engine_absent.finder() as finder:
            env = dict(finder.environment, SOLID_BUILD_DIR=build_dir)
            first = run(REPO_DIR, reference, env=env)
            first_reports = finder.run(first)
            second = run(REPO_DIR, reference, env=env)
            second_reports = finder.run(second)

        for child, reports in ((first, first_reports),
                               (second, second_reports)):
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertNotIn('manifold3d', child.stdout)
            self.assertEqual(reports.asks('machinome.engine.mesh'), 0)
            self.assertLessEqual(reports.askers('manifold3d'),
                                 mesh_engine_absent.TRIMESH_PROBES)
        self.assertGreater(first.counts['computations'], 0)
        self.assertEqual(second.counts['computations'], 0)
        self.assertEqual(second.counts['store_hits'],
                         first.counts['computations'])
        self.assertEqual(second.results, first.results)
