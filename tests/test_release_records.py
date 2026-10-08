# Machinome - Source code for machines
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The release facts agree wherever they are stated.

`pyproject.toml` states the version once; every other file that carries
it, and every record whose top entry must be the released version, is
held to that one statement, so a release moves the files together or
fails here naming the one left behind (changes `release-0-7-1` and
`release-0-8-0`).
"""

from datetime import datetime
import json
import re
import tomllib
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]


def released_version():
    return tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']['version']


def conf_value(name):
    conf = (ROOT / 'docs/conf.py').read_text()
    return re.search(rf"^{name} = '([^']*)'", conf, flags=re.M)[1]


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
            'setup.cfg': (
                f'current_version = {self.version}',
                (ROOT / 'setup.cfg').read_text()),
            'docs/conf.py': (
                f"release = '{self.version}'",
                (ROOT / 'docs/conf.py').read_text()),
        }
        for file, (statement, text) in statements.items():
            with self.subTest(file=file):
                self.assertIn(statement, text)
        with self.subTest(file='machinome/vet/universe.toml'):
            self.assertEqual(universe['universe']['version'], self.version)

    def test_the_matching_viewer_is_numbered_with_the_framework(self):
        self.assertEqual(conf_value('viewer_version'), self.version)

    def test_the_viewer_extras_floor_at_the_matching_viewer(self):
        """The two packages are numbered together, so the extras that
        install the viewer require the one the manual declares, or newer
        (change `viewer-extra-floors-at-the-matching-viewer`)."""
        extras = tomllib.loads((ROOT / 'pyproject.toml').read_text())[
            'project']['optional-dependencies']
        floor = f">={conf_value('viewer_version')}"
        for extra in ('viewer', 'web-snapshot'):
            with self.subTest(extra=extra):
                (requirement,) = extras[extra]
                name, _, specifier = requirement.partition('>')
                self.assertTrue(name.startswith('machinome-viewer'), requirement)
                self.assertEqual('>' + specifier, floor, requirement)

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
        self.assertNotIn('unreleased',
                         self.history.split(f'Machinome {self.version}')[0].lower())

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
        rules = json.loads((ROOT / 'context7.json').read_text())['rules']
        text = ' '.join(rules)
        self.assertIn(f'Machinome {self.version} '
                      f'(released {self.date.strftime("%Y-%m-%d")})', text)
        self.assertIn(f"The matching viewer is {conf_value('viewer_version')}, "
                      f"API {conf_value('viewer_api')}", text)
        self.assertIn('Frame(', text)
        self.assertIn('machinome vet', text)
