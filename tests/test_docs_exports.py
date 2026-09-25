# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The documentation build produces nothing.

Every ``.. machinome::`` directive names a directory that `machinome export`
produced, and the Sphinx extension fails the build if it is not there. Those
directories are committed under ``docs/_exports/``: the tutorial's models,
exported with ``--no-widget`` so the extension completes them from the
installed ``machinome-viewer`` package. Nothing is exported while the manual
builds, and the build installs ``docs/requirements.txt`` and nothing else.

It used to be otherwise. Three example machines were exported from Foundry
submodules by a step written twice, once in ``.readthedocs.yaml`` and once
in the GitHub Actions ``docs`` job, with OpenSCAD, Node and the mechanics
package installed for them. The Read the Docs build of the 0.7.0 tag ran
into the service's 900-second limit inside the third export (24 September
2026), and the machines moved to machinome.org.

These tests hold the rule so it cannot creep back: every embedded export is
committed, and neither build configuration exports, installs from a
repository, names a system package, a Node tool or a submodule.
"""

import os
import re
import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / 'docs'
WORKFLOW = REPO / '.github' / 'workflows' / 'python-app.yml'
READTHEDOCS = REPO / '.readthedocs.yaml'
REQUIREMENTS = 'docs/requirements.txt'

# Every export a page embeds lives here, committed.
COMMITTED = 'docs/_exports/'

# Only a directive at column 0 asks for an export. reference/sphinx.rst
# indents one inside a literal block to show the syntax; that is not a
# request to embed anything.
DIRECTIVE = re.compile(r'^\.\. +machinome:: +(\S+)', re.MULTILINE)

# What a build step must not do: run an export, install from a repository,
# or reach for a submodule.
FORBIDDEN = {
    'export': re.compile(r'\bexport\s+-o\b'),
    'repository install': re.compile(r'git\+|@\s*git|\.git\b'),
    'submodule': re.compile(r'submodule', re.IGNORECASE),
}

# A requirement the build may name: a distribution, optionally with extras,
# never a URL, a path or a VCS reference.
REQUIREMENT = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*(\[[^\]]+\])?$')

# Mirrors exclude_patterns in docs/conf.py: _build is output.
NOT_OUR_DOCS = ('_build',)


def embedded_exports():
    """(document, export directory) for every directive in the docs.

    Paths are repo-relative, resolved the way the directive resolves
    them: against the document, or against the Sphinx source directory
    when the argument is absolute.
    """
    found = []
    for rst in sorted(DOCS.rglob('*.rst')):
        relative = rst.relative_to(DOCS)
        if relative.parts[0] in NOT_OUR_DOCS:
            continue
        for target in DIRECTIVE.findall(rst.read_text()):
            base = DOCS if target.startswith('/') else rst.parent
            export = Path(os.path.normpath(base / target.lstrip('/')))
            found.append((relative.as_posix(),
                          export.relative_to(REPO).as_posix()))
    return found


def docs_job():
    return yaml.safe_load(WORKFLOW.read_text())['jobs']['docs']


def readthedocs():
    return yaml.safe_load(READTHEDOCS.read_text())


def requirements():
    """The distributions docs/requirements.txt names, comments dropped."""
    lines = (REPO / REQUIREMENTS).read_text().splitlines()
    return [line.strip() for line in lines
            if line.strip() and not line.lstrip().startswith('#')]


class EmbeddedExportsAreCommittedTest(unittest.TestCase):
    """Every model a page shows is a committed export."""

    def setUp(self):
        self.embedded = embedded_exports()

    def test_directives_are_found(self):
        """Guards the other tests from passing on an empty scan."""
        self.assertTrue(
            self.embedded,
            f'No `.. machinome::` directives found under {DOCS}. Either '
            'the documentation stopped embedding exports or DIRECTIVE no '
            'longer matches how they are written.',
        )

    def test_every_embedded_export_is_committed(self):
        """A directive names a directory under docs/_exports/, and it is
        there with its manifest: nothing is exported at build time."""
        for document, export in self.embedded:
            with self.subTest(document=document, export=export):
                self.assertTrue(
                    export.startswith(COMMITTED),
                    f'docs/{document} embeds {export}, which is not under '
                    f'{COMMITTED}. The documentation build produces '
                    'nothing: export the model with `machinome export '
                    '--no-widget` and commit it there.',
                )
                path = REPO / export
                self.assertTrue(
                    path.is_dir(),
                    f'docs/{document} embeds {export}, which is committed '
                    'documentation content but is missing. Restore it, or '
                    'regenerate it with `machinome export`.',
                )
                self.assertTrue(
                    (path / 'manifest.json').is_file(),
                    f'docs/{document} embeds {export}, which has no '
                    'manifest.json, so it is not a `machinome export` output '
                    'the directive can read.',
                )

    def test_no_example_is_pinned(self):
        """The manual pins no external repository: the real machines are
        on machinome.org, not built here."""
        self.assertFalse((REPO / '.gitmodules').exists(),
                         '.gitmodules exists; the manual pins no submodule')
        self.assertEqual(
            sorted(p.name for p in DOCS.glob('example-*.rst')), [],
            'an example page exists; the examples page sends readers to '
            'machinome.org instead')


class ReadTheDocsBuildsNothingTest(unittest.TestCase):
    """.readthedocs.yaml installs docs/requirements.txt and runs Sphinx."""

    def setUp(self):
        self.config = readthedocs()

    def test_no_build_jobs(self):
        build = self.config['build']
        self.assertNotIn('jobs', build, build.get('jobs'))
        self.assertNotIn('apt_packages', build, build.get('apt_packages'))
        self.assertNotIn('commands', build, build.get('commands'))

    def test_python_is_the_only_tool(self):
        self.assertEqual(list(self.config['build']['tools']), ['python'])

    def test_no_submodules(self):
        self.assertNotIn('submodules', self.config)

    def test_installs_the_requirements_alone(self):
        self.assertEqual(
            self.config['python']['install'],
            [{'requirements': REQUIREMENTS}],
        )


class ActionsDocsJobBuildsNothingTest(unittest.TestCase):
    """The CI docs job does what Read the Docs does, and fails on
    warnings."""

    def setUp(self):
        self.steps = docs_job()['steps']

    def test_no_forbidden_step(self):
        for step in self.steps:
            text = '\n'.join(str(v) for v in step.values())
            name = step.get('name') or step.get('uses') or text[:40]
            with self.subTest(step=name):
                for what, pattern in FORBIDDEN.items():
                    self.assertIsNone(
                        pattern.search(text),
                        f'the docs job step {name!r} has a {what}; the '
                        'documentation build produces nothing')
                self.assertNotIn(
                    'submodules', step.get('with') or {},
                    'the docs job checks out submodules')
                uses = step.get('uses', '')
                self.assertFalse(uses.startswith('actions/setup-node'),
                                 'the docs job installs Node')
                self.assertNotIn('apt', uses, 'the docs job installs an '
                                 'apt package')

    def test_installs_the_requirements_alone(self):
        installs = []
        for step in self.steps:
            installs += re.findall(r'pip install\s+(.+)', step.get('run', ''))
        self.assertEqual(installs, [f'-r {REQUIREMENTS}'])

    def test_builds_with_warnings_as_errors(self):
        runs = [step.get('run', '') for step in self.steps]
        self.assertTrue(
            any(re.search(r'sphinx\b.*\s-W\b', run) for run in runs),
            'the docs job does not build the manual with -W')


class DocsRequirementsTest(unittest.TestCase):
    """docs/requirements.txt is the whole of what the build installs."""

    def test_names_published_distributions_only(self):
        for line in requirements():
            with self.subTest(requirement=line):
                self.assertRegex(line, REQUIREMENT)

    def test_names_the_viewer(self):
        """The committed exports carry no widget; the published viewer
        completes them at build time."""
        names = [re.split(r'[\[=<>!~ ]', line, 1)[0]
                 for line in requirements()]
        self.assertIn('machinome-viewer', names)


class EmbeddedExportVersionWarningTest(unittest.TestCase):
    """(7.4b) The directive embeds a COMMITTED export it does not
    produce and cannot fix. It warns about a version the installed
    viewer cannot read and does not fail the build -- and it reads the
    version off the manifest it already opened, loading no CAD runtime
    to do it."""

    def warned(self, manifest, versions):
        from unittest.mock import Mock, patch

        from machinome import sphinx as sphinx_module

        directive = sphinx_module.Machinome.__new__(sphinx_module.Machinome)
        logger = Mock()
        with patch.object(sphinx_module, 'logger', logger), \
             patch.object(sphinx_module.viewer_bundle, 'document_versions',
                          return_value=versions):
            directive.warn_unreadable('docs/export', manifest)
        return logger

    def test_an_embedded_version_five_export_warns(self):
        logger = self.warned({'format': 'machinome-export', 'version': 5},
                             [1, 2, 3, 4])
        self.assertEqual(logger.warning.call_count, 1)
        message = logger.warning.call_args[0][0]
        self.assertIn('docs/export', message)
        self.assertIn('5', message)
        self.assertIn('1, 2, 3, 4', message)

    def test_an_export_the_viewer_can_read_warns_about_nothing(self):
        logger = self.warned({'format': 'machinome-export', 'version': 5},
                             [1, 2, 3, 4, 5])
        logger.warning.assert_not_called()

    def test_the_extension_loads_no_cad_runtime(self):
        import ast
        import inspect

        from machinome import sphinx as sphinx_module

        tree = ast.parse(inspect.getsource(sphinx_module))
        modules = {node.module for node in ast.walk(tree)
                   if isinstance(node, ast.ImportFrom) and node.module}
        modules |= {alias.name for node in ast.walk(tree)
                    if isinstance(node, ast.Import) for alias in node.names}
        heavy = {name for name in modules
                 if name.startswith('machinome.')
                 and not name.startswith('machinome.viewers')}
        self.assertEqual(heavy, set(), heavy)


if __name__ == '__main__':
    unittest.main()
