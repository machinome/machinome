"""The semantics `solid test` is measured against: what unittest itself
does with the same five methods. Run:

    PYTHONPATH="$PWD" .venv/bin/python openspec/changes/honour-skip-and-xfail/evidence/probe_unittest_reference.py
"""
import sys
import unittest


class ReferenceTest(unittest.TestCase):

    def test_plain_pass(self):
        pass

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


class SkipInsideExpectedFailure(unittest.TestCase):
    """What unittest does when a test that is expected to fail skips
    instead -- the precedence this change must copy."""

    @unittest.expectedFailure
    def test_skips(self):
        self.skipTest('no kernel here')


def _precedence():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        SkipInsideExpectedFailure)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f'skipped={len(result.skipped)} '
          f'expectedFailures={len(result.expectedFailures)} '
          f'unexpectedSuccesses={len(result.unexpectedSuccesses)} '
          f'wasSuccessful={result.wasSuccessful()}')


if __name__ == '__main__':
    print(f'python {sys.version}')
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(f'\ntestsRun={result.testsRun} '
          f'failures={len(result.failures)} '
          f'errors={len(result.errors)} '
          f'skipped={len(result.skipped)} '
          f'expectedFailures={len(result.expectedFailures)} '
          f'unexpectedSuccesses={len(result.unexpectedSuccesses)} '
          f'wasSuccessful={result.wasSuccessful()}')
    print('\n=== skip inside an expectedFailure test')
    _precedence()
    sys.exit(0 if result.wasSuccessful() else 1)
