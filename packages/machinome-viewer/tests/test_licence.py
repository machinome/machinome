# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The viewer is licensed as every package of the repository, and says so.

The grant is the set's SPDX expression, read from the framework's own
manifest: in both of this package's manifests, in every source header of
the package, in the banner every conveyed bundle opens with, and in the
README a reader lands on, in the words the manual states it with (change
`join-viewer`). The licence texts are the repository's, reached through the
links `LICENSE` and `LICENSES`. The archived records (the archived changes,
the decision log and the archived evidence) record what held when they
were written and are left out of the scan. A header carrying any other
expression fails the equality.
"""

import json
import re
import subprocess
import tomllib
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent
REPOSITORY = PACKAGE.parent.parent
WIDGET = PACKAGE / 'machinome' / 'viewer' / 'web' / 'widget'

#: The set's licence, as the framework's manifest declares it.
CORE = tomllib.loads(
    (REPOSITORY / 'packages' / 'machinome' / 'pyproject.toml').read_text())[
    'project']
GRANT = CORE['license']

#: The words the manual states the licence with.
WORDS = re.search(
    r"^framework_licence = '([^']*)'",
    (REPOSITORY / 'packages' / 'machinome' / 'docs' / 'conf.py').read_text(),
    flags=re.M)[1]

SOURCE = 'Source: https://github.com/machinome/machinome'

SPDX = re.compile(r'SPDX-License-Identifier: (\S+(?: OR \S+)*)')

# Records of what was decided when; they keep what held then.
HISTORY = ('openspec/changes/archive/', 'workflow/archive/', 'workflow/adrs/',
           'workflow/evidence/')

# This file spells the SPDX pattern it scans for; it is not a header to
# check beyond its own first lines.
SELF = 'tests/test_licence.py'


def tracked_files():
    out = subprocess.run(['git', 'ls-files', '-z', '--', '.'], cwd=PACKAGE,
                         check=True, capture_output=True).stdout
    return [Path(p) for p in out.decode().split('\0') if p]


def text_of(relative):
    try:
        return (PACKAGE / relative).read_text(encoding='utf-8')
    except (UnicodeDecodeError, IsADirectoryError):
        return None


class LicenceTest(unittest.TestCase):

    def test_the_manifests_agree(self):
        project = tomllib.loads((PACKAGE / 'pyproject.toml').read_text())[
            'project']
        self.assertEqual(project['license'], GRANT)
        self.assertEqual(project['license-files'], CORE['license-files'])
        package = json.loads((WIDGET / 'package.json').read_text())
        self.assertEqual(package['license'], GRANT)

    def test_the_licence_texts_are_the_repository_s(self):
        for entry in ('LICENSE', 'LICENSES'):
            with self.subTest(entry=entry):
                link = PACKAGE / entry
                self.assertTrue(link.is_symlink(), f'{link} is not a link')
                self.assertEqual(link.resolve(), REPOSITORY / entry)

    def test_every_header_states_the_grant(self):
        headers = 0
        for relative in tracked_files():
            if relative.as_posix().startswith(HISTORY):
                continue
            text = text_of(relative)
            if text is None:
                continue
            if relative.as_posix() == SELF:
                text = '\n'.join(text.splitlines()[:3])
            for identifier in SPDX.findall(text):
                headers += 1
                with self.subTest(file=relative.as_posix()):
                    self.assertEqual(identifier, GRANT)
        self.assertGreater(headers, 150, 'the scan found too few headers')

    def test_the_banner_template_states_the_grant_and_the_source(self):
        build = (WIDGET / 'build.mjs').read_text()
        self.assertIn(f'SPDX-License-Identifier: {GRANT}', build)
        self.assertIn(SOURCE, build)

    def test_the_readme_states_the_licence(self):
        readme = ' '.join((PACKAGE / 'README.md').read_text().split())
        self.assertIn(WORDS, readme)

    def test_a_built_bundle_opens_with_the_grant(self):
        bundle = WIDGET / 'dist' / 'machinome-viewer.js'
        if not bundle.exists():
            self.skipTest('no built bundle in this checkout')
        with bundle.open(encoding='utf-8') as fh:
            head = fh.read(2000)
        self.assertIn(f'SPDX-License-Identifier: {GRANT}', head)
        self.assertIn(SOURCE, head)


if __name__ == '__main__':
    unittest.main()
