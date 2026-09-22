"""A bound path reuses structure, never an earlier piece's numbers."""

import gc
import struct
import weakref
from unittest import TestCase
from unittest.mock import patch

from machinome.expression_graph import ExpressionNode
from machinome.scad_expression import GraphValue
from machinome.simulation.program import _PathValue


def name(text):
    return ExpressionNode('name', text=text)


class CompiledPathEvaluationTest(TestCase):
    def test_later_samples_reuse_operation_classification(self):
        x = name('x')
        y = name('y')
        difference = ExpressionNode('binop', '-', (x, y))
        minimum = ExpressionNode('call', 'min', (difference, y))
        root = ExpressionNode('binop', '+', (minimum, x))
        path = _PathValue(root, {'x'})
        self.assertEqual(path.bind({'x': 5, 'y': 2}), 7)

        original = ExpressionNode.__getattribute__

        def no_rediscovery(node, attribute):
            if attribute in ('kind', 'op'):
                raise AssertionError('path rediscovered immutable operation')
            return original(node, attribute)

        with patch.object(ExpressionNode, '__getattribute__', no_rediscovery):
            self.assertEqual(path.at({'x': 8, 'y': 2}), 10)
            self.assertEqual(path.at({'x': 1, 'y': 2}), 0)

    def test_later_samples_use_positional_structure_without_node_hashes(self):
        shared = ExpressionNode('binop', '*', (name('x'), name('x')))
        root = ExpressionNode('binop', '+', (shared, name('y')))
        path = _PathValue(root, {'x'})
        self.assertEqual(path.bind({'x': 2, 'y': 3}), 7)
        with patch.object(ExpressionNode, '__hash__',
                          side_effect=AssertionError('node hashed again')):
            self.assertEqual(path.at({'x': 4, 'y': 3}), 19)
            self.assertEqual(path.at({'x': 5, 'y': 3}), 28)

    def test_rebind_refreshes_standing_values_and_failed_rebind_is_atomic(self):
        root = ExpressionNode('binop', '+', (name('x'), name('y')))
        path = _PathValue(root, {'x'})
        self.assertEqual(path.bind({'x': 1, 'y': 2}), 3)
        self.assertEqual(path.at({'x': 3, 'y': 2}), 5)
        self.assertEqual(path.bind({'x': 4, 'y': 8}), 12)
        self.assertEqual(path.at({'x': 6, 'y': 8}), 14)
        with self.assertRaisesRegex(ValueError, "Unresolved motion input 'y'"):
            path.bind({'x': 10})
        self.assertEqual(path.at({'x': 7, 'y': 8}), 15)

    def test_extrema_keep_operand_bits_and_rebind_current_standing_operand(self):
        for op in ('min', 'max'):
            root = ExpressionNode('call', op, (name('x'), name('y')))
            path = _PathValue(root, {'x'})
            whole = GraphValue(root)
            for x, y in ((-0.0, 0.0), (0.0, -0.0),
                         (float('nan'), 1.0), (1.0, float('nan'))):
                path.bind({'x': x, 'y': y})
                with self.subTest(op=op, x=x, y=y):
                    self.assertEqual(struct.pack('!d', path.at({'x': x, 'y': y})),
                                     struct.pack('!d', whole.evaluate({'x': x, 'y': y})))

    def test_later_sample_keeps_earlier_arithmetic_error_precedence(self):
        division = ExpressionNode('binop', '/', (name('x'), name('y')))
        invalid = ExpressionNode('call', 'not_a_builtin',
                                 (ExpressionNode('num', text='1'),))
        root = ExpressionNode('binop', '+', (division, invalid))
        path = _PathValue(root, {'x'})
        with self.assertRaisesRegex(ValueError, 'Cannot numerically resolve'):
            path.bind({'x': 1, 'y': 1})
        # The first bind's eager unsupported call still prevents a path
        # program from being published; a later bind must fail in the same
        # earlier arithmetic node first.
        with self.assertRaises(ZeroDivisionError):
            path.bind({'x': 1, 'y': 0})

    def test_at_time_missing_input_keeps_earlier_arithmetic_error(self):
        division = ExpressionNode('binop', '/', (
            ExpressionNode('num', text='1'), name('x')))
        root = ExpressionNode('binop', '+', (division, name('later')))
        path = _PathValue(root, {'x', 'later'})
        self.assertEqual(path.bind({'x': 2, 'later': 3}), 3.5)
        with self.assertRaises(ZeroDivisionError):
            path.at({'x': 0})
        with self.assertRaisesRegex(ValueError, "Unresolved motion input 'later'"):
            path.at({'x': 2})

    def test_operation_program_does_not_retain_released_graph(self):
        def sampled_graph():
            x = name('x')
            root = ExpressionNode('call', 'max', (
                ExpressionNode('binop', '+', (x, name('y'))), x))
            reference = weakref.ref(root)
            path = _PathValue(root, {'x'})
            path.bind({'x': 1, 'y': 2})
            path.at({'x': 3, 'y': 2})
            return reference

        reference = sampled_graph()
        gc.collect()
        self.assertIsNone(reference())
