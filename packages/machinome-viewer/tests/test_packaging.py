# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from unittest import TestCase
from unittest.mock import call, patch
from pathlib import Path
import re
import tempfile

from machinome.viewer.web import packaging


class FrontendPackagingTest(TestCase):

    def test_packaging_refuses_shared_dependencies_before_installing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shared = root / 'primary-dependencies'
            shared.mkdir()
            marker = shared / 'keep'
            marker.write_text('untouched')
            widget = root / 'widget'
            widget.mkdir()
            (widget / 'node_modules').symlink_to(shared, target_is_directory=True)
            frontend = packaging.Frontend(widget, widget / 'dist' / 'bundle.js')
            with patch.object(packaging.subprocess, 'check_call') as invoke:
                with self.assertRaisesRegex(RuntimeError, 'symlink'):
                    packaging.build_frontend(frontend)
            invoke.assert_not_called()
            self.assertEqual(marker.read_text(), 'untouched')

    def test_packaging_refuses_a_shared_workspace_root(self):
        # Inside an npm workspace `npm ci` writes the root's node_modules,
        # so a linked node_modules above the widget is as shared as one in
        # it (change `join-viewer`).
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shared = root / 'primary-dependencies'
            shared.mkdir()
            marker = shared / 'keep'
            marker.write_text('untouched')
            workspace = root / 'workspace'
            widget = workspace / 'packages' / 'viewer' / 'widget'
            widget.mkdir(parents=True)
            (workspace / 'node_modules').symlink_to(
                shared, target_is_directory=True)
            frontend = packaging.Frontend(widget, widget / 'dist' / 'bundle.js')
            with patch.object(packaging.subprocess, 'check_call') as invoke:
                with self.assertRaisesRegex(
                        RuntimeError,
                        re.escape(str(workspace / 'node_modules'))):
                    packaging.build_frontend(frontend)
            invoke.assert_not_called()
            self.assertEqual(marker.read_text(), 'untouched')

    def test_packaging_installs_and_builds_private_dependencies(self):
        with tempfile.TemporaryDirectory() as temporary:
            widget = Path(temporary)
            frontend = packaging.Frontend(widget, widget / 'dist' / 'bundle.js')
            with patch.object(packaging.subprocess, 'check_call') as invoke:
                packaging.build_frontend(frontend)
            self.assertEqual(invoke.call_args_list, [
                call(['npm', 'ci'], cwd=widget),
                call(['npm', 'run', 'build'], cwd=widget)])

    def test_packaging_installs_at_the_workspace_root_that_names_the_widget(self):
        # Inside the repository's npm workspace, `npm ci` run from a member's
        # directory installs that member alone and empties every other
        # member's node_modules, the movie's among them; run at the root it
        # installs every member (change `join-movie`). The bundle is built
        # in the widget's directory.
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            widget = workspace / 'packages' / 'viewer' / 'widget'
            widget.mkdir(parents=True)
            (workspace / 'package.json').write_text(
                '{"private": true, "workspaces": '
                '["packages/viewer/widget", "packages/movie/js"]}')
            frontend = packaging.Frontend(widget, widget / 'dist' / 'bundle.js')
            with patch.object(packaging.subprocess, 'check_call') as invoke:
                packaging.build_frontend(frontend)
            self.assertEqual(invoke.call_args_list, [
                call(['npm', 'ci'], cwd=workspace),
                call(['npm', 'run', 'build'], cwd=widget)])

    def test_packaging_installs_in_the_widget_under_a_root_that_names_another(
            self):
        with tempfile.TemporaryDirectory() as temporary:
            outer = Path(temporary).resolve()
            widget = outer / 'widget'
            widget.mkdir()
            (outer / 'package.json').write_text(
                '{"private": true, "workspaces": ["elsewhere"]}')
            frontend = packaging.Frontend(widget, widget / 'dist' / 'bundle.js')
            with patch.object(packaging.subprocess, 'check_call') as invoke:
                packaging.build_frontend(frontend)
            self.assertEqual(invoke.call_args_list, [
                call(['npm', 'ci'], cwd=widget),
                call(['npm', 'run', 'build'], cwd=widget)])

    def test_source_distribution_builds_the_one_frontend(self):
        with patch('machinome.viewer.web.packaging.build_frontend') as build:
            packaging.build_distribution_frontends()
        self.assertEqual(build.call_args_list, [call(packaging.WIDGET)])

    def test_wheel_builds_the_widget_when_its_output_is_missing(self):
        with patch('machinome.viewer.web.packaging.build_frontend') as build, \
             patch.object(packaging.WIDGET, 'output_exists', return_value=False), \
             patch.object(packaging.WIDGET, 'output_is_stale', return_value=False):
            packaging.build_stale_frontends()
        build.assert_called_once_with(packaging.WIDGET)

    def test_wheel_builds_the_widget_when_its_output_is_stale(self):
        # ADR-059 decision 8. A wheel built from a checkout whose bundle
        # is older than the source beside it would otherwise SHIP the
        # stale bundle, and `scripts/check-dist` would install and smoke
        # it without noticing. That is a publishing hazard, not just a
        # development annoyance.
        with patch('machinome.viewer.web.packaging.build_frontend') as build, \
             patch.object(packaging.WIDGET, 'output_exists', return_value=True), \
             patch.object(packaging.WIDGET, 'output_is_stale', return_value=True):
            packaging.build_stale_frontends()
        build.assert_called_once_with(packaging.WIDGET)

    def test_wheel_builds_nothing_when_the_widget_is_built_and_current(self):
        with patch('machinome.viewer.web.packaging.build_frontend') as build, \
             patch.object(packaging.WIDGET, 'output_exists', return_value=True), \
             patch.object(packaging.WIDGET, 'output_is_stale', return_value=False):
            packaging.build_stale_frontends()
        build.assert_not_called()

    def test_staleness_is_decided_by_the_one_comparison(self):
        # Packaging does not carry a second opinion about what "stale"
        # means: it asks `currency`, the same module the lookup, the
        # server and the capture ask.
        with patch('machinome.viewer.web.currency.is_stale',
                   return_value=True) as stale:
            self.assertTrue(packaging.WIDGET.output_is_stale())
        stale.assert_called_once_with(packaging.WIDGET.directory)

    def test_the_wheel_hook_builds_what_is_missing_or_stale(self):
        with patch('machinome.viewer.web.packaging.build_stale_frontends') as build, \
             patch('setuptools.command.build_py.build_py.run'):
            packaging.BuildPythonWithFrontend(__import__('setuptools').Distribution()).run()
        build.assert_called_once_with()
