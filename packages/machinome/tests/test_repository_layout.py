# Machinome - Source code for machines
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The framework is the package directory `packages/machinome` of a monorepo.

The repository `machinome/machinome` holds each of its distributions in a
directory under `packages/` named as the distribution; the framework is
`packages/machinome/`. The root holds the repository's record and tooling:
the one licence, the contributor guide, the AI-use statement, the history,
the CI, a uv workspace with its lock, `scripts/check-dist`, `context7.json`
and the record of the campaigns that span packages. The package directory
reaches the five shared files through relative symbolic links, which
setuptools carries into the archives as regular files (change
`monorepo-layout`, ADR-182).

These tests pin the tree that makes that true. They read a checkout: an
unpacked sdist has no repository above it. `scripts/check-dist` proves the
archives built from the tree.
"""

import json
import os
import re
import tomllib
import unittest
from pathlib import Path

import yaml


PACKAGE = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[3]

#: The files the package directory reaches at the root by a symlink.
SHARED = ('LICENSE', 'LICENSES', 'HISTORY.rst', 'CONTRIBUTING.rst',
          'AI-USE.md')

#: The framework's entries, which live in its directory and never at the
#: repository root.
FRAMEWORK_ENTRIES = (
    'machinome', 'tests', 'docs', 'openspec', 'tools', 'spike', 'README.rst',
    'CREDITS.md', 'MANIFEST.in', 'setup.cfg', 'tox.ini', 'Makefile',
    'requirements.txt', 'requirements_dev.txt', '.readthedocs.yaml',
)

WORKFLOW = REPOSITORY / '.github' / 'workflows' / 'python-app.yml'

#: A link into the repository on GitHub, and the path it names.
GITHUB_PATH = re.compile(
    r'https://github\.com/machinome/machinome/(?:blob|tree)/main/'
    r'([^\s>)`#]+)')

#: A reStructuredText hyperlink with an embedded target.
RST_LINK = re.compile(r'`[^`<]*<([^>`]+)>`_', re.S)

#: A Markdown link target.
MARKDOWN_LINK = re.compile(r'\]\(([^)\s]+)\)')


def read_toml(path):
    return tomllib.loads(path.read_text())


def distribution_name(directory):
    return read_toml(directory / 'pyproject.toml')['project']['name']


def conf_value(name):
    conf = (PACKAGE / 'docs' / 'conf.py').read_text()
    return re.search(rf"^{name} = '([^']*)'", conf, flags=re.M)[1]


def relative(target):
    """A link target that names a file of the checkout."""
    return ('://' not in target and not target.startswith(('#', 'mailto:'))
            and not target.endswith('_'))


def package_directories():
    return sorted(path for path in (REPOSITORY / 'packages').iterdir()
                  if path.is_dir())


class ThePlaceTest(unittest.TestCase):
    """The framework is `packages/machinome` of a git repository."""

    def test_the_package_directory_is_named_as_its_distribution(self):
        self.assertEqual(
            PACKAGE, REPOSITORY / 'packages' / 'machinome',
            f'the framework is at {PACKAGE}, not at packages/machinome of '
            f'the repository {REPOSITORY}')
        self.assertEqual(PACKAGE.name, distribution_name(PACKAGE))
        self.assertTrue((REPOSITORY / '.git').exists(),
                        f'{REPOSITORY} is not the root of a git checkout')


class TheSharedFilesTest(unittest.TestCase):
    """The licence is stated once: the package reaches the root's files."""

    def test_each_shared_file_is_a_relative_link_to_the_root(self):
        for name in SHARED:
            with self.subTest(entry=name):
                link = PACKAGE / name
                self.assertTrue(link.is_symlink(),
                                f'{link} is not a symbolic link')
                self.assertEqual(os.readlink(link), f'../../{name}')
                self.assertEqual(link.resolve(), REPOSITORY / name)
                self.assertTrue((REPOSITORY / name).exists(),
                                f'{REPOSITORY / name} is missing')
                self.assertFalse((REPOSITORY / name).is_symlink(),
                                 f'{REPOSITORY / name} is itself a link')


class TheManifestTest(unittest.TestCase):
    """The archives still name the five files by their package names."""

    def test_the_sdist_manifest_names_the_shared_files(self):
        lines = (PACKAGE / 'MANIFEST.in').read_text().splitlines()
        for line in ('include AI-USE.md', 'include CONTRIBUTING.rst',
                     'include HISTORY.rst', 'include LICENSE',
                     'recursive-include LICENSES *.txt'):
            with self.subTest(line=line):
                self.assertIn(line, lines)

    def test_the_wheel_names_the_licence_files(self):
        project = read_toml(PACKAGE / 'pyproject.toml')['project']
        self.assertEqual(project['license-files'],
                         ['LICENSE', 'LICENSES/*.txt'])


class TheWorkspaceTest(unittest.TestCase):
    """The root manifest is a uv workspace with no distribution of its own."""

    def setUp(self):
        self.root = read_toml(REPOSITORY / 'pyproject.toml')

    def test_the_root_declares_no_distribution(self):
        self.assertNotIn('project', self.root,
                         'the root pyproject.toml declares a [project] table')

    def test_the_members_are_the_package_directories(self):
        self.assertEqual(self.root['tool']['uv']['workspace']['members'],
                         ['packages/*'])
        for directory in package_directories():
            with self.subTest(member=directory.name):
                self.assertTrue((directory / 'pyproject.toml').is_file(),
                                f'{directory} holds no pyproject.toml')

    def test_the_framework_is_a_workspace_source(self):
        self.assertEqual(self.root['tool']['uv']['sources']['machinome'],
                         {'workspace': True})

    def test_every_member_installs_editable_in_compat_mode(self):
        self.assertEqual(self.root['tool']['uv']['config-settings'],
                         {'editable_mode': 'compat'})

    def test_the_default_group_is_the_framework_dev_extra(self):
        self.assertEqual(self.root['dependency-groups']['dev'],
                         ['machinome[dev]'])

    def test_the_lock_records_the_member_editable(self):
        lock = REPOSITORY / 'uv.lock'
        self.assertTrue(lock.is_file(), f'{lock} is missing')
        self.assertIn('source = { editable = "packages/machinome" }',
                      lock.read_text())


class TheIndexTest(unittest.TestCase):
    """One context7.json, at the root, excluding folders that exist."""

    def test_context7_is_the_repository_s(self):
        self.assertFalse((PACKAGE / 'context7.json').exists(),
                         'context7.json is in the package directory')
        index = json.loads((REPOSITORY / 'context7.json').read_text())
        for folder in index['excludeFolders']:
            with self.subTest(folder=folder):
                self.assertTrue(
                    folder == 'workflow'
                    or folder.startswith('packages/machinome/'),
                    f'{folder} is neither the root workflow nor a folder '
                    'of the framework')
                if Path(folder).name != '_build':
                    self.assertTrue((REPOSITORY / folder).is_dir(),
                                    f'{folder} is not a directory')


class TheContinuousIntegrationTest(unittest.TestCase):
    """The workflow is the repository's; its jobs run from the package."""

    def setUp(self):
        self.jobs = yaml.safe_load(WORKFLOW.read_text())['jobs']

    def test_the_workflow_is_at_the_root(self):
        self.assertFalse((PACKAGE / '.github').exists(),
                         'the package directory holds a .github')
        from tests import test_docs_exports
        self.assertEqual(test_docs_exports.WORKFLOW, WORKFLOW)

    def test_every_job_runs_from_the_package_directory(self):
        for name, job in self.jobs.items():
            if name == 'dist':
                continue
            with self.subTest(job=name):
                directory = (job.get('defaults') or {}).get(
                    'run', {}).get('working-directory')
                self.assertEqual(directory, 'packages/machinome')

    def test_every_cache_path_names_a_file(self):
        for name, job in self.jobs.items():
            for step in job['steps']:
                paths = (step.get('with') or {}).get('cache-dependency-path')
                for path in (paths or '').split():
                    with self.subTest(job=name, path=path):
                        self.assertTrue((REPOSITORY / path).is_file(),
                                        f'{path} is not a file of the '
                                        'repository')

    def test_the_dist_job_checks_the_distributions(self):
        dist = self.jobs['dist']
        self.assertEqual(sorted(dist['needs']), ['docs', 'test'])
        runs = [step.get('run', '') for step in dist['steps']]
        self.assertIn('scripts/check-dist', runs)


class TheRootIsTheRepositorysTest(unittest.TestCase):
    """The root holds the repository's record, none of the framework's."""

    def test_the_repository_s_files_are_there(self):
        for name in ('README.md', '.gitignore', 'scripts/check-dist',
                     'workflow/README.md'):
            with self.subTest(entry=name):
                self.assertTrue((REPOSITORY / name).is_file(),
                                f'{REPOSITORY / name} is missing')
        self.assertTrue(os.access(REPOSITORY / 'scripts' / 'check-dist',
                                  os.X_OK),
                        'scripts/check-dist is not executable')

    def test_the_framework_s_entries_are_not(self):
        for name in FRAMEWORK_ENTRIES:
            with self.subTest(entry=name):
                self.assertFalse(os.path.lexists(REPOSITORY / name),
                                 f'{name} is at the repository root')
        self.assertTrue((PACKAGE / 'workflow' / 'warts.md').is_file(),
                        'the framework\'s working record is not in its '
                        'directory')

    def test_the_root_ignores_the_benches_and_the_venv(self):
        lines = (REPOSITORY / '.gitignore').read_text().splitlines()
        for pattern in ('/WTs/', '/.venv/'):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, lines)

    def test_the_readme_links_every_package_and_states_the_licence(self):
        readme = (REPOSITORY / 'README.md').read_text()
        targets = MARKDOWN_LINK.findall(readme)
        for directory in package_directories():
            with self.subTest(package=directory.name):
                self.assertIn(f'packages/{directory.name}/', targets)
        licence = conf_value('framework_licence')
        self.assertIn(licence, ' '.join(readme.split()),
                      f'README.md does not state {licence!r}')


class TheLinksTest(unittest.TestCase):
    """Every link into the repository names a path that exists."""

    def pages(self):
        yield PACKAGE / 'README.rst'
        yield REPOSITORY / 'README.md'
        yield REPOSITORY / 'CONTRIBUTING.rst'
        for page in sorted((PACKAGE / 'docs').rglob('*.rst')):
            if '_build' not in page.relative_to(PACKAGE / 'docs').parts:
                yield page

    def test_every_github_link_names_a_path_of_the_repository(self):
        for page in self.pages():
            for path in GITHUB_PATH.findall(page.read_text()):
                with self.subTest(page=page.name, path=path):
                    self.assertTrue(os.path.lexists(REPOSITORY / path),
                                    f'{page} links {path}, which is not a '
                                    'path of the repository')

    def test_every_relative_link_resolves(self):
        pages = (
            (PACKAGE / 'README.rst', PACKAGE, RST_LINK),
            (REPOSITORY / 'README.md', REPOSITORY, MARKDOWN_LINK),
            (REPOSITORY / 'CONTRIBUTING.rst', REPOSITORY, RST_LINK),
        )
        for page, base, link in pages:
            targets = [t.strip() for t in link.findall(page.read_text())]
            for target in filter(relative, targets):
                with self.subTest(page=page.name, target=target):
                    self.assertTrue((base / target).exists(),
                                    f'{page} links {target}, which does not '
                                    f'exist under {base}')


if __name__ == '__main__':
    unittest.main()
