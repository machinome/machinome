"""An empty exact common needs interior resolved beyond native face tolerance."""

from unittest import TestCase
from unittest.mock import patch

import cadquery as cq
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN, TopAbs_ON

from machinome import exact


class ResolvedExactWitnessTest(TestCase):
    def test_rounded_in_classification_on_tangent_faces_is_not_a_witness(self):
        first = cq.Solid.makeBox(1, 1, 1)
        second = cq.Solid.makeBox(1, 1, 1, cq.Vector(0, -1, 0))
        empty = cq.Compound.makeCompound([])

        class RoundedContactClassifier:
            def __init__(self, solid):
                self.native = BRepClass3d_SolidClassifier(solid)
                self.point = None

            def Perform(self, point, tolerance):
                self.point = point
                self.native.Perform(point, tolerance)

            def Rejected(self):
                return self.native.Rejected()

            def State(self):
                if (self.native.State() == TopAbs_ON and
                        abs(self.point.Y()) < 1e-12):
                    return TopAbs_IN
                return self.native.State()

        with patch('machinome.exact._boolean', return_value=empty), \
             patch('machinome.exact.BRepClass3d_SolidClassifier',
                   RoundedContactClassifier):
            self.assertEqual(len(exact.intersect_shapes(first, second,
                                                        'first', 'second').Solids()), 0)

    def test_rounded_boundary_point_is_not_a_resolved_interior(self):
        solid = cq.Solid.makeBox(1, 1, 1)
        self.assertFalse(exact._resolved_interior(solid,
                                                 gp_Pnt(1 - 1e-15, .5, .5)))
        self.assertTrue(exact._resolved_interior(solid, gp_Pnt(.5, .5, .5)))

    def test_failed_native_face_tolerance_refuses_empty_common(self):
        first = cq.Solid.makeBox(1, 1, 1)
        second = cq.Solid.makeBox(1, 1, 1, cq.Vector(.5, .5, .5))
        empty = cq.Compound.makeCompound([])
        with patch('machinome.exact._boolean', return_value=empty), \
             patch('machinome.exact.BRep_Tool.Tolerance_s',
                   side_effect=RuntimeError('face tolerance failed')):
            with self.assertRaisesRegex(exact.ExactCommonVerificationError,
                                        'face tolerance failed'):
                exact.intersect_shapes(first, second, 'first', 'second')

    def test_failed_native_face_distance_refuses_empty_common(self):
        first = cq.Solid.makeBox(1, 1, 1)
        second = cq.Solid.makeBox(1, 1, 1, cq.Vector(.5, .5, .5))
        empty = cq.Compound.makeCompound([])
        with patch('machinome.exact._boolean', return_value=empty), \
             patch('machinome.exact.cq.Vertex.makeVertex',
                   side_effect=RuntimeError('face distance failed')):
            with self.assertRaisesRegex(exact.ExactCommonVerificationError,
                                        'face distance failed'):
                exact.intersect_shapes(first, second, 'first', 'second')

    def test_nonfinite_native_face_tolerance_refuses_empty_common(self):
        first = cq.Solid.makeBox(1, 1, 1)
        second = cq.Solid.makeBox(1, 1, 1, cq.Vector(.5, .5, .5))
        empty = cq.Compound.makeCompound([])
        with patch('machinome.exact._boolean', return_value=empty), \
             patch('machinome.exact.BRep_Tool.Tolerance_s', return_value=float('nan')):
            with self.assertRaisesRegex(exact.ExactCommonVerificationError,
                                        'invalid native face tolerance or distance'):
                exact.intersect_shapes(first, second, 'first', 'second')

    def test_native_positive_common_never_uses_witness_gate(self):
        first = cq.Solid.makeBox(1, 1, 1)
        second = cq.Solid.makeBox(1, 1, 1, cq.Vector(.5, .5, .5))
        with patch('machinome.exact._resolved_interior',
                   side_effect=AssertionError('guard should not run')):
            self.assertGreater(exact.intersect_shapes(first, second,
                                                      'first', 'second').Volume(), 0)
