"""Independent review of explicit direction precision and construction paths."""

import copy
import math
import pickle
import unittest

from machinome.node import AssemblyNode, Frame
from machinome.motion.joints import Revolute
from .test_mate_rotation_adversarial import apply, rodrigues


class PresetFrame(Frame):
    def __init__(self):
        super().__init__(x=(1, 3e-10, 0), z=(0, 0, 1))


class Bare(AssemblyNode):
    pass


class FramePrecisionReviewTest(unittest.TestCase):
    def test_explicit_directions_passed_by_subclass_are_not_defaults(self):
        self.assertEqual(PresetFrame().resolve(Bare()).x[1], 3e-10)

    def test_copy_and_pickle_preserve_the_presence_distinction(self):
        precise = Frame(x=(1, 3e-10, 0), z=(0, 0, 1))
        defaulted = Frame(x=(1, 3e-10, 0))
        for frame, expected in ((precise, 3e-10), (defaulted, 0)):
            for clone in (copy.copy, copy.deepcopy,
                          lambda value: pickle.loads(pickle.dumps(value))):
                with self.subTest(expected=expected, clone=clone):
                    self.assertEqual(clone(frame).resolve(Bare()).x[1], expected)

    def test_components_near_unit_magnitude_remain_normalized(self):
        # Snap-to-one can also lose precision, even when no nonzero component
        # is below the snap-to-zero threshold.
        for sign in (-1, 1):
            for x, z in (((sign, 2e-5, 0), (0, 0, 1)),
                         ((1, 0, 0), (0, 2e-5, sign))):
                with self.subTest(x=x, z=z):
                    frame = Frame(x=x, z=z).resolve(Bare())
                    for vector in (frame.x, frame.y, frame.z):
                        self.assertAlmostEqual(sum(v*v for v in vector), 1, delta=4e-16)
                    self.assertAlmostEqual(sum(a*b for a, b in zip(frame.x, frame.z)),
                                           0, delta=1e-16)

    def test_tiny_moving_frame_rotation_affects_real_nonidentity_placement(self):
        tiny_radians = 3e-10
        moving_origin = (100, 20, 4)
        fixed_origin = (17, -23, 41)
        fixed_rotation = rodrigues((0, 0, 1), 37)

        class Part(AssemblyNode):
            connector = Frame(at=moving_origin,
                x=(math.cos(tiny_radians), math.sin(tiny_radians), 0),
                z=(0, 0, 1))
            turn = Revolute(axis=(0, 0, 1))

        class Mount(AssemblyNode):
            seat = Frame(at=fixed_origin,
                x=tuple(row[0] for row in fixed_rotation), z=(0, 0, 1))
            part = Part()
            attachment = part.connector.on(seat, part.turn)

        mount = Mount()
        mount.render()
        expected_rotation = rodrigues((0, 0, 1), 37 - math.degrees(tiny_radians))
        offset = tuple(a-b for a, b in zip(fixed_origin,
            apply(expected_rotation, moving_origin)))
        for point in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)):
            actual = (*point, 1)
            for operation in mount.part.operations:
                actual = operation.matrix() @ actual
            expected = tuple(a+b for a, b in zip(apply(expected_rotation, point), offset))
            for a, b in zip(actual, expected):
                self.assertAlmostEqual(a, b, delta=2e-13)
