# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The built browser surface carries the notices of the packages it bundles.

Vite minifies the packages the frontend imports into the files under
``static/assets/`` and drops the licence comments their sources carry, so
the surface would ship MIT and Apache code without the notice those
licences require to accompany every copy. The frontend's build writes
``THIRD-PARTY-NOTICES.txt`` beside the files from the packages the bundle
actually holds: each name, version, licence and the licence text it ships.
"""

import json
import re
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / 'machinome' / 'studio'
FRONTEND = PACKAGE / 'frontend'
STATIC = PACKAGE / 'static'
NOTICES = STATIC / 'THIRD-PARTY-NOTICES.txt'
CREDITS = Path(__file__).resolve().parents[2] / 'machinome' / 'CREDITS.md'
RULE = '-' * 70


@unittest.skipUnless((STATIC / 'index.html').is_file(),
                     'the surface is not built: npm run build in the frontend')
class ThirdPartyNoticesTest(unittest.TestCase):

    def entries(self):
        text = NOTICES.read_text(encoding='utf-8')
        parts = text.split(f'\n{RULE}\n')
        return parts[0], [part.strip() for part in parts[1:]]

    def test_the_surface_carries_the_notices_file(self):
        self.assertTrue(NOTICES.is_file(), f'{NOTICES} is not written by the build')

    def test_every_runtime_dependency_is_noticed_with_its_version(self):
        _, entries = self.entries()
        heads = [entry.splitlines()[0] for entry in entries]
        declared = json.loads((FRONTEND / 'package.json').read_text())['dependencies']
        for name in declared:
            self.assertTrue(any(re.fullmatch(rf'{re.escape(name)} \d+\.\d+\.\S+', head)
                                for head in heads), (name, heads))

    def test_every_entry_carries_a_licence_and_its_text(self):
        _, entries = self.entries()
        self.assertGreater(len(entries), 5, entries)
        for entry in entries:
            lines = entry.splitlines()
            self.assertRegex(lines[0], r'^\S+ \d+\.\d+\.\S+$')
            self.assertRegex(lines[1], r'^Licence: \S')
            self.assertRegex(lines[2], r'^Source: \S')
            body = '\n'.join(lines[3:])
            self.assertRegex(body, r'(?i)copyright|licen[cs]e', lines[0])
            self.assertGreater(len(body), 500, lines[0])

    def test_the_file_is_written_from_the_bundle_not_a_list(self):
        """Every entry's package is one the frontend installs, and its
        version is the installed one: the notice is read from the package
        the bundle took, not typed."""
        _, entries = self.entries()
        for entry in entries:
            name, version = entry.splitlines()[0].split(' ', 1)
            found = None
            for base in (FRONTEND / 'node_modules', FRONTEND.parents[4] / 'node_modules'):
                if (base / name / 'package.json').is_file():
                    found = json.loads((base / name / 'package.json').read_text())
                    break
            self.assertIsNotNone(found, name)
            self.assertEqual(found['version'], version, name)

    @unittest.skipUnless(CREDITS.is_file(), 'the credits file is the repository\'s')
    def test_the_credits_name_the_file(self):
        self.assertIn('THIRD-PARTY-NOTICES.txt', CREDITS.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
