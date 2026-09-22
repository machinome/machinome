"""A determined running constraint follows its actual path, sample for sample."""

import math
import struct
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from machinome.expression_graph import ExpressionNode
from machinome.scad_expression import GraphValue
from machinome.simulation.program import _PathValue, _SUBDIVISIONS
from machinome.simulation.run import Run
from machinome.simulation.trajectory import Motion, Propagation


def name(text):
    return ExpressionNode('name', text=text)


def bits(value):
    return struct.pack('!d', float(value))


def search(graph, x_motion, y_motion, *, x_delta=1, y_delta=0,
           determined=True, replay=None):
    keys = {'own': 0, 'x': 1, 'y': 2}
    calls = []
    fake = SimpleNamespace(
        bank={'own': 0.0}, keys=keys,
        program=SimpleNamespace(determiner={1: object()} if not determined else {}),
        _constraint_level=lambda _constraint, _held, _values, _admissions,
                                 t, _own: calls.append(t) or -1.0)
    constraint = SimpleNamespace(identifier='own', reads=('x', 'y'),
                                 graph=GraphValue(graph), side='high')
    values = {0: 0.0, 1: x_motion.start, 2: y_motion.start}
    deltas = Propagation({0: 0.0, 1: x_delta, 2: y_delta})
    if determined:
        deltas.motions.update({1: x_motion, 2: y_motion})
    elif replay is not None:
        deltas.motions[2] = y_motion
    contact = Run._searched_constraint(fake, constraint,
                                       {'own': 0.0, 'x': x_motion.start,
                                        'y': y_motion.start},
                                       values, {'driver': x_delta}, deltas)
    return contact, calls


class TracedConstraintPathTest(TestCase):
    def test_traced_samples_reuse_one_search_local_path_and_refresh_standing(self):
        graph = ExpressionNode('binop', '+', (name('x'), name('y')))
        seen = []
        original = _PathValue.at

        def counted(path, inputs):
            seen.append((path, inputs['x'], inputs['y']))
            return original(path, inputs)

        with patch.object(_PathValue, 'at', counted):
            first, _ = search(graph, Motion.line(0.0, 1.0),
                              Motion.line(2.0, 0.0))
            second, _ = search(graph, Motion.line(0.0, 1.0),
                               Motion.line(5.0, 0.0))
        self.assertIsNone(first)
        self.assertIsNone(second)
        self.assertEqual(len(seen), 2 * _SUBDIVISIONS)
        self.assertEqual([entry[2] for entry in seen[:_SUBDIVISIONS]],
                         [2.0] * _SUBDIVISIONS)
        self.assertEqual([entry[2] for entry in seen[_SUBDIVISIONS:]],
                         [5.0] * _SUBDIVISIONS)
        self.assertIsNot(seen[0][0], seen[-1][0])

    def test_first_sample_still_eagerly_reports_an_arithmetic_error(self):
        invalid = ExpressionNode('binop', '/', (
            ExpressionNode('num', text='1'),
            ExpressionNode('num', text='0')))
        graph = ExpressionNode('binop', '+', (name('x'), invalid))
        with self.assertRaises(ZeroDivisionError):
            search(graph, Motion.line(0.0, 1.0), Motion.line(2.0, 0.0))

    def test_signed_zero_and_nan_reads_are_not_frozen_by_numeric_equality(self):
        graph = ExpressionNode('call', 'min', (name('x'), name('y')))
        zero_motion = Motion(-0.0, 0.0,
                             [(0.0, 1.0, lambda _t: -0.0)])
        self.assertTrue(zero_motion.constant)  # numeric equality misses sign
        seen = []
        original = _PathValue.at

        def checked(path, inputs):
            actual = original(path, inputs)
            expected = GraphValue(graph).evaluate(inputs)
            seen.append((bits(inputs['x']), bits(actual), bits(expected)))
            return actual

        with patch.object(_PathValue, 'at', checked):
            search(graph, zero_motion, Motion.line(0.0, 0.0), x_delta=0)
        self.assertEqual(len(seen), _SUBDIVISIONS)
        self.assertEqual(seen[-1][0], bits(0.0))
        self.assertTrue(all(actual == expected for _, actual, expected in seen))
        self.assertEqual(seen[-1][1], bits(0.0))

        nan = float('nan')
        nan_motion = Motion(nan, nan, [(0.0, 1.0, lambda _t: nan)])
        self.assertFalse(nan_motion.constant)
        seen.clear()
        with patch.object(_PathValue, 'at', checked):
            search(graph, nan_motion, Motion.line(0.0, 0.0), x_delta=0)
        self.assertEqual(len(seen), _SUBDIVISIONS)
        self.assertTrue(math.isnan(struct.unpack('!d', seen[-1][1])[0]))

    def test_undetermined_read_keeps_prefix_replay_at_every_sample(self):
        graph = ExpressionNode('binop', '+', (name('x'), name('y')))
        with patch.object(_PathValue, 'bind',
                          side_effect=AssertionError('must replay')):
            contact, fractions = search(
                graph, Motion.line(0.0, 1.0), Motion.line(2.0, 0.0),
                determined=False)
        self.assertIsNone(contact)
        self.assertEqual(fractions,
                         [0.0] + [step / _SUBDIVISIONS
                                  for step in range(1, _SUBDIVISIONS + 1)])
