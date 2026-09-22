# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The framework's one lookup of the viewer it does not carry.

machinome-viewer registers the `machinome.viewer` entry point; the
framework resolves it and nothing else. These tests drive the lookup with
fake entry points so they hold whether or not the viewer is installed here.
"""

import ast
import inspect
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from machinome.viewers import bundle
from machinome.viewers.bundle import ViewerUnavailable


def fake_entry(result=None, error=None):
    entry = Mock()
    entry.name = 'bundle'
    describe = Mock(side_effect=error) if error else Mock(return_value=result)
    entry.load.return_value = describe
    return entry


REPORT = {
    'path': '/site/machinome_viewer/widget/dist/machinome-viewer.js',
    'index': '/site/machinome_viewer/widget/index.html',
    'apiVersion': 5,
    'version': '0.1.0',
}


class LookupTest(TestCase):

    def test_the_lookup_imports_only_the_standard_library(self):
        tree = ast.parse(inspect.getsource(bundle))
        imports = {node.names[0].name for node in ast.walk(tree)
                   if isinstance(node, ast.Import)}
        froms = {node.module for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom)}
        self.assertTrue(imports <= {'sys'}, imports)
        self.assertTrue(froms <= {'importlib.metadata', 'pathlib'}, froms)

    def test_without_the_entry_point_the_viewer_is_not_installed(self):
        with patch.object(bundle, 'entry_points', return_value=[]):
            self.assertFalse(bundle.has_bundle())
            with self.assertRaises(ViewerUnavailable) as raised:
                bundle.describe()
            remedy = bundle.missing_bundle_remedy()
        self.assertIn('pip install "machinome[viewer]"', remedy)
        self.assertEqual(str(raised.exception), remedy)
        self.assertNotIn('npm', remedy)

    def test_the_entry_point_answers_paths_and_version(self):
        with patch.object(bundle, 'entry_points', return_value=[fake_entry(REPORT)]):
            self.assertTrue(bundle.has_bundle())
            self.assertEqual(bundle.describe(), REPORT)
            self.assertEqual(bundle.bundle_path(), Path(REPORT['path']))
            self.assertEqual(bundle.index_path(), Path(REPORT['index']))
            self.assertEqual(bundle.api_version(), 5)

    def test_an_installed_viewer_without_a_bundle_speaks_for_itself(self):
        entry = fake_entry(error=FileNotFoundError('Viewer bundle not found; run npm'))
        with patch.object(bundle, 'entry_points', return_value=[entry]):
            self.assertFalse(bundle.has_bundle())
            self.assertEqual(bundle.missing_bundle_remedy(),
                             'Viewer bundle not found; run npm')

    def test_the_lookup_asks_the_documented_group_for_the_documented_entry(self):
        other = fake_entry(REPORT)
        other.name = 'something-else'
        ours = fake_entry(REPORT)
        ours.name = 'bundle'
        with patch.object(bundle, 'entry_points', return_value=[other, ours]) as points:
            bundle.describe()
        points.assert_called_once_with(group='machinome.viewer')
        other.load.assert_not_called()

    def test_the_viewer_runs_through_this_interpreter(self):
        self.assertEqual(bundle.viewer_command(),
                         [sys.executable, '-m', 'machinome_viewer'])


class DocumentVersionsTest(TestCase):
    """The versions the installed viewer renders, asked of the report
    rather than inferred from the viewer's own release counter."""

    def test_endpoint_era_viewer_refuses_source_timed_export(self):
        report = dict(REPORT, apiVersion=23,
                      documentVersions=list(range(1, 11)))
        with patch.object(bundle, 'entry_points',
                          return_value=[fake_entry(report)]):
            message = bundle.unreadable_document(11)
        self.assertIn('11', message)
        self.assertIn('1, 2, 3, 4, 5, 6, 7, 8, 9, 10', message)
        report['apiVersion'] = 24
        report['documentVersions'].append(11)
        with patch.object(bundle, 'entry_points',
                          return_value=[fake_entry(report)]):
            self.assertIsNone(bundle.unreadable_document(11))

    def test_the_report_says_which_documents_the_viewer_renders(self):
        report = dict(REPORT, documentVersions=[1, 2, 3, 4, 5])
        with patch.object(bundle, 'entry_points',
                          return_value=[fake_entry(report)]):
            self.assertEqual(bundle.document_versions(), [1, 2, 3, 4, 5])

    def test_a_viewer_that_predates_the_field_renders_one_to_four(self):
        with patch.object(bundle, 'entry_points',
                          return_value=[fake_entry(REPORT)]):
            self.assertEqual(bundle.document_versions(), [1, 2, 3, 4])

    def test_without_a_viewer_there_is_nothing_to_warn_about(self):
        with patch.object(bundle, 'entry_points', return_value=[]):
            self.assertIsNone(bundle.unreadable_document(5))

    def test_a_version_the_viewer_cannot_read_names_the_three_facts(self):
        with patch.object(bundle, 'entry_points',
                          return_value=[fake_entry(REPORT)]):
            message = bundle.unreadable_document(5)
        self.assertIn('5', message)
        self.assertIn('1, 2, 3, 4', message)
        self.assertIn('0.1.0', message)

    def test_a_version_the_viewer_reads_warns_about_nothing(self):
        report = dict(REPORT, documentVersions=[1, 2, 3, 4, 5])
        with patch.object(bundle, 'entry_points',
                          return_value=[fake_entry(report)]):
            self.assertIsNone(bundle.unreadable_document(5))
            self.assertIsNone(bundle.unreadable_document(4))


class ClockedDocumentVersionTest(TestCase):
    """(7.5) The framework needs NO new way to detect that the installed
    viewer cannot read a clocked document: `documentVersions` already
    carries the fact, and version 8 is simply not in the list until the
    viewer's own cycle adds it.

    `bundle.py` itself is UNCHANGED by the OpenSpec change
    ``publish-the-clocked-machine`` -- these are added tests only.
    """

    def test_a_viewer_reporting_eight_reads_a_clocked_document(self):
        report = dict(REPORT, documentVersions=[1, 2, 3, 4, 5, 8])
        with patch.object(bundle, 'entry_points',
                          return_value=[fake_entry(report)]):
            self.assertIsNone(bundle.unreadable_document(8))
            self.assertIsNone(bundle.unreadable_document(5))

    def test_a_viewer_that_does_not_report_it_names_the_three_facts(self):
        report = dict(REPORT, documentVersions=[1, 2, 3, 4, 5])
        with patch.object(bundle, 'entry_points',
                          return_value=[fake_entry(report)]):
            message = bundle.unreadable_document(8)
        self.assertIn('8', message)
        self.assertIn('1, 2, 3, 4, 5', message)
        self.assertIn('0.1.0', message)

    def test_a_viewer_reporting_none_at_all_is_read_as_one_to_four(self):
        with patch.object(bundle, 'entry_points',
                          return_value=[fake_entry(REPORT)]):
            self.assertEqual(bundle.document_versions(), [1, 2, 3, 4])
            message = bundle.unreadable_document(8)
        self.assertIn('1, 2, 3, 4', message)

    def test_bundle_itself_is_unchanged_by_this_cycle(self):
        """The version comparison is the ONE thing consulted, and this
        cycle adds nothing to it: no clocked name appears in the module
        at all."""
        import inspect

        source = inspect.getsource(bundle)
        for named in ('clocked', 'State', 'states'):
            self.assertNotIn(named, source)
