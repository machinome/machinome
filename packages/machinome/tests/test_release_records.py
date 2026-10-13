# Machinome - Source code for machines
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The release facts agree wherever they are stated.

`current_version` of the root's `.bumpversion.cfg` states the version once
(change `release-tooling`); every file that carries it, the framework's
`pyproject.toml` among them, and every record whose top entry must be the
released version, is held to that one statement, so a release moves the
files together or fails here naming the one left behind (changes
`release-0-7-1` and `release-0-8-0`). Every package of the repository
carries the framework's version, the mechanics helpers among them since
change `release-0-9-0` ended their own (change `join-mechanics`); the
viewer's Python package, its widget and the root's npm lock carry it too
(change `join-viewer`), and the movie's
JavaScript directory, its own lock and the root lock's entry for it (change
`join-movie`), and the studio's frontend and the root lock's entry for it
(change `join-studio`). Every pin between two of them is `~=` that version, and the
root's `.bumpversion.cfg` moves them all (change `cut-the-engines`), through
`make bump`, which neither commits nor tags (change `release-tooling`).
"""

import configparser
from datetime import datetime
import json
import re
import tomllib
from pathlib import Path
from unittest import TestCase

from packaging.requirements import Requirement
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]
# The repository holding the framework's directory, whose root holds
# context7.json (change `monorepo-layout`).
REPOSITORY = Path(__file__).resolve().parents[3]

# The one heading under which work landed after a release is recorded.
UNRELEASED = '\nUnreleased\n----------\n'


def bumpversion():
    """The `[bumpversion]` section of the root's `.bumpversion.cfg`."""
    config = configparser.ConfigParser(interpolation=None)
    config.read_string((REPOSITORY / '.bumpversion.cfg').read_text())
    return config['bumpversion']


def released_version():
    """The set's version, declared once (change `release-tooling`)."""
    return bumpversion()['current_version']


def conf_value(name):
    conf = (ROOT / 'docs/conf.py').read_text()
    return re.search(rf"^{name} = '([^']*)'", conf, flags=re.M)[1]


def members():
    """Every package of the repository: its directory and its `[project]`."""
    for manifest in sorted((REPOSITORY / 'packages').glob('*/pyproject.toml')):
        yield manifest.parent, tomllib.loads(manifest.read_text())['project']


def sections(text):
    """The titles of a reStructuredText page's dashed sections, in order."""
    return re.findall(r'^(\S.*)\n-{3,}$', text, flags=re.M)


class VersionFilesTest(TestCase):

    def setUp(self):
        self.version = released_version()

    def test_every_version_file_agrees_with_pyproject(self):
        universe = tomllib.loads(
            (ROOT / 'machinome/vet/universe.toml').read_text())
        statements = {
            'machinome/__init__.py': (
                f'__version__ = "{self.version}"',
                (ROOT / 'machinome/__init__.py').read_text()),
            'pyproject.toml': (
                f'version = "{self.version}"',
                (ROOT / 'pyproject.toml').read_text()),
            'docs/conf.py': (
                f"release = '{self.version}'",
                (ROOT / 'docs/conf.py').read_text()),
        }
        for file, (statement, text) in statements.items():
            with self.subTest(file=file):
                self.assertIn(statement, text)
        with self.subTest(file='machinome/vet/universe.toml'):
            self.assertEqual(universe['universe']['version'], self.version)

    def test_the_bump_neither_commits_nor_tags(self):
        """The configuration declares the version and nothing else: the
        pilot commits and tags (change `release-tooling`)."""
        self.assertEqual(list(bumpversion()), ['current_version'])

    def test_every_member_is_numbered_with_the_core(self):
        for directory, project in members():
            with self.subTest(member=directory.name):
                self.assertEqual(project['version'], self.version)

    def test_every_pin_between_members_is_compatible(self):
        projects = dict((project['name'], project) for _, project in members())
        for name, project in projects.items():
            lines = [*project.get('dependencies', []),
                     *(line for extra in project.get(
                         'optional-dependencies', {}).values()
                       for line in extra)]
            for line in lines:
                requirement = Requirement(line)
                if requirement.name == name \
                        or requirement.name not in projects:
                    continue
                with self.subTest(member=name, requirement=line):
                    self.assertEqual(str(requirement.specifier),
                                     f'~={self.version}', line)

    def test_the_version_is_bumped_from_the_root(self):
        tables = re.findall(r'^\[bumpversion:file(?:\([^)]*\))?:([^\]]+)\]$',
                            (REPOSITORY / '.bumpversion.cfg').read_text(),
                            flags=re.M)
        for directory, project in members():
            manifest = directory.relative_to(REPOSITORY) / 'pyproject.toml'
            with self.subTest(member=directory.name):
                self.assertIn(manifest.as_posix(), tables)
        self.assertNotIn('[bumpversion', (ROOT / 'setup.cfg').read_text(),
                         "the framework's setup.cfg holds a version table")

    def test_the_mechanics_helpers_are_bumped_with_their_two_pins(self):
        """The mechanics helpers, numbered with the set since
        `release-0-9-0` (ADR-187 amended), have the two tables of a package
        with pins, after the studio's: its version and its pin on the core;
        the manual states no version of theirs."""
        sections = re.findall(r'^\[(bumpversion:[^\]]+)\]$',
                              (REPOSITORY / '.bumpversion.cfg').read_text(),
                              flags=re.M)
        manifest = 'packages/machinome-mechanics/pyproject.toml'
        ours = [section for section in sections if section.endswith(manifest)]
        self.assertEqual(ours, [f'bumpversion:file(version):{manifest}',
                                f'bumpversion:file(pins):{manifest}'])
        self.assertNotIn('mechanics_version',
                         (ROOT / 'docs/conf.py').read_text())

    def test_the_openscad_viewer_is_bumped_with_its_two_pins(self):
        """The OpenSCAD viewer, a distribution of the set since
        `viewer-seam`, has the node packages' two tables, after the
        viewer's: its version and its pins on the core and on the OpenSCAD
        node family."""
        sections = re.findall(r'^\[(bumpversion:[^\]]+)\]$',
                              (REPOSITORY / '.bumpversion.cfg').read_text(),
                              flags=re.M)
        manifest = 'packages/machinome-viewer-openscad/pyproject.toml'
        ours = [section for section in sections if section.endswith(manifest)]
        self.assertEqual(ours, [f'bumpversion:file(version):{manifest}',
                                f'bumpversion:file(pins):{manifest}'])
        self.assertGreater(
            sections.index(ours[0]),
            sections.index('bumpversion:file(viewer):'
                           'packages/machinome/docs/conf.py'))

    def test_the_matching_viewer_is_numbered_with_the_framework(self):
        self.assertEqual(conf_value('viewer_version'), self.version)

    def test_the_viewer_extras_pin_the_set_s_viewer(self):
        """The viewer is a distribution of the repository numbered with the
        set, so the extras that install it pin the one the manual declares,
        `~=` as every pin between the set's distributions (change
        `join-viewer`)."""
        extras = tomllib.loads((ROOT / 'pyproject.toml').read_text())[
            'project']['optional-dependencies']
        expected = {'viewer': ('machinome-viewer', set()),
                    'web-snapshot': ('machinome-viewer', {'snapshot'})}
        for extra, (name, bracket) in expected.items():
            with self.subTest(extra=extra):
                (line,) = extras[extra]
                requirement = Requirement(line)
                self.assertEqual(requirement.name, name, line)
                self.assertEqual(requirement.extras, bracket, line)
                self.assertEqual(str(requirement.specifier),
                                 f"~={conf_value('viewer_version')}", line)

    def test_the_viewer_s_version_files_agree(self):
        """The viewer's Python package, its widget and the root's npm lock
        state the set's version; `.bumpversion.cfg` moves the first two, and
        npm the lock (change `join-viewer`)."""
        viewer = REPOSITORY / 'packages/machinome-viewer'
        package = viewer / 'machinome/viewer/web'
        widget = 'packages/machinome-viewer/machinome/viewer/web/widget'
        with self.subTest(file='__init__.py'):
            self.assertIn(f'__version__ = "{self.version}"',
                          (package / '__init__.py').read_text())
        with self.subTest(file='package.json'):
            self.assertEqual(json.loads(
                (package / 'widget/package.json').read_text())['version'],
                self.version)
        with self.subTest(file='package-lock.json'):
            lock = REPOSITORY / 'package-lock.json'
            self.assertTrue(lock.is_file(), f'{lock} is missing')
            self.assertEqual(json.loads(lock.read_text())['packages'][widget][
                'version'], self.version)
        tables = re.findall(r'^\[bumpversion:file(?:\([^)]*\))?:([^\]]+)\]$',
                            (REPOSITORY / '.bumpversion.cfg').read_text(),
                            flags=re.M)
        for path in (package / '__init__.py', package / 'widget/package.json'):
            with self.subTest(table=path.name):
                self.assertIn(path.relative_to(REPOSITORY).as_posix(), tables)

    def test_the_movie_s_node_version_files_agree(self):
        """The movie's JavaScript directory, its own lock's two root entries
        and the root lock's entry for it state the set's version;
        `.bumpversion.cfg` moves the `package.json`, and npm the locks
        (change `join-movie`)."""
        js = 'packages/machinome-movie/machinome/movie/js'
        with self.subTest(file='package.json'):
            self.assertEqual(json.loads(
                (REPOSITORY / js / 'package.json').read_text())['version'],
                self.version)
        with self.subTest(file=f'{js}/package-lock.json'):
            own = json.loads((REPOSITORY / js / 'package-lock.json').read_text())
            self.assertEqual(own['version'], self.version)
            self.assertEqual(own['packages']['']['version'], self.version)
        with self.subTest(file='package-lock.json'):
            root = json.loads((REPOSITORY / 'package-lock.json').read_text())
            self.assertIn(js, root['packages'],
                          'the root lock holds no entry for the movie')
            self.assertEqual(root['packages'][js]['version'], self.version)
        tables = re.findall(r'^\[bumpversion:file(?:\([^)]*\))?:([^\]]+)\]$',
                            (REPOSITORY / '.bumpversion.cfg').read_text(),
                            flags=re.M)
        self.assertIn(f'{js}/package.json', tables)

    def test_the_studio_s_frontend_version_files_agree(self):
        """The studio's frontend and the root lock's entry for it state the
        set's version; `.bumpversion.cfg` moves the `package.json`, and npm
        the lock. The frontend keeps no lock of its own (change
        `join-studio`)."""
        frontend = 'packages/machinome-studio/machinome/studio/frontend'
        with self.subTest(file='package.json'):
            self.assertEqual(json.loads(
                (REPOSITORY / frontend / 'package.json').read_text())[
                    'version'], self.version)
        with self.subTest(file='package-lock.json'):
            root = json.loads((REPOSITORY / 'package-lock.json').read_text())
            self.assertIn(frontend, root['packages'],
                          'the root lock holds no entry for the studio')
            self.assertEqual(root['packages'][frontend]['version'],
                             self.version)
        tables = re.findall(r'^\[bumpversion:file(?:\([^)]*\))?:([^\]]+)\]$',
                            (REPOSITORY / '.bumpversion.cfg').read_text(),
                            flags=re.M)
        self.assertIn(f'{frontend}/package.json', tables)

    def test_no_release_fact_is_trapped_in_inline_markup(self):
        """A substitution inside ``**...**`` is not resolved: the 0.7.0
        status page told its readers "Machinome |release| was released
        on |release_date|", literally."""
        trapped = re.compile(r'\*\*[^*\n]*\|[a-z_]+\|[^*\n]*\*\*')
        for page in sorted((ROOT / 'docs').rglob('*.rst')):
            if '_build' in page.parts:
                continue
            with self.subTest(page=page.relative_to(ROOT).as_posix()):
                self.assertIsNone(trapped.search(page.read_text()))


#: The products that keep a changelog of their own, by directory, and the
#: first version of the set each is released at: the viewer is numbered with
#: the set since 0.7.0; the mechanics helpers, the films and the studio first
#: release with it at 0.9.0 (changes `join-viewer`, `join-movie`,
#: `join-studio`, `release-0-9-0`).
PRODUCTS = {'machinome-viewer': '0.7.0', 'machinome-mechanics': '0.9.0',
            'machinome-movie': '0.9.0', 'machinome-studio': '0.9.0'}


class ReleaseRecordsTest(TestCase):
    """The changelog, the history, the status page and context7 describe
    the released version as released. Work done after it is recorded as it
    lands, in an `Unreleased` section above the release's own, and never
    inside it: a release moves that section down, not the other way."""

    def setUp(self):
        self.version = released_version()
        self.date = datetime.strptime(conf_value('release_date'), '%d %B %Y')
        self.changelog = (ROOT / 'docs/project/changelog.rst').read_text()
        self.history = (ROOT / 'HISTORY.rst').read_text()

    def section(self, text, title):
        titles = sections(text)
        start = text.index(f'{title}\n')
        following = [t for t in titles[titles.index(title) + 1:]]
        end = text.index(f'\n{following[0]}\n') if following else len(text)
        return text[start:end]

    def test_the_changelog_first_release_section_is_the_released_version(self):
        titles = sections(self.changelog)
        releases = [title for title in titles if title.startswith('Machinome ')]
        self.assertEqual(releases[0], f'Machinome {self.version}')
        # Only work after the release may precede it, under one heading.
        self.assertIn(titles[0], ('Unreleased', releases[0]))
        self.assertEqual(titles.count('Unreleased'), int(titles[0] == 'Unreleased'))
        entry = self.section(self.changelog, f'Machinome {self.version}')
        self.assertIn(f"Released on {self.date.strftime('%d/%b/%Y')}", entry)
        self.assertNotIn('unreleased', entry.lower())

    def test_the_0_7_1_entry_names_what_it_ships(self):
        entry = self.section(self.changelog, 'Machinome 0.7.1')
        for fragment in ('Frame', '.on(', 'Revolute', 'Prismatic',
                         'resolved_frames', '``machinome vet``',
                         ':doc:`/concepts/joints`', ':ref:`vet`'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, entry)

    def test_the_history_top_entry_is_the_released_version(self):
        first = re.search(r'^Machinome (\S+) \((\d{4}-\d{2}-\d{2})\)$',
                          self.history, flags=re.M)
        self.assertEqual(first[1], self.version)
        self.assertEqual(first[2], self.date.strftime('%Y-%m-%d'))
        # Only work after the release may precede it, under one heading.
        titles = sections(self.history)
        self.assertIn(titles[0], ('Unreleased', first[0]))
        self.assertEqual(titles.count('Unreleased'),
                         int(titles[0] == 'Unreleased'))
        head = self.history.split(f'Machinome {self.version}')[0]
        self.assertNotIn('unreleased',
                         head.replace(UNRELEASED, '\n', 1).lower())

    def test_the_status_page_describes_nothing_as_unreleased(self):
        status = (ROOT / 'docs/project/status.rst').read_text().lower()
        self.assertNotIn('unreleased', status)
        self.assertNotIn('current source', status)
        self.assertNotIn('since |release|', status)

    def test_the_release_note_has_the_dated_section(self):
        """A release's note is the page of its major.minor line: a `.0`
        release opens the page, whose title names the line; a patch adds
        the page's last section, which names the version (change
        `release-0-8-0`)."""
        major, minor, patch = self.version.split('.')
        page = ROOT / f'docs/releases/release-{major}.{minor}.rst'
        self.assertTrue(page.is_file(), page.relative_to(ROOT).as_posix())
        note = page.read_text()
        if patch == '0':
            title = note.splitlines()[0]
            self.assertIn(f'Machinome {major}.{minor}', title)
        else:
            self.assertIn(self.version, sections(note)[-1])
        self.assertIn(self.date.strftime('%-d %B %Y'), note)

    def test_context7_states_the_release(self):
        rules = json.loads((REPOSITORY / 'context7.json').read_text())['rules']
        text = ' '.join(rules)
        self.assertIn(f'Machinome {self.version} '
                      f'(released {self.date.strftime("%Y-%m-%d")})', text)
        self.assertIn(f"The matching viewer is {conf_value('viewer_version')}, "
                      f"API {conf_value('viewer_api')}", text)
        self.assertIn('Frame(', text)
        self.assertIn('machinome vet', text)

    def test_each_product_records_the_release(self):
        """A product numbered with a released version of the set records
        that release as its changelog's newest release section, dated the
        release's day, with at most one `Unreleased` section, above it
        (change `release-0-9-0`)."""
        version = Version(self.version)
        heading = (f'{self.version} \N{EM DASH} '
                   f"{self.date.strftime('%-d %B %Y')}")
        for name, first in PRODUCTS.items():
            if version < Version(first):
                continue
            changelog = REPOSITORY / 'packages' / name / 'CHANGELOG.md'
            headings = re.findall(r'^## (.+)$', changelog.read_text(),
                                  flags=re.M)
            with self.subTest(product=name):
                released = [one for one in headings if one != 'Unreleased']
                self.assertTrue(released, f'{name} records no release')
                self.assertEqual(released[0], heading)
                self.assertIn(headings[0], ('Unreleased', heading))
                self.assertLessEqual(headings.count('Unreleased'), 1)


class TheManualInTheSourceArchiveTest(TestCase):
    """The manual is distributed with the framework's source archive (the
    pilot's decision of 12 October 2026, `workflow/ongoing/release-0.9.md`
    at the repository root, decision 9), so the sdist carries every file
    its build reads: the pages, the configuration, the manual's own
    extension and its table under `docs/_ext/`, the static files, the
    committed exports under `docs/_exports/` and the example projects
    beside the pages (change `manual-extras`). The records Sphinx does not
    read, the `.md` files under `docs/`, and Git's own files stay out."""

    maxDiff = None

    #: What the build does not read.
    NOT_READ = re.compile(r'\.md$|(^|/)\.git(ignore|keep)$')

    def tracked(self):
        """The files under `docs/` Git tracks or would track, those the
        build does not read left out."""
        import subprocess
        try:
            listed = subprocess.run(
                ['git', 'ls-files', '-z', '--cached', '--others',
                 '--exclude-standard', 'docs'], cwd=ROOT, check=True,
                capture_output=True, text=True).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest('not a Git checkout: the tracked files are unknown')
        return sorted(path for path in listed.split('\0')
                      if path and not self.NOT_READ.search(path))

    def test_the_sdist_carries_what_the_manual_s_build_reads(self):
        import subprocess
        import sys
        import tarfile
        import tempfile

        expected = self.tracked()
        self.assertIn('docs/_ext/manual_extras.py', expected)
        with tempfile.TemporaryDirectory() as out:
            subprocess.run(
                [sys.executable, '-m', 'build', '--sdist', '--no-isolation',
                 '--outdir', out], cwd=ROOT, check=True,
                capture_output=True)
            (sdist,) = Path(out).glob('*.tar.gz')
            with tarfile.open(sdist) as archive:
                carried = {name.split('/', 1)[1]
                           for name in archive.getnames() if '/' in name}
        self.assertEqual([path for path in expected if path not in carried],
                         [], 'the sdist lacks files the manual reads')
        self.assertEqual(sorted(name for name in carried
                                if name.startswith('docs/_build/')), [],
                         'the sdist carries a build of the manual')
