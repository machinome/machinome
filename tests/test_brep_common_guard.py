"""An OCCT empty common may contradict the exact solids' shared interior.

The synthetic false-empty seam makes this regression independent of the
Curta STEP fixture.  The originating source-shape capture lives in the
archived change evidence and is rerun against that project separately.
"""

from unittest import TestCase
from unittest.mock import patch

import cadquery as cq
import numpy as np
from OCP.TopAbs import TopAbs_UNKNOWN

from machinome.engine import (BrepCommonInconsistency,
                                    BrepCommonVerificationError)
from machinome.engine.brep import intersect_shapes
from machinome.test import _brep_verdict


def box(x=0, y=0, z=0):
    return cq.Solid.makeBox(1, 1, 1, cq.Vector(x, y, z))


def empty_common():
    return cq.Compound.makeCompound([]).wrapped


class ExactCommonGuardTest(TestCase):
    def test_direct_shape_helper_refuses_false_empty_with_strict_interior(self):
        first, second = box(), box(.5, .5, .5)
        with patch('machinome.engine.brep._boolean', return_value=empty_common()):
            with self.assertRaisesRegex(BrepCommonInconsistency,
                                        'first.*second'):
                intersect_shapes(first, second, 'first', 'second')

    def test_managed_exact_verdict_does_not_turn_false_empty_green(self):
        first, second = box(), box(.5, .5, .5)
        with patch('machinome.engine.brep._boolean', return_value=empty_common()):
            with self.assertRaisesRegex(BrepCommonInconsistency,
                                        'first.*second'):
                _brep_verdict(first.wrapped, np.eye(4), second.wrapped,
                               np.eye(4), 'first', 'second')

    def test_disjoint_and_boundary_only_pairs_keep_empty_verdict(self):
        first = box()
        for second in (box(2), box(1), box(1, 1)):
            with self.subTest(other=(second.Center().toTuple())):
                with patch('machinome.engine.brep._boolean',
                           return_value=empty_common()):
                    result = intersect_shapes(first, second, 'first', 'second')
                self.assertEqual(len(cq.Shape.cast(result).Solids()), 0)

    def test_nonempty_overlap_and_containment_keep_native_volume(self):
        first = box()
        for second in (box(.5), cq.Solid.makeBox(.25, .25, .25,
                                                cq.Vector(.25, .25, .25))):
            with self.subTest(other=second.Center().toTuple()):
                expected = first.intersect(second)
                result = cq.Shape.cast(
                    intersect_shapes(first, second, 'first', 'second'))
                self.assertEqual(len(result.Solids()), len(expected.Solids()))
                self.assertAlmostEqual(result.Volume(), expected.Volume())

    def test_actual_face_and_edge_tangencies_keep_native_result(self):
        first = box()
        for second in (box(1), box(1, 1)):
            with self.subTest(other=second.Center().toTuple()):
                expected = first.intersect(second)
                result = cq.Shape.cast(
                    intersect_shapes(first, second, 'first', 'second'))
                self.assertEqual(len(result.Solids()), len(expected.Solids()))
                self.assertEqual(sum(solid.Volume() for solid in result.Solids()),
                                 sum(solid.Volume() for solid in expected.Solids()))

    def test_failed_independent_check_refuses_empty_as_clearance(self):
        with patch('machinome.engine.brep._boolean', return_value=empty_common()), \
             patch('machinome.engine.brep.BRepAlgoAPI_Section',
                   side_effect=RuntimeError('section failed')):
            with self.assertRaisesRegex(BrepCommonVerificationError,
                                        'first.*second.*section failed'):
                intersect_shapes(box(), box(2), 'first', 'second')

    def test_unknown_classifier_state_refuses_empty_as_clearance(self):
        with patch('machinome.engine.brep._boolean', return_value=empty_common()), \
             patch('machinome.engine.brep.BRepClass3d_SolidClassifier') as classify:
            classify.return_value.Rejected.return_value = False
            classify.return_value.State.return_value = TopAbs_UNKNOWN
            with self.assertRaisesRegex(BrepCommonVerificationError,
                                        'first.*second.*UNKNOWN'):
                intersect_shapes(box(), box(.5), 'first', 'second')


class InsideOutOperandTest(TestCase):
    """A classifier reads an inside-out solid as everything outside it, so
    no classifier verdict is taken on one: the guard refuses it by name and
    the containment tier declines without consulting (change
    `an-inside-out-operand-is-refused-by-name`)."""

    def test_the_guard_refuses_an_inside_out_operand_by_name(self):
        from machinome.engine import brep as engine
        normal = box().wrapped
        reversed_box = box(1).wrapped.Reversed()
        self.assertLess(engine.solid_volume(reversed_box), 0)
        with patch('machinome.engine.brep._boolean', return_value=empty_common()):
            with self.assertRaises(BrepCommonVerificationError) as caught:
                intersect_shapes(normal, reversed_box, 'first', 'second')
        message = str(caught.exception)
        self.assertIn('second is inside out', message)
        self.assertIn('-1.0', message)
        self.assertNotIn('strictly inside both', message)
        with patch('machinome.engine.brep._boolean', return_value=empty_common()):
            with self.assertRaisesRegex(BrepCommonVerificationError,
                                        'first is inside out'):
                intersect_shapes(reversed_box, normal, 'first', 'second')

    def test_the_containment_guard_declines_without_a_classifier(self):
        from machinome.engine import brep as engine
        normal = box().wrapped
        reversed_box = box(5).wrapped.Reversed()
        built = []

        def recorder(*args):
            built.append(args)
            raise AssertionError('a classifier was built')

        with patch.object(engine, 'BRepClass3d_SolidClassifier', recorder):
            self.assertFalse(engine.mutually_outside(normal, reversed_box))
            self.assertFalse(engine.mutually_outside(reversed_box, normal))
        self.assertEqual(built, [])
