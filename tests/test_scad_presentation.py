# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The SCAD presentation is the OpenSCAD node family's (OpenSpec changes
`scad-presentation` and `openscad-out`, capabilities `openscad-node`,
`backend-neutral-materialization`, `build-pipeline` and `web-snapshot`).

The core describes a node's presentation in its own types
(`machinome.node.presentation`) and the family's writer writes the text; so
no module outside the family but the template imports SolidPython, and only
the OpenSCAD viewer reaches the family's package. `assemble()` composes that
description and writes no file, and needs neither SolidPython nor the
family. A `.scad` is written only where a path reads it: a family leaf's, for
OpenSCAD to render its STL, and the root's, on demand and transient, for the
OpenSCAD snapshot renderer, which removes it once drawn. A build sweeps every
other, and a transient one whatever its document did.

The tests of an absent SolidPython or family run in subprocesses under
`tests/brep_engine_absent.py`'s finder, once for each missing module.
"""

import argparse
import glob
import hashlib
import inspect
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, skipUnless
from unittest.mock import patch

from machinome import currency
from machinome.viewers.bundle import has_bundle
from tests.brep_engine_absent import run_machinome, run_python
from tests.test_expression_type import (core_modules, names_the_engine_package,
                                        solid2_imports)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = 'tests/scad_where_read_project'
STL_BENCH = f'{FIXTURE}/native.py:StlBench'
EXACT_BENCH = f'{FIXTURE}/native.py:ExactBench'
LEGACY_BENCH = f'{FIXTURE}/legacy.py:LegacyBench'
MACHINE = f'{FIXTURE}/machine.py:Machine'
MIXED = f'{FIXTURE}/machine.py:Mixed'
GOLDEN = ROOT / 'tests' / 'data' / 'scad_presentation_golden.json'

#: Each module whose absence is an absent OpenSCAD node family, and the
#: words of the install that provides it.
ABSENCES = {
    'solid2': 'pip install "machinome[openscad]"',
    'machinome.node.openscad': 'pip install "machinome[openscad]"',
}

#: The modules outside the OpenSCAD node family that import SolidPython:
#: the template that scaffolds a `Solid2Node`.
SOLID2_IMPORTERS = {
    'machinome/manager/templates/project/root/solid2.py',
}

#: The modules outside the family that reach its package: the OpenSCAD
#: viewer, until the viewer cycle.
ENGINE_REACHES = {
    'machinome/viewers/openscad.py',
}

#: What a build log would say if it presented or skipped SCAD.
SCAD_LOGGED = re.compile(r'\.scad\b|SCAD presentation|OpenSCAD engine')


def scad_files(build_dir):
    """Every `.scad` under `build_dir`, relative to it."""
    return sorted(os.path.relpath(path, build_dir) for path in glob.glob(
        os.path.join(build_dir, '**', '*.scad'), recursive=True))


def scad_records(build_dir):
    """Every currency record of a `.scad` under `build_dir`, relative."""
    return sorted(os.path.relpath(path, build_dir) for path in glob.glob(
        os.path.join(build_dir, '**', '*.scad*'), recursive=True)
        if not path.endswith('.scad'))


def observed(build_dir):
    """`(inode, mtime_ns)` of every `.scad`, by relative path."""
    return {relative: (os.stat(os.path.join(build_dir, relative)).st_ino,
                       os.stat(os.path.join(build_dir, relative)).st_mtime_ns)
            for relative in scad_files(build_dir)}


def golden_file_digest(basename):
    """The presentation golden's SHA-256 of the `.scad` named `basename`."""
    with open(GOLDEN) as handle:
        files = json.load(handle)['fixture']['files']
    return next(entry['sha256'] for path, entry in files.items()
                if os.path.basename(path) == basename)


class _BuildDirectory(TestCase):

    def setUp(self):
        self.build_dir = tempfile.mkdtemp(prefix='scad-presentation-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)
        environment = patch.dict(os.environ,
                                 {'SOLID_BUILD_DIR': self.build_dir})
        environment.start()
        self.addCleanup(environment.stop)

    def build(self, reference=MACHINE):
        run = run_machinome('build', reference, blocked=False,
                            build_dir=self.build_dir)
        self.assertEqual(run.returncode, 0, run.output)
        return run

    def machine(self):
        """The fixture's root, built in this process at the paths the
        build writes, and its parts by name."""
        from tests.scad_where_read_project.machine import Machine
        node = Machine()
        node._prepare()
        parts = {}

        def walk(each):
            parts[each.name] = each
            for child in each.children:
                walk(child)

        walk(node)
        return node, parts


# 2.1 ---------------------------------------------------------------------

class ImportersTest(TestCase):

    def test_the_solid2_importer_outside_the_family_is_the_template(self):
        importing = {path for path, tree in core_modules()
                     if any(True for _ in solid2_imports(tree))}
        self.assertEqual(importing, SOLID2_IMPORTERS)

    def test_only_the_viewer_reaches_the_familys_package(self):
        reaching = {path for path, tree in core_modules()
                    if names_the_engine_package(tree)}
        self.assertEqual(reaching, ENGINE_REACHES)


# 2.2, 2.3 ----------------------------------------------------------------

#: assemble(), build_stls() and mesh on the native fixtures, and what was
#: imported and written.
NATIVE_NODES = '''
import glob, json, os, sys
from tests.scad_where_read_project.native import ExactBench, StlBench
out = {}
for Root in (StlBench, ExactBench):
    node = Root()
    described = node.assemble()
    node.build_stls()
    out[Root.__name__] = {
        'module': type(described).__module__,
        'linked': [child._parent is node for child in node.children],
        'low': [round(value, 3) for value in
                node.children[1].mesh.bounds[0].tolist()],
    }
out['scad'] = glob.glob(os.path.join(os.environ['SOLID_BUILD_DIR'], '**',
                                     '*.scad'), recursive=True)
out['solid2'] = sorted(name for name in sys.modules
                       if name == 'solid2' or name.startswith('solid2.'))
print('RESULT', json.dumps(out))
'''

#: The SCAD text of an STL part, asked of the family's writer, directly and
#: through the table of supported node types.
REFUSALS = '''
import glob, os
from machinome.extras import ExtraUnavailable
from machinome.node import supported
from tests.scad_where_read_project.native import Bracket
node = Bracket(name='bracket')
node.assemble()
for attempt in ('table', 'writer'):
    try:
        if attempt == 'table':
            supported.load('openscad')
        else:
            from machinome.node.openscad import writer
            writer.scad_code(node)
        print('ANSWERED', attempt)
    except ImportError as error:
        print('REFUSED', attempt, type(error).__name__, error)
print('SCAD', len(glob.glob(os.path.join(os.environ['SOLID_BUILD_DIR'], '**',
                                         '*.scad'), recursive=True)))
'''

#: The OpenSCAD snapshot renderer, its runner and the loader patched.
SNAPSHOT = '''
import argparse, glob, os
from unittest.mock import patch
import machinome.manager.snapshot as module
parser = argparse.ArgumentParser()
parser.add_argument('path')
module.Snapshot().add_arguments(parser)
image = os.path.join(os.environ['SOLID_BUILD_DIR'], 'shot.png')
args = parser.parse_args([{reference!r}, '-o', image, '--imgsize', '64x48'])
with patch.object(module, 'run') as runner, \\
        patch.object(module, 'load_node') as loaded:
    try:
        module.Snapshot().handle(args)
        print('EXIT none')
    except SystemExit as error:
        print('EXIT', error.code)
print('RUN', runner.call_count, 'LOADED', loaded.call_count)
print('IMAGE', os.path.exists(image))
print('SCAD', len(glob.glob(os.path.join(os.environ['SOLID_BUILD_DIR'], '**',
                                         '*.scad'), recursive=True)))
'''


class WithoutTheEngineTest(_BuildDirectory):
    """No SolidPython, or no engine package: a native project builds,
    assembles and measures; asking for SCAD text is refused by name."""

    def assert_native_build(self, missing, reference):
        build_dir = tempfile.mkdtemp(prefix='scad-absent-build-')
        self.addCleanup(shutil.rmtree, build_dir, ignore_errors=True)
        run = run_machinome('build', reference, absent=(missing,),
                            build_dir=build_dir)
        self.assertEqual(run.returncode, 0, run.output)
        self.assertTrue(os.path.exists(os.path.join(build_dir,
                                                    'viewer.json')))
        stls = glob.glob(os.path.join(build_dir, '**', '*.stl'),
                         recursive=True)
        self.assertEqual(len(stls), 2, stls)
        if reference == EXACT_BENCH:
            breps = glob.glob(os.path.join(build_dir, '**', '*.brep'),
                              recursive=True)
            self.assertEqual(len(breps), 2, breps)
        self.assertEqual(scad_files(build_dir), [])
        self.assertIsNone(SCAD_LOGGED.search(run.output), run.output)

    def test_native_projects_build_without_each_module(self):
        for missing in ABSENCES:
            for reference in (STL_BENCH, EXACT_BENCH):
                with self.subTest(missing=missing, reference=reference):
                    self.assert_native_build(missing, reference)

    def test_assemble_build_stls_and_mesh_without_each_module(self):
        for missing in ABSENCES:
            with self.subTest(missing=missing):
                run = run_python(NATIVE_NODES, absent=(missing,),
                                 build_dir=self.build_dir)
                self.assertEqual(run.returncode, 0, run.output)
                line = next(line for line in run.stdout.splitlines()
                            if line.startswith('RESULT '))
                result = json.loads(line[len('RESULT '):])
                for root in ('StlBench', 'ExactBench'):
                    self.assertEqual(result[root]['module'],
                                     'machinome.node.presentation')
                    self.assertEqual(result[root]['linked'], [True, True])
                self.assertAlmostEqual(result['StlBench']['low'][0], 27.0)
                self.assertAlmostEqual(result['ExactBench']['low'][2], -7.0)
                self.assertEqual(result['scad'], [])
                self.assertEqual(result['solid2'], [])

    def test_scad_text_is_refused_naming_the_module_and_its_install(self):
        for missing, remedy in ABSENCES.items():
            with self.subTest(missing=missing):
                run = run_python(REFUSALS, absent=(missing,),
                                 build_dir=self.build_dir)
                self.assertEqual(run.returncode, 0, run.output)
                refused = [line for line in run.stdout.splitlines()
                           if line.startswith('REFUSED ')]
                self.assertEqual([line.split()[1] for line in refused],
                                 ['table', 'writer'], run.output)
                self.assertIn('REFUSED table ExtraUnavailable', refused[0])
                self.assertIn(missing, refused[0])
                self.assertIn(remedy, refused[0])
                self.assertIn(missing, refused[1])
                self.assertIn('SCAD 0', run.stdout.splitlines())

    def test_a_build_holding_a_legacy_scad_leaf_is_refused_by_name(self):
        """A project leaf overriding `as_scad`, the legacy SCAD-only seam,
        is handed to no tool since `openscad-out`: it produced no STL, and
        the build refuses it naming the node (R7)."""
        run = run_machinome('build', LEGACY_BENCH, blocked=False,
                            build_dir=self.build_dir)
        self.assertNotEqual(run.returncode, 0, run.output)
        self.assertIn('node bracket (Bracket) produced no STL: its '
                      'materialization published nothing at', run.output)
        self.assertEqual(scad_files(self.build_dir), [])

    def test_the_openscad_snapshot_renderer_is_refused_before_loading(self):
        for missing, remedy in ABSENCES.items():
            with self.subTest(missing=missing):
                build_dir = tempfile.mkdtemp(prefix='scad-absent-shot-')
                self.addCleanup(shutil.rmtree, build_dir, ignore_errors=True)
                run = run_python(SNAPSHOT.format(reference=STL_BENCH),
                                 absent=(missing,), build_dir=build_dir)
                self.assertEqual(run.returncode, 0, run.output)
                lines = run.stdout.splitlines()
                self.assertIn('EXIT 1', lines)
                self.assertIn('RUN 0 LOADED 0', lines)
                self.assertIn('IMAGE False', lines)
                self.assertIn('SCAD 0', lines)
                self.assertIn('machinome snapshot --renderer openscad needs '
                              'the openscad extra', run.stderr)
                self.assertIn(missing, run.stderr)
                self.assertIn(remedy, run.stderr)
                self.assertIn('--renderer web', run.stderr)


# 2.6 ---------------------------------------------------------------------

class DescriptionTest(_BuildDirectory):

    def presentation(self):
        import importlib
        return importlib.import_module('machinome.node.presentation')

    def test_the_module_holds_the_six_types(self):
        presentation = self.presentation()
        for name in ('ArtifactImport', 'Color', 'Rotate', 'Translate',
                     'Union', 'Authored'):
            with self.subTest(name):
                self.assertTrue(inspect.isclass(getattr(presentation, name)))

    def test_reanchored_rewrites_only_artifact_imports(self):
        p = self.presentation()
        authored = object()
        leaf = p.ArtifactImport('sim/part-a.stl')
        original = p.Union((
            p.Color((1.0, 0.0, 0.0), 1, p.Rotate(30, [0, 0, 1], leaf)),
            p.Translate([1, 2, 3], p.Authored(authored)),
        ))
        build_dir = '/build'
        moved = p.reanchored(original, build_dir, '/build/sim/tools')

        rotated = moved.children[0].child.child
        self.assertEqual(rotated.path, os.path.relpath(
            '/build/sim/part-a.stl', '/build/sim/tools'))
        self.assertEqual(rotated.path, '../part-a.stl')
        self.assertIs(moved.children[1], original.children[1])
        self.assertIs(moved.children[1].child.geometry, authored)
        self.assertEqual(leaf.path, 'sim/part-a.stl')
        self.assertIs(original.children[0].child.child, leaf)

    def test_presented_holds_the_operations_own_values(self):
        from machinome.expression_graph import get_animation_time
        from machinome.node.operations import Rotation, Translation
        p = self.presentation()
        child = p.ArtifactImport('a.stl')
        angle = get_animation_time() * 360
        axis = [0, 0, 1]
        rotation = Rotation(angle, axis)
        rotated = rotation.presented(child)
        self.assertIsInstance(rotated, p.Rotate)
        self.assertIs(rotated.angle, angle)
        self.assertIs(rotated.axis, axis)
        self.assertIs(rotated.child, child)
        vector = [1, angle, 0]
        translated = Translation(vector).presented(child)
        self.assertIsInstance(translated, p.Translate)
        self.assertIs(translated.vector, vector)
        self.assertIs(translated.child, child)

    def test_assemble_returns_a_description_for_every_leaf_kind(self):
        from tests.scad_presentation_project import parts
        p = self.presentation()
        kinds = (p.ArtifactImport, p.Color, p.Rotate, p.Translate, p.Union,
                 p.Authored)
        coil = parts.Coil()
        coil.height = 4.0
        for node in (parts.FineCylinder(), parts.Bracket(), parts.Block(),
                     coil, parts.Plate(), parts.Legacy(),
                     parts.InlineCylinder()):
            with self.subTest(type(node).__name__):
                self.assertIsInstance(node.assemble(), kinds)


# 2.7 ---------------------------------------------------------------------

class WrittenOnlyWhereReadTest(_BuildDirectory):

    def test_a_build_writes_only_the_scad_authored_leafs_scad(self):
        self.build()
        node, parts = self.machine()
        fine = parts['FineCylinder']
        expected = os.path.relpath(fine.scad_file, self.build_dir)
        self.assertEqual(scad_files(self.build_dir), [expected])
        with open(fine.scad_file, 'rb') as handle:
            self.assertEqual(
                hashlib.sha256(handle.read()).hexdigest(),
                golden_file_digest(
                    'parts-' + os.path.basename(fine.scad_file).split(
                        '-', 1)[1]))
        spring = os.path.basename(parts['Spring'].basepath)
        snapshots = [name for name in os.listdir(
            os.path.dirname(parts['Spring'].basepath))
            if name.startswith(spring + '-') and name.endswith('.stl')]
        self.assertEqual(snapshots, [])

        before = observed(self.build_dir)
        node.assemble()
        self.assertEqual(observed(self.build_dir), before)

    def test_the_builder_takes_no_scad_output(self):
        from machinome.core.builder import Builder
        self.assertNotIn('scad_output', inspect.signature(Builder).parameters)


# 2.8 ---------------------------------------------------------------------

class SweepTest(_BuildDirectory):

    def seed(self):
        from machinome.node.openscad.writer import scad_file
        node, parts = self.machine()
        seeded = []
        for each in (node, parts['Group'], parts['Fused'], parts['Spring'],
                     parts['Block']):
            currency.publish_text(scad_file(each), f'// seed {each.name}\n',
                                  each.mtime_ns, each.source_digest,
                                  each.source_fingerprint)
            seeded.append(scad_file(each))
        fine = parts['FineCylinder']
        renamed = os.path.join(os.path.dirname(fine.scad_file),
                               'machine-OldCylinder-000000000000.scad')
        currency.publish_text(renamed, '// seed renamed\n', fine.mtime_ns,
                              fine.source_digest, fine.source_fingerprint)
        seeded.append(renamed)
        for path in seeded:
            self.assertTrue(os.path.exists(currency.sidecar(path)), path)
        return fine

    def test_presentation_scad_and_a_renamed_leafs_scad_are_swept(self):
        fine = self.seed()
        self.build()
        kept = os.path.relpath(fine.scad_file, self.build_dir)
        self.assertEqual(scad_files(self.build_dir), [kept])
        self.assertEqual(
            scad_records(self.build_dir),
            [os.path.relpath(currency.sidecar(fine.scad_file),
                             self.build_dir)])

        self.build()
        self.assertEqual(scad_files(self.build_dir), [kept])
        self.assertTrue(os.path.exists(currency.sidecar(fine.scad_file)))


# 2.9 ---------------------------------------------------------------------

class SnapshotOnDemandTest(_BuildDirectory):
    """The OpenSCAD renderer writes the root's `.scad` for its pose, has
    OpenSCAD read it, and removes it (the coordinator's correction of
    Decision 3); a build removes one a killed render left."""

    def setUp(self):
        super().setUp()
        #: What OpenSCAD was given: `(scad_file, its text, the .scad files
        #: under the build directory)` at the moment it ran.
        self.drawn = []

    def runner(self, command, **_):
        scad_file = command[-1]
        with open(scad_file) as handle:
            text = handle.read()
        self.drawn.append((scad_file, text, scad_files(self.build_dir)))
        with open(command[command.index('-o') + 1], 'wb') as image:
            image.write(b'\x89PNG')
        return SimpleNamespace(stdout='', stderr='', returncode=0)

    def snapshot(self, renderer, time=0.0, root='Machine'):
        from machinome.manager.snapshot import Snapshot
        parser = argparse.ArgumentParser()
        parser.add_argument('path')
        Snapshot().add_arguments(parser)
        image = os.path.join(self.build_dir, f'shot-{renderer}-{time}.png')
        args = parser.parse_args([
            str(ROOT / FIXTURE / 'machine.py') + f':{root}', '-o', image,
            '--renderer', renderer, '--time', str(time),
            '--imgsize', '64x48'])
        with patch('machinome.manager.snapshot.run', self.runner), \
                patch('machinome.viewers.browser.BrowserRenderer.capture',
                      lambda _, staging, args, output: open(
                          output, 'wb').close()):
            Snapshot().handle(args)
        self.assertTrue(os.path.exists(image))

    def expected(self, time):
        """The root's `scad_code` in that pose, loaded as the snapshot
        command loads it."""
        from machinome.core.loader import load_node
        from machinome.node.openscad.writer import scad_code
        node = load_node(str(ROOT / FIXTURE / 'machine.py') + ':Machine')
        node.set_keyframe(time)
        node.assemble()
        return scad_code(node)

    def test_the_openscad_renderer_draws_the_roots_scad_for_its_pose(self):
        from machinome.node.openscad import writer
        self.build()
        node, parts = self.machine()
        root = os.path.relpath(writer.scad_file(node), self.build_dir)
        fine = os.path.relpath(parts['FineCylinder'].scad_file,
                               self.build_dir)

        for time in (0.0, 0.5):
            self.snapshot('openscad', time)
        texts = {}
        for time, (scad_file, text, present) in zip((0.0, 0.5), self.drawn):
            self.assertEqual(scad_file, os.path.join(
                self.build_dir, root))
            self.assertEqual(present, sorted([root, fine]))
            imported = re.findall(r'import\(file = "([^"]*)"', text)
            self.assertTrue(imported, text)
            for path in imported:
                self.assertTrue(os.path.exists(os.path.join(
                    os.path.dirname(scad_file), path)), path)
            texts[time] = text
        for time, text in texts.items():
            self.assertEqual(text, self.expected(time))
        self.assertNotEqual(texts[0.0], texts[0.5])

    def test_the_renderer_removes_the_roots_scad_after_drawing_it(self):
        from machinome.node.openscad.writer import scad_file
        self.build()
        node, parts = self.machine()
        self.snapshot('openscad')
        self.assertEqual(len(self.drawn), 1)
        fine = os.path.relpath(parts['FineCylinder'].scad_file,
                               self.build_dir)
        self.assertEqual(scad_files(self.build_dir), [fine])
        self.assertFalse(os.path.exists(currency.sidecar(scad_file(node))))

    def test_the_renderer_removes_the_roots_scad_when_drawing_fails(self):
        from subprocess import CalledProcessError
        self.build()
        node, parts = self.machine()

        def failing(command, **_):
            self.assertTrue(os.path.exists(command[-1]))
            raise CalledProcessError(1, command, stderr='broken')

        self.runner = failing
        with self.assertRaises(SystemExit):
            self.snapshot('openscad')
        self.assertEqual(
            scad_files(self.build_dir),
            [os.path.relpath(parts['FineCylinder'].scad_file,
                             self.build_dir)])

    def test_a_scad_authored_root_keeps_its_own_scad(self):
        from tests.scad_where_read_project.machine import FineCylinder
        self.snapshot('openscad', root='FineCylinder')
        self.assertEqual(len(self.drawn), 1)
        self.assertTrue(os.path.exists(FineCylinder().scad_file))

    def test_a_build_removes_a_root_scad_a_killed_render_left(self):
        """An unchanged build still removes a transient artifact: the
        document is the one already published, and the root's `.scad`,
        which the renderer published transient, goes (`openscad-out`)."""
        from machinome.node.openscad.writer import generate_scad, scad_file
        self.build()
        node, parts = self.machine()
        generate_scad(node, lambda: '// left by a killed render\n')
        self.assertIs(currency.recorded_transient(scad_file(node)), True)
        with open(os.path.join(self.build_dir, 'viewer.json'), 'rb') as one:
            document = one.read()
        self.build()
        with open(os.path.join(self.build_dir, 'viewer.json'), 'rb') as two:
            self.assertEqual(two.read(), document)
        self.assertEqual(
            scad_files(self.build_dir),
            [os.path.relpath(parts['FineCylinder'].scad_file,
                             self.build_dir)])
        self.assertFalse(os.path.exists(currency.sidecar(scad_file(node))))

    @skipUnless(has_bundle(),
                'machinome-viewer not installed (pip install "machinome[viewer]")')
    def test_the_web_renderer_writes_no_scad(self):
        self.snapshot('web')
        node, parts = self.machine()
        self.assertEqual(
            scad_files(self.build_dir),
            [os.path.relpath(parts['FineCylinder'].scad_file,
                             self.build_dir)])


# 2.10 --------------------------------------------------------------------

#: The develop builder, as run_builder constructs it, without watching.
DEVELOP_BUILDER = '''
import inspect
from machinome.core.builder import Builder
extra = ({{'scad_output': False}}
         if 'scad_output' in inspect.signature(Builder).parameters else {{}})
Builder({reference!r}, watch=False, lifecycle=True, overrides=[],
        **extra).start()
'''


class DevelopTest(_BuildDirectory):
    """Characterisation, green before and after: `develop` has had no
    OpenSCAD path since ADR-103, and its builder writes a SCAD-authored
    leaf's `.scad` and no other."""

    def test_develop_without_the_viewer_is_refused_and_starts_nothing(self):
        from machinome.manager.develop import Develop
        from machinome.viewers.bundle import INSTALL_REMEDY
        args = SimpleNamespace(path=MIXED, web=False, web_dev=False,
                               no_web=False, debug_builder=False,
                               callback=None, set=None)
        with patch('machinome.manager.develop.has_bundle',
                   return_value=False), \
                patch('machinome.manager.develop.Popen') as popen, \
                patch('machinome.manager.develop.Process') as process, \
                patch('sys.stderr.write') as written:
            with self.assertRaises(SystemExit) as raised:
                Develop().handle(args)
        self.assertEqual(raised.exception.code, 1)
        self.assertIn(INSTALL_REMEDY, ''.join(
            call.args[0] for call in written.call_args_list))
        popen.assert_not_called()
        process.assert_not_called()

    def test_the_develop_builder_writes_only_the_solid2node_scad(self):
        run = run_python(DEVELOP_BUILDER.format(reference=MIXED),
                         blocked=False, build_dir=self.build_dir)
        self.assertEqual(run.returncode, 0, run.output)
        files = scad_files(self.build_dir)
        self.assertEqual(len(files), 1, files)
        self.assertRegex(files[0], r'machine-FineCylinder-\w+\.scad$')
