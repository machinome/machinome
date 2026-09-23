"""One integration may reuse only complete, successful profile work."""

import math
import struct
import unittest
from unittest.mock import patch

from machinome.simulation import profile as contact
from machinome.simulation.profile import ConvexProfile, profile_overlap


SQUARE = ConvexProfile((((0.0, 0.0), (1.0, 0.0),
                         (1.0, 1.0), (0.0, 1.0)),))


def squares(count, start=0.0):
    return ConvexProfile(tuple(
        ((x, 0.0), (x + 1.0, 0.0), (x + 1.0, 1.0), (x, 1.0))
        for x in (start + 3.0 * index for index in range(count))))


class ProfileIntegrationCacheTest(unittest.TestCase):

    def test_large_reused_right_indexes_only_after_success(self):
        left, right = squares(32), squares(16, 1000.0)
        right_key = contact._placement_key(right, 0.0, (0.0, 0.0))
        with contact._profile_integration_cache() as cache:
            self.assertEqual(profile_overlap(left, right, 0.0, 0.0), 0.0)
            self.assertIsNone(getattr(cache.placements[right_key], 'box_tree', None))
            self.assertEqual(profile_overlap(left, right, 1.0, 0.0), 0.0)
            self.assertIsNotNone(cache.placements[right_key].box_tree)
            self.assertEqual(len(cache.placements), 3)
        self.assertIsNone(contact._INTEGRATION_CACHE.get())

    def test_skewed_reused_right_does_not_build_index(self):
        right = squares(512, 10000.0)
        right_key = contact._placement_key(right, 0.0, (0.0, 0.0))
        for left in (squares(1), squares(2)):
            with self.subTest(left=len(left.polygons)):
                with contact._profile_integration_cache() as cache:
                    for angle in (0.0, 1.0, 2.0):
                        self.assertEqual(profile_overlap(left, right, angle, 0.0), 0.0)
                    self.assertIsNone(getattr(cache.placements[right_key], 'box_tree', None))

    def test_index_preserves_late_pair_contact_and_strict_clearance(self):
        left = squares(32)
        right = ConvexProfile(squares(15, 1000.0).polygons +
                              squares(1, 94.0).polygons)
        with contact._profile_integration_cache() as cache:
            self.assertEqual(profile_overlap(left, right, 0.0, 0.0,
                                             left_xy=(-1000.0, 0.0)), 0.0)
            self.assertEqual(profile_overlap(left, right, 0.0, 0.0), 1.0)
            self.assertIsNotNone(cache.placements[
                contact._placement_key(right, 0.0, (0.0, 0.0))].box_tree)
            self.assertEqual(profile_overlap(left, right, 0.0, 0.0,
                                             left_xy=(0.0, 1.0000000000000002)), 0.0)

    def test_later_sat_failure_does_not_attach_tree_to_cached_right(self):
        huge = ((0.0, 0.0), (1e200, 0.0),
                (1e200, 1e200), (0.0, 1e200))
        # The last polygon sorts before the first huge one spatially. If the
        # tree's traversal order leaked into SAT, it would return contact
        # instead of the first pair's projection refusal.
        late_contact = ((-0.5, 0.0), (0.5, 0.0),
                        (0.5, 1.0), (-0.5, 1.0))
        right = ConvexProfile((huge,) + squares(14, 10000.0).polygons +
                              (late_contact,))
        safe_left = squares(32, -1000.0)
        failing_left = ConvexProfile((late_contact,) +
                                     squares(31, -10000.0).polygons)
        right_key = contact._placement_key(right, 0.0, (0.0, 0.0))
        with contact._profile_integration_cache() as cache:
            self.assertEqual(profile_overlap(safe_left, right, 0.0, 0.0), 0.0)
            self.assertIsNone(getattr(cache.placements[right_key], 'box_tree', None))
            with self.assertRaisesRegex(ValueError, 'projection'):
                profile_overlap(failing_left, right, 0.0, 0.0)
            self.assertIsNone(getattr(cache.placements[right_key], 'box_tree', None))

    def test_apparent_early_contact_cannot_hide_later_collapsed_edge(self):
        width = 4e284
        def broad_square(x):
            return ((x, 0.0), (x + width, 0.0),
                    (x + width, width), (x, width))

        left = ConvexProfile(tuple(broad_square(1e300 + 1e286 * index)
                                   for index in range(32)))
        right = ConvexProfile((broad_square(0.0),) + squares(15).polygons)
        with contact._profile_integration_cache() as cache:
            with self.assertRaisesRegex(ValueError, 'collapsed'):
                profile_overlap(left, right, 0.0, 0.0,
                                right_xy=(1e300, 0.0))
            self.assertEqual(len(cache.placements), 0)
            self.assertEqual(len(cache.pairs), 0)

    def test_failed_tree_build_and_custom_operand_leave_cache_untouched(self):
        left, right = squares(32), squares(16, 1000.0)
        right_key = contact._placement_key(right, 0.0, (0.0, 0.0))

        class CustomAngle:
            calls = 0

            def __float__(self):
                self.calls += 1
                return 2.0

        custom = CustomAngle()
        with contact._profile_integration_cache() as cache:
            self.assertEqual(profile_overlap(left, right, 0.0, 0.0), 0.0)
            with patch.object(contact, '_box_tree', side_effect=RuntimeError('tree build')):
                with self.assertRaisesRegex(RuntimeError, 'tree build'):
                    profile_overlap(left, right, 1.0, 0.0)
            self.assertIsNone(cache.placements[right_key].box_tree)
            self.assertEqual(len(cache.pairs), 1)
            self.assertEqual(profile_overlap(left, right, custom, 0.0), 0.0)
            self.assertEqual(custom.calls, 1)
            self.assertIsNone(cache.placements[right_key].box_tree)

    def test_cached_tree_evicts_with_placement(self):
        left, right = squares(32), squares(16, 1000.0)
        right_key = contact._placement_key(right, 0.0, (0.0, 0.0))
        with contact._profile_integration_cache() as cache:
            self.assertEqual(profile_overlap(left, right, 0.0, 0.0), 0.0)
            self.assertEqual(profile_overlap(left, right, 1.0, 0.0), 0.0)
            self.assertIsNotNone(cache.placements[right_key].box_tree)
            for index in range(260):
                self.assertEqual(profile_overlap(SQUARE, SQUARE, 0.0, 0.0,
                                                 right_xy=(float(index + 2), 0.0)), 0.0)
            self.assertNotIn(right_key, cache.placements)
            self.assertLessEqual(len(cache.placements), 256)

    def test_index_bounds_do_not_overflow_extreme_finite_separation(self):
        def huge_profile(count, origin):
            return ConvexProfile(tuple(
                ((x, -0.0), (x + 4e292, -0.0),
                 (x + 4e292, 4e292), (x, 4e292))
                for x in (origin + 1e294 * index for index in range(count))))

        left = huge_profile(32, -1e308)
        right = huge_profile(16, 1e308)
        with contact._profile_integration_cache() as cache:
            for angle in (-0.0, 0.0):
                self.assertEqual(struct.pack('!d', profile_overlap(
                    left, right, angle, 0.0)), struct.pack('!d', 0.0))
            self.assertIsNotNone(cache.placements[
                contact._placement_key(right, 0.0, (0.0, 0.0))].box_tree)

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
