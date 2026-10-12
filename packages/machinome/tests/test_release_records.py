# Machinome - Source code for machines
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The release facts agree wherever they are stated.

`pyproject.toml` states the version once; every other file that carries
it, and every record whose top entry must be the released version, is
held to that one statement, so a release moves the files together or
fails here naming the one left behind (changes `release-0-7-1` and
`release-0-8-0`). Every package of the repository carries the framework's
version, but the mechanics helpers, which carry their own (change
`join-mechanics`); the viewer's Python package, its widget and the root's npm
lock carry it too (change `join-viewer`). Every pin between two of them is
`~=` that version, and the root's `.bumpversion.cfg` moves them all (change
`cut-the-engines`).
"""

from datetime import datetime
import json
import re
import tomllib
from pathlib import Path
from unittest import TestCase

from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[1]
# The repository holding the framework's directory, whose root holds
# context7.json (change `monorepo-layout`).
REPOSITORY = Path(__file__).resolve().parents[3]

# The members the set does not number: each carries its own version, held
# to its changelog's release and to the manual's statement of it, outside
# .bumpversion.cfg, and a requirement on or from it is a floor (the pilot's
# decision of 12 October 2026, change `join-mechanics`, ADR-187).
OWN_VERSION = ('machinome-mechanics',)

# The one heading under which work landed after a release is recorded.
UNRELEASED = '\nUnreleased\n----------\n'


def released_version():
    return tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']['version']


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
            '.bumpversion.cfg': (
                f'current_version = {self.version}',
                (REPOSITORY / '.bumpversion.cfg').read_text()),
            'docs/conf.py': (
                f"release = '{self.version}'",
                (ROOT / 'docs/conf.py').read_text()),
        }
        for file, (statement, text) in statements.items():
            with self.subTest(file=file):
                self.assertIn(statement, text)
        with self.subTest(file='machinome/vet/universe.toml'):
            self.assertEqual(universe['universe']['version'], self.version)

    def test_every_member_is_numbered_with_the_core(self):
        for directory, project in members():
            if project['name'] in OWN_VERSION:
                continue
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
                    if name in OWN_VERSION \
                            or requirement.name in OWN_VERSION:
                        # A floor that the required member's version in
                        # the tree satisfies.
                        required = projects[requirement.name]['version']
                        self.assertEqual(
                            [spec.operator for spec in requirement.specifier],
                            ['>='], line)
                        self.assertTrue(
                            requirement.specifier.contains(required), line)
                    else:
                        self.assertEqual(str(requirement.specifier),
                                         f'~={self.version}', line)

    def test_the_version_is_bumped_from_the_root(self):
        tables = re.findall(r'^\[bumpversion:file(?:\([^)]*\))?:([^\]]+)\]$',
                            (REPOSITORY / '.bumpversion.cfg').read_text(),
                            flags=re.M)
        for directory, project in members():
            if project['name'] in OWN_VERSION:
                continue
            manifest = directory.relative_to(REPOSITORY) / 'pyproject.toml'
            with self.subTest(member=directory.name):
                self.assertIn(manifest.as_posix(), tables)
        self.assertNotIn('[bumpversion', (ROOT / 'setup.cfg').read_text(),
                         "the framework's setup.cfg holds a version table")

    def test_a_member_of_its_own_version_is_outside_the_bump(self):
        tables = re.findall(r'^\[bumpversion:file(?:\([^)]*\))?:([^\]]+)\]$',
                            (REPOSITORY / '.bumpversion.cfg').read_text(),
                            flags=re.M)
        projects = {project['name']: (directory, project)
                    for directory, project in members()}
        for name in OWN_VERSION:
            with self.subTest(member=name):
                directory, project = projects[name]
                manifest = directory.relative_to(REPOSITORY) / 'pyproject.toml'
                self.assertNotIn(manifest.as_posix(), tables)
                headings = re.findall(
                    r'^## (.+)$', (directory / 'CHANGELOG.md').read_text(),
                    flags=re.M)
                released = next(heading for heading in headings
                                if heading != 'Unreleased')
                self.assertEqual(released.split()[0], project['version'],
                                 released)
                self.assertEqual(conf_value('mechanics_version'),
                                 project['version'])

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
