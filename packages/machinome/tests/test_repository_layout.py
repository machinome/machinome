# Machinome - Source code for machines
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The framework is the package directory `packages/machinome` of a monorepo.

The repository `machinome/machinome` holds each of its distributions in a
directory under `packages/` named as the distribution; the framework is
`packages/machinome/`. The root holds the repository's record and tooling:
the one licence, the contributor guide, the AI-use statement, the history,
the CI, a uv workspace with its lock, the `Makefile` of the repository's
steps, `scripts/check-dist`, `context7.json` and the record of the campaigns
that span packages. The package directory
reaches the five shared files through relative symbolic links, which
setuptools carries into the archives as regular files (change
`monorepo-layout`, ADR-182). The framework's extension packages are
siblings under `packages/`, each holding its manifest, a README, the links
to the licence and its namespace portion, numbered with the framework and
installed editable by the workspace (change `cut-the-engines`, ADR-183):
the two engines and the node packages `machinome-node-cadquery`,
`machinome-node-build123d`, `machinome-node-step` and
`machinome-node-molejo`, each a portion of `machinome.node` (change
`cut-the-brep-nodes`), and `machinome-node-openscad`,
`machinome-node-solid2`, `machinome-node-jscad` and `machinome-node-stl`
(change `cut-the-mesh-nodes`), the first of them a package directory with
its own `__init__.py`, and `machinome-node-freecad`, a package directory
too, which joined the repository from a repository of its own (change
`join-freecad`). The core's `machinome/node/` then holds no node type and its
`machinome/viewers/` no node type's renderer. A product that joined from a
repository of its own and is not an extension package keeps its record in its
directory, at its own version: the mechanics helpers `machinome-mechanics`,
the package `machinome.mechanics`, with their changelog, tests, specs and
working record (change `join-mechanics`, ADR-187), the browser viewer
`machinome-viewer`, the package `machinome.viewer.web`, numbered with the set,
with its changelog, tests, specs and decision log, whose widget is the one
member of the npm workspace the root declares beside the uv workspace (change
`join-viewer`, ADR-188), and the skills package `machinome-skills`, the
package `machinome.skills`, numbered with the set, with its tests and working
record, its specification the framework's `skills-distribution` (change
`join-skills`, ADR-190), and the films `machinome-movie`, the package
`machinome.movie`, numbered with the set, with its changelog, tests, specs,
decision log and working record, whose JavaScript directory is the npm
workspace's second member, its direct dependencies installed beside it by the
root's `.npmrc`, with a lock of its own for an installed copy (change
`join-movie`, ADR-191), and the studio `machinome-studio`, the package
`machinome.studio`, numbered with the set, with its changelog, tests, specs,
decision log and working record, whose frontend is the npm workspace's third
member, with no lock of its own (change `join-studio`, ADR-193). The
repository's steps are the targets of the root `Makefile`, which declares
every package and the packages with tests of their own, and the CI's jobs
call those targets (change `release-tooling`, ADR-192), the test job
installing the OpenSpec CLI the studio's tests run (`join-studio`); the
framework keeps no Makefile of its own.

These tests pin the tree that makes that true. They read a checkout: an
unpacked sdist has no repository above it. `scripts/check-dist` proves the
archives built from the tree.
"""

import importlib
import json
import os
import re
import subprocess
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
    'CREDITS.md', 'MANIFEST.in', 'setup.cfg', 'tox.ini',
    'requirements.txt', 'requirements_dev.txt', '.readthedocs.yaml',
)

WORKFLOW = REPOSITORY / '.github' / 'workflows' / 'python-app.yml'

#: The repository's steps, one target each (change `release-tooling`).
MAKEFILE = REPOSITORY / 'Makefile'

#: The Makefile's targets with a help line, `help` the default.
TARGETS = ('help', 'version', 'bump', 'sync', 'test', 'lint', 'docs',
           'widget', 'dist', 'upload', 'check', 'clean')

#: A rule of the Makefile: its targets, its prerequisites, its recipe.
#: A target spelled by a function (`$(addprefix ...)`) is not read.
RULE = re.compile(r'^([^\s:#=.$][^:#=]*):(?![=:])([^\n#]*)(?:#[^\n]*)?\n'
                  r'((?:\t[^\n]*(?:\n|$))*)', flags=re.M)

#: The framework's extension packages, by directory: the module each
#: ships, by its address, and the core's extra that installs it.
EXTENSIONS = {
    'machinome-engine-brep': ('machinome.engine.brep', 'brep'),
    'machinome-engine-mesh': ('machinome.engine.mesh', 'mesh'),
    'machinome-node-cadquery': ('machinome.node.cadquery', 'cadquery'),
    'machinome-node-build123d': ('machinome.node.build123d', 'build123d'),
    'machinome-node-step': ('machinome.node.step', 'step'),
    'machinome-node-molejo': ('machinome.node.molejo', 'molejo'),
    'machinome-node-openscad': ('machinome.node.openscad', 'openscad'),
    'machinome-node-solid2': ('machinome.node.solid2', 'solid2'),
    'machinome-node-jscad': ('machinome.node.jscad', 'jscad'),
    'machinome-node-stl': ('machinome.node.stl', 'stl'),
    'machinome-node-freecad': ('machinome.node.freecad', 'freecad'),
}

#: The products of the repository that keep their record in their own
#: directory, by directory: the address of the package directory they
#: ship, the core's extra that installs it, and the entries the directory
#: holds beside the package (`join-mechanics`). A product's specs are in
#: its directory or in the framework's (`join-skills`).
PRODUCTS = {
    'machinome-mechanics': ('machinome.mechanics', 'mechanics',
                            ('.gitignore', 'CHANGELOG.md', 'LICENSE',
                             'LICENSES', 'MANIFEST.in', 'README.md',
                             'machinome', 'openspec', 'pyproject.toml',
                             'tests', 'workflow')),
    'machinome-viewer': ('machinome.viewer.web', 'viewer',
                         ('.gitignore', 'CHANGELOG.md', 'LICENSE',
                          'LICENSES', 'MANIFEST.in', 'README.md',
                          'machinome', 'openspec', 'pyproject.toml',
                          'scripts', 'tests', 'workflow')),
    'machinome-skills': ('machinome.skills', 'skills',
                         ('.gitignore', 'LICENSE', 'LICENSES', 'MANIFEST.in',
                          'README.md', 'machinome', 'pyproject.toml', 'tests',
                          'workflow')),
    'machinome-movie': ('machinome.movie', 'movie',
                        ('.gitignore', 'CHANGELOG.md', 'LICENSE',
                         'LICENSES', 'MANIFEST.in', 'README.md',
                         'experiments', 'machinome', 'openspec',
                         'pyproject.toml', 'tests', 'workflow')),
    'machinome-studio': ('machinome.studio', 'studio',
                         ('.gitignore', 'CHANGELOG.md', 'LICENSE',
                          'LICENSES', 'MANIFEST.in', 'README.md',
                          'machinome', 'openspec', 'pyproject.toml',
                          'scripts', 'tests', 'workflow')),
}

#: The npm workspace's members: the repository's JavaScript projects, each
#: by its directory, in the root's order, and the name its `package.json`
#: gives it (`join-viewer`, `join-movie`, `join-studio`).
NODE_MEMBERS = {
    'packages/machinome-viewer/machinome/viewer/web/widget': '@machinome/viewer',
    'packages/machinome-movie/machinome/movie/js': '@machinome/movie',
    'packages/machinome-studio/machinome/studio/frontend': '@machinome/studio',
}

#: The members that keep a lock of their own beside the root's, from which
#: an installed copy installs its dependencies outside the workspace
#: (`join-movie`).
OWN_LOCKS = ('packages/machinome-movie/machinome/movie/js',)

#: The movie's JavaScript directory.
MOVIE_JS = 'packages/machinome-movie/machinome/movie/js'

#: The extension packages whose portion is a package directory at its
#: address, with its own `__init__.py` below the levels the core defines,
#: and the modules it holds (`cut-the-mesh-nodes`, `join-freecad`).
PACKAGE_PORTIONS = {
    'machinome-node-openscad': ('__init__', 'binary', 'leaf', 'renderer',
                                'writer'),
    'machinome-node-freecad': ('__init__', 'adapter', 'runtime', 'worker'),
}

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


def makefile():
    """The root Makefile's text, its continued lines joined."""
    return MAKEFILE.read_text().replace('\\\n', ' ')


def make_variable(name):
    """The words of a variable the Makefile assigns once, with `:=`."""
    text = makefile()
    found = re.findall(rf'^{re.escape(name)}\s*:=\s*(.*)$', text, flags=re.M)
    if len(found) != 1:
        raise AssertionError(f'the Makefile assigns {name} {len(found)} '
                             'times with :=')
    if re.search(rf'^{re.escape(name)}\s*[+?!]?=', text, flags=re.M):
        raise AssertionError(f'the Makefile assigns {name} other than with :=')
    return found[0].split()


def make_expanded(words):
    """The words with each leading `$(NAME)` replaced by its value."""
    out = []
    for word in words:
        reference = re.fullmatch(r'\$\((\w+)\)(.*)', word)
        if reference:
            out += [value + reference[2]
                    for value in make_expanded(make_variable(reference[1]))]
        else:
            out.append(word)
    return out


def make_rules():
    """{target: (prerequisites, recipe)} of every rule the Makefile spells."""
    rules = {}
    for match in RULE.finditer(makefile()):
        for target in match[1].split():
            rules[target] = (match[2].split(), match[3])
    return rules


def make_targets():
    """The targets with a help line (`target: ... ## what it does`)."""
    return re.findall(r'^([a-z][a-z-]*):[^\n]*## ', MAKEFILE.read_text(),
                      flags=re.M)


def portion_files(name, address):
    """The files an extension package ships under `machinome/`: its module
    at its address, or its package directory's modules."""
    base = address.replace('.', '/')
    if name in PACKAGE_PORTIONS:
        return [f'{base}/{module}.py' for module in PACKAGE_PORTIONS[name]]
    return [f'{base}.py']


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

    def test_every_member_is_a_workspace_source(self):
        members = [directory.name for directory in package_directories()]
        self.assertEqual(self.root['tool']['uv']['sources'],
                         {name: {'workspace': True} for name in members})
        lock = REPOSITORY / 'uv.lock'
        self.assertTrue(lock.is_file(), f'{lock} is missing')
        text = lock.read_text()
        for name in members:
            with self.subTest(member=name):
                self.assertIn(f'source = {{ editable = "packages/{name}" }}',
                              text)

    def test_every_member_installs_editable_in_compat_mode(self):
        self.assertEqual(self.root['tool']['uv']['config-settings'],
                         {'editable_mode': 'compat'})

    def test_the_default_group_is_the_framework_dev_and_the_products_extras(
            self):
        # `cut-the-engines`: the bench venv is the universe sweep's
        # environment, so it carries the mechanics package the catalogue's
        # projects import; `join-skills`: and the skills package, whose
        # tests run from its directory and whose command the suite's
        # conformance walk reads; `join-movie`: and the movie package, alike;
        # `join-studio`: and the studio, alike.
        self.assertEqual(self.root['dependency-groups']['dev'],
                         ['machinome[dev]', 'machinome[mechanics]',
                          'machinome[skills]', 'machinome[movie]',
                          'machinome[studio]'])


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
                    or folder.startswith('packages/machinome/')
                    or any(folder.startswith(f'packages/{product}/')
                           for product in PRODUCTS),
                    f'{folder} is neither the root workflow nor a folder '
                    'of the framework or of a product')
                if Path(folder).name != '_build':
                    self.assertTrue((REPOSITORY / folder).is_dir(),
                                    f'{folder} is not a directory')


class TheContinuousIntegrationTest(unittest.TestCase):
    """The workflow is the repository's; its jobs call the root Makefile's
    targets (change `release-tooling`)."""

    def setUp(self):
        self.jobs = yaml.safe_load(WORKFLOW.read_text())['jobs']

    def test_the_workflow_is_at_the_root(self):
        self.assertFalse((PACKAGE / '.github').exists(),
                         'the package directory holds a .github')
        from tests import test_docs_exports
        self.assertEqual(test_docs_exports.WORKFLOW, WORKFLOW)

    #: The targets each job calls, in order.
    CALLS = {
        'lint': ['make lint'],
        'test': ['make widget', 'make test'],
        'browser-snapshot': ['make widget'],
        'docs': ['make docs'],
        'dist': ['make check'],
        'build': ['make dist'],
    }

    #: What a target runs, which no job spells itself.
    SPELLED = {
        'flake8': r'\bflake8\b', 'black': r'\bblack\b',
        'sphinx': r'\bsphinx\b', 'coverage': r'\bcoverage\b',
        'scripts/check-dist': r'scripts/check-dist', 'twine': r'\btwine\b',
        'pip install': r'\bpip install\b', 'npm': r'\bnpm ',
        'pytest': r'\bpytest\b',
    }

    #: The one setup step a job spells with npm: the OpenSpec CLI the
    #: studio's tests run, installed as a maker installs it (`join-studio`).
    OPENSPEC = 'npm install -g @fission-ai/openspec@1.6.0'

    @staticmethod
    def calls(job):
        return [line.strip() for step in job['steps']
                for line in step.get('run', '').splitlines()
                if re.match(r'make\s', line.strip())]

    def test_every_job_calls_the_makefile(self):
        self.assertEqual(sorted(self.jobs), sorted(self.CALLS))
        for name, job in self.jobs.items():
            with self.subTest(job=name):
                for step in job['steps']:
                    if name == 'browser-snapshot' and step.get('env', {}).get(
                            'MACHINOME_WEB_SNAPSHOT_E2E'):
                        continue
                    if name == 'test' and step.get('run', '').strip() == (
                            self.OPENSPEC):
                        continue
                    for command, pattern in self.SPELLED.items():
                        self.assertIsNone(
                            re.search(pattern, step.get('run', '')),
                            f'the {name} job spells {command} in its step '
                            f'{step.get("name")!r}')
                self.assertEqual(self.calls(job), self.CALLS[name])
                self.assertIsNone(job.get('defaults'),
                                  f'the {name} job sets defaults for its '
                                  'commands')

    def test_every_cache_path_names_a_file(self):
        for name, job in self.jobs.items():
            for step in job['steps']:
                paths = (step.get('with') or {}).get('cache-dependency-path')
                for path in (paths or '').split():
                    with self.subTest(job=name, path=path):
                        self.assertTrue((REPOSITORY / path).is_file(),
                                        f'{path} is not a file of the '
                                        'repository')

    def test_the_test_job_runs_each_product_s_tests(self):
        # A product keeps its tests in its directory; the core's suite does
        # not collect them, so `make test`, which the test job runs, runs
        # every package of the Makefile's tested list (`join-mechanics`,
        # `release-tooling`).
        self.assertIn('make test', self.calls(self.jobs['test']))
        tested = make_variable('TESTED')
        for product in PRODUCTS:
            with self.subTest(product=product):
                self.assertIn(product, tested,
                              f'the Makefile\'s TESTED omits {product}')

    def test_the_dist_job_checks_the_distributions(self):
        dist = self.jobs['dist']
        self.assertEqual(sorted(dist['needs']), ['docs', 'test'])
        self.assertIn('make check', self.calls(dist))

    @staticmethod
    def index(steps, found, what):
        for number, step in enumerate(steps):
            if found(step):
                return number
        raise AssertionError(f'the job has no step that {what}')

    def test_the_test_job_builds_the_bundles_and_chromium_before_the_tests(
            self):
        # The widget is the npm workspace's member: `make widget` installs
        # the workspace at the root and builds its bundle, after Node is set
        # up; Chromium after the workspace's sync; both before `make test`
        # (`join-viewer`, `release-tooling`). The Makefile's viewer rule
        # type-checks, tests and builds the widget, by name, so the movie's
        # Node suite does not run there, before the viewer's pytest.
        steps = self.jobs['test']['steps']
        node = self.index(
            steps, lambda step: step.get('uses', '').startswith(
                'actions/setup-node@'), 'sets up Node')
        sync = self.index(
            steps, lambda step: 'uv sync --locked' in step.get('run', ''),
            'syncs the workspace')
        widget = self.index(
            steps, lambda step: step.get('run', '').strip() == 'make widget',
            'runs make widget')
        chromium = self.index(
            steps, lambda step: 'playwright install --with-deps chromium'
            in step.get('run', ''), 'installs Chromium')
        tests = self.index(
            steps, lambda step: step.get('run', '').strip() == 'make test',
            'runs make test')
        self.assertLess(node, widget, 'make widget runs before Node is set up')
        self.assertLess(sync, chromium,
                        'Chromium is installed before the workspace')
        self.assertLess(widget, tests, 'make widget runs after make test')
        self.assertLess(chromium, tests, 'Chromium is installed after '
                        'make test')
        rules = make_rules()
        self.assertIn('widget', rules)
        self.assertRegex(rules['widget'][1], r'\$\(NPM\) ci\b')
        recipe = rules['test-machinome-viewer'][1]
        self.assertEqual(make_variable('WIDGET'), [next(iter(NODE_MEMBERS))])
        self.assertNotIn('--workspaces', recipe,
                         "the viewer's rule runs every npm member")
        at = [recipe.index(command) for command in (
            '$(NPM) run typecheck --workspace $(WIDGET)',
            '$(NPM) test --workspace $(WIDGET)',
            '$(NPM) run build --workspace $(WIDGET)',
            'cd packages/machinome-viewer && $(PYTHON) -m pytest')]
        self.assertEqual(at, sorted(at), "the viewer's rule runs its steps "
                         'out of order')

    def test_the_test_job_runs_the_movie_s_node_projects_without_a_browser(
            self):
        # The movie's Node suite: its `pure` and `stage` projects, which open
        # no browser, run no FFmpeg and write no film, from the root after
        # its `npm ci` (`join-movie`): the Makefile's movie rule, which
        # `make test` runs after `make widget` (`release-tooling`).
        calls = self.calls(self.jobs['test'])
        self.assertLess(calls.index('make widget'), calls.index('make test'))
        self.assertEqual(make_variable('MOVIE_JS'), [MOVIE_JS])
        recipe = make_rules()['test-machinome-movie'][1]
        python = recipe.index('cd packages/machinome-movie && $(PYTHON) -m '
                              'pytest')
        node = recipe.index('$(NPM) test --workspace $(MOVIE_JS) -- '
                            '--project pure --project stage')
        self.assertLess(python, node)

    def test_the_test_job_installs_the_openspec_cli_before_the_tests(self):
        # The studio's tests run the OpenSpec CLI, the studio's runtime
        # prerequisite, which `make test` finds on the PATH (`join-studio`).
        steps = self.jobs['test']['steps']
        node = self.index(
            steps, lambda step: step.get('uses', '').startswith(
                'actions/setup-node@'), 'sets up Node')
        openspec = self.index(
            steps, lambda step: step.get('run', '').strip() == self.OPENSPEC,
            'installs the OpenSpec CLI')
        tests = self.index(
            steps, lambda step: step.get('run', '').strip() == 'make test',
            'runs make test')
        self.assertLess(node, openspec)
        self.assertLess(openspec, tests)

    def test_the_studio_s_rule_builds_its_frontend_before_its_tests(self):
        # The studio's tests serve the built surface; its browser tests skip
        # unless MACHINOME_STUDIO_E2E=1 (`join-studio`).
        self.assertEqual(make_variable('STUDIO_FRONTEND'),
                         [list(NODE_MEMBERS)[2]])
        recipe = make_rules()['test-machinome-studio'][1]
        at = [recipe.index(command) for command in (
            '$(NPM) test --workspace $(STUDIO_FRONTEND)',
            '$(NPM) run build --workspace $(STUDIO_FRONTEND)',
            'cd packages/machinome-studio && $(PYTHON) -m pytest')]
        self.assertEqual(at, sorted(at), "the studio's rule runs its steps "
                         'out of order')
        self.assertIn('packages/machinome-studio/machinome/studio/static',
                      make_variable('CLEAN'))

    def test_the_dist_job_sets_up_node_before_checking(self):
        # The viewer's source distribution builds its bundle with npm.
        steps = self.jobs['dist']['steps']
        node = self.index(
            steps, lambda step: step.get('uses', '').startswith(
                'actions/setup-node@'), 'sets up Node')
        check = self.index(
            steps, lambda step: step.get('run', '').strip() == 'make check',
            'runs make check')
        self.assertLess(node, check)


class TheMakefileTest(unittest.TestCase):
    """The repository's steps are the targets of one Makefile at the root,
    which declares the packages once (change `release-tooling`)."""

    def test_the_makefile_is_the_repository_s(self):
        self.assertTrue(MAKEFILE.is_file(), f'{MAKEFILE} is missing')
        own = PACKAGE / 'Makefile'
        self.assertFalse(os.path.lexists(own), f'{own} exists')

    def test_the_package_list_is_the_package_directories(self):
        listed = make_variable('PACKAGES')
        directories = [directory.name for directory in package_directories()]
        for name in directories:
            with self.subTest(package=name):
                self.assertIn(name, listed,
                              f'the Makefile\'s PACKAGES omits {name}')
        for name in listed:
            with self.subTest(listed=name):
                self.assertIn(name, directories,
                              f'the Makefile\'s PACKAGES names {name}, which '
                              'is not a directory of packages/')
        self.assertEqual(listed, sorted(directories))

    def test_the_tested_list_is_the_core_and_the_products(self):
        tested = make_variable('TESTED')
        rules = make_rules()
        for name in ('machinome', *PRODUCTS):
            with self.subTest(package=name):
                self.assertIn(name, tested,
                              f'the Makefile\'s TESTED omits {name}')
                self.assertIn(f'test-{name}', rules,
                              f'the Makefile has no rule test-{name}')
                self.assertIn('-m pytest', rules[f'test-{name}'][1],
                              f'the rule test-{name} runs no pytest')
        for name in tested:
            with self.subTest(tested=name):
                self.assertIn(name, ('machinome', *PRODUCTS),
                              f'the Makefile\'s TESTED names {name}, which '
                              'keeps no tests of its own')
        self.assertEqual(len(tested), len(set(tested)))

    def test_the_targets_are_the_decided_ones(self):
        targets = make_targets()
        for name in targets:
            with self.subTest(target=name):
                self.assertIn(name, TARGETS,
                              f'the Makefile has a target {name} with a help '
                              'line')
        self.assertEqual(sorted(targets), sorted(TARGETS))
        phony = re.search(r'^\.PHONY:(.*)$', makefile(), flags=re.M)[1].split()
        for name in TARGETS:
            with self.subTest(phony=name):
                self.assertIn(name, phony, f'{name} is not .PHONY')
        self.assertEqual(make_variable('.DEFAULT_GOAL'), ['help'])
        for name, (_, recipe) in make_rules().items():
            with self.subTest(rule=name):
                self.assertNotIn('sweep', name)
                self.assertNotIn('load-projects', recipe,
                                 f'the rule {name} runs the universe sweep')

    def test_upload_is_reached_by_no_other_target(self):
        rules = make_rules()
        self.assertEqual(rules['upload'][0], [],
                         'the rule upload has a prerequisite')
        for name, (prerequisites, recipe) in rules.items():
            with self.subTest(rule=name):
                for target in ('dist', 'upload'):
                    self.assertNotIn(target, prerequisites,
                                     f'the rule {name} depends on {target}')
                if name != 'upload':
                    self.assertNotIn('twine upload', recipe,
                                     f'the rule {name} runs twine upload')
        self.assertIn('twine upload $(RELEASE)/*', rules['upload'][1])
        self.assertRegex(rules['dist'][1],
                         r'scripts/check-dist --out (\$\(CURDIR\)/)?'
                         r'\$\(RELEASE\)')
        self.assertEqual(make_variable('RELEASE'), ['dist/v$(CURRENT)'])
        current = ' '.join(make_variable('CURRENT'))
        self.assertIn('current_version', current)
        self.assertIn('.bumpversion.cfg', current)

    def test_the_bump_neither_commits_nor_tags(self):
        recipe = make_rules()['bump'][1]
        self.assertIn('--no-commit --no-tag', recipe)
        for command in ('git commit', 'git tag'):
            with self.subTest(command=command):
                self.assertNotIn(command, recipe)

    def test_clean_removes_only_what_git_ignores(self):
        recipe = make_rules()['clean'][1]
        self.assertEqual(recipe.strip(), 'rm -rf $(CLEAN)')
        names = [directory.name for directory in package_directories()]
        for pattern in make_expanded(make_variable('CLEAN')):
            paths = ([pattern.replace('*', name) for name in names]
                     if '*' in pattern else [pattern])
            for path in paths:
                with self.subTest(path=path):
                    parts = Path(path).parts
                    for kept in ('.venv', 'node_modules'):
                        self.assertNotIn(kept, parts,
                                         f'make clean removes {path}')
                    self.assertNotEqual(parts[0], 'dist',
                                        f'make clean removes {path}')
                    ignored = subprocess.run(
                        ['git', 'check-ignore', '-q', '--no-index',
                         f'{path}/'], cwd=REPOSITORY).returncode
                    self.assertEqual(ignored, 0,
                                     f'make clean removes {path}, which Git '
                                     'does not ignore')


class TheRootIsTheRepositorysTest(unittest.TestCase):
    """The root holds the repository's record, none of the framework's."""

    def test_the_repository_s_files_are_there(self):
        for name in ('README.md', '.gitignore', 'scripts/check-dist',
                     'workflow/README.md', 'package.json',
                     'package-lock.json', '.npmrc'):
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
        for pattern in ('/WTs/', '/.venv/', '/.docs-venv/'):
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


class TheExtensionPackagesTest(unittest.TestCase):
    """Each extension package carries only what distinguishes it: its
    manifest, a README, the links to the root's licence and its portion."""

    def test_each_extension_directory_holds_only_what_distinguishes_it(self):
        for name, (address, _extra) in EXTENSIONS.items():
            with self.subTest(package=name):
                directory = REPOSITORY / 'packages' / name
                self.assertTrue(directory.is_dir(), f'{directory} is missing')
                listed = subprocess.run(
                    ['git', 'ls-files', '--cached', '--others',
                     '--exclude-standard', '--', f'packages/{name}'],
                    cwd=REPOSITORY, capture_output=True, text=True,
                    check=True).stdout.split()
                self.assertEqual(
                    sorted(path.removeprefix(f'packages/{name}/')
                           for path in listed),
                    sorted(['pyproject.toml', 'README.md', 'LICENSE',
                            'LICENSES', *portion_files(name, address)]))
                for entry in ('LICENSE', 'LICENSES'):
                    self.assertTrue((directory / entry).is_symlink(),
                                    f'{directory / entry} is not a link')
                    self.assertEqual(os.readlink(directory / entry),
                                     f'../../{entry}')
                # The only `__init__.py` under `machinome/` is a package
                # portion's own, at its address: none at the levels the
                # core defines.
                own = ([directory / address.replace('.', '/') / '__init__.py']
                       if name in PACKAGE_PORTIONS else [])
                self.assertEqual(
                    sorted((directory / 'machinome').rglob('__init__.py')),
                    own, f'{name} ships an __init__.py of the core\'s')

    def test_each_extension_manifest_is_a_portion_of_the_set(self):
        core = read_toml(PACKAGE / 'pyproject.toml')['project']
        for name, (address, _extra) in EXTENSIONS.items():
            with self.subTest(package=name):
                manifest = read_toml(
                    REPOSITORY / 'packages' / name / 'pyproject.toml')
                project = manifest['project']
                self.assertEqual(project['name'], name)
                self.assertEqual(project['license'], core['license'])
                self.assertEqual(project['license-files'],
                                 core['license-files'])
                include = (address if name in PACKAGE_PORTIONS
                           else address.rpartition('.')[0])
                self.assertEqual(
                    manifest['tool']['setuptools']['packages']['find'],
                    {'include': [include], 'namespaces': True})

    def test_each_extension_readme_names_its_install_and_the_licence(self):
        licence = conf_value('framework_licence')
        for name, (_address, extra) in EXTENSIONS.items():
            with self.subTest(package=name):
                readme = ' '.join(
                    (REPOSITORY / 'packages' / name / 'README.md')
                    .read_text().split())
                self.assertIn(f'pip install "machinome[{extra}]"', readme)
                self.assertIn(licence, readme,
                              f'{name}/README.md does not state {licence!r}')

    def test_each_portion_resolves_from_its_package(self):
        from machinome import engine as seams
        seam = {'machinome.engine.brep': seams.brep_engine,
                'machinome.engine.mesh': seams.mesh_engine}
        for name, (address, _extra) in EXTENSIONS.items():
            with self.subTest(package=name):
                module = importlib.import_module(address)
                self.assertEqual(
                    Path(module.__file__).resolve(),
                    REPOSITORY / 'packages' / name
                    / portion_files(name, address)[0])
                if address in seam:
                    self.assertIs(seam[address](), module)

    def test_the_core_engine_package_holds_only_the_seams(self):
        entries = {path.name
                   for path in (PACKAGE / 'machinome' / 'engine').iterdir()
                   if path.name != '__pycache__'}
        self.assertEqual(entries, {'__init__.py'})

    def test_the_core_node_package_holds_no_extension_module(self):
        node = PACKAGE / 'machinome' / 'node'
        for address, _extra in EXTENSIONS.values():
            package, _, last = address.rpartition('.')
            if package != 'machinome.node':
                continue
            with self.subTest(module=address):
                self.assertFalse((node / f'{last}.py').exists(),
                                 f'{node / last}.py is in the core')
                self.assertFalse((node / last).exists(),
                                 f'{node / last}/ is in the core')

    def test_the_core_node_package_holds_no_node_type(self):
        from machinome.node.supported import NODE_TYPES
        node = PACKAGE / 'machinome' / 'node'
        for key in NODE_TYPES:
            with self.subTest(node_type=key):
                self.assertFalse((node / f'{key}.py').exists(),
                                 f'{node / key}.py is in the core')
                self.assertFalse((node / key).exists(),
                                 f'{node / key}/ is in the core')

    def test_the_core_viewers_hold_no_node_type_s_renderer(self):
        entries = {path.name
                   for path in (PACKAGE / 'machinome' / 'viewers').iterdir()
                   if path.name != '__pycache__'}
        self.assertEqual(entries, {'__init__.py', 'browser.py', 'bundle.py'})

    def test_every_sibling_is_in_the_table(self):
        siblings = [directory.name for directory in package_directories()
                    if directory.name != 'machinome']
        for name in siblings:
            with self.subTest(package=name):
                self.assertTrue(name in EXTENSIONS or name in PRODUCTS,
                                f'packages/{name} is in neither EXTENSIONS '
                                'nor PRODUCTS')

    def test_the_guide_installs_every_member_without_uv(self):
        guide = (REPOSITORY / 'CONTRIBUTING.rst').read_text()
        with self.subTest(names='editable_mode=compat'):
            self.assertTrue('editable_mode=compat' in guide,
                            'CONTRIBUTING.rst does not install in compat '
                            'mode')
        for directory in package_directories():
            spelling = ('-e "packages/machinome[dev]"'
                        if directory.name == 'machinome'
                        else f'-e packages/{directory.name}')
            with self.subTest(package=directory.name):
                self.assertTrue(spelling in guide,
                                f'CONTRIBUTING.rst does not name {spelling}')
        for retired in (r'\btox\b', r'requirements\.txt'):
            with self.subTest(retired=retired):
                found = re.search(retired, guide)
                self.assertIsNone(
                    found, f'CONTRIBUTING.rst names {found and found[0]!r}')

    def test_the_guide_runs_the_movie_s_two_suites(self):
        # The movie package's Python tests from its directory and its Node
        # suite from the root, after the root's `npm ci` (`join-movie`).
        guide = ' '.join((REPOSITORY / 'CONTRIBUTING.rst').read_text().split())
        for spelled in ('``python -m pytest`` from ``packages/machinome-movie``',
                        f'``npm test --workspace {MOVIE_JS}`` from the root',
                        'after ``npm ci`` there', '``.npmrc``',
                        '``machinome movie setup`` is for an installed copy'):
            with self.subTest(spelled=spelled):
                self.assertIn(spelled, guide)


class TheProductsTest(unittest.TestCase):
    """A product that joined from a repository of its own keeps its record
    in its directory beside its package (`join-mechanics`)."""

    def test_each_product_directory_holds_its_package_and_its_record(self):
        for name, (address, _extra, entries) in PRODUCTS.items():
            with self.subTest(package=name):
                directory = REPOSITORY / 'packages' / name
                self.assertTrue(directory.is_dir(), f'{directory} is missing')
                listed = subprocess.run(
                    ['git', 'ls-files', '--cached', '--others',
                     '--exclude-standard', '--', f'packages/{name}'],
                    cwd=REPOSITORY, capture_output=True, text=True,
                    check=True).stdout.splitlines()
                # One path a line: the studio's design reference holds a
                # file whose name has a space (`join-studio`).
                self.assertEqual(
                    sorted({path.removeprefix(f'packages/{name}/')
                            .split('/')[0] for path in listed}),
                    sorted(entries))
                for entry in ('LICENSE', 'LICENSES'):
                    self.assertTrue((directory / entry).is_symlink(),
                                    f'{directory / entry} is not a link')
                    self.assertEqual(os.readlink(directory / entry),
                                     f'../../{entry}')
                    self.assertEqual((directory / entry).resolve(),
                                     REPOSITORY / entry)
                package = directory / address.replace('.', '/')
                # No `__init__.py` at any level above the package directory:
                # `machinome/` is the core's, and `machinome/viewer/` the
                # level the viewer seam writes in the core (`join-viewer`).
                levels = address.split('.')[:-1]
                for depth in range(1, len(levels) + 1):
                    level = directory.joinpath(*levels[:depth])
                    self.assertFalse(
                        (level / '__init__.py').exists(),
                        f'{name} ships {level / "__init__.py"}, a level '
                        'above its package')
                self.assertTrue((package / '__init__.py').is_file(),
                                f'{package} holds no __init__.py')

    def test_each_product_manifest_states_the_set_s_licence(self):
        core = read_toml(PACKAGE / 'pyproject.toml')['project']
        for name, (address, _extra, _entries) in PRODUCTS.items():
            with self.subTest(package=name):
                manifest = read_toml(
                    REPOSITORY / 'packages' / name / 'pyproject.toml')
                project = manifest['project']
                self.assertEqual(project['name'], name)
                self.assertEqual(project['license'], core['license'])
                self.assertEqual(project['license-files'],
                                 core['license-files'])
                # The package directory at its address, then any subpackage
                # beneath it: the studio's `backends` (`join-studio`).
                find = manifest['tool']['setuptools']['packages']['find']
                self.assertEqual(sorted(find), ['include', 'namespaces'])
                self.assertIs(find['namespaces'], True)
                self.assertEqual(find['include'][0], address)
                for include in find['include'][1:]:
                    self.assertTrue(include.startswith(f'{address}.'),
                                    f'{name} finds {include}, outside '
                                    f'{address}')

    def test_each_product_readme_names_its_install_and_the_licence(self):
        licence = conf_value('framework_licence')
        for name, (_address, extra, _entries) in PRODUCTS.items():
            with self.subTest(package=name):
                readme = ' '.join(
                    (REPOSITORY / 'packages' / name / 'README.md')
                    .read_text().split())
                self.assertIn(f'pip install "machinome[{extra}]"', readme)
                self.assertIn(licence, readme,
                              f'{name}/README.md does not state {licence!r}')

    def test_each_product_resolves_from_its_directory(self):
        # On the interpreter running this suite.
        for name, (address, _extra, _entries) in PRODUCTS.items():
            with self.subTest(package=name):
                module = importlib.import_module(address)
                self.assertEqual(
                    Path(module.__file__).resolve(),
                    REPOSITORY / 'packages' / name
                    / address.replace('.', '/') / '__init__.py')

    def test_each_product_keeps_its_tests_and_specs(self):
        # Every product's tests are in its directory; a product whose
        # entries name `openspec` keeps its specs there, the others' are
        # the framework's (`join-skills`).
        for name, (_address, _extra, entries) in PRODUCTS.items():
            with self.subTest(package=name):
                directory = REPOSITORY / 'packages' / name
                self.assertTrue(any((directory / 'tests').glob('test_*.py')),
                                f'{name}/tests holds no test_*.py')
                if 'openspec' in entries:
                    self.assertTrue(
                        (directory / 'openspec' / 'specs').is_dir(),
                        f'{name} holds no openspec/specs/')


class TheNodeWorkspaceTest(unittest.TestCase):
    """The root declares an npm workspace beside the uv workspace: a private
    `package.json` with no package of its own, one lockfile, its
    `node_modules/` ignored (`join-viewer`); its second member, the movie's
    JavaScript directory, keeps a lock of its own for an installed copy, and
    the root's `.npmrc` installs each member's direct dependencies beside it
    (`join-movie`); its third, the studio's frontend, keeps no lock of its
    own, its wheel carrying the built surface (`join-studio`)."""

    def tracked(self):
        return subprocess.run(['git', 'ls-files'], cwd=REPOSITORY,
                              capture_output=True, text=True,
                              check=True).stdout.splitlines()

    def test_the_root_package_is_a_private_workspace(self):
        manifest = json.loads((REPOSITORY / 'package.json').read_text())
        self.assertIs(manifest.get('private'), True)
        self.assertNotIn('version', manifest)
        self.assertEqual(manifest['workspaces'], list(NODE_MEMBERS))
        for member, name in NODE_MEMBERS.items():
            with self.subTest(member=member):
                package = json.loads(
                    (REPOSITORY / member / 'package.json').read_text())
                self.assertEqual(package['name'], name)
                self.assertIs(package.get('private'), True)

    def test_the_root_s_lock_names_each_member_and_the_movie_keeps_its_own(
            self):
        locks = [path for path in self.tracked()
                 if path.rpartition('/')[2] == 'package-lock.json']
        self.assertEqual(sorted(locks), sorted(
            ['package-lock.json',
             *(f'{member}/package-lock.json' for member in OWN_LOCKS)]))
        lock = json.loads((REPOSITORY / 'package-lock.json').read_text())
        for member, name in NODE_MEMBERS.items():
            with self.subTest(member=member):
                self.assertEqual(lock['packages'][member]['name'], name)
        for member in OWN_LOCKS:
            with self.subTest(own=member):
                own = json.loads(
                    (REPOSITORY / member / 'package-lock.json').read_text())
                self.assertEqual(own['name'], NODE_MEMBERS[member])
                self.assertEqual(own['packages']['']['name'],
                                 NODE_MEMBERS[member])

    def test_the_movie_s_own_lock_agrees_with_its_manifest_and_the_root_s(
            self):
        # Both locks list exactly the dependencies the movie's package.json
        # declares, and resolve each direct dependency to its exact version:
        # the root's for the checkout, the member's for an installed copy,
        # which `machinome movie setup` installs from (`join-movie`).
        manifest = json.loads(
            (REPOSITORY / MOVIE_JS / 'package.json').read_text())
        declared = {kind: manifest.get(kind, {})
                    for kind in ('dependencies', 'devDependencies')}
        root = json.loads((REPOSITORY / 'package-lock.json').read_text())
        own = json.loads(
            (REPOSITORY / MOVIE_JS / 'package-lock.json').read_text())
        locks = {
            'package-lock.json': (root['packages'][MOVIE_JS],
                                  root['packages'],
                                  (f'{MOVIE_JS}/node_modules', 'node_modules')),
            f'{MOVIE_JS}/package-lock.json': (own['packages'][''],
                                              own['packages'],
                                              ('node_modules',)),
        }
        for lock, (entry, packages, places) in locks.items():
            for kind, dependencies in declared.items():
                with self.subTest(lock=lock, kind=kind):
                    self.assertEqual(entry.get(kind, {}), dependencies,
                                     f'{lock} disagrees with the movie\'s '
                                     f'package.json in its {kind}')
                for name, version in dependencies.items():
                    with self.subTest(lock=lock, dependency=name):
                        resolved = next(
                            (packages[f'{place}/{name}'] for place in places
                             if f'{place}/{name}' in packages), None)
                        self.assertIsNotNone(
                            resolved, f'{lock} does not resolve {name}')
                        self.assertEqual(resolved['version'], version,
                                         f'{lock} resolves {name} to '
                                         f"{resolved['version']}, not "
                                         f'{version}')

    def test_the_root_installs_each_member_s_dependencies_beside_it(self):
        # The movie's tool reads its packages from its own node_modules, and
        # its esbuild, TypeScript, vitest and jsdom differ in major from the
        # widget's (`join-movie`, ADR-191).
        npmrc = REPOSITORY / '.npmrc'
        self.assertTrue(npmrc.is_file(), f'{npmrc} is missing')
        settings = [line.strip() for line in npmrc.read_text().splitlines()
                    if line.strip() and not line.lstrip().startswith('#')]
        self.assertEqual(settings, ['install-strategy=shallow'])
        lock = json.loads((REPOSITORY / 'package-lock.json').read_text())
        manifest = json.loads(
            (REPOSITORY / MOVIE_JS / 'package.json').read_text())
        for name in manifest['dependencies']:
            with self.subTest(dependency=name):
                self.assertIn(f'{MOVIE_JS}/node_modules/{name}',
                              lock['packages'],
                              f'the root lock does not install {name} '
                              "in the movie's node_modules")

    def test_the_root_ignores_node_modules(self):
        lines = (REPOSITORY / '.gitignore').read_text().splitlines()
        self.assertIn('/node_modules/', lines)

    def test_no_install_or_bundle_is_tracked(self):
        found = [path for path in self.tracked()
                 if 'node_modules/' in path or 'widget/dist/' in path]
        self.assertEqual(found, [])


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
