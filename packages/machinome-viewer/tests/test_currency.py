# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The built bundle is checked against the sources it is built from.

OpenSpec `keep-the-bundle-current`, ADR-059. The failure these tests
encode is the one a maker met: `describe()` reported `apiVersion: 16` and
`documentVersions: [1..7]` from `package.json` while the bundle it handed
the path of carried `viewer API 15` and refused version 7, so a correct
document was refused and the message blamed the document.
"""

import ast
import inspect
import json
import os
import re
import subprocess
import tempfile
import threading
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from solid_node_viewer import bundle, currency


def checkout(root, *, bundle_ns=1_000_000_000_000_000_000, source_ns=None,
             dependencies=True, sources=True):
    """A widget directory shaped like a checkout, with times we control.

    `source_ns` defaults to one second BEFORE the bundle, so the tree is
    current unless a test says otherwise. Times are set explicitly in
    nanoseconds because that is the comparison under test.
    """
    widget = Path(root) / 'widget'
    (widget / 'dist').mkdir(parents=True)
    (widget / 'dist' / 'solid-widget.js').write_text('/* built */')
    if dependencies:
        (widget / 'node_modules' / 'esbuild').mkdir(parents=True)
        (widget / 'node_modules' / 'esbuild' / 'index.js').write_text('x')
    if sources:
        (widget / 'src' / 'run').mkdir(parents=True)
        (widget / 'src' / 'viewer.ts').write_text('// viewer')
        (widget / 'src' / 'run' / 'program.ts').write_text('// program')
        (widget / 'build.mjs').write_text('// build')
        (widget / 'tsconfig.json').write_text('{}')
    (widget / 'package.json').write_text(json.dumps({
        'solidNodeViewerApi': 16,
        'solidNodeDocumentVersions': [1, 2, 3, 4, 5, 6, 7],
    }))
    if source_ns is None:
        source_ns = bundle_ns - 1_000_000_000
    for path in widget.rglob('*'):
        if path.is_file() and 'dist' not in path.parts:
            os.utime(path, ns=(source_ns, source_ns))
    built = widget / 'dist' / 'solid-widget.js'
    os.utime(built, ns=(bundle_ns, bundle_ns))
    return widget


def touch(path, ns):
    os.utime(path, ns=(ns, ns))


class CurrencyModuleTest(TestCase):
    """The module is as cheap to import as the lookup that uses it."""

    def test_deciding_currency_imports_only_the_standard_library(self):
        tree = ast.parse(inspect.getsource(currency))
        imports = {node.names[0].name for node in ast.walk(tree)
                   if isinstance(node, ast.Import)}
        froms = {node.module for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom)}
        self.assertTrue(
            imports <= {'logging', 'os', 'subprocess', 'fcntl'}, imports)
        self.assertTrue(
            froms <= {'pathlib', 'solid_node_viewer.bundle'}, froms)


class StalenessTest(TestCase):

    def test_a_source_newer_than_the_bundle_is_stale(self):
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root)
            self.assertFalse(currency.is_stale(widget))
            touch(widget / 'src' / 'viewer.ts', 2_000_000_000_000_000_000)
            self.assertTrue(currency.is_stale(widget))

    def test_every_declared_input_counts(self):
        # The declaration and the build program are inputs as much as the
        # TypeScript is: the bug that started this cycle was a bundle
        # built from an older `package.json`.
        for name in ('package.json', 'build.mjs', 'tsconfig.json',
                     'src/run/program.ts'):
            with self.subTest(input=name):
                with tempfile.TemporaryDirectory() as root:
                    widget = checkout(root)
                    touch(widget / name, 2_000_000_000_000_000_000)
                    self.assertTrue(currency.is_stale(widget))

    def test_equal_times_are_current(self):
        # The tolerant direction on a coarse filesystem: only STRICTLY
        # newer is stale (design D2).
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root, bundle_ns=1_500_000_000_000_000_000,
                              source_ns=1_500_000_000_000_000_000)
            self.assertFalse(currency.is_stale(widget))

    def test_currency_is_decided_in_integer_nanoseconds(self):
        # A difference too small to survive float seconds still counts.
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root, bundle_ns=1_500_000_000_000_000_000)
            touch(widget / 'src' / 'viewer.ts', 1_500_000_000_000_000_001)
            self.assertIsInstance(currency.newest_input_ns(widget), int)
            self.assertTrue(currency.is_stale(widget))

    def test_the_dependencies_are_not_an_input(self):
        # Walking node_modules would cost orders of magnitude more than
        # the check it serves, and a dependency change is an install --
        # which this path refuses to perform (design D2, D4).
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root)
            touch(widget / 'node_modules' / 'esbuild' / 'index.js',
                  2_000_000_000_000_000_000)
            self.assertFalse(currency.is_stale(widget))
            self.assertNotIn(
                widget / 'node_modules' / 'esbuild' / 'index.js',
                set(currency.build_inputs(widget)))


class InstalledDistributionTest(TestCase):

    def test_a_tree_without_sources_is_not_a_source_checkout(self):
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root, sources=False)
            self.assertFalse(currency.is_source_checkout(widget))

    def test_an_installed_distribution_is_current_without_scanning(self):
        # A wheel carries the bundle and package.json but no src/ and no
        # build.mjs, so there is nothing to compare: one is_file(), never
        # stale, npm never looked for (design D9).
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root, sources=False, dependencies=False)
            with patch.object(subprocess, 'run') as run:
                self.assertFalse(currency.is_stale(widget))
                currency.ensure_current(widget)
            run.assert_not_called()


class RebuildTest(TestCase):

    def stub(self, widget, *, returncode=0, stdout='', stderr=''):
        """A build program that records its argv and touches the bundle."""
        calls = []

        def run(argv, **kwargs):
            calls.append((argv, kwargs))
            if returncode == 0:
                built = widget / 'dist' / 'solid-widget.js'
                built.write_text('/* rebuilt */')
                touch(built, 3_000_000_000_000_000_000)
            return subprocess.CompletedProcess(
                argv, returncode, stdout=stdout, stderr=stderr)

        return calls, run

    def test_a_stale_bundle_is_rebuilt(self):
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root)
            touch(widget / 'src' / 'viewer.ts', 2_000_000_000_000_000_000)
            calls, run = self.stub(widget)
            with patch.object(subprocess, 'run', run):
                currency.ensure_current(widget)
            self.assertEqual(len(calls), 1)
            self.assertFalse(currency.is_stale(widget))

    def test_a_current_bundle_is_not_rebuilt(self):
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root)
            calls, run = self.stub(widget)
            with patch.object(subprocess, 'run', run):
                currency.ensure_current(widget)
            self.assertEqual(calls, [])

    def test_a_rebuild_builds_and_never_installs(self):
        # ADR-059 decision 4. `npm ci` through a worktree's symlinked
        # node_modules has EMPTIED the primary checkout's dependencies in
        # this workspace. A lookup must never be able to do that.
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root)
            touch(widget / 'src' / 'viewer.ts', 2_000_000_000_000_000_000)
            calls, run = self.stub(widget)
            with patch.object(subprocess, 'run', run):
                currency.ensure_current(widget)
            argv, kwargs = calls[0]
            self.assertNotIn('ci', argv)
            self.assertNotIn('install', argv)
            self.assertIn('build', argv)
            self.assertEqual(Path(kwargs['cwd']), widget)
            self.assertTrue((widget / 'node_modules' / 'esbuild' / 'index.js').exists())

    def test_the_build_writes_nothing_to_standard_output(self):
        # `describe` prints one JSON object on stdout and callers parse
        # it (design D7), so the build's own output is captured.
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root)
            touch(widget / 'src' / 'viewer.ts', 2_000_000_000_000_000_000)
            calls, run = self.stub(widget)
            with patch.object(subprocess, 'run', run):
                currency.ensure_current(widget)
            _, kwargs = calls[0]
            self.assertTrue(kwargs.get('capture_output') or
                            kwargs.get('stdout') is not None, kwargs)


class RefusalTest(TestCase):

    def test_a_stale_bundle_without_dependencies_is_refused(self):
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root, dependencies=False)
            touch(widget / 'src' / 'viewer.ts', 2_000_000_000_000_000_000)
            with patch.object(subprocess, 'run') as run:
                with self.assertRaises(currency.BundleStale) as caught:
                    currency.ensure_current(widget)
            run.assert_not_called()
            message = str(caught.exception)
            self.assertIn('solid-widget.js', message)
            self.assertIn('viewer.ts', message)
            self.assertIn('npm ci', message)
            self.assertIn('npm run build', message)

    def test_a_failed_build_is_refused_with_what_it_printed(self):
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root)
            touch(widget / 'src' / 'viewer.ts', 2_000_000_000_000_000_000)
            _, run = RebuildTest().stub(
                widget, returncode=1, stderr='viewer.ts:10:2: ERROR: nope')
            with patch.object(subprocess, 'run', run):
                with self.assertRaises(currency.BundleStale) as caught:
                    currency.ensure_current(widget)
            self.assertIn('nope', str(caught.exception))

    def test_a_missing_build_program_is_refused_not_ignored(self):
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root)
            touch(widget / 'src' / 'viewer.ts', 2_000_000_000_000_000_000)
            with patch.object(subprocess, 'run', side_effect=FileNotFoundError('npm')):
                with self.assertRaises(currency.BundleStale) as caught:
                    currency.ensure_current(widget)
            self.assertIn('npm', str(caught.exception))

    def test_a_stale_bundle_is_never_handed_out(self):
        # The whole point: what cannot be repaired is named, not served
        # (design D5). The stale file is still on disk untouched.
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root, dependencies=False)
            touch(widget / 'src' / 'viewer.ts', 2_000_000_000_000_000_000)
            with self.assertRaises(currency.BundleStale):
                currency.ensure_current(widget)
            self.assertEqual(
                (widget / 'dist' / 'solid-widget.js').read_text(), '/* built */')


class ConcurrentRebuildTest(TestCase):

    def test_two_callers_produce_one_build(self):
        # Two esbuild runs writing one outfile can leave a torn file
        # (design D6): the second caller waits for the lock and then
        # finds the bundle current.
        with tempfile.TemporaryDirectory() as root:
            widget = checkout(root)
            touch(widget / 'src' / 'viewer.ts', 2_000_000_000_000_000_000)
            calls = []
            started = threading.Event()

            def run(argv, **kwargs):
                calls.append(argv)
                started.set()
                threading.Event().wait(0.2)
                built = widget / 'dist' / 'solid-widget.js'
                built.write_text('/* rebuilt */')
                touch(built, 3_000_000_000_000_000_000)
                return subprocess.CompletedProcess(argv, 0, stdout='', stderr='')

            errors = []

            def ask():
                try:
                    currency.ensure_current(widget)
                except Exception as error:  # pragma: no cover - reported below
                    errors.append(error)

            with patch.object(subprocess, 'run', run):
                first = threading.Thread(target=ask)
                first.start()
                started.wait(2)
                second = threading.Thread(target=ask)
                second.start()
                first.join(10)
                second.join(10)

            self.assertEqual(errors, [])
            self.assertEqual(len(calls), 1, calls)
            self.assertFalse(currency.is_stale(widget))


class ThisInstallationTest(TestCase):
    """The invariant that broke, asserted against the real installation.

    `describe()` answers for the bundle at its own `path`; these read that
    file and check the answer against what it actually carries. With a
    stale bundle they disagree -- which is exactly what a maker met.
    """

    def setUp(self):
        if not bundle.has_bundle():
            self.skipTest('this installation carries no built bundle')
        self.described = bundle.describe()
        self.text = Path(self.described['path']).read_text()

    def test_the_bundle_named_carries_the_api_version_reported(self):
        # The banner is specified content: "the bundle it carries SHALL
        # open with a banner naming ... the declared viewer API version".
        banner = re.search(r'viewer API (\d+)', self.text[:2000])
        self.assertIsNotNone(banner, 'the bundle carries no API banner')
        self.assertEqual(int(banner.group(1)), self.described['apiVersion'])

    def test_the_bundle_named_refuses_by_the_versions_reported(self):
        # A containment check, not a parse: the compact array the build
        # substitutes for __DOCUMENT_VERSIONS__ must be present. It
        # cannot prove the bundle refuses by nothing else, but it does
        # catch a bundle built from an older declaration, which is the
        # failure this cycle exists for.
        compact = json.dumps(self.described['documentVersions'],
                             separators=(',', ':'))
        # Asserted as a boolean, never `assertIn`: the haystack is a
        # 741 kb minified bundle, and a failure must name the two lists
        # rather than print the whole artifact.
        carried = re.search(r'=(\[(?:\d+,)*\d+\])[,;]', self.text)
        self.assertTrue(
            compact in self.text,
            f'describe() reports documentVersions {compact}, but the bundle '
            f'at {self.described["path"]} does not carry that list '
            f'(it carries {carried.group(1) if carried else "none"})')
