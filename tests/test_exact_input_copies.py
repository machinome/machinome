"""Framework OCCT operations give default-mode Booleans private input B-reps."""

from unittest import TestCase
from unittest.mock import patch
import struct

import cadquery as cq
from OCP.BRep import BRep_Tool

import machinome.exact as exact


def box(x=0):
    return cq.Solid.makeBox(1, 1, 1, cq.Vector(x, 0, 0))


def input_fingerprint(shape):
    """Sample exact topology, coordinates and every subshape tolerance."""
    vertices, edges, faces = shape.Vertices(), shape.Edges(), shape.Faces()
    return (
        len(vertices), len(edges), len(faces),
        tuple((tuple(struct.pack('!d', coordinate)
                     for coordinate in vertex.toTuple()),
               struct.pack('!d', BRep_Tool.Tolerance_s(vertex.wrapped)))
              for vertex in vertices),
        tuple(struct.pack('!d', BRep_Tool.Tolerance_s(edge.wrapped))
              for edge in edges),
        tuple(struct.pack('!d', BRep_Tool.Tolerance_s(face.wrapped))
              for face in faces),
    )


class ObserveBuild:
    """Forward an OCCT algorithm, recording mode and actual B-rep operands."""

    def __init__(self, algorithm, observed, first, second):
        self.algorithm = algorithm
        self.observed = observed
        self.first = first
        self.second = second

    def __getattr__(self, name):
        return getattr(self.algorithm, name)

    def Build(self):
        self.observed.append((
            self.algorithm.NonDestructive(),
            self.algorithm.Arguments().First().IsSame(self.first.wrapped),
            self.algorithm.Tools().First().IsSame(self.second.wrapped),
        ))
        return self.algorithm.Build()


class NativeInputPreservationTest(TestCase):
    def assert_private_copies(self, algorithm_name, operation, shift):
        original = getattr(exact, algorithm_name)
        first, second = box(), box(shift)

        def observed(*args):
            return ObserveBuild(original(*args), observed_builds, first, second)

        observed_builds = []
        with patch.object(exact, algorithm_name, side_effect=observed):
            operation(first, second)
        self.assertEqual(observed_builds, [(False, False, False)])

    def test_common_receives_private_inputs_in_default_mode(self):
        self.assert_private_copies('BRepAlgoAPI_Common',
                                   lambda a, b: exact.intersect_shapes(
                                       a, b, 'left', 'right'), .5)

    def test_fuse_receives_private_inputs_in_default_mode(self):
        self.assert_private_copies('BRepAlgoAPI_Fuse',
                                   lambda a, b: exact.fuse_shapes(
                                       a, b, 'left', 'right'), .5)

    def test_false_empty_section_receives_private_inputs_in_default_mode(self):
        self.assert_private_copies('BRepAlgoAPI_Section',
                                   lambda a, b: exact.intersect_shapes(
                                       a, b, 'left', 'right'), 2)

    def test_copy_failure_refuses_with_named_pair(self):
        for operation in (exact.intersect_shapes, exact.fuse_shapes):
            with self.subTest(operation=operation.__name__):
                with patch.object(cq.Shape, 'copy', side_effect=RuntimeError(
                        'copy failed')):
                    with self.assertRaisesRegex(RuntimeError, 'left and right'):
                        operation(box(), box(.5), 'left', 'right')

    def test_section_copy_failure_refuses_verification_with_named_pair(self):
        original_copy = cq.Shape.copy
        calls = []

        def fail_third(shape, mesh=False):
            calls.append(shape)
            if len(calls) == 3:
                raise RuntimeError('section copy failed')
            return original_copy(shape, mesh=mesh)

        with patch.object(cq.Shape, 'copy', autospec=True,
                          side_effect=fail_third):
            with self.assertRaisesRegex(exact.ExactCommonVerificationError,
                                        'left and right'):
                exact.intersect_shapes(box(), box(2), 'left', 'right')

    def test_native_contact_verdicts_and_repeated_inputs(self):
        first = box()
        for shift in (2, 1, .5):
            with self.subTest(shift=shift):
                second = box(shift)
                for _ in range(2):
                    result = exact.intersect_shapes(first, second,
                                                    'left', 'right')
                    self.assertTrue(result.isValid())
                    if shift == .5:
                        self.assertGreater(result.Volume(), 0)
                    else:
                        self.assertEqual(result.Volume(), 0)

    def test_common_fuse_and_section_preserve_both_inputs(self):
        operations = (
            ('common', lambda a, b: exact.intersect_shapes(a, b, 'a', 'b'), .5),
            ('fuse', lambda a, b: exact.fuse_shapes(a, b, 'a', 'b'), .5),
            ('section', lambda a, b: exact.intersect_shapes(a, b, 'a', 'b'), 2),
        )
        for name, operation, shift in operations:
            with self.subTest(operation=name):
                first, second = box(), box(shift)
                before = input_fingerprint(first), input_fingerprint(second)
                operation(first, second)
                self.assertEqual(
                    (input_fingerprint(first), input_fingerprint(second)), before)
