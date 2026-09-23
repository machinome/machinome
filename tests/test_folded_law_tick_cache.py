"""Successful structural law folds are reused only inside one tick."""

import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from machinome.expression_graph import ExpressionNode
from machinome.simulation import program
from machinome.simulation.run import Run


def name(text):
    return ExpressionNode('name', text=text)


def plus(root):
    return ExpressionNode('binop', '+', (root, name('other')))


class FoldedLawTickCacheTest(unittest.TestCase):
    def test_repeated_exact_fold_reuses_success_only_inside_scope(self):
        root = plus(name('x'))
        original = program._folded_uncached
        calls = []

        def counted(node, values):
            calls.append(1)
            return original(node, values)

        with patch.object(program, '_folded_uncached', side_effect=counted):
            with program._folded_tick_cache():
                first = program._folded(root, {'x': 1.0})
                self.assertIs(program._folded(root, {'x': 1.0}), first)
            self.assertEqual(len(calls), 1)
        self.assertIsNot(program._folded(root, {'x': 1.0}), first)

    def test_root_and_entire_mapping_and_signed_zero_are_distinct(self):
        root = ExpressionNode('call', 'max', (name('x'), name('other')))
        other_root = ExpressionNode('call', 'max', (name('x'), name('other')))
        with program._folded_tick_cache():
            first = program._folded(root, {'x': 0.0, 'unused': 1})
            self.assertIsNot(program._folded(root, {'x': -0.0, 'unused': 1}), first)
            self.assertIsNot(program._folded(root, {'x': 0.0, 'unused': 2}), first)
            self.assertIsNot(program._folded(other_root, {'x': 0.0, 'unused': 1}), first)

    def test_custom_and_nonfinite_never_reuse(self):
        root = plus(name('x'))

        class Converts:
            calls = 0

            def __float__(self):
                self.calls += 1
                return 2.0

        value = Converts()
        with program._folded_tick_cache():
            first = program._folded(root, {'x': value})
            second = program._folded(root, {'x': value})
            self.assertIsNot(first, second)
            self.assertEqual(value.calls, 2)
            first = program._folded(root, {'x': math.inf})
            self.assertIsNot(program._folded(root, {'x': math.inf}), first)
            first = program._folded(root, {'x': math.nan})
            self.assertIsNot(program._folded(root, {'x': math.nan}), first)

    def test_overflowing_unused_builtin_int_takes_original_fold(self):
        root = plus(name('x'))
        enormous = 10 ** 10000
        with program._folded_tick_cache():
            first = program._folded(root, {'x': 2, 'unused': enormous})
            self.assertIsNot(program._folded(root, {'x': 2,
                                                     'unused': enormous}),
                             first)

    def test_eligible_failed_fold_does_not_publish(self):
        root = plus(name('x'))
        original = program._folded_uncached
        calls = []

        def once_failing(node, values):
            calls.append(1)
            if len(calls) == 1:
                raise ValueError('original first error')
            return original(node, values)

        with patch.object(program, '_folded_uncached', side_effect=once_failing):
            with program._folded_tick_cache():
                with self.assertRaisesRegex(ValueError, 'original first error'):
                    program._folded(root, {'x': 2.0})
                good = program._folded(root, {'x': 2.0})
                self.assertIs(program._folded(root, {'x': 2.0}), good)
        self.assertEqual(len(calls), 2)

    def test_failed_fold_is_not_published_and_scope_resets_on_failure(self):
        root = plus(name('x'))
        with self.assertRaises(ValueError):
            with program._folded_tick_cache():
                result = program._folded(root, {'x': 3.0})
                self.assertIs(program._folded(root, {'x': 3.0}), result)
                for _ in range(2):
                    with self.assertRaises(ValueError):
                        program._folded(root, {'x': 'not a number'})
                raise ValueError('tick failed')
        with program._folded_tick_cache():
            self.assertIsNot(program._folded(root, {'x': 3.0}), result)

    def test_eviction_recomputes_oldest_entry(self):
        root = ExpressionNode('call', 'max', (name('x'), name('other')))
        with program._folded_tick_cache():
            first = program._folded(root, {'x': 0})
            for value in range(1, 257):
                program._folded(root, {'x': value})
            self.assertIsNot(program._folded(root, {'x': 0}), first)

    def test_nested_scope_does_not_import_other_runs_entry(self):
        root = plus(name('x'))
        with program._folded_tick_cache():
            outer = program._folded(root, {'x': 1})
            with program._folded_tick_cache():
                self.assertIsNot(program._folded(root, {'x': 1}), outer)
            self.assertIs(program._folded(root, {'x': 1}), outer)

    def test_advance_scopes_each_run_and_releases_failed_tick(self):
        root = plus(name('x'))
        results = []

        def integrate(_tick, advance):
            self.assertTrue(advance)
            result = program._folded(root, {'x': 3})
            self.assertIs(program._folded(root, {'x': 3}), result)
            results.append(result)

        first_run = SimpleNamespace(sim=SimpleNamespace(tick=0),
                                    integrate=integrate)
        second_run = SimpleNamespace(sim=SimpleNamespace(tick=0),
                                     integrate=integrate)
        Run.advance(first_run)
        Run.advance(second_run)
        self.assertIsNot(results[0], results[1])

        def fails(_tick, advance):
            result = program._folded(root, {'x': 3})
            results.append(result)
            raise ValueError('tick refused')

        first_run.integrate = fails
        with self.assertRaisesRegex(ValueError, 'tick refused'):
            Run.advance(first_run)
        first_run.integrate = integrate
        Run.advance(first_run)
        self.assertIsNot(results[-1], results[-2])
