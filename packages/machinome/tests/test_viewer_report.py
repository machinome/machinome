# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The report of the installed web viewer and the versions it reads, asked
through the seam `machinome.viewer` (OpenSpec change `viewer-seam`).

The framework finds the web viewer by importing `machinome.viewer.web` and
nothing else: no entry point is read, and none is declared. Its report is
the one `machinome-viewer describe` prints, and the sentence a producer
writes about a document it cannot read names the version written, the
versions the viewer reads and its distribution's version. These tests
stand the provider's answers in where they need a version the installed
viewer does not have.
"""

import ast
import json
import subprocess
import sys
from importlib.metadata import entry_points
from pathlib import Path
from unittest import TestCase, skipUnless
from unittest.mock import patch

import machinome.viewer as viewers
from machinome.viewer.web.bundle import has_bundle

ROOT = Path(__file__).resolve().parents[1]
SEAM = ROOT / 'machinome' / 'viewer' / '__init__.py'

web = viewers.viewer('web')


def reading(versions, version='0.1.0'):
    """The web viewer reading `versions`, released as `version`."""
    return (patch.object(web, 'document_versions', return_value=versions),
            patch.object(web, 'identity',
                         return_value=('machinome-viewer', version)))


class LookupTest(TestCase):

    def test_the_seam_imports_only_the_standard_library_and_extras(self):
        tree = ast.parse(SEAM.read_text())
        imported = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module)
        self.assertEqual(
            {name for name in imported
             if name.split('.')[0] == 'machinome'},
            {'machinome', 'machinome.extras'})
        self.assertFalse({name for name in imported
                          if name.split('.')[0] not in sys.stdlib_module_names
                          and name.split('.')[0] != 'machinome'})

    def test_no_entry_point_is_declared_or_read(self):
        self.assertEqual(list(entry_points(group='machinome.viewer')), [])
        self.assertNotIn('entry_points', SEAM.read_text())

    def test_the_web_viewer_is_found_at_its_address(self):
        self.assertEqual(web.__name__, 'machinome.viewer.web')
        self.assertIs(viewers.require('web', 'embed', 'machinome viewer'),
                      web)

    @skipUnless(has_bundle(), 'machinome-viewer has no built bundle')
    def test_the_report_is_the_one_the_viewer_s_own_command_prints(self):
        ours = subprocess.run(
            [sys.executable, '-c',
             'from machinome.cli import manage; manage()', 'viewer'],
            capture_output=True, text=True, timeout=120)
        theirs = subprocess.run(
            [sys.executable, '-m', 'machinome.viewer.web', 'describe'],
            capture_output=True, text=True, timeout=120)
        self.assertEqual((ours.returncode, theirs.returncode), (0, 0),
                         ours.stderr + theirs.stderr)
        self.assertEqual(ours.stdout, theirs.stdout)
        report = json.loads(ours.stdout)
        self.assertEqual(report['documentVersions'],
                         web.document_versions())
        self.assertEqual(report['version'], web.identity()[1])


class DocumentVersionsTest(TestCase):
    """The versions the installed viewer renders, asked of the provider
    rather than inferred from the viewer's own release counter."""

    def test_endpoint_era_viewer_refuses_source_timed_export(self):
        versions, identity = reading(list(range(1, 11)))
        with versions, identity:
            message = viewers.unreadable(11, 'web')
        self.assertIn('11', message)
        self.assertIn('1, 2, 3, 4, 5, 6, 7, 8, 9, 10', message)
        versions, identity = reading(list(range(1, 12)))
        with versions, identity:
            self.assertIsNone(viewers.unreadable(11, 'web'))

    def test_the_provider_says_which_documents_the_viewer_renders(self):
        from machinome.viewer.web.bundle import document_versions
        self.assertEqual(web.document_versions(), document_versions())
        self.assertTrue(web.readable(web.document_versions()[-1]))

    def test_without_a_viewer_there_is_nothing_to_warn_about(self):
        with patch.object(viewers, 'viewer',
                          side_effect=viewers.absent('web')):
            self.assertIsNone(viewers.unreadable(5, 'web'))

    def test_a_version_the_viewer_cannot_read_names_the_three_facts(self):
        versions, identity = reading([1, 2, 3, 4])
        with versions, identity:
            message = viewers.unreadable(5, 'web')
        self.assertEqual(
            message, 'this model needs document version 5, and the installed '
                     'web viewer renders 1, 2, 3, 4 (machinome-viewer 0.1.0)')

    def test_a_version_the_viewer_reads_warns_about_nothing(self):
        versions, identity = reading([1, 2, 3, 4, 5])
        with versions, identity:
            self.assertIsNone(viewers.unreadable(5, 'web'))
            self.assertIsNone(viewers.unreadable(4, 'web'))


class ClockedDocumentVersionTest(TestCase):
    """(7.5) The framework needs NO new way to detect that the installed
    viewer cannot read a clocked document: the versions it reads already
    carry the fact, and version 8 is simply not in the list until the
    viewer's own cycle adds it."""

    def test_a_viewer_reporting_eight_reads_a_clocked_document(self):
        versions, identity = reading([1, 2, 3, 4, 5, 8])
        with versions, identity:
            self.assertIsNone(viewers.unreadable(8, 'web'))
            self.assertIsNone(viewers.unreadable(5, 'web'))

    def test_a_viewer_that_does_not_report_it_names_the_three_facts(self):
        versions, identity = reading([1, 2, 3, 4, 5])
        with versions, identity:
            message = viewers.unreadable(8, 'web')
        self.assertIn('8', message)
        self.assertIn('1, 2, 3, 4, 5', message)
        self.assertIn('0.1.0', message)

    def test_the_seam_names_no_clocked_thing(self):
        """The version comparison is the ONE thing consulted: no clocked
        name appears in the seam at all."""
        source = SEAM.read_text()
        for named in ('clocked', 'State', 'states'):
            self.assertNotIn(named, source)
