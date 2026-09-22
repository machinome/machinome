"""Numeric extrema on a motion path keep graph operand semantics."""

import struct
from unittest import TestCase
from unittest.mock import patch

from machinome import math as motion_math
from machinome.expression_graph import ExpressionNode
from machinome.scad_expression import GraphValue
from machinome.simulation.program import _PathValue


def extremum(name):
    return ExpressionNode('call', name, (
        ExpressionNode('name', text='x'),
        ExpressionNode('name', text='y'),
    ))


class NumericPathCallsTest(TestCase):
    def test_numeric_extrema_keep_graph_bits_without_generic_face_dispatch(self):
        for name in ('min', 'max'):
            root = extremum(name)
            graph = GraphValue(root)
            path = _PathValue(root, {'x'})
            for x, y in ((-0.0, 0.0), (0.0, -0.0),
                         (float('nan'), 1.0), (1.0, float('nan')),
                         (2.0, -3.0)):
                values = {'x': x, 'y': y}
                expected = graph.evaluate(values)
                with patch.object(motion_math, '_face', wraps=motion_math._face) as face:
                    actual = path.bind(values)
                self.assertEqual(struct.pack('!d', actual),
                                 struct.pack('!d', expected))
                self.assertEqual(face.call_count, 0)

            with self.assertRaisesRegex(ValueError, 'Unresolved motion input'):
                path.bind({'x': 1.0})
            self.assertEqual(path.bind({'x': 2.0, 'y': 3.0}),
                             graph.evaluate({'x': 2.0, 'y': 3.0}))
