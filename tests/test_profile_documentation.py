"""The current-source profile API must not rewrite the 0.7 release story."""

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

    def test_current_source_status_and_unreleased_changelog(self):
        status = (ROOT / 'docs/project/status.rst').read_text().lower()
        changelog = (ROOT / 'docs/project/changelog.rst').read_text().lower()
        self.assertIn('current source', status)
        self.assertIn('profile contact', status)
        self.assertIn('version 13', status)
        self.assertIn('unreleased', changelog)
        self.assertIn('profile contact', changelog.split('machinome 0.7.0')[0])
        self.assertIn('version 13', changelog.split('machinome 0.7.0')[0])


if __name__ == '__main__':
    unittest.main()
