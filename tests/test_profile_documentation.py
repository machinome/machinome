"""Finite profile contact is documented as part of the 0.7.0 release."""

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
        # The first section of each record is the 0.7.0 release itself.
        self.assertNotIn('unreleased', changelog.split('machinome 0.7.0')[0])
        self.assertNotIn('unreleased', history.split('machinome 0.7.0')[0])
        self.assertIn('profile contact', status)
        self.assertIn('schema 13', status)
        released = changelog.split('machinome 0.7.0')[1]
        self.assertIn('finite profile contact', released)
        self.assertIn('schema 13', released)
        self.assertIn('api 26 and schemas 1–13', released)
        self.assertIn('adr-144', history.split('0.6.0 (')[0])
        self.assertIn("viewer_api = '26'", conf)
        self.assertIn("document_versions = '1 to 13'", conf)


if __name__ == '__main__':
    unittest.main()
