"""One path may reuse only its own immediately preceding proven bind."""

import math
import struct
from unittest import TestCase
from unittest.mock import patch

from machinome.expression_graph import ExpressionNode
from machinome.simulation.program import _PathValue


def name(text):
    return ExpressionNode('name', text=text)


def num(value):
    return ExpressionNode('num', text=str(value))


def bits(value):
    return struct.pack('!d', float(value))


class IdenticalPathBindTest(TestCase):
    def test_same_finite_inputs_skip_the_walk_but_later_at_remains_live(self):
        root = ExpressionNode('binop', '+', (name('moving'), name('still')))
        path = _PathValue(root, {'moving'})
        self.assertEqual(path.bind({'moving': 2, 'still': 3}), 5)
        self.assertEqual(path.at({'moving': 9}), 12)
        with patch('machinome.simulation.program._path_node_value',
                   side_effect=AssertionError('identical bind walked again')):
            self.assertEqual(path.bind({'moving': 2.0, 'still': 3.0,
                                        'irrelevant': 99}), 5)
        self.assertEqual(path.at({'moving': 10}), 13)
        self.assertEqual(len(path._last_bind), 5)

        fresh = _PathValue(root, {'moving'})
        with patch('machinome.simulation.program._path_node_value',
                   side_effect=AssertionError('new path was not bound')):
            with self.assertRaisesRegex(AssertionError, 'new path'):
                fresh.bind({'moving': 2, 'still': 3})

    def test_changed_bits_and_uncertain_values_take_the_eager_walk(self):
        root = name('x')
        path = _PathValue(root, {'x'})
        self.assertEqual(bits(path.bind({'x': 0.0})), bits(0.0))
        self.assertEqual(bits(path.bind({'x': -0.0})), bits(-0.0))
        self.assertEqual(bits(path.bind({'x': 1.0})), bits(1.0))
        with self.assertRaisesRegex(ValueError, "Unresolved motion input 'x'"):
            path.bind({})

        class Converting:
            calls = 0

            def __float__(self):
                self.calls += 1
                return 1.0

        custom = Converting()
        self.assertEqual(path.bind({'x': custom}), 1.0)
        self.assertEqual(custom.calls, 1)
        self.assertEqual(path.bind({'x': custom}), 1.0)
        self.assertEqual(custom.calls, 2)

        for value in (float('nan'), float('inf'), -float('inf')):
            with self.subTest(value=value):
                first = path.bind({'x': value})
                second = path.bind({'x': value})
                self.assertEqual(math.isnan(first), math.isnan(second))
                with patch('machinome.simulation.program._path_node_value',
                           side_effect=AssertionError('nonfinite rebound')):
                    with self.assertRaisesRegex(AssertionError, 'nonfinite'):
                        path.bind({'x': value})

        class ObservedDict(dict):
            reads = 0

            def __getitem__(self, key):
                self.reads += 1
                return super().__getitem__(key)

        observed = ObservedDict(x=1.0)
        path.bind(observed)
        path.bind(observed)
        self.assertEqual(observed.reads, 2)

    def test_failed_rebind_preserves_previous_success_and_first_error(self):
        early = ExpressionNode('binop', '/', (num(1), name('standing')))
        late = ExpressionNode('call', 'sqrt', (name('moving'),))
        root = ExpressionNode('binop', '+', (early, late))
        path = _PathValue(root, {'moving'})
        self.assertEqual(path.bind({'standing': 1, 'moving': 1}), 2)
        with self.assertRaises(ZeroDivisionError):
            path.bind({'standing': 0, 'moving': -1})
        with patch('machinome.simulation.program._path_node_value',
                   side_effect=AssertionError('earlier success was lost')):
            self.assertEqual(path.bind({'standing': 1, 'moving': 1}), 2)
        with self.assertRaisesRegex(ValueError,
                                    "Unresolved motion input 'standing'"):
            path.bind({'moving': -1})
        self.assertEqual(path.at({'moving': 4}), 3)

    def test_successful_bind_from_invalidates_an_older_local_result(self):
        root = ExpressionNode('binop', '+', (name('moving'), name('still')))
        path = _PathValue(root, {'moving'})
        self.assertEqual(path.bind({'moving': 1, 'still': 2}), 3)
        donor = _PathValue(root, {'moving'})
        self.assertEqual(donor.bind({'moving': 5, 'still': 7}), 12)
        snapshot = donor.standing_snapshot({'moving': 5, 'still': 7})
        self.assertEqual(path.bind_from({'moving': 8, 'still': 7}, snapshot),
                         (True, 15))
        self.assertEqual(path.bind({'moving': 1, 'still': 2}), 3)
        self.assertEqual(path.at({'moving': 9}), 11)
