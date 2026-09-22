"""A running Bound can reuse a proven unchanged standing first-sample DAG."""

import struct
from unittest import TestCase
from unittest.mock import patch

from machinome.expression_graph import ExpressionNode
from machinome.motion.joints import Bound, Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver, Sim
from machinome.simulation.program import _PathValue

from .running_project.parts import Arbor


def name(text):
    return ExpressionNode('name', text=text)


def num(value):
    return ExpressionNode('num', text=str(value))


def bits(value):
    return struct.pack('!d', float(value))


class RunningStandingBound(AssemblyNode):
    time = Time.running()
    crank = Driver(default=0.0, unit='deg')
    gap = Driver(default=2.0, unit='deg')
    wheel = Arbor(turn=Revolute(axis=(0, 0, 1), unit='deg', range=(
        None, Bound(lambda own, crank, gap: crank + gap + 100,
                    reads=(crank, gap)))))
    crank.drives(wheel.turn, ratio=1.0)


class BoundStandingBindCacheTest(TestCase):
    def test_same_standing_bits_reuse_but_moving_first_sample_is_fresh(self):
        standing = ExpressionNode('binop', '*', (name('rest'), num(7)))
        root = ExpressionNode('binop', '+', (standing, name('moving')))
        first = _PathValue(root, {'moving'})
        self.assertEqual(first.bind({'rest': 3, 'moving': 1}), 22)
        saved = first.standing_snapshot({'rest': 3, 'moving': 1})

        second = _PathValue(root, {'moving'})
        with patch('machinome.simulation.program._path_node_value',
                   side_effect=AssertionError('standing graph rebound')):
            hit, result = second.bind_from({'rest': 3, 'moving': 4}, saved)
        self.assertTrue(hit)
        self.assertEqual(result, 25)
        self.assertEqual(second.at({'moving': 6}), 27)

        changed = _PathValue(root, {'moving'})
        self.assertFalse(changed.bind_from({'rest': 4, 'moving': 4}, saved)[0])
        self.assertEqual(changed.bind({'rest': 4, 'moving': 4}), 32)
        shape = _PathValue(root, {'rest'})
        self.assertFalse(shape.bind_from({'rest': 3, 'moving': 4}, saved)[0])

        class ConvertingNumber:
            calls = 0

            def __float__(self):
                self.calls += 1
                return 3.0

        custom = ConvertingNumber()
        uncertain = _PathValue(root, {'moving'})
        self.assertFalse(uncertain.bind_from({'rest': custom,
                                              'moving': 4}, saved)[0])
        self.assertEqual(custom.calls, 0)
        self.assertEqual(uncertain.bind({'rest': custom, 'moving': 4}), 25)
        self.assertEqual(custom.calls, 1)

    def test_signed_zero_nonfinite_missing_and_failed_bind_do_not_alias(self):
        root = ExpressionNode('binop', '+', (
            ExpressionNode('binop', '*', (name('rest'), num(1))),
            name('moving')))
        first = _PathValue(root, {'moving'})
        first.bind({'rest': 0.0, 'moving': 1})
        saved = first.standing_snapshot({'rest': 0.0, 'moving': 1})
        for value in (-0.0, float('nan'), float('inf'), -float('inf')):
            with self.subTest(value=value):
                self.assertFalse(_PathValue(root, {'moving'}).bind_from(
                    {'rest': value, 'moving': 1}, saved)[0])
        self.assertFalse(_PathValue(root, {'moving'}).bind_from(
            {'moving': 1}, saved)[0])

        negative = _PathValue(root, {'moving'})
        negative.bind({'rest': -0.0, 'moving': 0.0})
        self.assertNotEqual(bits(first.standing[standing_name(root)]),
                            bits(negative.standing[standing_name(root)]))
        self.assertIsNone(negative.standing_snapshot(
            {'rest': float('nan'), 'moving': 0.0}))

        failing = ExpressionNode('binop', '/', (num(1), name('rest')))
        bad = _PathValue(failing, {'moving'})
        with self.assertRaises(ZeroDivisionError):
            bad.bind({'rest': 0, 'moving': 1})
        self.assertIsNone(bad.standing_snapshot({'rest': 0, 'moving': 1}))

    def test_changed_standing_preserves_first_error_and_failed_hit_is_atomic(self):
        standing = name('rest')
        moving = ExpressionNode('binop', '/', (num(1), name('moving')))
        root = ExpressionNode('binop', '+', (standing, moving))
        first = _PathValue(root, {'moving'})
        self.assertEqual(first.bind({'rest': 2, 'moving': 2}), 2.5)
        saved = first.standing_snapshot({'rest': 2, 'moving': 2})

        changed = _PathValue(root, {'moving'})
        self.assertFalse(changed.bind_from({'moving': 0}, saved)[0])
        with self.assertRaisesRegex(ValueError,
                                    "Unresolved motion input 'rest'"):
            changed.bind({'moving': 0})
        self.assertIsNone(changed.standing_snapshot({'rest': 2,
                                                     'moving': 2}))

        failing_hit = _PathValue(root, {'moving'})
        with self.assertRaises(ZeroDivisionError):
            failing_hit.bind_from({'rest': 2, 'moving': 0}, saved)
        self.assertIsNone(failing_hit.standing_snapshot({'rest': 2,
                                                         'moving': 0}))
        recovered = _PathValue(root, {'moving'})
        self.assertEqual(recovered.bind_from({'rest': 2, 'moving': 4},
                                             saved), (True, 2.25))

        earlier = ExpressionNode('binop', '/', (num(1), name('rest')))
        later = ExpressionNode('call', 'sqrt', (name('moving'),))
        ordered = ExpressionNode('binop', '+', (earlier, later))
        good = _PathValue(ordered, {'moving'})
        good.bind({'rest': 1, 'moving': 1})
        old = good.standing_snapshot({'rest': 1, 'moving': 1})
        both_bad = _PathValue(ordered, {'moving'})
        self.assertFalse(both_bad.bind_from({'rest': 0, 'moving': -1},
                                             old)[0])
        with self.assertRaises(ZeroDivisionError):
            both_bad.bind({'rest': 0, 'moving': -1})

    def test_run_owns_one_entry_and_clears_it_on_restore_and_reset(self):
        sim = Sim(RunningStandingBound(), dt=.1)
        self.assertEqual(len(sim._run._constraint_bind_cache), 0)
        sim.run(.1)
        self.assertEqual(len(sim._run._constraint_bind_cache), 0)
        initial = sim.snapshot()
        sim.move('crank', by=2, duration=.2)
        sim.run(.1)
        self.assertEqual(len(sim._run._constraint_bind_cache), 1)
        first = next(iter(sim._run._constraint_bind_cache.values()))
        root = first.root
        original = _PathValue.bind

        def no_full_rebind(path, values):
            if path.root is root:
                raise AssertionError('standing bound was fully rebound')
            return original(path, values)

        with patch.object(_PathValue, 'bind', no_full_rebind):
            sim.run(.1)
        self.assertEqual(len(sim._run._constraint_bind_cache), 1)
        self.assertIsNot(first, next(iter(sim._run._constraint_bind_cache.values())))
        self.assertEqual(sim.state['wheel.turn'], 2.0)
        sim.restore(initial)
        self.assertEqual(len(sim._run._constraint_bind_cache), 0)
        sim.reset()
        self.assertEqual(len(sim._run._constraint_bind_cache), 0)
        another = Sim(RunningStandingBound(), dt=.1)
        self.assertEqual(len(another._run._constraint_bind_cache), 0)


def standing_name(root):
    return root.children[0]
