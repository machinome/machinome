# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A model's own app (OpenSpec change `declare-a-models-app`, capability
`model-app`, design Decision 10).

The originating project is `projects/enigma-i`: its root class `Enigma` is
to declare `app = 'app/index.tsx'`, and every document the framework
publishes for the browser is to carry that app, bundled by the viewer
through the seam's operation `bundle`, beside the document. The fixture is
`tests/app_project/`, the suite's clocked `Calculator` declaring an app of
two instruction buttons and four window digits.

D1-D2 the declaration; P1-P4 a build publishes it; R1-R4 refusals are
recorded, not substituted; W1-W5 `develop` follows the app and tells the
open page when the document is published; E1-E4 an export carries it; X1
and X2 the export page and the open development page in a real browser.

Every test that writes builds a temporary copy of the fixture project,
never the committed tree.
"""

import asyncio
import hashlib
import http.server
import io
import json
import logging
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from unittest import TestCase, skipIf, skipUnless
from unittest.mock import patch

from tests.brep_engine_absent import run_machinome

TESTS = Path(__file__).resolve().parent
APP_PROJECT = TESTS / 'app_project'
CALCULATOR_FILE = TESTS / 'clocked_project' / 'calculator.py'

#: The SHA-256 of `Calculator`'s `viewer.json` as the base `50bdffdf`
#: published it, each `"mtime": <seconds>` written `"mtime": 0`: a source
#: file's modification time is a property of the checkout, not of the
#: document (the golden documents normalize it the same way). Recorded
#: before any source change, in `evidence.md` beside the raw bytes' digest.
P4_SHA256 = 'eb5141b77c9568e3d7d5d423ca0db8296202c672a8343f4786d634ffc479e5e6'

DIGITS = ('w3.digit', 'w2.digit', 'w1.digit', 'w0.digit')

#: `machinome.viewer.web.capture.Capture.launch`'s arguments.
CHROMIUM_ARGS = ['--use-gl=angle', '--use-angle=swiftshader',
                 '--enable-unsafe-swiftshader']

CLI = 'from machinome.cli import manage; manage()'

#: How long an edit may take to reach the page, or the disk.
BOUND = 90.0


def _toolchain_refusal():
    """Why the web viewer cannot bundle an app here, or None."""
    try:
        from machinome.viewer.web.app import refusal
    except ImportError as error:
        return f'the web viewer is not importable ({error})'
    return refusal()


TOOLCHAIN = _toolchain_refusal()
needs_toolchain = skipIf(
    TOOLCHAIN is not None,
    f"bundling an app needs the web viewer's toolchain: {TOOLCHAIN}")
needs_openscad = skipUnless(
    shutil.which('openscad'),
    "the fixture's parts are Solid2Node leaves, rendered by OpenSCAD, and "
    'no openscad is on the PATH')


def _playwright_refusal():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return 'playwright is not installed'
    try:
        with sync_playwright() as playwright:
            if not os.path.exists(playwright.chromium.executable_path):
                return "playwright's Chromium is not installed"
    except Exception as error:  # pragma: no cover - environment
        return f'Chromium cannot be found ({error})'
    return None


def normalized_sha256(data):
    return hashlib.sha256(
        re.sub(rb'"mtime": [0-9.e+-]+', b'"mtime": 0', data)).hexdigest()


def wait_until(predicate, timeout=BOUND, interval=0.05):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(interval)
    return predicate()


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    assert port != 9010
    return port


def drawn(png):
    """Whether a screenshot holds more than a few colours: a model drawn."""
    try:
        from PIL import Image
    except ImportError:  # pragma: no cover - the bench has Pillow
        return True
    image = Image.open(io.BytesIO(png)).convert('RGB')
    colours = image.getcolors(maxcolors=1 << 16)
    return colours is None or len(colours) > 8


class _Scratch(TestCase):
    """A temporary copy of the fixture project, `<base>/proj/app_project/`,
    with its manifest, so `../../` of a fixture file is outside it."""

    def setUp(self):
        super().setUp()
        temporary = tempfile.mkdtemp(prefix='model-app-')
        self.addCleanup(shutil.rmtree, temporary, ignore_errors=True)
        self.base = Path(os.path.realpath(temporary))
        self.project = self.base / 'proj'
        shutil.copytree(APP_PROJECT, self.project / 'app_project',
                        ignore=shutil.ignore_patterns('__pycache__'))
        (self.project / 'pyproject.toml').write_text(
            '[tool.machinome]\n'
            'model = "app_project.calculator_app:CalculatorApp"\n')
        self.build_dir = self.project / '_build'
        present = 'SOLID_BUILD_DIR' in os.environ
        previous = os.environ.get('SOLID_BUILD_DIR')

        def restore():
            if present:
                os.environ['SOLID_BUILD_DIR'] = previous
            else:
                os.environ.pop('SOLID_BUILD_DIR', None)
        self.addCleanup(restore)

    def reference(self, module='calculator_app', name='CalculatorApp',
                  project=None):
        return f'{project or self.project}/app_project/{module}.py:{name}'

    def build(self, module='calculator_app', name='CalculatorApp',
              reference=None):
        from machinome.core.builder import Builder
        builder = Builder(reference or self.reference(module, name),
                          build_dir=str(self.build_dir), watch=False)
        return asyncio.run(builder._start())

    def published(self):
        return (self.build_dir / 'viewer.json').read_bytes()

    def document(self):
        return json.loads(self.published())

    def load(self, reference):
        from machinome.core.loader import load_node
        os.environ['SOLID_BUILD_DIR'] = str(self.build_dir)
        return load_node(reference)

    def edit(self, relative, old, new):
        path = self.project / 'app_project' / relative
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new))


# -- D: the declaration ------------------------------------------------------


class DeclarationTest(TestCase):

    def test_d1_a_value_that_is_not_an_app_is_refused_where_it_is_written(self):
        from machinome.node.assembly import AssemblyNode

        for value in (42, '/abs/x.tsx', 'x.py', '', 'C:/x.tsx', 'app\\x.tsx'):
            with self.subTest(value=value):
                with self.assertRaises(TypeError) as raised:
                    class Enigma(AssemblyNode):
                        app = value
                message = str(raised.exception)
                self.assertEqual(
                    message,
                    f"Enigma.app is {value!r}. On a node class `app` names "
                    f"the model's app: a TypeScript or JavaScript file "
                    f"relative to this file, such as 'app/index.tsx'; the "
                    f"name is reserved")

    def test_d1_the_forms_of_an_app_are_accepted(self):
        from machinome.node.assembly import AssemblyNode

        for value in ('app/index.tsx', 'panel.ts', '../ui/main.jsx',
                      'app.js'):
            with self.subTest(value=value):
                class Accepted(AssemblyNode):
                    app = value
                self.assertEqual(Accepted.app, value)

    def test_d2_the_app_is_relative_to_the_class_that_declared_it(self):
        from machinome.core.app import declared_app
        from tests.app_project.calculator_app import CalculatorApp
        from tests.app_project.derived.inherited import InheritedApp
        from tests.clocked_project.calculator import Calculator

        expected = str(APP_PROJECT / 'app' / 'index.tsx')
        self.assertEqual(declared_app(CalculatorApp()), expected)
        # Declared in `derived/`, inherited: still beside the file whose
        # class body wrote it.
        self.assertEqual(declared_app(InheritedApp()), expected)
        self.assertIsNone(declared_app(Calculator()))

    def test_d2_only_the_root_s_declaration_is_read(self):
        from machinome.core.app import declared_app
        from machinome.node.assembly import AssemblyNode
        from tests.clocked_project.parts import Dial

        class AppDial(Dial):
            app = 'dial/index.tsx'

        class Holder(AssemblyNode):
            dial = AppDial()

        self.assertIsNone(declared_app(Holder()))


# -- P: a build publishes the app --------------------------------------------


@needs_openscad
@needs_toolchain
class PublicationTest(_Scratch):

    def test_p1_a_build_names_the_bundled_app_beside_the_document(self):
        from machinome.core.builder import BuildOutcome

        self.assertEqual(self.build(), BuildOutcome.CURRENT)
        document = self.document()
        app = document['app']
        self.assertEqual(set(app), {'script', 'stylesheet'})
        self.assertRegex(app['script'], r'^app-[0-9a-f]{16}\.js$')
        self.assertRegex(app['stylesheet'], r'^app-[0-9a-f]{16}\.css$')
        for name in app.values():
            self.assertTrue((self.build_dir / name).is_file(), name)
        # Additive: the version is the clocked model's own.
        self.assertEqual(document['version'], 8)
        # The body's last key, ahead of what the producer adds.
        self.assertEqual(list(document)[-3:], ['app', 'root', 'pieces'])

    def test_p2_an_unchanged_model_is_not_republished_for_its_app(self):
        self.build()
        document = self.build_dir / 'viewer.json'
        script = self.build_dir / self.document()['app']['script']
        before = (self.published(), document.stat().st_mtime_ns,
                  script.stat().st_mtime_ns)

        self.build()

        self.assertEqual((self.published(), document.stat().st_mtime_ns,
                          script.stat().st_mtime_ns), before)

    def test_p3_an_edited_app_replaces_the_old_one(self):
        self.build()
        first = self.document()['app']

        self.edit('app/Readout.tsx', '>Window<', '>Register<')
        self.build()

        second = self.document()['app']
        self.assertNotEqual(second['script'], first['script'])
        self.assertTrue((self.build_dir / second['script']).is_file())
        self.assertFalse((self.build_dir / first['script']).exists())
        # The stylesheet's bytes did not change, nor its name.
        self.assertEqual(second['stylesheet'], first['stylesheet'])
        self.assertTrue((self.build_dir / second['stylesheet']).is_file())


@needs_openscad
class NoAppTest(_Scratch):

    def test_p4_a_model_without_an_app_is_unchanged_and_asks_no_viewer(self):
        from machinome.core.builder import BuildOutcome

        with patch('machinome.viewer.resolve',
                   side_effect=AssertionError('a viewer was asked')):
            outcome = self.build(
                reference=f'{CALCULATOR_FILE}:Calculator')
        self.assertEqual(outcome, BuildOutcome.CURRENT)
        self.assertNotIn('app', self.document())
        self.assertEqual(normalized_sha256(self.published()), P4_SHA256)


# -- R: refusals are recorded, not substituted --------------------------------


class _Refusal(_Scratch):

    def refused(self, module, name, *, absent=()):
        """Build in process, then once with `machinome build`; answer the
        refusal the first published."""
        from machinome.core.builder import BuildOutcome

        with self.assertLogs('core', level='ERROR') as logged:
            outcome = self.build(module, name)
        self.assertEqual(outcome, BuildOutcome.CURRENT)
        document = self.document()
        self.assertEqual(set(document['app']), {'refusal'})
        refusal = document['app']['refusal']
        # Logged once, as the error it is.
        self.assertEqual([record.getMessage() for record in logged.records],
                         [refusal])
        self.assertFalse((self.build_dir / 'errors.json').exists())
        # The model is published as usual: its parts and their meshes.
        self.assertEqual(document['root']['name'], name)
        self.assertTrue(any(path.suffix == '.stl'
                            for path in self.build_dir.rglob('*.stl')))
        self.assertEqual(list(self.build_dir.glob('app-*')), [])

        blocking = {'blocked': True, 'absent': absent} if absent else {
            'blocked': False}
        run = run_machinome('build', f'app_project/{module}.py:{name}',
                            build_dir=str(self.build_dir),
                            cwd=str(self.project), **blocking)
        self.assertEqual(run.returncode, 0, run.output)
        self.assertEqual(self.document()['app'], {'refusal': refusal})
        self.assertFalse((self.build_dir / 'errors.json').exists())
        return refusal


@needs_openscad
class RefusalTest(_Refusal):

    def test_r1_a_declared_file_that_does_not_exist(self):
        refusal = self.refused('missing', 'Missing')
        self.assertEqual(
            refusal,
            f"Missing.app = 'app/absent.tsx' names "
            f"{self.project}/app_project/app/absent.tsx, which does not "
            f"exist")

    def test_r2_a_file_outside_the_project_is_refused_by_the_core(self):
        (self.base / 'outside-app.tsx').write_text(
            'export default function Outside() { return null; }\n')
        with patch('machinome.viewer.resolve',
                   side_effect=AssertionError('a viewer was asked')):
            refusal = self.refused('outside', 'Outside')
        # The core's sentence, not the viewer's own check behind it.
        self.assertEqual(
            refusal,
            f"Outside.app = '../../outside-app.tsx' names "
            f"{self.base}/outside-app.tsx, which is outside the project at "
            f"{self.project}; an app's files are the project's own")

    def test_r3_no_viewer_to_bundle_with(self):
        import machinome.viewer as viewers

        def absent(name):
            raise viewers.absent(name)

        with patch.object(viewers, 'viewer', side_effect=absent):
            refusal = self.refused('calculator_app', 'CalculatorApp',
                                   absent=('machinome.viewer.web',))
        self.assertEqual(
            refusal,
            "CalculatorApp.app = 'app/index.tsx' cannot be bundled: the web "
            "viewer needs machinome.viewer.web, which is not installed; "
            "install it with 'pip install \"machinome[viewer]\"'")

    @needs_toolchain
    def test_r4_an_app_the_viewer_refuses_to_bundle(self):
        refusal = self.refused('broken', 'Broken')
        self.assertTrue(refusal.startswith(
            "Broken.app = 'app/broken.tsx' cannot be bundled: the app "
            "app_project/app/broken.tsx does not build:\n"
            "app_project/app/broken.tsx:"), refusal)


# -- W: develop follows the app ----------------------------------------------


class _Watching(_Scratch):
    """A watching builder run as `machinome develop` runs it, in a thread
    of this process so its loads can be counted."""

    def watch(self, module='calculator_app', name='CalculatorApp',
              reference=None):
        from machinome.core import builder as building

        loads = []
        real = building.load_node

        def counted(*arguments, **keywords):
            loads.append(arguments)
            return real(*arguments, **keywords)

        patcher = patch.object(building, 'load_node', side_effect=counted)
        patcher.start()
        self.addCleanup(patcher.stop)
        builder = building.Builder(reference or self.reference(module, name),
                                   build_dir=str(self.build_dir),
                                   lifecycle=True)
        exit_codes = []

        def run():
            try:
                builder.start()
            except SystemExit as stop:
                exit_codes.append(stop.code)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

        def stop():
            if thread.is_alive() and getattr(builder, 'loop', None):
                builder.loop.call_soon_threadsafe(
                    builder._resolve_file_changed)
            thread.join(30)
        self.addCleanup(stop)
        document = self.build_dir / 'viewer.json'
        self.assertTrue(wait_until(document.is_file), 'nothing published')
        # The publication is written after the watches are scheduled; give
        # the builder the moment to reach its wait.
        time.sleep(1.0)
        self.assertTrue(thread.is_alive(), exit_codes)
        return builder, thread, exit_codes, loads


@needs_openscad
@needs_toolchain
class DevelopFollowsTheAppTest(_Watching):

    def test_w1_an_app_edit_is_republished_in_place_by_the_watching_builder(self):
        unused = self.project / 'app_project' / 'app' / 'Unused.tsx'
        unused.write_text('export const unused = 1;\n')
        builder, thread, exit_codes, loads = self.watch()
        first = self.document()['app']
        meshes = {path: path.stat().st_mtime_ns
                  for path in self.build_dir.rglob('*.stl')}
        self.assertTrue(meshes)

        self.edit('app/Readout.tsx', '>Window<', '>Register<')

        self.assertTrue(wait_until(
            lambda: self.document()['app']['script'] != first['script']),
            'the app edit was not republished')
        second = self.document()['app']
        self.assertTrue((self.build_dir / second['script']).is_file())
        self.assertTrue(wait_until(
            lambda: not (self.build_dir / first['script']).exists()))
        self.assertTrue(thread.is_alive(), exit_codes)
        self.assertEqual(len(loads), 1)
        self.assertEqual({path: path.stat().st_mtime_ns
                          for path in self.build_dir.rglob('*.stl')}, meshes)

        # A file the app does not read changes nothing.
        published = self.published()
        unused.write_text('export const unused = 2;\n')
        time.sleep(2.0)
        self.assertEqual(self.published(), published)
        self.assertTrue(thread.is_alive(), exit_codes)
        self.assertEqual(len(loads), 1)

    def test_w2_a_repaired_app_is_published_by_the_same_builder(self):
        builder, thread, exit_codes, loads = self.watch('broken', 'Broken')
        self.assertIn('refusal', self.document()['app'])

        (self.project / 'app_project' / 'app' / 'broken.tsx').write_text(
            'export default function Broken() {\n'
            '  return <div className="broken" />;\n'
            '}\n')

        self.assertTrue(wait_until(
            lambda: 'script' in self.document()['app']),
            'the repaired app was not published')
        self.assertNotIn('refusal', self.document()['app'])
        self.assertTrue(thread.is_alive(), exit_codes)
        self.assertEqual(len(loads), 1)

    def test_w3_another_producer_published_meanwhile(self):
        from machinome.core.builder import BuildOutcome, atomic_write

        builder, thread, exit_codes, loads = self.watch()
        document = self.document()
        document['instructions'] = {}
        atomic_write(str(self.build_dir / 'viewer.json'),
                     json.dumps(document).encode())

        with self.assertLogs('core.builder', level='INFO') as logged:
            self.edit('app/Readout.tsx', '>Window<', '>Register<')
            thread.join(BOUND)
        self.assertFalse(thread.is_alive())
        self.assertEqual(exit_codes, [BuildOutcome.SOURCE_CHANGED.value])
        self.assertIn(
            'the published document changed since this builder published '
            'it; reloading the model to publish the app',
            [record.getMessage() for record in logged.records])

    def test_w4_a_model_source_edit_still_rebuilds(self):
        from machinome.core.builder import BuildOutcome

        builder, thread, exit_codes, loads = self.watch()

        self.edit('calculator_app.py', '"""`Calculator`, operated',
                  '"""The `Calculator`, operated')
        thread.join(BOUND)

        self.assertFalse(thread.is_alive())
        self.assertEqual(exit_codes, [BuildOutcome.SOURCE_CHANGED.value])

    def test_w1_through_a_symlinked_project(self):
        """The originating project is reached through a symbolic link
        (`projects` -> `/mnt/data/...`), and the viewer answers the app's
        inputs as real paths: the watch must still see them."""
        link = self.base / 'link'
        link.symlink_to(self.project, target_is_directory=True)
        builder, thread, exit_codes, loads = self.watch(
            reference=self.reference(project=link))
        first = self.document()['app']
        self.assertEqual(set(first), {'script', 'stylesheet'})

        (link / 'app_project' / 'app' / 'Readout.tsx').write_text(
            (link / 'app_project' / 'app' / 'Readout.tsx').read_text()
            .replace('>Window<', '>Register<'))

        self.assertTrue(wait_until(
            lambda: self.document()['app']['script'] != first['script']),
            'the app edit through the link was not republished')
        self.assertTrue(thread.is_alive(), exit_codes)
        self.assertEqual(len(loads), 1)


class _Session:
    def __init__(self):
        self.reloads = 0

    def reload(self):
        self.reloads += 1


class PublicationWatchTest(TestCase):

    def test_w5_the_page_is_told_once_per_replacement_of_the_document(self):
        from machinome.core.builder import atomic_write
        from machinome.manager.develop import watch_publication

        directory = tempfile.mkdtemp(prefix='publication-watch-')
        self.addCleanup(shutil.rmtree, directory, ignore_errors=True)
        build = os.path.join(directory, '_build')
        session = _Session()
        observer = watch_publication(build, session)
        self.addCleanup(observer.join)
        self.addCleanup(observer.stop)
        self.assertTrue(os.path.isdir(build))
        time.sleep(0.3)

        atomic_write(os.path.join(build, 'viewer.json'), b'{}')
        self.assertTrue(wait_until(lambda: session.reloads == 1, 10))
        atomic_write(os.path.join(build, 'errors.json'), b'{}')
        atomic_write(os.path.join(build, 'app-0123456789abcdef.js'), b'')
        with open(os.path.join(build, 'note.txt'), 'w') as stream:
            stream.write('x')
        os.makedirs(os.path.join(build, 'clocked_project'))
        atomic_write(os.path.join(build, 'clocked_project', 'viewer.json'),
                     b'{}')
        time.sleep(1.0)
        self.assertEqual(session.reloads, 1)
        atomic_write(os.path.join(build, 'viewer.json'), b'{"a": 1}')
        self.assertTrue(wait_until(lambda: session.reloads == 2, 10))
        time.sleep(0.5)
        self.assertEqual(session.reloads, 2)


# -- E: an export carries the app --------------------------------------------


@needs_openscad
class ExportTest(_Scratch):

    @needs_toolchain
    def test_e1_an_export_carries_its_app_beside_the_manifest(self):
        from machinome.core.export import export_node

        output = self.base / 'export'
        node = self.load(self.reference())
        manifest = export_node(node, str(output))

        app = manifest['app']
        self.assertEqual(set(app), {'script', 'stylesheet'})
        for name in app.values():
            self.assertTrue((output / name).is_file(), name)
        written = json.loads((output / 'manifest.json').read_text())
        self.assertEqual(written['app'], app)
        self.assertEqual(list(written).index('app'),
                         list(written).index('root') - 1)
        self.assertTrue((output / 'index.html').is_file())
        self.assertTrue((output / 'machinome-viewer.js').is_file())

    @needs_toolchain
    def test_e2_an_app_that_does_not_build_fails_the_export(self):
        from machinome.core.export import ExportAppRefused, export_node

        output = self.base / 'export'
        node = self.load(self.reference('broken', 'Broken'))
        with self.assertRaises(ExportAppRefused) as raised:
            export_node(node, str(output))
        self.assertTrue(str(raised.exception).startswith(
            "Broken.app = 'app/broken.tsx' cannot be bundled: the app "
            "app_project/app/broken.tsx does not build:"),
            str(raised.exception))
        self.assertFalse(output.exists())

    def test_e2_a_missing_app_fails_the_export_naming_the_class_and_file(self):
        from machinome.core.export import ExportAppRefused, export_node

        output = self.base / 'export'
        node = self.load(self.reference('missing', 'Missing'))
        with self.assertRaises(ExportAppRefused) as raised:
            export_node(node, str(output))
        self.assertEqual(
            str(raised.exception),
            f"Missing.app = 'app/absent.tsx' names "
            f"{self.project}/app_project/app/absent.tsx, which does not "
            f"exist")
        self.assertFalse(output.exists())

    def test_e3_a_widget_less_export_of_a_model_with_an_app_is_refused(self):
        output = self.base / 'export'
        run = run_machinome('export', '--no-widget', '-o', str(output),
                            'app_project/calculator_app.py:CalculatorApp',
                            blocked=False, build_dir=str(self.build_dir),
                            cwd=str(self.project))
        self.assertEqual(run.returncode, 1, run.output)
        self.assertIn(
            "Error: machinome export --no-widget does not carry a model's "
            "app, and CalculatorApp declares app = 'app/index.tsx'; export "
            "it with its widget\n", run.stderr)
        self.assertFalse(output.exists())
        # Refused before anything was built.
        self.assertEqual(list(self.build_dir.rglob('*.stl'))
                         if self.build_dir.exists() else [], [])

    def test_e3_export_node_refuses_it_before_anything_is_built(self):
        from machinome.core.export import ExportAppRefused, export_node

        output = self.base / 'export'
        node = self.load(self.reference())
        with patch.object(type(node), 'build_stls',
                          side_effect=AssertionError('built')):
            with self.assertRaises(ExportAppRefused):
                export_node(node, str(output), widget=False)
        self.assertFalse(output.exists())

    def test_e4_a_widget_less_export_of_a_model_without_an_app(self):
        from machinome.core.export import export_node

        output = self.base / 'export'
        node = self.load(f'{CALCULATOR_FILE}:Calculator')
        manifest = export_node(node, str(output), widget=False)
        self.assertNotIn('app', manifest)
        self.assertEqual(sorted(os.listdir(output)),
                         ['manifest.json', 'models'])


# -- X: in a real browser -----------------------------------------------------


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *arguments):
        pass


@contextmanager
def serving(directory):
    server = http.server.ThreadingHTTPServer(
        ('127.0.0.1', 0), partial(_Quiet, directory=str(directory)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_address[1]}'
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


class _Browsing(_Scratch):

    def setUp(self):
        super().setUp()
        refusal = _playwright_refusal()
        if refusal is not None:
            self.skipTest(refusal)
        self.errors = []

    @contextmanager
    def browsing(self):
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=CHROMIUM_ARGS)
            try:
                page = browser.new_page(viewport={'width': 1000,
                                                  'height': 700})
                page.set_default_timeout(int(BOUND * 1000))
                page.on('pageerror',
                        lambda error: self.errors.append(str(error)))
                page.on('console', lambda message: self.errors.append(
                    message.text) if message.type == 'error' else None)
                yield page
            finally:
                browser.close()

    def wait_for_app(self, page):
        page.wait_for_selector('.calculator-app .calculator-app-key')

    def keys_enabled(self, page):
        page.wait_for_function("""() => [...document.querySelectorAll(
          '.calculator-app-key')].every((key) => !key.disabled)""")

    def digits(self, page):
        return page.evaluate("""() => Object.fromEntries(
          [...document.querySelectorAll('.calculator-app-readout')].map(
            (one) => [one.dataset.readout,
                      Number(one.querySelector('.calculator-app-digit')
                             .textContent)]))""")


@needs_openscad
@needs_toolchain
class ExportPageTest(_Browsing):

    def test_x1_the_export_page_shows_the_app_and_its_keys_play_the_machine(self):
        output = self.base / 'export'
        run = subprocess.run(
            [sys.executable, '-c', CLI, 'export', '-o', str(output),
             'app_project/calculator_app.py:CalculatorApp'],
            cwd=self.project, capture_output=True, text=True, timeout=600,
            env=dict(os.environ, SOLID_BUILD_DIR=str(self.build_dir)))
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        app = json.loads((output / 'manifest.json').read_text())['app']

        with serving(output) as base, self.browsing() as page:
            requested = []
            page.on('request', lambda request: requested.append(request.url))
            page.goto(f'{base}/index.html')
            self.wait_for_app(page)
            self.assertEqual(page.locator('.calculator-app-key').count(), 2)
            self.assertEqual(page.locator('.clocked-controls').count(), 0)
            self.assertIn(f'{base}/{app["script"]}', requested)
            self.assertEqual(self.digits(page), dict.fromkeys(DIGITS, 0))

            page.click('.calculator-app-key[data-instruction="Set four"]')
            self.keys_enabled(page)
            page.click('.calculator-app-key[data-instruction="Stroke"]')
            self.assertEqual(page.evaluate("""() => [...document
              .querySelectorAll('.calculator-app-key')].map(
                (key) => key.disabled)"""), [True, True])
            started = time.monotonic()
            self.keys_enabled(page)
            self.assertGreater(time.monotonic() - started, 1.0)
            self.assertEqual(self.digits(page), {
                'w3.digit': 0, 'w2.digit': 0, 'w1.digit': 0, 'w0.digit': 4})
            self.assertTrue(drawn(
                page.locator('.calculator-app-picture').screenshot()))
        self.assertEqual(self.errors, [])


@needs_openscad
@needs_toolchain
class DevelopmentPageTest(_Browsing):
    """`machinome develop` on the scratch project, on a port bound free,
    the session and every process it started stopped in the end."""

    def setUp(self):
        super().setUp()
        self.port = free_port()
        self.log_path = self.base / 'develop.log'
        log = open(self.log_path, 'w')
        self.addCleanup(log.close)
        self.develop = subprocess.Popen(
            [sys.executable, '-c', CLI, 'develop'], cwd=self.project,
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
            env=dict(os.environ, MACHINOME_PORT=str(self.port),
                     SOLID_BUILD_DIR=str(self.build_dir)))
        self.addCleanup(self.stop_develop)
        self.url = f'http://127.0.0.1:{self.port}/'

        def listening():
            try:
                urllib.request.urlopen(self.url, timeout=2).close()
            except OSError:
                return False
            return (self.build_dir / 'viewer.json').is_file()
        self.assertTrue(wait_until(listening, 180), self.log())

    def stop_develop(self):
        try:
            os.killpg(self.develop.pid, signal.SIGINT)
        except ProcessLookupError:
            return
        try:
            self.develop.wait(30)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(self.develop.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self.develop.wait(30)

    def log(self):
        return self.log_path.read_text()

    def starts(self):
        return self.log().count('core.builder - START')

    def test_x2_the_open_page_shows_the_edited_app_the_picture_standing(self):
        with self.browsing() as page:
            requested = []
            page.on('request', lambda request: requested.append(request.url))
            page.goto(self.url)
            self.wait_for_app(page)
            page.wait_for_timeout(500)
            page.evaluate("""() => {
              window.__marker = 'the same page';
              window.__canvas = document.querySelector('canvas'); }""")
            self.assertEqual(
                page.locator('.calculator-app-label').first.text_content(),
                'Window')
            self.assertEqual(self.starts(), 1, self.log())
            mark = len(requested)

            edited = time.monotonic()
            self.edit('app/Readout.tsx', '>Window<', '>Register<')
            page.wait_for_function("""() => {
              const label = document.querySelector('.calculator-app-label');
              return label !== null && label.textContent === 'Register'; }""")
            self.app_seconds = time.monotonic() - edited
            page.wait_for_timeout(500)
            after = page.evaluate("""() => ({
              marker: window.__marker,
              sameCanvas: document.querySelector('canvas') === window.__canvas,
              apps: document.querySelectorAll('.calculator-app').length })""")
            self.assertEqual(after, {'marker': 'the same page',
                                     'sameCanvas': True, 'apps': 1})
            self.assertTrue(drawn(page.locator('canvas').screenshot()))
            fetched = requested[mark:]
            self.assertEqual([url for url in fetched if url.endswith('.stl')],
                             [])
            self.assertEqual(self.starts(), 1, self.log())
        self.assertEqual(self.errors, [])
        print(f'X2 app edit to page: {self.app_seconds:.2f} s')

    def test_x2_the_open_page_shows_a_python_edit_when_it_is_published(self):
        with self.browsing() as page:
            documents = []

            def on_response(response):
                if response.url.endswith('/build/viewer.json'):
                    try:
                        documents.append((time.monotonic(), response.json()))
                    except Exception:  # pragma: no cover - a failed fetch
                        pass
            page.on('response', on_response)
            page.goto(self.url)
            # The model, whether or not its app is shown: this half is about
            # when the page reads a published document.
            page.wait_for_selector('canvas')
            page.wait_for_timeout(2000)

            # One write: a second instruction, and its import.
            source = self.project / 'app_project' / 'calculator_app.py'
            text = source.read_text()
            edited_text = text.replace(
                'from tests.clocked_project.calculator import Calculator\n',
                'from machinome.simulation import Instruction\n'
                'from tests.clocked_project.calculator import Calculator\n'
            ).replace(
                "    app = 'app/index.tsx'\n",
                "    app = 'app/index.tsx'\n"
                "    instructions = {**Calculator.instructions,\n"
                "                    'Set five': Instruction(\n"
                "                        {'operand': 5}, duration=0.5)}\n")
            self.assertNotEqual(edited_text.count('Set five'), 0)
            edited = time.monotonic()
            source.write_text(edited_text)

            def shown():
                return [at for at, body in documents
                        if at > edited and 'Set five' in body['instructions']]
            # Waited on the page, so Playwright dispatches its responses.
            deadline = time.monotonic() + 60
            while not shown() and time.monotonic() < deadline:
                page.wait_for_timeout(50)
            self.assertTrue(shown(),
                            'the page never read the published edit; it '
                            'read ' + repr([sorted(body['instructions'])
                                            for _, body in documents])
                            + '\n' + self.log()[-4000:])
            self.python_seconds = shown()[0] - edited
            self.assertEqual(page.evaluate('() => window.location.href'),
                             self.url)
        print(f'X2 Python edit to page: {self.python_seconds:.2f} s')
