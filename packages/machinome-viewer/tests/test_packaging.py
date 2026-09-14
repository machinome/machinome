# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

from unittest import TestCase
from unittest.mock import call, patch

from solid_node_viewer import packaging


class FrontendPackagingTest(TestCase):

    def test_source_distribution_builds_the_one_frontend(self):
        with patch('solid_node_viewer.packaging.build_frontend') as build:
            packaging.build_distribution_frontends()
        self.assertEqual(build.call_args_list, [call(packaging.WIDGET)])

    def test_wheel_builds_the_widget_only_when_its_output_is_missing(self):
        with patch('solid_node_viewer.packaging.build_frontend') as build, \
             patch.object(packaging.WIDGET, 'output_exists', return_value=False):
            packaging.build_missing_frontends()
        build.assert_called_once_with(packaging.WIDGET)

    def test_wheel_builds_nothing_when_the_widget_is_already_built(self):
        with patch('solid_node_viewer.packaging.build_frontend') as build, \
             patch.object(packaging.WIDGET, 'output_exists', return_value=True):
            packaging.build_missing_frontends()
        build.assert_not_called()
