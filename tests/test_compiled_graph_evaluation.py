"""An expression value reuses structure, never earlier numeric results."""

import gc
import struct
import weakref
from unittest import TestCase
from unittest.mock import patch

from machinome import math as motion_math
from machinome.expression_graph import ExpressionNode
from machinome.scad_expression import GraphValue
from machinome.simulation.program import _PathValue


def name(text):
    return ExpressionNode('name', text=text)


def extrema(op):
    return ExpressionNode('call', op, (name('x'), name('y')))


class CompiledGraphEvaluationTest(TestCase):
    def test_repeated_evaluation_uses_positional_structure_not_node_keys(self):
        shared = extrema('max')
        root = ExpressionNode('binop', '+', (shared, shared))
        value = GraphValue(root)
        self.assertEqual(value.evaluate({'x': 2, 'y': 3}), 6)
        with patch.object(ExpressionNode, '__hash__',
                          side_effect=AssertionError('node hashed again')):
            self.assertEqual(value.evaluate({'x': 5, 'y': 4}), 10)

    def test_numeric_extrema_keep_operand_bits_without_face_dispatch(self):
        for op in ('min', 'max'):
            value = GraphValue(extrema(op))
            for x, y in ((-0.0, 0.0), (0.0, -0.0),
                         (float('nan'), 1.0), (1.0, float('nan'))):
                expected = getattr(motion_math, op)(float(x), float(y))
                with patch.object(motion_math, '_face', wraps=motion_math._face) as face:
                    actual = value.evaluate({'x': x, 'y': y})
                self.assertEqual(struct.pack('!d', actual),
                                 struct.pack('!d', expected))
                self.assertEqual(face.call_count, 0)

    def test_earlier_error_precedes_later_unknown_operation_after_compilation(self):
        invalid = ExpressionNode('call', 'not_a_builtin',
                                 (ExpressionNode('num', text='1'),))
        root = ExpressionNode('binop', '+', (name('first'), invalid))
        value = GraphValue(root)
        for _ in range(2):
            with self.assertRaisesRegex(ValueError, "Unresolved motion input 'first'"):
                value.evaluate({})
        with self.assertRaisesRegex(ValueError, 'Cannot numerically resolve'):
            value.evaluate({'first': 2})

        division = ExpressionNode('binop', '/', (
            ExpressionNode('num', text='1'),
            ExpressionNode('num', text='0')))
        arithmetic_first = GraphValue(ExpressionNode('binop', '+',
                                                     (division, invalid)))
        for _ in range(2):
            with self.assertRaises(ZeroDivisionError):
                arithmetic_first.evaluate({})

    def test_numeric_extrema_invalid_arity_keeps_public_error(self):
        for op in ('min', 'max'):
            for count in (0, 1, 3):
                args = [float(index) for index in range(count)]
                with self.assertRaises(TypeError) as expected:
                    getattr(motion_math, op)(*args)
                root = ExpressionNode('call', op, tuple(
                    ExpressionNode('num', text=str(value)) for value in args))
                for evaluator in (GraphValue(root), _PathValue(root, set())):
                    with self.assertRaises(TypeError) as actual:
                        if isinstance(evaluator, GraphValue):
                            evaluator.evaluate({})
                        else:
                            evaluator.bind({})
                    self.assertEqual(str(actual.exception),
                                     str(expected.exception))

    def test_discarded_compiled_value_releases_graph(self):
        root = extrema('min')
        reference = weakref.ref(root)
        value = GraphValue(root)
        value.evaluate({'x': 1, 'y': 2})
        del value, root
        gc.collect()
        self.assertIsNone(reference())
