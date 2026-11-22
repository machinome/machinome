# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The web viewer bundles a model's app with its own toolchain (OpenSpec
`show-a-models-own-app`, design Decision 11 and Decision 15, U1 to U10).

The provider answers the seam's operation `bundle` with
`bundle_app(entry, root, output_dir)`: the app's own TypeScript, JavaScript
and CSS, the viewer's own esbuild, its own React and React DOM and the
helper `@machinome/viewer/app`, bundled into one script and at most one
stylesheet named by their content. It refuses by name, writing nothing,
whatever it cannot bundle, and installs nothing.

The fixture is `tests/fixtures/calculator-app/`, copied to a temporary
directory for every bundling so nothing is written beside the repository's
own files. U1 to U8 run Node.js and the widget's JavaScript dependencies;
where either is absent they are skipped, saying which.
"""

import hashlib
import json
import os
import re
import shutil
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock

import machinome.viewer.web as web
from machinome.viewer import ViewerError
from machinome.viewer.web.bundle import bundle_path

FIXTURES = Path(__file__).parent / 'fixtures'
APP_FIXTURE = FIXTURES / 'calculator-app'
PACKAGE = Path(__file__).resolve().parent.parent
REPOSITORY = PACKAGE.parent.parent
WIDGET = PACKAGE / 'machinome' / 'viewer' / 'web' / 'widget'

GRANT = tomllib.loads(
    (REPOSITORY / 'packages' / 'machinome' / 'pyproject.toml').read_text())[
    'project']['license']

#: What an app may import, as the refusal says it.
ALLOWED = ('an app imports its own files, react, react-dom and '
           '@machinome/viewer/app')

NAME = re.compile(r'^app-[0-9a-f]{16}\.(js|css)$')


def _toolchain_absent():
    """Why the bundler cannot run here, or None."""
    if shutil.which('node') is None:
        return 'no Node.js on the PATH'
    missing = []
    for package in ('esbuild', 'react', 'react-dom'):
        if not any((directory / 'node_modules' / package).is_dir()
                   for directory in (WIDGET, *WIDGET.parents)):
            missing.append(package)
    if missing:
        return ('the widget\'s JavaScript dependencies are not installed: '
                + ', '.join(missing))
    return None


ABSENT = _toolchain_absent()
needs_toolchain = unittest.skipIf(ABSENT is not None, ABSENT or '')


def _sha16(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


class _Bench(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.base = Path(self.tempdir.name)

    def project(self, where='project'):
        """A copy of the fixture's project, at `where` under the bench."""
        target = self.base / where
        shutil.copytree(APP_FIXTURE, target)
        return target

    def output(self, name='out'):
        target = self.base / name
        target.mkdir(parents=True)
        return target

    def bundle(self, entry, root, output):
        return web.bundle_app(str(entry), str(root), str(output))


@needs_toolchain
class BundleTest(_Bench):

    def test_u1_the_app_bundles_to_a_script_and_a_stylesheet_named_by_content(self):
        project = self.project()
        out = self.output()
        record = self.bundle(project / 'app' / 'index.tsx', project, out)
        self.assertEqual(sorted(record), ['inputs', 'script', 'stylesheet'])
        self.assertRegex(record['script'], NAME)
        self.assertTrue(record['script'].endswith('.js'))
        self.assertRegex(record['stylesheet'], NAME)
        self.assertTrue(record['stylesheet'].endswith('.css'))
        self.assertEqual(sorted(p.name for p in out.iterdir()),
                         sorted([record['script'], record['stylesheet']]))
        self.assertEqual(record['script'], f'app-{_sha16(out / record["script"])}.js')
        self.assertEqual(record['stylesheet'],
                         f'app-{_sha16(out / record["stylesheet"])}.css')
        self.assertIn('.calculator-app',
                      (out / record['stylesheet']).read_text())
        # An unchanged app publishes nothing: the files are left as they are.
        stamps = {p.name: p.stat().st_mtime_ns for p in out.iterdir()}
        again = self.bundle(project / 'app' / 'index.tsx', project, out)
        self.assertEqual(again, record)
        self.assertEqual({p.name: p.stat().st_mtime_ns for p in out.iterdir()},
                         stamps)

    def test_u1_an_app_importing_no_css_has_no_stylesheet(self):
        project = self.project()
        (project / 'app' / 'plain.tsx').write_text(
            "import { Viewport } from '@machinome/viewer/app';\n"
            'export default function Plain() { return <Viewport />; }\n')
        out = self.output()
        record = self.bundle(project / 'app' / 'plain.tsx', project, out)
        self.assertIsNone(record['stylesheet'])
        self.assertEqual([p.name for p in out.iterdir()], [record['script']])

    def test_u2_the_script_opens_with_react_s_notice_and_the_helper_s_grant(self):
        project = self.project()
        out = self.output()
        record = self.bundle(project / 'app' / 'index.tsx', project, out)
        script = (out / record['script']).read_text()
        head = script[:1500]
        self.assertTrue(head.startswith('/*!'), head[:40])
        version = json.loads((WIDGET / 'package.json').read_text())['version']
        react = json.loads(
            (Path(_resolve_react()) / 'package.json').read_text())['version']
        self.assertIn(f'machinome-viewer app bundle, built by machinome-viewer '
                      f'{version}', head)
        self.assertIn(f'Bundles React and React DOM {react}', head)
        self.assertIn('Copyright (c) Meta Platforms, Inc. and affiliates', head)
        self.assertIn('MIT License', head)
        self.assertIn('https://github.com/facebook/react/blob/main/LICENSE', head)
        self.assertIn('Bundles @machinome/viewer/app', head)
        # Spelled in two pieces, so the licence test's scan of every
        # header does not read this line as one.
        self.assertIn('SPDX-License-' f'Identifier: {GRANT}', head)
        self.assertIn('Source: https://github.com/machinome/machinome', head)
        # It dispatches the contract's event from its own script element.
        self.assertIn('machinome:app', script)
        self.assertIn('currentScript', script)

    def test_u3_an_import_the_viewer_does_not_provide_is_refused_by_name(self):
        project = self.project()
        out = self.output()
        with self.assertRaises(ViewerError) as raised:
            self.bundle(project / 'app' / 'imports-three.tsx', project, out)
        message = str(raised.exception)
        self.assertIn("imports 'three'", message)
        self.assertIn(ALLOWED, message)
        self.assertIn('imports-three.tsx', message)
        self.assertEqual(list(out.iterdir()), [])

    def test_u4_a_file_outside_the_project_is_refused_naming_it(self):
        project = self.project()
        outside = self.base / 'elsewhere'
        outside.mkdir()
        (outside / 'helper.ts').write_text('export const label = "far";\n')
        (project / 'app' / 'reaches.tsx').write_text(
            "import { Viewport } from '@machinome/viewer/app';\n"
            "import { label } from '../../elsewhere/helper';\n"
            'export default function Reaches() {\n'
            '  return <div>{label}<Viewport /></div>;\n}\n')
        out = self.output()
        with self.assertRaises(ViewerError) as raised:
            self.bundle(project / 'app' / 'reaches.tsx', project, out)
        message = str(raised.exception)
        self.assertIn(str((outside / 'helper.ts').resolve()), message)
        self.assertIn(str(project.resolve()), message)
        self.assertEqual(list(out.iterdir()), [])

    def test_u5_source_that_does_not_build_is_refused_with_its_file_and_line(self):
        project = self.project()
        out = self.output()
        with self.assertRaises(ViewerError) as raised:
            self.bundle(project / 'app' / 'broken.tsx', project, out)
        message = str(raised.exception)
        self.assertIn('the app app/broken.tsx does not build', message)
        self.assertRegex(message, r'app/broken\.tsx:\d+:\d+: ')
        self.assertEqual(list(out.iterdir()), [])

    def test_u7_two_copies_of_a_project_bundle_to_the_same_bytes(self):
        first = self.project('one/project')
        second = self.project('two/levels/deeper/elsewhere')
        out_first = self.output('out-one')
        out_second = self.output('out-two/nested')
        a = self.bundle(first / 'app' / 'index.tsx', first, out_first)
        b = self.bundle(second / 'app' / 'index.tsx', second, out_second)
        self.assertEqual((a['script'], a['stylesheet']),
                         (b['script'], b['stylesheet']))
        for name in (a['script'], a['stylesheet']):
            self.assertEqual((out_first / name).read_bytes(),
                             (out_second / name).read_bytes(), name)
        script = (out_first / a['script']).read_text()
        for path in (first, second, WIDGET):
            self.assertNotIn(str(path), script)

    def test_u8_inputs_are_the_project_s_own_files_and_nothing_of_the_widget(self):
        project = self.project()
        out = self.output()
        record = self.bundle(project / 'app' / 'index.tsx', project, out)
        expected = sorted(str((project / 'app' / name).resolve())
                          for name in ('index.tsx', 'Readout.tsx', 'app.css'))
        self.assertEqual(sorted(record['inputs']), expected)


class ToolchainRefusalTest(_Bench):
    """(U6) Where the toolchain is not, the operation refuses before Node
    runs, naming why, and writes nothing."""

    def bundle_with(self, widget):
        from machinome.viewer.web.app import bundle_app
        project = self.project()
        out = self.output()
        try:
            bundle_app(str(project / 'app' / 'index.tsx'), str(project),
                       str(out), widget=widget)
        finally:
            self.assertEqual(list(out.iterdir()), [])

    def test_u6_an_installed_viewer_without_the_toolchain_refuses_with_the_release_s_limit(self):
        widget = self.base / 'installed' / 'widget'
        widget.mkdir(parents=True)
        shutil.copy2(WIDGET / 'package.json', widget / 'package.json')
        (widget / 'dist').mkdir()
        with self.assertRaises(ViewerError) as raised:
            self.bundle_with(widget)
        message = str(raised.exception)
        self.assertIn('was installed without the toolchain that bundles a '
                      "model's app", message)
        self.assertIn('in this release an app is bundled only from a source '
                      'checkout of the machinome repository with its '
                      'JavaScript dependencies installed', message)

    def test_u6_a_checkout_without_its_dependencies_names_them_and_npm_ci(self):
        widget = self.base / 'checkout' / 'widget'
        widget.mkdir(parents=True)
        shutil.copy2(WIDGET / 'package.json', widget / 'package.json')
        shutil.copy2(WIDGET / 'app-build.mjs', widget / 'app-build.mjs')
        shutil.copytree(WIDGET / 'app', widget / 'app')
        with self.assertRaises(ViewerError) as raised:
            self.bundle_with(widget)
        message = str(raised.exception)
        self.assertIn("the viewer's JavaScript dependencies are not installed "
                      '(esbuild, react, react-dom)', message)
        self.assertIn('install them with npm ci in', message)

    @needs_toolchain
    def test_u6_no_node_on_the_path_is_named(self):
        with mock.patch.dict(os.environ, {'PATH': str(self.base / 'empty')}):
            with self.assertRaises(ViewerError) as raised:
                self.bundle_with(WIDGET)
        self.assertEqual(str(raised.exception),
                         "bundling a model's app needs Node.js, and none is "
                         'on the PATH')


class ViewerBundleTest(unittest.TestCase):

    def test_u9_the_viewer_s_own_bundle_carries_no_react(self):
        bundle = bundle_path()
        if not Path(bundle).is_file():
            self.skipTest('no built viewer bundle in this checkout')
        text = Path(bundle).read_text()
        for marker in ('react.production', '__SECRET_INTERNALS',
                       'ReactCurrentDispatcher', 'react-dom'):
            self.assertNotIn(marker, text)


class ProviderTest(unittest.TestCase):

    def test_u10_the_provider_declares_bundle_and_keeps_its_contract(self):
        self.assertIn('bundle', web.OPERATIONS)
        self.assertTrue(callable(getattr(web, 'bundle_app', None)))
        self.assertEqual(web.CONTRACT, 1)
        self.assertEqual(web.OPERATIONS, frozenset(
            {'present', 'capture', 'serve', 'embed', 'bundle'}))


def _resolve_react():
    """The directory of the React the widget resolves."""
    for directory in (WIDGET, *WIDGET.parents):
        candidate = directory / 'node_modules' / 'react'
        if candidate.is_dir():
            return candidate
    raise AssertionError('no react beside the widget')


if __name__ == '__main__':
    unittest.main()
