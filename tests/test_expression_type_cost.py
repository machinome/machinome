# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The symbolic path costs no more than it did in 0.7.1 (OpenSpec change
`expression-type`, design.md Decision 6, "Cost").

A count, not a time, so it is deterministic on any machine: the Python
calls one operation makes (`call` and `c_call` profile events), measured
after a warm-up. The ceilings are the counts recorded on the unmodified tree
(`openspec/changes/archive/<date>-expression-type/evidence.md`, 1.3); an
operation over a SolidPython constant may cost up to 10 % more, for the
seam's cached lookup, measured on a constant the framework has never read
(the engine keeps the node it reads on the constant it read it from).
"""

import sys
from unittest import TestCase

from solid2.core.object_base import scad_inline

import machinome.math as m

from tests.expression_type_project.machine import SharedMotion

#: operation: its call count at 0.7.1 (edff84e).
NATIVE = {
    't+1': (lambda t: t + 1, 11), '1+t': (lambda t: 1 + t, 11),
    't*t': (lambda t: t * t, 8), 't-t': (lambda t: t - t, 8),
    't/2': (lambda t: t / 2, 11), 't%2': (lambda t: t % 2, 11),
    't**2': (lambda t: t ** 2, 11), '-t': (lambda t: -t, 6),
    'abs(t)': (lambda t: abs(t), 11), 't<1': (lambda t: t < 1, 11),
    'sin(t)': (lambda t: m.sin(t), 18),
    'atan2(t,1)': (lambda t: m.atan2(t, 1), 28),
    'min(t,1)': (lambda t: m.min(t, 1), 28),
    'clamp01(t)': (lambda t: m.clamp01(t), 56),
}

#: The same, with a SolidPython constant `L` beside `t`.
SOLIDPYTHON = {
    't+L': (lambda t, L: t + L, 125), 'L+t': (lambda t, L: L + t, 125),
    'sin(L)': (lambda t, L: m.sin(L), 135),
}


def calls(operation, *operands, fresh=None):
    """The calls `operation(*operands)` makes, itself included, after two
    warm-up calls. `fresh`, when given, makes the last operand anew for
    every call, so the measured one meets a value never read before."""
    def operands_now():
        return (*operands, fresh()) if fresh else operands

    operation(*operands_now())
    operation(*operands_now())
    measured = operands_now()
    count = [0]

    def profile(frame, event, arg):
        if event in ('call', 'c_call'):
            count[0] += 1

    sys.setprofile(profile)
    try:
        operation(*measured)
    finally:
        sys.setprofile(None)
    return count[0]


class CallCountTest(TestCase):

    def setUp(self):
        self.t = SharedMotion().time

    def test_native_operations_cost_no_more_than_in_0_7_1(self):
        for name, (operation, ceiling) in NATIVE.items():
            with self.subTest(name):
                self.assertLessEqual(calls(operation, self.t),
                                     ceiling)

    def test_solidpython_operands_cost_at_most_ten_percent_more(self):
        for name, (operation, ceiling) in SOLIDPYTHON.items():
            with self.subTest(name):
                self.assertLessEqual(
                    calls(operation, self.t,
                          fresh=lambda: scad_inline('($t * 2)')),
                    ceiling * 1.1)
