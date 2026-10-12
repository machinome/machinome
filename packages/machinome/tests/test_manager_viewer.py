# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`machinome viewer`: the web viewer's report, asked through the seam
`machinome.viewer` (OpenSpec change `viewer-seam`), printed as JSON."""

import io
import json
from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from unittest import TestCase
from unittest.mock import patch

import machinome.viewer as viewers
from machinome.manager.viewer import Viewer

REPORT = {'path': '/tmp/machinome-viewer.js', 'index': '/tmp/index.html',
          'apiVersion': 5, 'version': '0.1.0'}


def reported(report):
    return patch.object(viewers.viewer('web'), 'describe',
                        return_value=report)


class ViewerCommandTest(TestCase):

    def test_reports_the_installed_viewer_as_json(self):
        output = io.StringIO()
        with reported(REPORT), redirect_stdout(output):
            Viewer().handle(Namespace())
        self.assertEqual(json.loads(output.getvalue()), REPORT)

    def refused(self, refusal):
        output, errors = io.StringIO(), io.StringIO()
        with refusal, redirect_stdout(output), redirect_stderr(errors), \
                self.assertRaises(SystemExit) as raised:
            Viewer().handle(Namespace())
        self.assertEqual(raised.exception.code, 1)
        self.assertEqual(output.getvalue(), '')
        return errors.getvalue()

    def test_missing_viewer_exits_with_remedy_and_no_stdout(self):
        errors = self.refused(patch.object(
            viewers, 'viewer', side_effect=viewers.absent('web')))
        self.assertEqual(
            errors, 'the web viewer needs machinome.viewer.web, which is not '
                    'installed; install it with \'pip install '
                    '"machinome[viewer]"\'\n')

    def test_a_viewer_without_its_bundle_speaks_for_itself(self):
        errors = self.refused(patch.object(
            viewers.viewer('web'), 'describe',
            side_effect=FileNotFoundError('Viewer bundle not found; build it')))
        self.assertEqual(errors, 'Viewer bundle not found; build it\n')


class DocumentVersionsReportTest(TestCase):
    """`machinome viewer` is the one report, so a field the viewer added
    reaches a host through it unchanged."""

    def test_the_report_carries_the_document_versions(self):
        report = dict(REPORT, documentVersions=[1, 2, 3, 4, 5])
        output = io.StringIO()
        with reported(report), redirect_stdout(output):
            Viewer().handle(Namespace())
        self.assertEqual(json.loads(output.getvalue())['documentVersions'],
                         [1, 2, 3, 4, 5])
