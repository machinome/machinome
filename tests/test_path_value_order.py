"""An expression path rebinds values without revisiting its immutable DAG."""

import gc
import weakref
from unittest import TestCase
from unittest.mock import patch

from machinome.expression_graph import ExpressionNode, postorder
from machinome.simulation.program import _PathValue


def expression():
    moving = ExpressionNode('name', text='x')
    standing = ExpressionNode('name', text='y')
    return ExpressionNode('binop', '+', (moving, standing))


class PathValueOrderTest(TestCase):
    def test_repeated_bind_uses_current_standing_value_and_one_traversal(self):
        path = _PathValue(expression(), {'x'})
        traversals = []

        def counted(roots):
            traversals.append(1)
            yield from postorder(roots)

        with patch('machinome.simulation.program.postorder', counted):
            self.assertEqual(path.bind({'x': 1, 'y': 2}), 3)
            self.assertEqual(path.at({'x': 2, 'y': 2}), 4)
            self.assertEqual(path.bind({'x': 3, 'y': 4}), 7)
            self.assertEqual(path.at({'x': 4, 'y': 4}), 8)

        self.assertEqual(len(traversals), 1)

    def test_failed_first_bind_retries_and_releases_graph(self):
        root = expression()
        reference = weakref.ref(root)
        path = _PathValue(root, {'x'})
        with self.assertRaisesRegex(ValueError, 'Unresolved motion input'):
            path.bind({'x': 1})
        self.assertEqual(path.bind({'x': 1, 'y': 2}), 3)
        self.assertEqual(path.bind({'x': 2, 'y': 5}), 7)
        del path, root
        gc.collect()
        self.assertIsNone(reference())
