"""Full-graph scalar dispatch keeps author-visible arithmetic and errors."""

import ast
import inspect
import math
import operator
import struct
import textwrap
from unittest import TestCase
from unittest.mock import patch

from machinome import math as degree_math
from machinome.expression_graph import ExpressionNode
from machinome.scad_expression import GraphValue


def num(value):
    return ExpressionNode('num', text=str(value))


def name(value):
    return ExpressionNode('name', text=value)


def binary(op, left, right):
    return GraphValue(ExpressionNode('binop', op, (left, right)))


class GraphValueScalarDispatchTest(TestCase):
    def test_scalar_leaves_and_binary_node_do_not_run_child_list_comprehension(self):
        value = binary('+', num(2), name('x'))
        self.assertEqual(value.evaluate({'x': 3}), 5)
        self.assertEqual(value.evaluate({'x': 4}), 6)
        source = textwrap.dedent(inspect.getsource(GraphValue.evaluate))
        syntax = ast.parse(source)
        loop = next(node for node in ast.walk(syntax) if isinstance(node, ast.For)
                    and isinstance(node.target, ast.Tuple)
                    and ast.unparse(node.target).replace(' ', '')
                    == '(index,(node,children))')
        before_dispatch = []
        for statement in loop.body:
            if isinstance(statement, ast.If):
                break
            before_dispatch.append(statement)
        self.assertFalse(any(isinstance(node, ast.ListComp)
                             for statement in before_dispatch
                             for node in ast.walk(statement)))
        binop_arm = next(node for node in ast.walk(loop) if isinstance(node, ast.If)
                         and ast.unparse(node.test) == "node.kind == 'binop'")
        valid_binary_arm = binop_arm.body[0]
        self.assertIsInstance(valid_binary_arm, ast.If)
        self.assertEqual(ast.unparse(valid_binary_arm.test), 'len(children) == 2')
        self.assertFalse(any(isinstance(node, ast.ListComp)
                             for statement in valid_binary_arm.body
                             for node in ast.walk(statement)))

    def test_binary_signed_zero_and_nonfinite_results_keep_python_bits(self):
        for op, left, right in (('+', -0.0, -0.0),
                                ('-', 0.0, 0.0),
                                ('%', -0.0, 3.0),
                                ('*', float('inf'), -2.0),
                                ('+', float('nan'), 1.0)):
            value = binary(op, name('left'), name('right'))
            expected = {'+': operator.add, '-': operator.sub,
                        '%': math.fmod, '*': operator.mul}[op](left, right)
            for _ in range(2):
                actual = value.evaluate({'left': left, 'right': right})
                self.assertEqual(struct.pack('!d', actual),
                                 struct.pack('!d', expected))

    def test_custom_binary_operands_keep_left_then_right_order(self):
        calls = []

        class Operand:
            def __init__(self, label):
                self.label = label

            def __add__(self, other):
                calls.append((self.label, other.label))
                return 11

        left = ExpressionNode('profile', value=Operand('left'))
        right = ExpressionNode('profile', value=Operand('right'))
        value = binary('+', left, right)
        self.assertEqual(value.evaluate({}), 11)
        self.assertEqual(value.evaluate({}), 11)
        self.assertEqual(calls, [('left', 'right'), ('left', 'right')])

    def test_live_operator_lookup_and_custom_mapping_keep_order(self):
        value = binary('+', name('left'), name('right'))
        self.assertEqual(value.evaluate({'left': 1, 'right': 2}), 3)
        with patch.object(operator, 'add', side_effect=lambda left, right: left - right):
            self.assertEqual(value.evaluate({'left': 5, 'right': 2}), 3)
        self.assertEqual(value.evaluate({'left': 5, 'right': 2}), 7)

        events = []

        class LoggedInputs(dict):
            def __contains__(self, key):
                events.append(('contains', key))
                return super().__contains__(key)

            def __getitem__(self, key):
                events.append(('getitem', key))
                return super().__getitem__(key)

        self.assertEqual(value.evaluate(LoggedInputs(left=2, right=4)), 6)
        self.assertEqual(events, [('contains', 'left'), ('getitem', 'left'),
                                  ('contains', 'right'), ('getitem', 'right')])

        class BadScalar:
            def __float__(self):
                events.append(('convert', 'left'))
                raise TypeError('left conversion failed')

        events.clear()
        with self.assertRaisesRegex(TypeError, 'left conversion failed'):
            value.evaluate(LoggedInputs(left=BadScalar(), right=4))
        self.assertEqual(events, [('contains', 'left'), ('getitem', 'left'),
                                  ('convert', 'left')])

    def test_malformed_arity_and_competing_errors_keep_first_failure(self):
        for count, message in ((0, 'add expected 2 arguments, got 0'),
                               (1, 'add expected 2 arguments, got 1'),
                               (3, 'add expected 2 arguments, got 3')):
            root = ExpressionNode('binop', '+', tuple(num(i) for i in range(count)))
            value = GraphValue(root)
            for _ in range(2):
                with self.assertRaises(TypeError) as actual:
                    value.evaluate({})
                self.assertEqual(str(actual.exception), message)

        empty_unary = GraphValue(ExpressionNode('unary', '-', ()))
        for _ in range(2):
            with self.assertRaises(IndexError) as actual:
                empty_unary.evaluate({})
            self.assertEqual(str(actual.exception), 'list index out of range')
        extra_unary = GraphValue(ExpressionNode('unary', '-', (num(2), num(3))))
        self.assertEqual(extra_unary.evaluate({}), -2)

        invalid_min = GraphValue(ExpressionNode('call', 'min',
                                                (num(1), num(2), num(3))))
        with self.assertRaises(TypeError) as expected:
            degree_math.min(1.0, 2.0, 3.0)
        with self.assertRaises(TypeError) as actual:
            invalid_min.evaluate({})
        self.assertEqual(str(actual.exception), str(expected.exception))

        left = ExpressionNode('binop', '/', (num(1), name('divisor')))
        root = ExpressionNode('binop', '+', (left, name('later')))
        value = GraphValue(root)
        with self.assertRaises(ZeroDivisionError):
            value.evaluate({'divisor': 0})
        with self.assertRaisesRegex(ValueError, "Unresolved motion input 'later'"):
            value.evaluate({'divisor': 1})
        self.assertEqual(value.evaluate({'divisor': 1, 'later': 2}), 3)

        unknown = ExpressionNode('call', 'unknown', (num(1),))
        before_unknown = GraphValue(ExpressionNode('binop', '+', (name('first'), unknown)))
        with self.assertRaisesRegex(ValueError, "Unresolved motion input 'first'"):
            before_unknown.evaluate({})
        with self.assertRaisesRegex(ValueError, 'Cannot numerically resolve'):
            before_unknown.evaluate({'first': 1})
