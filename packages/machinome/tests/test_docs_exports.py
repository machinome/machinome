# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The documentation build produces nothing.

Every ``.. machinome::`` directive names a directory that `machinome export`
produced, and the Sphinx extension fails the build if it is not there. Those
directories are committed under ``docs/_exports/``: the tutorial's models,
exported with ``--no-widget`` so the extension completes them from the
repository's own web viewer, which the framework finds through its seam
``machinome.viewer``. Nothing is exported while the manual builds; the build
installs ``docs/requirements.txt`` and nothing else of Python, and builds the
viewer's bundle with npm from the root's lock first (change `viewer-seam`,
design.md Decision 13).

It used to be otherwise. Three example machines were exported from Foundry
submodules by a step written twice, once in ``.readthedocs.yaml`` and once
in the GitHub Actions ``docs`` job, with OpenSCAD, Node and the mechanics
package installed for them. The Read the Docs build of the 0.7.0 tag ran
into the service's 900-second limit inside the third export (24 September
2026), and the machines moved to machinome.org.

These tests hold the rule so it cannot creep back: every embedded export is
committed, and neither build configuration exports, installs from a
repository, names a system package or a submodule, nor runs Node for
anything but the viewer's widget. The CI docs job builds through the root
Makefile's `docs` target, whose recipe is held to the same rule (change
`release-tooling`).
"""

import ast
import os
import re
import unittest
from pathlib import Path

import yaml


# The framework's directory, packages/machinome of the repository, whose
# root holds the CI workflow (change `monorepo-layout`).
PACKAGE = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[3]
DOCS = PACKAGE / 'docs'
WORKFLOW = REPOSITORY / '.github' / 'workflows' / 'python-app.yml'
MAKEFILE = REPOSITORY / 'Makefile'
READTHEDOCS = PACKAGE / '.readthedocs.yaml'
REQUIREMENTS = 'docs/requirements.txt'

# The viewer's widget, the one npm workspace member the manual needs, and
# the two Node steps that build it from the root's lock.
WIDGET = 'packages/machinome-viewer/machinome/viewer/web/widget'
NODE_STEPS = ['npm ci --no-audit --no-fund',
              f'npm run build --workspace {WIDGET}']

# Read the Docs reads every path of its configuration from the repository
# root, not from the file's directory.
FROM_THE_ROOT = 'packages/machinome/'

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

    Paths are relative to the package directory, resolved the way the directive resolves
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
                          export.relative_to(PACKAGE).as_posix()))
    return found


def docs_job():
    return yaml.safe_load(WORKFLOW.read_text())['jobs']['docs']


def docs_recipe():
    """The recipe of the root Makefile's `docs` target, continued lines
    joined."""
    text = MAKEFILE.read_text().replace('\\\n', ' ')
    found = re.search(r'^docs:[^\n]*\n((?:\t[^\n]*(?:\n|$))*)', text,
                      flags=re.M)
    if found is None:
        raise AssertionError(f'{MAKEFILE} has no docs target')
    return found[1]


def readthedocs():
    return yaml.safe_load(READTHEDOCS.read_text())


def requirements():
    """The distributions docs/requirements.txt names, comments dropped."""
    lines = (PACKAGE / REQUIREMENTS).read_text().splitlines()
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
                path = PACKAGE / export
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
        self.assertFalse((REPOSITORY / '.gitmodules').exists(),
                         '.gitmodules exists; the manual pins no submodule')
        self.assertEqual(
            sorted(p.name for p in DOCS.glob('example-*.rst')), [],
            'an example page exists; the examples page sends readers to '
            'machinome.org instead')


class ReadTheDocsBuildsNothingTest(unittest.TestCase):
    """.readthedocs.yaml installs docs/requirements.txt, builds the viewer's
    widget with Node 22 and runs Sphinx."""

    def setUp(self):
        self.config = readthedocs()

    def test_one_build_job_builds_the_widget(self):
        build = self.config['build']
        self.assertEqual(build.get('jobs'), {'pre_build': NODE_STEPS})
        self.assertNotIn('apt_packages', build, build.get('apt_packages'))
        self.assertNotIn('commands', build, build.get('commands'))

    def test_python_and_node_are_the_tools(self):
        self.assertEqual(self.config['build']['tools'],
                         {'python': '3.12', 'nodejs': '22'})

    def test_no_submodules(self):
        self.assertNotIn('submodules', self.config)

    def test_installs_the_requirements_alone(self):
        self.assertEqual(
            self.config['python']['install'],
            [{'requirements': FROM_THE_ROOT + REQUIREMENTS}],
        )

    def test_configures_the_framework_manual(self):
        self.assertEqual(self.config['sphinx']['configuration'],
                         FROM_THE_ROOT + 'docs/conf.py')


class ActionsDocsJobBuildsNothingTest(unittest.TestCase):
    """The CI docs job does what Read the Docs does, and fails on warnings:
    it runs the root Makefile's `docs` target, whose recipe installs the
    requirements alone into an environment of its own and builds with -W
    (change `release-tooling`)."""

    def setUp(self):
        self.steps = docs_job()['steps']
        self.recipe = docs_recipe()

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
                self.assertNotIn('apt', uses, 'the docs job installs an '
                                 'apt package')
        with self.subTest(step='the Makefile\'s docs target'):
            for what, pattern in FORBIDDEN.items():
                self.assertIsNone(
                    pattern.search(self.recipe),
                    f'the Makefile\'s docs target has a {what}; the '
                    'documentation build produces nothing')
            for tool in (r'\bnpm\b', r'\bnode\b', r'\bapt\b',
                         r'\bsubmodule'):
                self.assertIsNone(
                    re.search(tool, self.recipe),
                    f'the Makefile\'s docs target runs {tool}')

    def test_the_job_runs_the_makefile_s_docs_target(self):
        runs = [step['run'].strip() for step in self.steps if 'run' in step]
        self.assertEqual(runs, ['make widget', 'make docs'])

    def test_the_job_installs_node_22(self):
        nodes = [step for step in self.steps
                 if step.get('uses', '').startswith('actions/setup-node')]
        self.assertEqual(len(nodes), 1, self.steps)
        self.assertEqual(str(nodes[0]['with']['node-version']), '22')

    def test_the_docs_target_builds_the_bundle_first(self):
        target = re.search(r'^docs:([^#\n]*)', MAKEFILE.read_text(),
                           flags=re.M)
        self.assertIsNotNone(target)
        self.assertEqual(target[1].split(), ['bundle'])

    def test_installs_the_requirements_alone(self):
        installs = re.findall(
            r'pip install\s+(?:--python\s+\S+\s+)?(.+)', self.recipe)
        self.assertEqual(installs, [f'-r {FROM_THE_ROOT}{REQUIREMENTS}'])

    def test_builds_with_warnings_as_errors(self):
        self.assertRegex(self.recipe, r'sphinx\b.*\s-W\b',
                         'the docs target does not build the manual with -W')


class StrictBuildTest(unittest.TestCase):
    """Both warnings-as-errors builds refuse a cross-reference to
    nothing."""

    def test_the_configuration_is_nitpicky(self):
        tree = ast.parse((DOCS / 'conf.py').read_text())
        values = {target.id: node.value
                  for node in tree.body if isinstance(node, ast.Assign)
                  for target in node.targets
                  if isinstance(target, ast.Name)}
        self.assertIn('nitpicky', values,
                      'docs/conf.py does not set nitpicky')
        self.assertIs(ast.literal_eval(values['nitpicky']), True)

    def test_read_the_docs_fails_on_warnings(self):
        self.assertIs(readthedocs()['sphinx']['fail_on_warning'], True)


class DocsRequirementsTest(unittest.TestCase):
    """docs/requirements.txt is the whole of what the build installs."""

    def test_names_published_distributions_only(self):
        for line in requirements():
            with self.subTest(requirement=line):
                self.assertRegex(line, REQUIREMENT)

    def test_names_sphinx_and_its_theme_alone(self):
        """The committed exports carry no widget; the repository's viewer
        completes them at build time, so no published viewer is named."""
        names = [re.split(r'[\[=<>!~ ]', line, 1)[0]
                 for line in requirements()]
        self.assertEqual(names, ['sphinx', 'sphinx_rtd_theme'])

    def test_the_configuration_takes_the_repository_s_viewer(self):
        """docs/conf.py puts every package directory on the path, the
        viewer's among them, before the framework's seam is imported."""
        import sys
        source = (DOCS / 'conf.py').read_text()
        head = source[:source.index('# -- Project information')]
        before = list(sys.path)
        cwd = os.getcwd()
        try:
            os.chdir(DOCS)
            exec(compile(head, str(DOCS / 'conf.py'), 'exec'), {})
            added = sys.path[:len(sys.path) - len(before)]
        finally:
            os.chdir(cwd)
            sys.path[:] = before
        self.assertIn(str(REPOSITORY / 'packages' / 'machinome-viewer'),
                      added)


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
        web = sphinx_module.viewers.viewer('web')
        with patch.object(sphinx_module, 'logger', logger), \
             patch.object(web, 'document_versions', return_value=versions):
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
                 and name != 'machinome.viewer'}
        self.assertEqual(heavy, set(), heavy)


if __name__ == '__main__':
    unittest.main()
