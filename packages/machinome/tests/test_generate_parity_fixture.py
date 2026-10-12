# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`tools/generate_parity_fixture.py`'s coverage check, task 4.1 (ADR-080).

`uncovered_builtins` used to read only the cases' own `expression` text.
With a `bindings` table, `sin(` can live in an entry and appear in no
case's own expression -- the sharing corpus (`tests/expression_project/
sharing.py`) is built exactly so `floor` reaches this scan only through a
binding, once for real. This is the tool's own coverage function under
direct test, so the guard is caught by the framework's suite -- not only
by running the generator by hand.

`DefaultFixturePathTest` pins where the tool writes when given no path:
the fixture the viewer's widget commits in the same checkout of the
repository, `packages/machinome-viewer/`, found from the framework's
directory without Git, so a worktree writes its own; and a refusal, before
anything is built, when there is none (change `join-viewer`).
"""

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL_PATH = os.path.join(ROOT, 'tools', 'generate_parity_fixture.py')


def _load_tool():
    """Load the generator as a module without running its `main()` --
    `spec_from_file_location` rather than a package import, because
    `tools/` is a script directory, not a package (no `__init__.py`), by
    design: this tool is meant to be run, not imported by a project."""
    spec = importlib.util.spec_from_file_location(
        'generate_parity_fixture', TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CoverageAcrossBindingsAndCasesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tool = _load_tool()

    def test_a_name_in_a_case_expression_is_covered_as_before(self):
        cases = [{'expression': '(floor($t) + 1.0)'}]

        self.assertNotIn('floor', self.tool.uncovered_builtins(cases, []))

    def test_a_name_appearing_only_inside_a_binding_is_covered(self):
        """The exact hole design.md D10 names: a builtin call moved
        entirely into a `bindings` entry, with no case's own expression
        naming it."""
        cases = [{'expression': '_b0'}]
        bindings = [{'name': '_b0', 'expression': 'floor($t)'}]

        without_the_table = self.tool.uncovered_builtins(cases, [])
        with_the_table = self.tool.uncovered_builtins(cases, bindings)

        self.assertIn('floor', without_the_table)
        self.assertNotIn('floor', with_the_table)

    def test_a_name_in_neither_still_fails(self):
        cases = [{'expression': '_b0'}]
        bindings = [{'name': '_b0', 'expression': '($t + 1.0)'}]

        self.assertIn('floor', self.tool.uncovered_builtins(cases, bindings))

    def test_the_real_fixture_build_covers_every_emitted_builtin(self):
        """The full regeneration: every corpus together, coverage checked
        the way `build()` checks it before writing anything."""
        fixture = self.tool.build()

        self.assertEqual(
            self.tool.uncovered_builtins(fixture['cases'], fixture['bindings']),
            [])

    def test_the_sharing_corpus_puts_floor_only_inside_a_binding(self):
        """Not just a synthetic case above: the real sharing corpus's own
        `floor` call reaches the fixture exclusively through a binding
        entry, because `time_only`'s and `time_nested`'s cases hold only
        the bound name or a superset expression naming it -- proving the
        scan this task adds is load-bearing for a real corpus, not only
        for a hand-built example."""
        cases, table, bindings = self.tool.sharing_cases()

        self.assertTrue(bindings)
        case_text = ' '.join(case['expression'] for case in cases)
        binding_text = ' '.join(entry['expression'] for entry in bindings)
        self.assertNotIn('floor(', case_text)
        self.assertIn('floor(', binding_text)


#: The viewer's widget sources, from the repository's root (change
#: `join-viewer`).
VIEWER_SOURCE = ('packages', 'machinome-viewer', 'machinome', 'viewer', 'web',
                 'widget', 'src')

# The smallest fixture `main()` can summarise after writing it.
EMPTY_FIXTURE = {
    'bindings': [], 'cases': [], 'conversions': [],
    'flexible': {'cases': [], 'vertex_count': 0, 'sentinels': []},
}


class DefaultFixturePathTest(TestCase):
    """With no argument, the generator writes the fixture the viewer's
    widget commits in the same checkout of the repository, found from the
    framework's directory without Git, and refuses before building when the
    checkout holds no viewer (change `join-viewer`)."""

    @classmethod
    def setUpClass(cls):
        cls.tool = _load_tool()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix='machinome-parity-fixture-')
        self.addCleanup(temporary.cleanup)
        self.repository = Path(temporary.name).resolve()
        self.framework = self.repository / 'packages' / 'machinome'
        self.viewer_source = self.repository.joinpath(*VIEWER_SOURCE)
        self.framework.mkdir(parents=True)
        self.viewer_source.mkdir(parents=True)
        self.expected = str(self.viewer_source / 'parity-fixture.json')

    def test_the_default_is_the_viewer_package_of_the_same_checkout(self):
        self.assertEqual(self.tool.default_fixture(str(self.framework)),
                         self.expected)

    def test_no_git_command_is_run(self):
        with patch.object(subprocess, 'run',
                          side_effect=AssertionError('ran')) as run:
            self.tool.default_fixture(str(self.framework))

        run.assert_not_called()

    def test_no_viewer_package_is_refused_by_name(self):
        shutil.rmtree(self.repository / 'packages' / 'machinome-viewer')

        with self.assertRaises(SystemExit) as raised:
            self.tool.default_fixture(str(self.framework))

        message = str(raised.exception.code)
        self.assertIn(str(self.viewer_source), message)
        self.assertIn('argument', message)

    def test_the_refusal_comes_before_anything_is_built(self):
        shutil.rmtree(self.repository / 'packages' / 'machinome-viewer')

        with patch.object(self.tool, 'ROOT', str(self.framework)), \
                patch.object(self.tool, 'build',
                             side_effect=AssertionError('built')) as build:
            with self.assertRaises(SystemExit):
                self.tool.main([])

        build.assert_not_called()

    def test_an_explicit_path_is_written_wherever_the_checkout_stands(self):
        shutil.rmtree(self.repository / 'packages' / 'machinome-viewer')
        output = self.repository / 'out.json'

        with patch.object(self.tool, 'ROOT', str(self.framework)), \
                patch.object(self.tool, 'build', return_value=EMPTY_FIXTURE):
            self.tool.main([str(output)])

        self.assertEqual(json.loads(output.read_text()), EMPTY_FIXTURE)
