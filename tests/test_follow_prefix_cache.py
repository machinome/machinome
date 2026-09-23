"""A shared Follow prefix is evaluated once per identical Bound probe."""

from copy import copy
from dataclasses import replace
import math
from unittest import TestCase
from unittest.mock import patch

from machinome.simulation import Sim
from machinome.simulation.program import Edge
from machinome.simulation.run import Run

from .test_running_follow import TwoSurfaces


class FollowPrefixCacheTest(TestCase):
    @staticmethod
    def _probe_inputs(sim):
        run = sim._run
        low = run.program.constraints[('ball.slide', 'low')]
        high = run.program.constraints[('ball.slide', 'high')]
        values = run.program.values_of(run.bank)
        admissions = {'low': 2.0, 'high': -2.0}
        return run, low, high, values, admissions

    @staticmethod
    def _level(run, constraint, values, admissions, t, cache):
        return run._constraint_level(
            constraint, run.bank, values, admissions, t,
            run.bank['ball.slide'], cache)

    def test_paired_bounds_do_not_replay_the_same_follow_prefix_twice(self):
        sim = Sim(TwoSurfaces(), dt=1.0)
        lower = sim.move('low', to=2.0, duration=1.0)
        upper = sim.move('high', to=1.0, duration=1.0)
        calls = []
        original = Edge.increments

        def observed(edge, *args, **kwargs):
            if edge.kind == 'follow':
                calls.append(edge)
            return original(edge, *args, **kwargs)

        with patch.object(Edge, 'increments', observed):
            sim.run(1.0)
        self.assertEqual((lower.status, upper.status), ('blocked', 'blocked'))
        self.assertEqual((sim.state['low'], sim.state['high'],
                          sim.state['ball.slide']), (1.5, 1.5, 1.5))
        # Baseline f4c48f6 replays Follow 157 times here: the two Bounds
        # repeat the same certified prefix at most of their common samples.
        self.assertLess(len(calls), 120)

    def test_exact_fraction_bits_and_distinct_edges_miss(self):
        sim = Sim(TwoSurfaces(), dt=1.0)
        run, low, high, values, admissions = self._probe_inputs(sim)
        other_edge = replace(high, edges=high.edges[:-1] +
                             (copy(high.edges[-1]),))
        cache = {}
        fractions = (0.5, math.nextafter(0.5, -math.inf),
                     0.0, -0.0)
        original = Edge.increments
        calls = []

        def observed(edge, *args, **kwargs):
            if edge.kind == 'follow':
                calls.append(edge)
            return original(edge, *args, **kwargs)

        with patch.object(Edge, 'increments', observed):
            for fraction in fractions:
                for constraint in (low, high):
                    expected = self._level(run, constraint, values,
                                           admissions, fraction, None)
                    actual = self._level(run, constraint, values,
                                         admissions, fraction, cache)
                    self.assertEqual(float(actual).hex(),
                                     float(expected).hex())
            self._level(run, other_edge, values, admissions, 0.5, cache)
        # Each uncached reference above deliberately walks Follow once;
        # the optimized pair walks it once more, not twice.
        self.assertEqual(len(calls), 2 * len(fractions) +
                         len(fractions) + 1)
        self.assertEqual(len(cache), len(fractions) + 1)

    def test_failed_prefix_is_not_published_and_bound_still_evaluates(self):
        sim = Sim(TwoSurfaces(), dt=1.0)
        run, low, high, values, admissions = self._probe_inputs(sim)
        cache = {}
        original = Edge.increments

        def failing(edge, *args, **kwargs):
            if edge.kind == 'follow':
                raise ValueError('first prefix failure')
            return original(edge, *args, **kwargs)

        class FailingBound:
            def evaluate(self, arguments):
                raise ZeroDivisionError('own bound failure')

        changed = replace(high, graph=FailingBound())
        with patch.object(Edge, 'increments', failing):
            with self.assertRaisesRegex(ValueError, 'first prefix failure'):
                self._level(run, changed, values, admissions, 0.5, cache)
        self.assertEqual(cache, {})
        self._level(run, low, values, admissions, 0.5, cache)
        with self.assertRaisesRegex(ZeroDivisionError, 'own bound failure'):
            self._level(run, changed, values, admissions, 0.5, cache)
        self.assertEqual(len(cache), 1)

    def test_restore_replay_uses_a_new_stretch_local_cache(self):
        sim = Sim(TwoSurfaces(), dt=1.0)
        rest = sim.snapshot()
        seen = []
        original = Run._constraint_level

        def observed(run, constraint, held, values, admissions, t, own,
                     prefix_cache=None):
            if prefix_cache is not None and all(
                    prefix_cache is not prior for prior in seen):
                seen.append(prefix_cache)  # Keep identities alive.
            return original(run, constraint, held, values, admissions, t,
                            own, prefix_cache)

        with patch.object(Run, '_constraint_level', observed):
            for replay in (False, True):
                if replay:
                    sim.restore(rest)
                lower = sim.move('low', to=2.0, duration=1.0)
                upper = sim.move('high', to=1.0, duration=1.0)
                sim.run(1.0)
                self.assertEqual((lower.status, upper.status),
                                 ('blocked', 'blocked'))
                if not replay:
                    stopped = sim.snapshot()
                    first_stretch_caches = tuple(seen)
                else:
                    self.assertEqual(sim.snapshot(), stopped)
        self.assertGreater(len(seen), len(first_stretch_caches))
        self.assertTrue(all(cache is not prior
                            for cache in seen[len(first_stretch_caches):]
                            for prior in first_stretch_caches))

    def test_changed_admission_uses_a_fresh_tick_cache(self):
        sim = Sim(TwoSurfaces(), dt=1.0)
        original = Run._constraint_level
        seen = []

        def observed(run, constraint, held, values, admissions, t, own,
                     prefix_cache=None):
            if prefix_cache is not None and all(
                    prefix_cache is not prior for prior in seen):
                seen.append(prefix_cache)
            return original(run, constraint, held, values, admissions, t,
                            own, prefix_cache)

        with patch.object(Run, '_constraint_level', observed):
            first = sim.move('low', to=1.0, duration=1.0)
            sim.run(1.0)
            first_caches = tuple(seen)
            second = sim.move('high', to=2.0, duration=1.0)
            sim.run(1.0)
        self.assertEqual((first.status, second.status),
                         ('completed', 'completed'))
        self.assertEqual((sim.state['low'], sim.state['high'],
                          sim.state['ball.slide']), (1.0, 2.0, 1.0))
        self.assertTrue(first_caches)
        self.assertGreater(len(seen), len(first_caches))
        self.assertTrue(all(cache is not prior
                            for cache in seen[len(first_caches):]
                            for prior in first_caches))
