"""One integration may reuse only complete, successful profile work."""

import math
import unittest
from unittest.mock import patch

from machinome.simulation import profile as contact
from machinome.simulation.profile import ConvexProfile, profile_overlap


SQUARE = ConvexProfile((((0.0, 0.0), (1.0, 0.0),
                         (1.0, 1.0), (0.0, 1.0)),))


class ProfileIntegrationCacheTest(unittest.TestCase):

    def test_repeated_pair_and_placement_skip_only_successful_work(self):
        with patch.object(contact, '_placed', wraps=contact._placed) as placed:
            with contact._profile_integration_cache() as cache:
                self.assertEqual(profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                                                 right_xy=(2.0, 0.0)), 0.0)
                self.assertEqual(profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                                                 right_xy=(2.0, 0.0)), 0.0)
                self.assertEqual(placed.call_count, 2)
                self.assertEqual(len(cache.pairs), 1)
                self.assertEqual(len(cache.placements), 2)
            self.assertEqual(profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                                             right_xy=(2.0, 0.0)), 0.0)
            self.assertEqual(placed.call_count, 4)

    def test_signed_zero_and_distinct_profile_objects_do_not_alias(self):
        equal_other = ConvexProfile(SQUARE.polygons)
        with contact._profile_integration_cache() as cache:
            profile_overlap(SQUARE, SQUARE, -0.0, 0.0,
                            right_xy=(2.0, 0.0))
            profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                            right_xy=(2.0, 0.0))
            profile_overlap(equal_other, SQUARE, 0.0, 0.0,
                            right_xy=(2.0, 0.0))
            self.assertEqual(len(cache.pairs), 3)

    def test_custom_numeric_and_failed_placement_are_never_cached(self):
        class ChangingAngle:
            calls = 0

            def __float__(self):
                self.calls += 1
                return 0.0

        angle = ChangingAngle()
        with contact._profile_integration_cache() as cache:
            for _ in range(2):
                self.assertEqual(profile_overlap(SQUARE, SQUARE, angle, 0.0,
                                                 right_xy=(2.0, 0.0)), 0.0)
            self.assertEqual(angle.calls, 2)
            with self.assertRaisesRegex(ValueError, 'collapsed'):
                profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                                left_xy=(1e300, 0.0),
                                right_xy=(-1e300, 0.0))
            with self.assertRaisesRegex(ValueError, 'finite'):
                profile_overlap(SQUARE, SQUARE, math.nan, 0.0)
            self.assertEqual(len(cache.pairs), 0)

    def test_failed_right_placement_does_not_publish_left_preparation(self):
        with contact._profile_integration_cache() as cache:
            for _ in range(2):
                with self.assertRaisesRegex(ValueError, 'collapsed'):
                    profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                                    right_xy=(1e300, 0.0))
            self.assertEqual(len(cache.placements), 0)
            self.assertEqual(len(cache.pairs), 0)

    def test_cache_preflight_does_not_reorder_first_invalid_operand(self):
        with contact._profile_integration_cache() as cache:
            with self.assertRaisesRegex(ValueError, 'collapsed'):
                profile_overlap(SQUARE, SQUARE, 0.0, math.nan,
                                left_xy=(1e300, 0.0))
            self.assertEqual(len(cache.placements), 0)
            self.assertEqual(len(cache.pairs), 0)

    def test_projection_failure_after_both_placements_publishes_nothing(self):
        huge = ConvexProfile((((0.0, 0.0), (1e200, 0.0),
                               (1e200, 1e200), (0.0, 1e200)),))
        with contact._profile_integration_cache() as cache:
            for _ in range(2):
                with self.assertRaisesRegex(ValueError, 'projection'):
                    profile_overlap(huge, huge, 0.0, 0.0)
            self.assertEqual(len(cache.placements), 0)
            self.assertEqual(len(cache.pairs), 0)

    def test_custom_xy_indexing_has_no_extra_cache_preflight_reads(self):
        class MeasuredXY:
            reads = 0

            def __getitem__(self, index):
                self.reads += 1
                return (2.0, 0.0)[index]

            def __iter__(self):
                return iter((2.0, 0.0))

        xy = MeasuredXY()
        with contact._profile_integration_cache() as cache:
            for _ in range(2):
                self.assertEqual(profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                                                 right_xy=xy), 0.0)
            self.assertEqual(xy.reads, 4)
            self.assertEqual(len(cache.pairs), 0)
            self.assertEqual(len(cache.placements), 0)

    def test_both_entry_limits_evict_without_changing_results(self):
        with contact._profile_integration_cache() as cache:
            for index in range(1030):
                self.assertEqual(profile_overlap(
                    SQUARE, SQUARE, 0.0, 0.0,
                    right_xy=(float(index + 2), 0.0)), 0.0)
            self.assertLessEqual(len(cache.pairs), 1024)
            self.assertLessEqual(len(cache.placements), 256)
            self.assertEqual(profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                                             right_xy=(2.0, 0.0)), 0.0)

    def test_nested_attempts_and_exception_do_not_share_entries(self):
        self.assertIsNone(contact._INTEGRATION_CACHE.get())
        with contact._profile_integration_cache() as first:
            profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                            right_xy=(2.0, 0.0))
            self.assertEqual(len(first.pairs), 1)
            with contact._profile_integration_cache() as second:
                self.assertIsNot(first, second)
                self.assertEqual(len(second.pairs), 0)
            self.assertIs(contact._INTEGRATION_CACHE.get(), first)
        self.assertIsNone(contact._INTEGRATION_CACHE.get())
        with self.assertRaisesRegex(RuntimeError, 'abort'):
            with contact._profile_integration_cache() as aborted:
                profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                                right_xy=(2.0, 0.0))
                raise RuntimeError('abort')
        self.assertEqual(len(aborted.pairs), 1)
        self.assertIsNone(contact._INTEGRATION_CACHE.get())


if __name__ == '__main__':
    unittest.main()
