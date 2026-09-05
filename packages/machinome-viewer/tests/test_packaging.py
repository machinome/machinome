# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

from unittest import TestCase
from unittest.mock import call, patch

from solid_node_viewer import packaging


class FrontendPackagingTest(TestCase):

    def test_source_distribution_builds_both_frontends(self):
        with patch('solid_node_viewer.packaging.build_frontend') as build:
            packaging.build_distribution_frontends()
        self.assertEqual(build.call_args_list, [
            call(packaging.WIDGET), call(packaging.DEVELOPMENT_APP),
        ])

    def test_wheel_builds_only_frontends_with_missing_outputs(self):
        with patch('solid_node_viewer.packaging.build_frontend') as build, \
             patch.object(packaging.DEVELOPMENT_APP, 'output_exists', return_value=True), \
             patch.object(packaging.WIDGET, 'output_exists', return_value=False):
            packaging.build_missing_frontends()
        build.assert_called_once_with(packaging.WIDGET)
