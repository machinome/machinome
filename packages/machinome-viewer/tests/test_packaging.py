# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

from unittest import TestCase
from unittest.mock import call, patch
from pathlib import Path
import tempfile

from machinome_viewer import packaging


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

    def test_packaging_installs_and_builds_private_dependencies(self):
        with tempfile.TemporaryDirectory() as temporary:
            widget = Path(temporary)
            frontend = packaging.Frontend(widget, widget / 'dist' / 'bundle.js')
            with patch.object(packaging.subprocess, 'check_call') as invoke:
                packaging.build_frontend(frontend)
            self.assertEqual(invoke.call_args_list, [
                call(['npm', 'ci'], cwd=widget),
                call(['npm', 'run', 'build'], cwd=widget)])

    def test_source_distribution_builds_the_one_frontend(self):
        with patch('machinome_viewer.packaging.build_frontend') as build:
            packaging.build_distribution_frontends()
        self.assertEqual(build.call_args_list, [call(packaging.WIDGET)])

    def test_wheel_builds_the_widget_when_its_output_is_missing(self):
        with patch('machinome_viewer.packaging.build_frontend') as build, \
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
        with patch('machinome_viewer.packaging.build_frontend') as build, \
             patch.object(packaging.WIDGET, 'output_exists', return_value=True), \
             patch.object(packaging.WIDGET, 'output_is_stale', return_value=True):
            packaging.build_stale_frontends()
        build.assert_called_once_with(packaging.WIDGET)

    def test_wheel_builds_nothing_when_the_widget_is_built_and_current(self):
        with patch('machinome_viewer.packaging.build_frontend') as build, \
             patch.object(packaging.WIDGET, 'output_exists', return_value=True), \
             patch.object(packaging.WIDGET, 'output_is_stale', return_value=False):
            packaging.build_stale_frontends()
        build.assert_not_called()

    def test_staleness_is_decided_by_the_one_comparison(self):
        # Packaging does not carry a second opinion about what "stale"
        # means: it asks `currency`, the same module the lookup, the
        # server and the capture ask.
        with patch('machinome_viewer.currency.is_stale',
                   return_value=True) as stale:
            self.assertTrue(packaging.WIDGET.output_is_stale())
        stale.assert_called_once_with(packaging.WIDGET.directory)

    def test_the_wheel_hook_builds_what_is_missing_or_stale(self):
        with patch('machinome_viewer.packaging.build_stale_frontends') as build, \
             patch('setuptools.command.build_py.build_py.run'):
            packaging.BuildPythonWithFrontend(__import__('setuptools').Distribution()).run()
        build.assert_called_once_with()
