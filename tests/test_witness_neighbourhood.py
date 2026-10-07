"""A witness against an empty B-rep common is interior in its neighbourhood.

No face of a solid lies closer to a candidate than its smallest face
distance, so the candidate's six axis neighbours at half that distance have
its true state. A zero-tolerance IN that those neighbours contradict is a
classifier's error, not shared interior, and does not overturn an empty
common. OpenAstroMount's bearing seat is that case: its insert's classifier
answers IN at one point 0.1357 mm outside the insert's sphere and OUT at
that point's neighbours.
"""

from ast import literal_eval
import re
from unittest import TestCase
from unittest.mock import patch

import cadquery as cq
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN, TopAbs_UNKNOWN

from machinome.engine import (BrepCommonInconsistency,
                              BrepCommonVerificationError)
from machinome.engine import brep as engine


def empty_common():
    return cq.Compound.makeCompound([]).wrapped


def witness_of(error):
    found = re.search(r'solids: (\([^)]*\))', str(error))
    return literal_eval(found.group(1))


class LoneInsideReadingTest(TestCase):
    def test_a_lone_inside_reading_is_not_a_witness(self):
        # Two unit boxes touch along y = 1: their common is truly empty.
        # The second box's classifier answers IN at exactly one point, the
        # first one strictly below the contact it is asked about, beyond
        # every face tolerance, and truthfully everywhere else.
        first = cq.Solid.makeBox(1, 1, 1)
        second = cq.Solid.makeBox(1, 1, 1, cq.Vector(0, 1, 0))
        lied_at = []

        class LoneFalseIn:
            def __init__(self, solid):
                self.native = BRepClass3d_SolidClassifier(solid)
                low, _high = engine.bounds(solid)
                self.is_second = abs(low[1] - 1.0) < 1e-6
                self.point = None

            def Perform(self, point, tolerance):
                self.point = point
                self.native.Perform(point, tolerance)

            def _lies(self):
                if not self.is_second:
                    return False
                key = (self.point.X(), self.point.Y(), self.point.Z())
                if not lied_at and .9 < key[1] < 1 - 1e-6:
                    lied_at.append(key)
                return key in lied_at

            def Rejected(self):
                return False if self._lies() else self.native.Rejected()

            def State(self):
                return TopAbs_IN if self._lies() else self.native.State()

        with patch('machinome.engine.brep._boolean',
                   return_value=empty_common()), \
             patch('machinome.engine.brep.BRepClass3d_SolidClassifier',
                   LoneFalseIn):
            result = engine.intersect_shapes(first, second, 'first', 'second')
        self.assertEqual(len(lied_at), 1)
        self.assertEqual(len(cq.Shape.cast(result).Solids()), 0)


class ResolvedMarginTest(TestCase):
    def test_resolved_interior_reports_the_smallest_face_distance(self):
        solid = cq.Solid.makeBox(1, 1, 1).wrapped
        self.assertAlmostEqual(
            engine._resolved_interior(solid, gp_Pnt(.5, .5, .5)), .5,
            delta=1e-12)
        self.assertAlmostEqual(
            engine._resolved_interior(solid, gp_Pnt(.9, .5, .5)), .1,
            delta=1e-12)
        self.assertIsNone(
            engine._resolved_interior(solid, gp_Pnt(1 - 1e-15, .5, .5)))


class UndecidedNeighbourTest(TestCase):
    def test_an_undecided_neighbour_refuses_verification(self):
        # The boxes share the cube [.5, 1]³. Every classifier answers
        # natively until the second box's has once answered IN, and UNKNOWN
        # after that: the first query left is a neighbour's.
        first = cq.Solid.makeBox(1, 1, 1)
        second = cq.Solid.makeBox(1, 1, 1, cq.Vector(.5, .5, .5))
        undecided = []

        class UndecidedAfterFirstIn:
            def __init__(self, solid):
                self.native = BRepClass3d_SolidClassifier(solid)
                low, _high = engine.bounds(solid)
                self.is_second = abs(low[0] - .5) < 1e-6

            def Perform(self, point, tolerance):
                self.native.Perform(point, tolerance)

            def Rejected(self):
                return False if undecided else self.native.Rejected()

            def State(self):
                if undecided:
                    return TopAbs_UNKNOWN
                state = self.native.State()
                if self.is_second and state == TopAbs_IN:
                    undecided.append(True)
                return state

        with patch('machinome.engine.brep._boolean',
                   return_value=empty_common()), \
             patch('machinome.engine.brep.BRepClass3d_SolidClassifier',
                   UndecidedAfterFirstIn):
            with self.assertRaisesRegex(BrepCommonVerificationError,
                                        'first.*second.*UNKNOWN'):
                engine.intersect_shapes(first, second, 'first', 'second')


class SharedInteriorStillRefusedTest(TestCase):
    def test_a_slab_of_shared_interior_is_still_refused(self):
        # Real material of both solids around the witness, as in Voron-2's
        # thread seats: the boxes share a 0.4 mm slab, 0.6 < y < 1.
        first = cq.Solid.makeBox(1, 1, 1)
        second = cq.Solid.makeBox(1, 1, 1, cq.Vector(0, .6, 0))
        with patch('machinome.engine.brep._boolean',
                   return_value=empty_common()):
            with self.assertRaises(BrepCommonInconsistency) as refused:
                engine.intersect_shapes(first, second, 'first', 'second')
        x, y, z = witness_of(refused.exception)
        self.assertTrue(0 < x < 1 and .6 < y < 1 and 0 < z < 1, (x, y, z))
