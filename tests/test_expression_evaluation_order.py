"""Repeated numeric evaluation of one immutable expression graph."""

import gc
import weakref
from unittest import TestCase
from unittest.mock import patch

from machinome.expression_graph import ExpressionNode, postorder
from machinome.scad_expression import GraphValue


class ExpressionEvaluationOrderTest(TestCase):
    def test_repeated_evaluation_reuses_order_but_not_numeric_values(self):
        x = ExpressionNode('name', text='x')
        shared = ExpressionNode('binop', '+', (x, x))
        graph = GraphValue(ExpressionNode('binop', '*', (shared, shared)))
        traversals = []

        def counted(roots):
            traversals.append(1)
            yield from postorder(roots)

        with patch('machinome.expression_graph.postorder', counted):
            self.assertEqual(graph.evaluate({'x': 2}), 16)
            self.assertEqual(graph.evaluate({'x': 3}), 36)
            with self.assertRaisesRegex(ValueError, 'Unresolved motion input'):
                graph.evaluate({})

        self.assertEqual(len(traversals), 1)

    def test_operator_order_degree_math_and_release(self):
        x = ExpressionNode('name', text='x')
        large = ExpressionNode('num', text='1e16')
        negative = ExpressionNode('num', text='-1e16')
        add = ExpressionNode('binop', '+', (large, negative))
        ordered = GraphValue(ExpressionNode('binop', '+', (add, x)))
        self.assertEqual(ordered.evaluate({'x': 1}), 1)
        self.assertEqual(ordered.evaluate({'x': 2}), 2)
        sine = GraphValue(ExpressionNode('call', 'sin', (x,)))
        self.assertAlmostEqual(sine.evaluate({'x': 30}), .5)

        def evaluated_reference():
            node = ExpressionNode('name', text='transient')
            graph = GraphValue(node)
            graph.evaluate({'transient': 4})
            return weakref.ref(graph), weakref.ref(node)

        value_ref, node_ref = evaluated_reference()
        gc.collect()
        self.assertIsNone(value_ref())
        self.assertIsNone(node_ref())
