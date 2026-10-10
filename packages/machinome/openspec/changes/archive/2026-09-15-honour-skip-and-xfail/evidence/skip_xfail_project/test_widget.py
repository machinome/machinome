import unittest

from solid_node.test import TestCase


class WidgetTest(TestCase):

    def test_plain_pass(self):
        self.assertIsNotNone(self.node)

    def test_skipped(self):
        self.skipTest('the exact kernel is not available here')

    @unittest.expectedFailure
    def test_expected_failure_raises(self):
        raise AssertionError('the known kernel gap')

    @unittest.expectedFailure
    def test_expected_failure_passes(self):
        pass

    def test_plain_fail(self):
        raise AssertionError('a real regression')
