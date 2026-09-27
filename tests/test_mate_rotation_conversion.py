"""Independent proper-rotation witnesses for mate rest placement."""
import math
import unittest

import numpy as np

from machinome.motion.mates import _axis_angle, _SNAP
from machinome.node import AssemblyNode, Solid2Node, Frame
from .base import BaseNodeTest


def rodrigues(axis, degrees):
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    skew = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    angle = math.radians(degrees)
    return (math.cos(angle) * np.eye(3)
            + (1 - math.cos(angle)) * np.outer(axis, axis)
            + math.sin(angle) * skew)


class RotationConversionTest(unittest.TestCase):
    def assertReconstructs(self, matrix, tolerance=2e-15):
        angle, axis = _axis_angle(matrix)
        np.testing.assert_allclose(rodrigues(axis, angle), matrix,
                                   atol=tolerance, rtol=0)
        return angle, axis

    def test_curta_negative_z_has_no_phantom_components(self):
        self.assertEqual(_axis_angle(rodrigues((0, 0, 1), -95.6)),
                         (95.6, [0, 0, -1]))

    def test_signed_principal_axes_and_ninety_degree_branch(self):
        for index in range(3):
            axis = np.eye(3)[index]
            for degrees in (-179, -120, -95.6, -90.000001, -90,
                            -89.999999, 89.999999, 90, 90.000001, 95.6, 120, 179):
                with self.subTest(index=index, degrees=degrees):
                    _, recovered = self.assertReconstructs(rodrigues(axis, degrees))
                    expected = axis * (1 if degrees > 0 else -1)
                    self.assertEqual(recovered, list(expected))

    def test_true_small_components_survive_large_and_half_turns(self):
        for axis in ((2e-9, -4e-9, 1), (-2e-9, 1, 4e-9),
                     (1, 2e-9, 4e-9), (2e-6, -4e-6, 1)):
            for degrees in (95.6, 179.999999, 180, -179.999999):
                with self.subTest(axis=axis, degrees=degrees):
                    _, recovered = self.assertReconstructs(rodrigues(axis, degrees))
                    for original, component in zip(axis, recovered):
                        self.assertNotEqual(component, 0)
                        expected = abs(original) / np.linalg.norm(axis)
                        if abs(expected - 1) <= _SNAP:
                            expected = 1  # The pre-existing whole-number snap.
                        self.assertAlmostEqual(abs(component), expected,
                                               delta=2e-15)

    def test_half_turn_symmetry_and_mixed_signs(self):
        for axis in ((0, 1, 1), (1, -1, 0), (1, 1, 1), (1, -2, 3)):
            with self.subTest(axis=axis):
                angle, recovered = self.assertReconstructs(rodrigues(axis, 180))
                self.assertEqual(angle, 180)
                if axis == (0, 1, 1):
                    self.assertEqual(recovered[1], recovered[2])
                if axis == (1, 1, 1):
                    self.assertEqual(recovered[0], recovered[1])
                    self.assertEqual(recovered[1], recovered[2])

    def test_existing_snap_and_identity_boundaries(self):
        self.assertEqual(_SNAP, 1e-9)
        self.assertIsNone(_axis_angle(np.eye(3)))
        self.assertIsNone(_axis_angle(rodrigues((0, 0, 1), .5e-9)))
        self.assertIsNotNone(_axis_angle(rodrigues((0, 0, 1), 2e-9)))
        self.assertEqual(_axis_angle(rodrigues((0, 0, 1), 120 + .5e-9))[0], 120)
        self.assertNotEqual(_axis_angle(rodrigues((0, 0, 1), 120 + 2e-9))[0], 120)
        self.assertEqual(_axis_angle(rodrigues((.5e-9, 0, 1), 95.6))[1][0], 0)
        self.assertNotEqual(_axis_angle(rodrigues((2e-9, 0, 1), 95.6))[1][0], 0)


class PublicFrameRotationTest(BaseNodeTest):
    def test_negative_z_rest_operations_and_physical_basis(self):
        class Part(Solid2Node):
            axle = Frame()

        rotation = rodrigues((0, 0, 1), -95.6)

        class Mount(AssemblyNode):
            seat = Frame(at=(7, -3, 11), z=tuple(rotation[:, 2]),
                         x=tuple(rotation[:, 0]))
            part = Part()
            held = part.axle.on(seat)

        mount = Mount()
        mount.render()
        operations = mount.part.operations
        self.assertEqual([op.serialized[0] for op in operations], ['r', 't'])
        self.assertEqual(operations[0].serialized, ['r', '95.6', [0, 0, -1]])
        actual = np.eye(4)
        for operation in operations:
            actual = operation.matrix() @ actual
        expected = np.eye(4)
        expected[:3, :3] = rotation
        expected[:3, 3] = (7, -3, 11)
        for point in ((0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1),
                      (0, 0, 1, 1), (81.5, -68, 123, 1)):
            np.testing.assert_allclose(actual @ point, expected @ point,
                                       atol=3e-14, rtol=0)
