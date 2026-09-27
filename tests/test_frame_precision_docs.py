"""The public precision distinction is taught at its existing entry points."""
from pathlib import Path
import unittest
from machinome.node.frames import Frame, ResolvedFrame

ROOT = Path(__file__).resolve().parents[1]


class PrecisionDocumentationTest(unittest.TestCase):
    def test_docstrings_and_manual_distinguish_presence_and_final_snap(self):
        passages = (Frame.__doc__, ResolvedFrame.__doc__,
                    (ROOT / 'docs/concepts/joints.rst').read_text())
        for passage in passages:
            with self.subTest(passage=passage[:40]):
                for phrase in ('both', 'explicitly', 'omitted', 'snap'):
                    self.assertIn(phrase, passage)
                self.assertIn('mate', passage)
                self.assertIn('joint', passage.lower())
                self.assertIn('both directions explicitly', passage)

    def test_changelog_records_precision_in_the_release_that_ships_it(self):
        text = (ROOT / 'docs/project/changelog.rst').read_text()
        current, earlier = text.split('Machinome 0.7.0', 1)
        self.assertIn('Machinome 0.7.1', current)
        self.assertNotIn('Unreleased', current)
        self.assertIn('explicit direction precision', current)
        self.assertNotIn('explicit direction precision', earlier)
