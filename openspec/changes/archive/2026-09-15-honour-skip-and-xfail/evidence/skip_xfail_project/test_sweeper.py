import unittest

from solid_node.test import TestCase, testing_steps


class SweeperTest(TestCase):

    def setUp(self):
        # setUp runs once per test method, so the counter counts the
        # instants the runner iterates over inside one method.
        self.seen = []

    @testing_steps(3)
    def test_skip_at_one_instant(self):
        self.seen.append(len(self.seen))
        print(f"  [body ran, instant #{len(self.seen)}]")
        if len(self.seen) == 2:
            self.skipTest('nothing to compare at mid-sweep')

    @testing_steps(3)
    def test_fail_at_one_instant(self):
        self.seen.append(len(self.seen))
        if len(self.seen) == 2:
            raise AssertionError('mid-sweep regression')

    @unittest.expectedFailure
    @testing_steps(3)
    def test_expected_failure_over_a_sweep(self):
        self.seen.append(len(self.seen))
        if len(self.seen) == 2:
            raise AssertionError('the known kernel gap, mid-sweep')

    def test_instants_attribute_survives_the_decorator_pair(self):
        print('  instants on test_expected_failure_over_a_sweep: '
              f'{getattr(SweeperTest.test_expected_failure_over_a_sweep, "testing_instants", None)}'
              '; __unittest_expecting_failure__: '
              f'{getattr(SweeperTest.test_expected_failure_over_a_sweep, "__unittest_expecting_failure__", None)}')
