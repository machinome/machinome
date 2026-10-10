# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The three faces of `machinome.math` are one semantics (OpenSpec change
`expression-type`; ADR-022).

For every primitive in `SYMBOLIC_BUILTINS` and every composition and vector
helper of `machinome.math.__all__`, over sample points inside its domain:
the numeric face at `x`, the symbolic face over the core's own animation
time evaluated at `$t = x`, and -- where the function takes a declared
argument -- the declared face on a node constructed with that parameter
bound to `x`, agree: to the bit for the primitives, to 1e-12 for the
compositions. A characterisation, green before and after the symbolic value
became the core's own type.
"""

import math as pymath
from unittest import TestCase

import machinome.math as m
from machinome.node.solid2 import Solid2Node
from machinome.parameters import Angle, Ratio, evaluate

from tests.expression_type_project.machine import SharedMotion

#: The 0.7.1 inventory, verbatim.
BUILTINS_0_7_1 = (
    'sin', 'cos', 'tan',
    'asin', 'acos', 'atan', 'atan2',
    'sqrt',
    'abs', 'floor', 'ceil', 'sign', 'min', 'max',
)

ANGLES = (-170.0, -45.0, 0.0, 30.0, 60.0, 89.0, 135.0, 400.0)
UNIT = (-1.0, -0.5, 0.0, 0.3, 0.5, 1.0)
WAYPOINTS = ((0.0, 0.0), (0.25, 4.0), (0.5, 6.0), (1.0, 1.0))

#: name: (the call with `x` in one argument, the kind `x` is declared as
#: for the declared face, sample points inside the function's domain).
PRIMITIVES = {
    'sin': (lambda x: m.sin(x), Angle, ANGLES),
    'cos': (lambda x: m.cos(x), Angle, ANGLES),
    'tan': (lambda x: m.tan(x), Angle, (-60.0, -45.0, 0.0, 30.0, 89.0)),
    'asin': (lambda x: m.asin(x), Ratio, UNIT),
    'acos': (lambda x: m.acos(x), Ratio, UNIT),
    'atan': (lambda x: m.atan(x), Ratio, (-3.0, -0.5, 0.0, 0.5, 2.0)),
    'atan2': (lambda x: m.atan2(x, 1.5), Ratio, (-2.0, 0.0, 0.5, 3.0)),
    'atan2 x': (lambda x: m.atan2(0.5, x), Ratio, (-2.0, -0.5, 0.0, 2.0)),
    'sqrt': (lambda x: m.sqrt(x), Ratio, (0.0, 0.25, 2.0, 9.0)),
    'abs': (lambda x: m.abs(x), Ratio, (-2.5, 0.0, 3.0)),
    'floor': (lambda x: m.floor(x), Ratio, (-2.5, -1.0, 0.0, 0.3, 2.7)),
    'ceil': (lambda x: m.ceil(x), Ratio, (-2.5, -1.0, 0.0, 0.3, 2.7)),
    'sign': (lambda x: m.sign(x), Ratio, (-2.0, 0.0, 0.5)),
    'min': (lambda x: m.min(x, 0.5), Ratio, (-1.0, 0.5, 2.0)),
    'max': (lambda x: m.max(0.5, x), Ratio, (-1.0, 0.5, 2.0)),
}

COMPOSITIONS = {
    'clamp': (lambda x: m.clamp(x, 0.2, 0.8), Ratio, (-1.0, 0.2, 0.5, 0.9)),
    'clamp01': (lambda x: m.clamp01(x), Ratio, (-0.5, 0.0, 0.4, 1.0, 1.5)),
    'ramp': (lambda x: m.ramp(x, 0.25, 0.75), Ratio,
             (0.0, 0.25, 0.6, 0.75, 1.0)),
    'lerp': (lambda x: m.lerp(2.0, 5.0, x), Ratio, (-0.5, 0.0, 0.3, 1.0, 2.0)),
    'wrap': (lambda x: m.wrap(x, 360.0), Ratio,
             (-400.0, -180.0, 0.0, 179.0, 181.0, 540.0)),
    'piecewise': (lambda x: m.piecewise(x, WAYPOINTS), Ratio,
                  (-0.5, 0.0, 0.1, 0.25, 0.4, 0.75, 1.0, 1.5)),
    'bump': (lambda x: m.bump(x), Ratio, (-0.5, 0.0, 0.25, 0.5, 0.9, 1.2)),
}

#: The vector helpers: a tuple of components, each compared as a
#: composition is.
VECTORS = {
    'polar': (lambda x: m.polar(2.0, x), Angle, ANGLES),
    'turn': (lambda x: m.turn((1.0, 2.0), x), Angle, ANGLES),
    'turn about': (lambda x: m.turn((1.0, 2.0), x, about=(0.5, -0.5)),
                   Angle, ANGLES),
    'rotate_x': (lambda x: m.rotate_x((1.0, 2.0, 3.0), x), Angle, ANGLES),
    'rotate_y': (lambda x: m.rotate_y((1.0, 2.0, 3.0), x), Angle, ANGLES),
    'rotate_z': (lambda x: m.rotate_z((1.0, 2.0, 3.0), x), Angle, ANGLES),
}


class ThreeFacesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.t = SharedMotion().time

    def symbolic(self, function, x):
        return function(self.t).evaluate({'$t': x})

    def declared(self, kind, function, x):
        token = kind(0.0)
        derived = function(token)
        node = type('Declared', (Solid2Node,), {
            'x': token, 'y': derived, '__module__': __name__,
            'render': lambda self: None})
        return node(x=x).y

    def test_the_inventory_is_the_0_7_1_inventory(self):
        self.assertEqual(m.SYMBOLIC_BUILTINS, BUILTINS_0_7_1)
        covered = {name.split()[0] for name in PRIMITIVES}
        self.assertEqual(covered, set(BUILTINS_0_7_1))
        helpers = set(m.__all__) - set(BUILTINS_0_7_1) - {'SYMBOLIC_BUILTINS'}
        self.assertEqual(helpers, set(COMPOSITIONS) | {
            name.split()[0] for name in VECTORS})

    def test_primitives_agree_to_the_bit(self):
        for name, (function, kind, points) in PRIMITIVES.items():
            for x in points:
                with self.subTest(name, x=x):
                    numeric = function(x)
                    self.assertEqual(self.symbolic(function, x), numeric)
                    self.assertEqual(self.declared(kind, function, x),
                                     numeric)

    def test_compositions_agree_to_1e_12(self):
        for name, (function, kind, points) in COMPOSITIONS.items():
            for x in points:
                with self.subTest(name, x=x):
                    numeric = function(x)
                    self.assertAlmostEqual(self.symbolic(function, x),
                                           numeric, delta=1e-12)
                    self.assertAlmostEqual(self.declared(kind, function, x),
                                           numeric, delta=1e-12)

    def test_vector_helpers_agree_to_1e_12(self):
        for name, (function, kind, points) in VECTORS.items():
            for x in points:
                with self.subTest(name, x=x):
                    numeric = function(x)
                    symbolic = function(self.t)
                    token = kind(0.0)
                    token.__set_name__(type('Owner', (), {}), 'x')
                    declared = function(token)
                    self.assertEqual(len(symbolic), len(numeric))
                    for value, read, formula in zip(numeric, symbolic,
                                                    declared):
                        if not isinstance(read, (int, float)):
                            read = read.evaluate({'$t': x})
                        self.assertAlmostEqual(read, value, delta=1e-12)
                        self.assertAlmostEqual(
                            evaluate(formula, {'x': x}), value, delta=1e-12)

    def test_degree_conventions(self):
        self.assertEqual(m.sin(90), 1.0)
        self.assertEqual(m.atan2(1, 0), 90.0)
        # degrees(asin(0.5)) is 30.000000000000004 in IEEE doubles, in the
        # numeric face as in Python's own math: equal to 30 to 1e-12.
        self.assertAlmostEqual(m.asin(0.5), 30.0, delta=1e-12)
        self.assertEqual(m.asin(0.5), pymath.degrees(pymath.asin(0.5)))
