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
working record (change `join-mechanics`, ADR-187), and the browser viewer
`machinome-viewer`, the package `machinome.viewer.web`, numbered with the set,
with its changelog, tests, specs and decision log, whose widget is the one
member of the npm workspace the root declares beside the uv workspace (change
`join-viewer`, ADR-188).

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
    'CREDITS.md', 'MANIFEST.in', 'setup.cfg', 'tox.ini', 'Makefile',
    'requirements.txt', 'requirements_dev.txt', '.readthedocs.yaml',
)

WORKFLOW = REPOSITORY / '.github' / 'workflows' / 'python-app.yml'

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
#: holds beside the package (`join-mechanics`).
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
}

#: The npm workspace's members: the repository's JavaScript projects, each
#: by its directory (`join-viewer`).
NODE_MEMBERS = ['packages/machinome-viewer/machinome/viewer/web/widget']

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

    def test_the_default_group_is_the_framework_dev_and_mechanics_extras(self):
        # `cut-the-engines`: the bench venv is the universe sweep's
        # environment, so it carries the mechanics package the catalogue's
        # projects import.
        self.assertEqual(self.root['dependency-groups']['dev'],
                         ['machinome[dev]', 'machinome[mechanics]'])


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

    def test_the_test_job_runs_each_product_s_tests(self):
        # A product keeps its tests in its directory; the core's suite does
        # not collect them, so the test job runs them there
        # (`join-mechanics`).
        steps = self.jobs['test']['steps']
        for product in PRODUCTS:
            with self.subTest(product=product):
                self.assertTrue(
                    any(step.get('working-directory')
                        == f'packages/{product}'
                        and 'pytest' in step.get('run', '')
                        for step in steps),
                    f'the test job runs no pytest from packages/{product}')

    def test_the_dist_job_checks_the_distributions(self):
        dist = self.jobs['dist']
        self.assertEqual(sorted(dist['needs']), ['docs', 'test'])
        runs = [step.get('run', '') for step in dist['steps']]
        self.assertIn('scripts/check-dist', runs)

    @staticmethod
    def index(steps, found, what):
        for number, step in enumerate(steps):
            if found(step):
                return number
        raise AssertionError(f'the job has no step that {what}')

    def test_the_test_job_builds_and_tests_the_widget_before_the_suite(self):
        # The widget is the npm workspace's member: one install at the root,
        # its typecheck, tests and bundle before the suite photographs
        # through it, and Chromium before the viewer's tests (`join-viewer`).
        steps = self.jobs['test']['steps']
        node = self.index(
            steps, lambda step: step.get('uses', '').startswith(
                'actions/setup-node@'), 'sets up Node')
        suite = self.index(steps, lambda step: step.get('name') == 'Run tests',
                           'is named "Run tests"')
        for command in ('npm ci', 'npm run typecheck', 'npm test',
                        'npm run build'):
            with self.subTest(command=command):
                at = self.index(
                    steps, lambda step: command in step.get('run', '')
                    and step.get('working-directory') == '.',
                    f'runs {command} at the root')
                self.assertLess(node, at, f'{command} runs before Node is set up')
                self.assertLess(at, suite, f'{command} runs after the suite')
        viewer = self.index(
            steps, lambda step: step.get('working-directory')
            == 'packages/machinome-viewer' and 'pytest' in step.get('run', ''),
            "runs the viewer's tests")
        chromium = self.index(
            steps, lambda step: 'playwright install --with-deps chromium'
            in step.get('run', ''), 'installs Chromium')
        self.assertLessEqual(chromium, viewer,
                             "Chromium is installed after the viewer's tests")
        if chromium == viewer:
            run = steps[viewer]['run']
            self.assertLess(run.index('playwright install'),
                            run.index('pytest'))

    def test_the_dist_job_sets_up_node_before_checking(self):
        # The viewer's source distribution builds its bundle with npm.
        steps = self.jobs['dist']['steps']
        node = self.index(
            steps, lambda step: step.get('uses', '').startswith(
                'actions/setup-node@'), 'sets up Node')
        check = self.index(
            steps, lambda step: step.get('run', '') == 'scripts/check-dist',
            'runs scripts/check-dist')
        self.assertLess(node, check)


class TheRootIsTheRepositorysTest(unittest.TestCase):
    """The root holds the repository's record, none of the framework's."""

    def test_the_repository_s_files_are_there(self):
        for name in ('README.md', '.gitignore', 'scripts/check-dist',
                     'workflow/README.md', 'package.json',
                     'package-lock.json'):
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
                    check=True).stdout.split()
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
                self.assertEqual(
                    manifest['tool']['setuptools']['packages']['find'],
                    {'include': [address], 'namespaces': True})

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
        for name in PRODUCTS:
            with self.subTest(package=name):
                directory = REPOSITORY / 'packages' / name
                self.assertTrue(
                    list((directory / 'tests').glob('test_*.py')),
                    f'{name}/tests holds no test module')
                self.assertTrue((directory / 'openspec' / 'specs').is_dir(),
                                f'{name} holds no openspec/specs/')


class TheNodeWorkspaceTest(unittest.TestCase):
    """The root declares an npm workspace beside the uv workspace: a private
    `package.json` with no package of its own, one lockfile, its
    `node_modules/` ignored (`join-viewer`)."""

    def tracked(self):
        return subprocess.run(['git', 'ls-files'], cwd=REPOSITORY,
                              capture_output=True, text=True,
                              check=True).stdout.splitlines()

    def test_the_root_package_is_a_private_workspace(self):
        manifest = json.loads((REPOSITORY / 'package.json').read_text())
        self.assertIs(manifest.get('private'), True)
        self.assertNotIn('version', manifest)
        self.assertEqual(manifest['workspaces'], NODE_MEMBERS)

    def test_one_lockfile_at_the_root_names_the_widget(self):
        locks = [path for path in self.tracked()
                 if path.rpartition('/')[2] == 'package-lock.json']
        self.assertEqual(locks, ['package-lock.json'])
        lock = json.loads((REPOSITORY / 'package-lock.json').read_text())
        for member in NODE_MEMBERS:
            with self.subTest(member=member):
                self.assertEqual(lock['packages'][member]['name'],
                                 '@machinome/viewer')

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
