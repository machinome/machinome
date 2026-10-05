"""Finite profile contact is documented as part of the 0.7.0 release."""

import re
import unittest
from pathlib import Path

from machinome.simulation.profile import ConvexProfile, profile_overlap


ROOT = Path(__file__).resolve().parent.parent


class ProfileDocumentationTest(unittest.TestCase):

    def test_public_imports_describe_pointwise_limit(self):
        self.assertEqual(ConvexProfile.__module__, 'machinome.simulation.profile')
        self.assertEqual(profile_overlap.__module__, 'machinome.simulation.profile')
        self.assertIn('pointwise', profile_overlap.__doc__.lower())
        self.assertIn('running bound', profile_overlap.__doc__.lower())

    def test_released_status_changelog_and_history(self):
        status = (ROOT / 'docs/project/status.rst').read_text().lower()
        changelog = (ROOT / 'docs/project/changelog.rst').read_text().lower()
        history = (ROOT / 'HISTORY.rst').read_text().lower()
        conf = (ROOT / 'docs/conf.py').read_text()
        for text in (status, changelog, history):
            self.assertNotIn('current source', text)
        # The first RELEASED section of each record is the 0.7.0 release
        # itself. Work since the release sits above it in the changelog's
        # one `Unreleased` section (skills/write-the-manual, "Work after
        # a release"), and nowhere else.
        head = changelog.split('machinome 0.7.0')[0]
        self.assertNotIn('unreleased',
                         head.replace('\nunreleased\n----------\n', '\n', 1))
        self.assertNotIn('unreleased', history.split('machinome 0.7.0')[0])
        self.assertIn('profile contact', status)
        self.assertIn('schema 13', status)
        released = changelog.split('machinome 0.7.0')[1]
        self.assertIn('finite profile contact', released)
        self.assertIn('schema 13', released)
        self.assertIn('api 27 and schemas 1–13', released)
        self.assertIn('two turn controls', released)
        self.assertIn('compatible child replacement', released)
        self.assertIn('adr-144', history.split('0.6.0 (')[0])
        self.assertIn('adr-146', history.split('0.6.0 (')[0])
        # Profile contact and two Turn handles on one part arrived with
        # viewer API 27; a later matching viewer keeps them.
        api = re.search(r"^viewer_api = '(\d+)'", conf, flags=re.M)[1]
        self.assertGreaterEqual(int(api), 27)
        self.assertIn("document_versions = '1 to 13'", conf)


if __name__ == '__main__':
    unittest.main()
