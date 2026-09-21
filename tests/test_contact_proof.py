# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from machinome.math import min, max, abs, sin
from machinome.scad_expression import symbol, as_node
from machinome.simulation.contact_proof import constant_contact


class ContactProofTest(TestCase):
    def proves(self, skeleton, level, start=0, delta=1):
        return constant_contact(as_node(skeleton), as_node(level),
                                {'x': start, 'q': -3.2}, {'x': delta},
                                'q', -3.2, 1)

    def test_constant_offset_does_not_change_relative_motion(self):
        x, q = symbol('x'), symbol('q')
        self.assertTrue(self.proves(32+1+x/7, q+4.2-(1+x/7)))

    def test_no_positive_or_negative_nonzero_slope_is_treated_as_zero(self):
        x, q = symbol('x'), symbol('q')
        for tiny in (1e-30, -1e-30, 5e-324, -5e-324):
            with self.subTest(tiny=tiny):
                self.assertFalse(self.proves(x+tiny*x, q-x))

    def test_selection_must_hold_throughout_the_interval(self):
        x, q = symbol('x'), symbol('q')
        self.assertTrue(self.proves(max(x, -1), q-x))
        self.assertTrue(self.proves(min(x, 2), q-x))
        self.assertTrue(self.proves(abs(x), q-x))
        self.assertFalse(self.proves(max(x, .5), q-x))
        self.assertFalse(self.proves(abs(x), q-x, start=-.5))
        self.assertTrue(self.proves(max(x, .5), q-max(x, .5)))
        self.assertTrue(self.proves(abs(x)+min(x, .3),
                                   q-abs(x)-min(x, .3), start=-.5))

    def test_exhausted_work_and_nonfinite_inputs_cannot_furnish_a_proof(self):
        x, q = symbol('x'), symbol('q')
        self.assertFalse(constant_contact(as_node(max(x, .5)),
            as_node(q-max(x, .5)), {'x': 0, 'q': 0}, {'x': 1},
            'q', 0, 1, max_pieces=1))
        self.assertFalse(self.proves(x, q-x, start=float('inf')))

    def test_unsupported_curves_and_moving_divisor_are_not_certified(self):
        x, q = symbol('x'), symbol('q')
        self.assertFalse(self.proves(sin(x), q-sin(x)))
        self.assertFalse(self.proves(1/(x+1), q-1/(x+1)))
        self.assertFalse(self.proves(x*x, q-x*x))
