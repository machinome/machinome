"""A finite contact profile is authored data, not a pairwise graph."""

import math
import json
import struct
import unittest
from pathlib import Path

from machinome.simulation.profile import ConvexProfile, profile_overlap
from machinome.scad_expression import GraphValue, symbol
from machinome.expression_graph import ExpressionNode
from machinome.simulation.program import (_PathValue, _checked_bound_graph,
                                          checked_expression)


SQUARE = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))


class ConvexProfileContactTest(unittest.TestCase):

    def test_shared_numeric_and_polygon_corpus(self):
        corpus = json.loads((Path(__file__).parent / 'fixtures' /
                             'profile_overlap_numeric_corpus.json').read_text())
        profile = ConvexProfile(corpus['profile'])
        for case in corpus['cases']:
            with self.subTest(case=case['name']):
                call = lambda: profile_overlap(
                    profile, profile, case['left_angle'], case['right_angle'],
                    left_xy=case['left_xy'], right_xy=case['right_xy'])
                if 'error' in case:
                    with self.assertRaisesRegex(ValueError, case['error']):
                        call()
                else:
                    self.assertEqual(struct.pack('!d', call()),
                                     struct.pack('!d', case['result']))
        for case in corpus['invalid_polygons']:
            with self.subTest(case=case['name']):
                with self.assertRaises(ValueError):
                    ConvexProfile((case['points'],))
        self.assertEqual(ConvexProfile((corpus['valid_collinear'],)).polygons[0],
                         tuple(tuple(point) for point in corpus['valid_collinear']))

    def test_public_import_and_docstrings(self):
        self.assertIn('convex', ConvexProfile.__doc__.lower())
        self.assertIn('pointwise', profile_overlap.__doc__.lower())

    def test_numeric_clearance_and_touch(self):
        square = ConvexProfile((SQUARE,))
        self.assertEqual(profile_overlap(square, square, 0.0, 0.0,
                                         right_xy=(2.0, 0.0)), 0.0)
        self.assertEqual(profile_overlap(square, square, 0.0, 0.0,
                                         right_xy=(1.0, 0.0)), 1.0)
        self.assertEqual(profile_overlap(square, square, 0.0, 0.0,
                                         right_xy=(1.0, 1.0)), 1.0)
        one_ulp_out = math.nextafter(1.0, math.inf)
        self.assertEqual(profile_overlap(square, square, 0.0, 0.0,
                                         right_xy=(one_ulp_out, 1.0)), 0.0)

    def test_repeated_vertex_zero_edge_and_crossing_refuse(self):
        pentagram = ((0.0, 3.0), (1.8, -2.4), (-2.9, 0.9),
                     (2.9, 0.9), (-1.8, -2.4))
        for polygon in (SQUARE + (SQUARE[0],),
                        (SQUARE[0], SQUARE[0]) + SQUARE[1:], pentagram):
            with self.subTest(polygon=polygon):
                with self.assertRaises(ValueError):
                    ConvexProfile((polygon,))

    def test_collinear_corner_is_retained(self):
        loop = ((0.0, 0.0), (0.5, 0.0), (1.0, 0.0),
                (1.0, 1.0), (0.0, 1.0))
        self.assertEqual(ConvexProfile((loop,)).polygons[0], loop)

    def test_distant_profile_does_not_hide_collapsed_edge(self):
        square = ConvexProfile((SQUARE,))
        with self.assertRaises(ValueError):
            profile_overlap(square, square, 0.0, 0.0,
                            left_xy=(1e300, 0.0), right_xy=(-1e300, 0.0))

    def test_projection_overflow_refuses(self):
        huge = ConvexProfile((((0.0, 0.0), (1e200, 0.0),
                               (1e200, 1e200), (0.0, 1e200)),))
        with self.assertRaises(ValueError):
            profile_overlap(huge, huge, 0.0, 0.0)

    def test_input_is_immutable_and_empty_refuses(self):
        square = ConvexProfile((SQUARE,))
        with self.assertRaises(AttributeError):
            square.polygons = ()
        with self.assertRaises(AttributeError):
            del square._polygons
        with self.assertRaises(ValueError):
            ConvexProfile(())

    def test_huge_finite_angle_has_no_artificial_cutoff(self):
        square = ConvexProfile((SQUARE,))
        self.assertEqual(profile_overlap(square, square, 1e308, 0.0,
                                         right_xy=(100.0, 0.0)), 0.0)

    def test_unrepresentable_numeric_angle_refuses(self):
        square = ConvexProfile((SQUARE,))
        with self.assertRaises(ValueError):
            profile_overlap(square, square, 10 ** 1000, 0.0)

    def test_positive_zero_and_one(self):
        square = ConvexProfile((SQUARE,))
        for shift, expected in ((2.0, 0.0), (1.0, 1.0)):
            actual = profile_overlap(square, square, -0.0, 0.0,
                                     right_xy=(shift, 0.0))
            self.assertEqual(struct.pack('!d', actual),
                             struct.pack('!d', expected))

    def test_symbolic_contact_is_one_graph_operation(self):
        square = ConvexProfile((SQUARE,))
        contact = profile_overlap(square, square, symbol('turn'), 0.0,
                                  right_xy=(1.0, 0.0))
        self.assertIsInstance(contact, GraphValue)
        self.assertEqual(contact._expression_node.kind, 'call')
        self.assertEqual(contact._expression_node.op, 'profileOverlap')
        self.assertEqual(contact.evaluate({'turn': 0.0}), 1.0)
        self.assertEqual(contact.evaluate({'turn': 180.0}), 0.0)

    def test_path_bind_and_later_sample_use_same_contact(self):
        square = ConvexProfile((SQUARE,))
        graph = profile_overlap(square, square, symbol('turn'), 0.0,
                                right_xy=(1.0, 0.0))
        path = _PathValue(graph, {'turn'})
        self.assertEqual(path.bind({'turn': 0.0}), 1.0)
        self.assertEqual(path.at({'turn': 180.0}), 0.0)
        with self.assertRaisesRegex(ValueError, 'Unresolved motion input'):
            _PathValue(graph, {'turn'}).bind({})

    def test_eager_first_error_order_matches_full_graph_and_path(self):
        square = ConvexProfile((SQUARE,))
        collapsed = profile_overlap(square, square, symbol('turn'), 0.0,
                                    left_xy=(1e300, 0.0),
                                    right_xy=(-1e300, 0.0))
        divisor = symbol('other') - symbol('other')
        divided = symbol('other') / divisor
        for graph, error in ((collapsed + divided, ValueError),
                             (divided + collapsed, ZeroDivisionError)):
            with self.subTest(error=error):
                inputs = {'turn': 0.0, 'other': 1.0}
                with self.assertRaises(error):
                    graph.evaluate(inputs)
                with self.assertRaises(error):
                    _PathValue(graph, {'turn'}).bind(inputs)

    def test_failed_profile_bind_does_not_publish_partial_standing_values(self):
        square = ConvexProfile((SQUARE,))
        graph = profile_overlap(square, square, symbol('turn'), 0.0,
                                left_xy=(symbol('shift'), 0.0),
                                right_xy=(100.0, 0.0))
        path = _PathValue(graph, {'turn'})
        self.assertEqual(path.bind({'turn': 0.0, 'shift': 0.0}), 0.0)
        with self.assertRaisesRegex(ValueError, 'collapsed'):
            path.bind({'turn': 0.0, 'shift': 1e300})
        self.assertEqual(path.at({'turn': 0.0, 'shift': 0.0}), 0.0)
        self.assertEqual(path.bind({'turn': 0.0, 'shift': 0.0}), 0.0)

    def test_shared_profile_leaf_cannot_escape_contact_operands(self):
        square = ConvexProfile((SQUARE,))
        profile = ExpressionNode('profile', value=square)
        zero = ExpressionNode('num', text='0.0')
        contact = ExpressionNode('call', 'profileOverlap',
                                 (profile, profile, zero, zero, zero,
                                  zero, zero, zero))
        escaped = ExpressionNode('binop', '+', (profile, contact))

        def refuse(detail):
            raise ValueError(detail)

        with self.assertRaisesRegex(ValueError, 'outside the first two'):
            _checked_bound_graph(escaped, refuse)

    def test_profile_graph_refuses_symbolic_pose_and_law_contexts(self):
        square = ConvexProfile((SQUARE,))
        graph = profile_overlap(square, square, symbol('turn'), 0.0)
        with self.assertRaisesRegex(ValueError, 'only in a running Bound'):
            str(graph)

        def refuse(detail):
            raise ValueError(detail)

        with self.assertRaisesRegex(ValueError, 'symbolic only inside a running Bound'):
            checked_expression(graph, refuse)


if __name__ == '__main__':
    unittest.main()
