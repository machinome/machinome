"""A touching pair is settled without the slower classifier.

After an empty common the witness search asks first the classifiers of the
operand with fewer faces, and for a point inside it reads the point's side
of each solid from that solid's nearest boundary point before the other
operand's classifiers are asked: a point outside, or on the boundary of,
every solid of an operand is no candidate. Wall clock 02's weight shell
against its screw is that case: the shell's classifier answers in 200 ms
and more near the screw, and no stencil point is inside both. A side
reading never makes a point count, so every refusal stays where it was.
"""

from ast import literal_eval
from collections import Counter
import re
from unittest import TestCase
from unittest.mock import patch

import cadquery as cq
from OCP.BRep import BRep_Builder
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN, TopAbs_REVERSED
from OCP.TopoDS import (TopoDS_Iterator, TopoDS_Shape, TopoDS_Shell,
                        TopoDS_Solid)

from machinome.engine import BrepCommonInconsistency
from machinome.engine import brep as engine


def empty_common():
    return cq.Compound.makeCompound([]).wrapped


def witness_of(error):
    found = re.search(r'solids: (\([^)]*\))', str(error))
    return literal_eval(found.group(1))


def box(x=0, y=0, z=0, a=1, b=1, c=1):
    return cq.Solid.makeBox(a, b, c, cq.Vector(x, y, z)).wrapped


def pin_in_hole(interference):
    """A 20 x 20 x 6 plate with a 6 mm hole (7 faces), and a 12 mm pin
    through it (3 faces), `interference` over the hole's radius."""
    plate = (cq.Workplane().box(20, 20, 6).faces('>Z').workplane()
             .hole(6).val().wrapped)
    pin = cq.Solid.makeCylinder(3 + interference, 12,
                                cq.Vector(0, 0, -6)).wrapped
    return plate, pin


def slot_and_key(interference):
    """A 10 x 10 x 4 block with a 3 mm slot 2 mm deep, and a key
    `interference` wider than the slot on each side, 0.5 mm into its
    floor."""
    slotted = (cq.Workplane().box(10, 10, 4).faces('>Z').workplane()
               .rect(3, 12).cutBlind(-2).val().wrapped)
    key = box(-1.5 - interference, -6, -.5, 3 + 2 * interference, 12, 2)
    return slotted, key


def with_reversed_shell(solid):
    """`solid` rebuilt from a shell stored REVERSED, each of whose faces is
    reversed in it: the same right-side-out solid, its faces' orientations
    reaching the solid only through the shell's."""
    builder = BRep_Builder()
    shell = TopoDS_Shell()
    builder.MakeShell(shell)
    for face in engine._faces(solid):
        builder.Add(shell, face.Reversed())
    shell.Closed(True)
    rebuilt = TopoDS_Solid()
    builder.MakeSolid(rebuilt)
    builder.Add(rebuilt, shell.Reversed())
    return rebuilt


class NearestSideTest(TestCase):
    def side(self, shape, *coords):
        solid = engine._solids(shape)[0]
        return engine._nearest_side(engine._boundary(solid), gp_Pnt(*coords))

    def test_a_point_reads_its_side_from_its_nearest_boundary_point(self):
        cube = box()
        ell = (cq.Solid.makeBox(2, 2, 1)
               .cut(cq.Solid.makeBox(1, 1, 1, cq.Vector(1, 1, 0))).wrapped)
        cylinder = cq.Solid.makeCylinder(1, 2).wrapped
        cases = (
            ('box, centre', cube, (.5, .5, .5), 'in'),
            ('box, past a face', cube, (1.5, .5, .5), 'out'),
            ('box, past an edge', cube, (1.5, 1.5, .5), 'out'),
            ('box, 1e-9 outside a face', cube, (1 + 1e-9, .5, .5), 'on'),
            ('box, 1e-9 inside a face', cube, (1 - 1e-9, .5, .5), 'on'),
            ('box, past a corner', cube, (1.5, 1.5, 1.5), None),
            ('L, by its concave edge', ell, (.9, .9, .5), 'in'),
            ('cylinder, outside by its seam', cylinder, (1.1, 0, 1), 'out'),
            ('cylinder, inside by its seam', cylinder, (.9, 0, 1), 'in'),
        )
        for label, shape, coords, expected in cases:
            with self.subTest(label):
                self.assertEqual(self.side(shape, *coords), expected)

    def test_a_face_is_oriented_as_its_solid_holds_it(self):
        # The shell is stored REVERSED and each face reversed in it, so a
        # normal read from the face as the shell holds it points into the
        # solid; the solid's own composition points it out.
        cube = with_reversed_shell(box())
        self.assertEqual(TopoDS_Iterator(cube).Value().Orientation(),
                         TopAbs_REVERSED)
        self.assertGreater(engine.solid_volume(cube), 0)
        for label, coords, expected in (
                ('centre', (.5, .5, .5), 'in'),
                ('inside, by a face', (.5, .5, .9), 'in'),
                ('past a face', (1.5, .5, .5), 'out'),
                ('past an edge', (1.5, 1.5, .5), 'out')):
            with self.subTest(label):
                self.assertEqual(self.side(cube, *coords), expected)


class CountingExtrema:
    """The native extrema, counting the faces of every shape loaded into
    it."""

    faces = 0
    loaded = []

    def __init__(self, *args):
        for arg in args:
            if isinstance(arg, TopoDS_Shape):
                self.count(arg)
        self.native = BRepExtrema_DistShapeShape(*args)

    @staticmethod
    def count(shape):
        CountingExtrema.faces += len(engine._faces(shape))
        CountingExtrema.loaded.append(shape)

    def LoadS1(self, shape):
        self.count(shape)
        self.native.LoadS1(shape)

    def LoadS2(self, shape):
        self.count(shape)
        self.native.LoadS2(shape)

    def __getattr__(self, name):
        return getattr(self.native, name)


class NearestSideSearchTest(TestCase):
    def test_a_point_near_one_face_is_measured_against_few_faces(self):
        # A 240-gon prism has 242 faces. A point 0.01 mm from the middle of
        # one side face is nearest that face; the faces' boxes leave only
        # the faces whose box comes as close as it to be measured.
        prism = cq.Workplane().polygon(240, 20).extrude(5).val()
        solid = engine._solids(prism.wrapped)[0]
        total = len(engine._faces(solid))
        self.assertEqual(total, 242)
        side_face = next(face for face in prism.Faces()
                         if abs(face.normalAt().z) < 1e-9)
        centre, normal = side_face.Center(), side_face.normalAt()
        boundary = engine._boundary(solid)
        for label, offset, expected in (('outside', .01, 'out'),
                                        ('inside', -.01, 'in')):
            with self.subTest(label):
                at = centre + normal * offset
                CountingExtrema.faces = 0
                with patch('machinome.engine.brep.BRepExtrema_DistShapeShape',
                           CountingExtrema):
                    side = engine._nearest_side(boundary,
                                                gp_Pnt(at.x, at.y, at.z))
                self.assertEqual(side, expected)
                self.assertLess(CountingExtrema.faces, total // 10)

    def test_a_tilted_flat_face_is_passed_over_by_its_plane(self):
        # The prism turned 45 degrees about an axis in its end face: each
        # end face's box is a slab holding a point 0.01 mm outside the
        # middle of a side face, 2.5 mm from either end face's plane.
        prism = cq.Workplane().polygon(240, 20).extrude(5).val()
        side_face = max((face for face in prism.Faces()
                         if abs(face.normalAt().z) < 1e-9),
                        key=lambda face: face.normalAt().dot(
                            cq.Vector(1, 1, 0)))
        at = side_face.Center() + side_face.normalAt() * .01
        axis = ((0, 0, 0), (1, 0, 0))
        tilted = prism.rotate(*axis, 45)
        at = cq.Vertex.makeVertex(*at.toTuple()).rotate(*axis, 45).toTuple()
        solid = engine._solids(tilted.wrapped)[0]
        ends = [face.wrapped for face in tilted.Faces() if face.Area() > 100]
        self.assertEqual(len(ends), 2)
        for low, high in (engine.bounds(end) for end in ends):
            self.assertTrue(all(low[i] < at[i] < high[i] for i in range(3)))
        boundary = engine._boundary(solid)
        CountingExtrema.faces, CountingExtrema.loaded = 0, []
        with patch('machinome.engine.brep.BRepExtrema_DistShapeShape',
                   CountingExtrema):
            side = engine._nearest_side(boundary, gp_Pnt(*at))
        self.assertEqual(side, 'out')
        measured = [shape for shape in CountingExtrema.loaded
                    if any(shape.IsSame(end) for end in ends)]
        self.assertEqual(measured, [], f'{CountingExtrema.faces} faces '
                         f'measured, the end faces among them')


class Counting:
    """The native classifier, counting its calls by its solid's faces."""

    asked = Counter()

    def __init__(self, solid):
        self.native = BRepClass3d_SolidClassifier(solid)
        self.faces = len(engine._faces(solid))

    def Perform(self, point, tolerance):
        Counting.asked[self.faces] += 1
        self.native.Perform(point, tolerance)

    def Rejected(self):
        return self.native.Rejected()

    def State(self):
        return self.native.State()


class PinInItsHoleTest(TestCase):
    def test_a_pin_that_fits_its_hole_is_settled_without_the_plate(self):
        # The plate (7 faces) and the pin (3 faces) touch on the hole's
        # cylinder; every stencil point inside the pin reads outside the
        # plate, or on its boundary, from its nearest boundary point.
        plate, pin = pin_in_hole(0)
        for label, first, second in (('plate first', plate, pin),
                                     ('pin first', pin, plate)):
            with self.subTest(label):
                Counting.asked.clear()
                with patch('machinome.engine.brep._boolean',
                           return_value=empty_common()), \
                     patch('machinome.engine.brep.BRepClass3d_SolidClassifier',
                           Counting):
                    result = engine.intersect_shapes(first, second,
                                                     'first', 'second')
                self.assertEqual(engine.solid_count(result), 0)
                self.assertGreater(Counting.asked[3], 0)
                self.assertEqual(Counting.asked[7], 0)


class RefusalUnmovedTest(TestCase):
    def refused_at(self, first, second):
        with patch('machinome.engine.brep._boolean',
                   return_value=empty_common()):
            with self.assertRaises(BrepCommonInconsistency) as refused:
                engine.intersect_shapes(first, second, 'first', 'second')
        return witness_of(refused.exception)

    def test_a_side_reading_does_not_move_a_refusal(self):
        # Shared material the Boolean is made to miss: the search with
        # every side undecided, which classifies as before, and the search
        # with the side readings refuse at the same point.
        cases = (
            ('overlapping boxes', box(), box(.5, .5, .5)),
            ('a 0.4 mm slab', box(), box(0, .6, 0)),
            ('a pin 0.2 mm over its hole', *pin_in_hole(.2)),
            ('a key 0.1 mm into its slot', *slot_and_key(.1)),
        )
        for label, first, second in cases:
            with self.subTest(label):
                with patch('machinome.engine.brep._nearest_side',
                           return_value=None):
                    undecided = self.refused_at(first, second)
                self.assertEqual(self.refused_at(first, second), undecided)


class LoneInsideReadingUnaskedTest(TestCase):
    def test_the_side_reading_excludes_a_lone_inside_reading_unasked(self):
        # LoneInsideReadingTest's boxes and lie: the second box's classifier
        # would answer IN at the first point strictly below the contact it
        # is asked about. Every such point reads outside the second box
        # from its nearest boundary point, so the lie is never asked for.
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
        self.assertEqual(lied_at, [])
        self.assertEqual(engine.solid_count(result), 0)
