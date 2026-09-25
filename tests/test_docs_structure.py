# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The manual is organised by reader intent, and says where it is going.

These checks pin the shape the user-documentation spec describes: the
navigation sections in order, one tutorial chapter for each stage of the
counter, the release facts defined once, and no publication caveat outside
the status page.
"""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / 'docs'

CAPTIONS = ['Start', 'Tutorial: a machine that counts', 'How-to guides',
            'How it works', 'Examples', 'Reference', 'Project']

CHAPTERS = ['01-part', '02-input', '03-dimensions', '04-relations',
            '05-buttons', '06-fit', '07-scenario', '08-running',
            '09-clocked', '10-share']

# Phrases that describe an unpublished state. They belong on the status
# page and in release records, never on a page that teaches.
CAVEATS = re.compile(
    r'in preparation|not yet published|awaiting publication|'
    r'release preparation|still unpublished|is unreleased',
    re.IGNORECASE)

ALLOWED_CAVEATS = ('project/status.rst', 'releases/')

# The viewer grants AGPL-3.0-or-later (25 September 2026). Nothing the manual
# describes is licensed version-3-only, so the spelling is a stale fact.
STALE_GRANT = 'AGPL-3.0-only'

# The real machines are shown on machinome.org; the examples page sends the
# reader there and the manual pins no example repository.
SITE_FOUNDRY = 'https://machinome.org/foundry/'


def documents():
    for rst in sorted(DOCS.rglob('*.rst')):
        relative = rst.relative_to(DOCS).as_posix()
        if relative.startswith('_build'):
            continue
        yield relative, rst.read_text()


class NavigationTest(unittest.TestCase):

    def test_sections_in_order(self):
        index = (DOCS / 'index.rst').read_text()
        captions = re.findall(r':caption:\s*(.+)', index)
        self.assertEqual(captions, CAPTIONS)

    def test_every_chapter_has_a_page_and_a_module(self):
        for chapter in CHAPTERS:
            with self.subTest(chapter=chapter):
                self.assertTrue((DOCS / 'tutorial' / f'{chapter}.rst').is_file())
        modules = sorted(p.stem for p in (DOCS / 'tutorial' / 'counter').glob('c*.py'))
        self.assertEqual(
            [m[:3] for m in modules],
            [f'c{n:02d}' for n in range(1, 10)],
            'one module per chapter that builds a machine; chapter ten '
            'shares the ninth')

    def test_the_examples_are_on_the_site(self):
        page = (DOCS / 'examples.rst').read_text()
        self.assertIn(SITE_FOUNDRY, page)
        for kind in ('posed', 'running', 'clocked'):
            with self.subTest(kind=kind):
                self.assertIn(kind, page)
        self.assertNotIn('.. machinome::', page,
                         'the examples page embeds a model')
        self.assertEqual(sorted(p.name for p in DOCS.glob('example-*.rst')),
                         [], 'an example page exists')
        self.assertFalse((REPO / '.gitmodules').exists(),
                         'the manual pins a submodule')

    def test_internal_records_are_not_in_the_manual(self):
        for retired in ('expression-graphs.rst', 'flexible-parts.rst',
                        'releases/development-0.7.rst'):
            with self.subTest(retired=retired):
                self.assertFalse((DOCS / retired).exists(), retired)


class LicenceWordingTest(unittest.TestCase):

    def test_no_page_names_the_old_viewer_grant(self):
        pages = list(documents()) + [('README.rst', (REPO / 'README.rst').read_text())]
        for relative, text in pages:
            with self.subTest(document=relative):
                self.assertNotIn(STALE_GRANT, text)


class ReleaseFactsTest(unittest.TestCase):

    def test_facts_are_substitutions(self):
        conf = (DOCS / 'conf.py').read_text()
        for name in ('release_date', 'viewer_version', 'viewer_api',
                     'document_versions', 'mechanics_version'):
            with self.subTest(name=name):
                self.assertIn(f'|{name}|', conf)

    def test_no_caveat_outside_the_status_page(self):
        for relative, text in documents():
            if relative.startswith(ALLOWED_CAVEATS):
                continue
            with self.subTest(document=relative):
                found = CAVEATS.search(text)
                if found is not None:
                    self.fail(f'{relative} says {found.group(0)!r}; '
                              'publication state belongs on the status page')


if __name__ == '__main__':
    unittest.main()
