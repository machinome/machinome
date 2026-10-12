# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later

"""The viewer grants AGPL-3.0-or-later, and says so everywhere.

The grant is the SPDX expression: in every source header, in both package
manifests, in the banner every conveyed bundle opens with, and on the pages
a reader lands on. The `LICENSE` file is the AGPL version 3 text and carries
no version choice of its own, so these checks are what keeps the grant one
and the same across the repository. History (the archived changes, the
decision log and the pre-0.7 changelog) records the earlier `-only` grant
and is left out of the scan.
"""

import json
import re
import subprocess
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WIDGET = REPO / 'machinome_viewer' / 'widget'

GRANT = 'AGPL-3.0-or-later'
STALE = 'AGPL-3.0-only'

SPDX = re.compile(r'SPDX-License-Identifier: (\S+)')

# Records of what was decided when; they keep the grant that held then.
HISTORY = ('workflow/archive/', 'workflow/adrs/', 'openspec/changes/')

# This file names the stale grant in order to refuse it, and spells the
# SPDX pattern it scans for; it is not a header to check.
SELF = 'tests/test_licence.py'

# A licence named the way SPDX names one (`Name-1.0`, `Name-1.0-or-later`),
# and a licence named by a capitalised word before "licence"/"license".
IDENTIFIER = re.compile(r'\b(?:[A-Z][A-Za-z]*-)+\d+\.\d+(?:-or-later|-only)?\b')
NAMED_LICENCE = re.compile(r'\b[A-Z][A-Za-z]+ [Ll]icen[cs]e\b')

# Pages a reader lands on, each of which states the grant.
READER_FACING = ('README.md', 'docs/index.rst', 'docs/sharing.rst',
                 'context7.json')


def tracked_files():
    out = subprocess.run(['git', 'ls-files', '-z'], cwd=REPO, check=True,
                         capture_output=True).stdout
    return [Path(p) for p in out.decode().split('\0') if p]


def text_of(relative):
    try:
        return (REPO / relative).read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return None


class LicenceTest(unittest.TestCase):

    def test_the_manifests_agree(self):
        pyproject = tomllib.loads((REPO / 'pyproject.toml').read_text())
        self.assertEqual(pyproject['project']['license'], GRANT)
        package = json.loads((WIDGET / 'package.json').read_text())
        self.assertEqual(package['license'], GRANT)

    def test_the_banner_template_names_the_grant(self):
        build = (WIDGET / 'build.mjs').read_text()
        self.assertIn(f'SPDX-License-Identifier: {GRANT}', build)
        self.assertNotIn(STALE, build)

    def test_every_header_grants_or_later(self):
        headers = 0
        for relative in tracked_files():
            if relative.as_posix().startswith(HISTORY) \
               or relative.as_posix() == SELF:
                continue
            text = text_of(relative)
            if text is None:
                continue
            for identifier in SPDX.findall(text):
                headers += 1
                with self.subTest(file=relative.as_posix()):
                    self.assertEqual(identifier, GRANT)
        self.assertGreater(headers, 100, 'the scan found too few headers')

    def test_nothing_current_says_only(self):
        for relative in tracked_files():
            if relative.as_posix().startswith(HISTORY) \
               or relative.as_posix() == SELF:
                continue
            text = text_of(relative)
            if text is None:
                continue
            with self.subTest(file=relative.as_posix()):
                self.assertNotIn(STALE, text)

    def test_reader_facing_pages_state_the_grant(self):
        for relative in READER_FACING:
            with self.subTest(file=relative):
                self.assertIn(GRANT, (REPO / relative).read_text())

    def test_reader_facing_pages_name_only_the_viewers_grant(self):
        """The viewer states its own licence and never the framework's,
        which is licensed separately and states its licence in its own
        manual (OpenSpec `release-0-8-0`). The patterns are generic: any
        SPDX-shaped identifier, and any name written before the word."""
        pages = ['README.md', 'CHANGELOG.md', 'context7.json']
        pages += sorted(p.relative_to(REPO).as_posix()
                        for p in (REPO / 'docs').rglob('*.rst')
                        if '_build' not in p.parts)
        for relative in pages:
            text = (REPO / relative).read_text()
            with self.subTest(file=relative):
                self.assertEqual(
                    [name for name in IDENTIFIER.findall(text)
                     if name != GRANT], [])
                self.assertEqual(NAMED_LICENCE.findall(text), [])

    def test_a_built_bundle_opens_with_the_grant(self):
        bundle = WIDGET / 'dist' / 'machinome-viewer.js'
        if not bundle.exists():
            self.skipTest('no built bundle in this checkout')
        with bundle.open(encoding='utf-8') as fh:
            head = fh.read(2000)
        self.assertIn(f'SPDX-License-Identifier: {GRANT}', head)
        self.assertNotIn(STALE, head)


if __name__ == '__main__':
    unittest.main()
