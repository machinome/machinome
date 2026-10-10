"""Independent reconstruction and composed-frame review of mate rotations."""

import math
import random
import unittest

from machinome.node.assembly import AssemblyNode
from machinome.node.frames import Frame
from machinome.motion.joints import Revolute
from machinome.motion.mates import _axis_angle


def rodrigues(axis, degrees):
    length = math.sqrt(sum(value * value for value in axis))
    x, y, z = (value / length for value in axis)
    cosine = math.cos(math.radians(degrees))
    sine = math.sin(math.radians(degrees))
    versine = 1 - cosine
    return (
        (cosine + x*x*versine, x*y*versine-z*sine, x*z*versine+y*sine),
        (x*y*versine+z*sine, cosine+y*y*versine, y*z*versine-x*sine),
        (x*z*versine-y*sine, y*z*versine+x*sine, cosine+z*z*versine),
    )


def multiply(left, right):
    return tuple(tuple(sum(left[row][i] * right[i][column] for i in range(3))
                       for column in range(3)) for row in range(3))


def apply(matrix, point):
    return tuple(sum(a*b for a, b in zip(row, point)) for row in matrix)


class MateRotationAdversarialTest(unittest.TestCase):
    def test_seeded_general_rotations_reconstruct_with_existing_snap_allowance(self):
        rng = random.Random(195609)
        largest_error = 0
        for _ in range(1200):
            axis = tuple(rng.uniform(-1, 1) for _ in range(3))
            angle = rng.uniform(-360, 360)
            original = rodrigues(axis, angle)
            recovered_angle, recovered_axis = _axis_angle(original)
            recovered = rodrigues(recovered_axis, recovered_angle)
            largest_error = max(largest_error, max(abs(a-b)
                for row_a, row_b in zip(original, recovered)
                for a, b in zip(row_a, row_b)))
        # Existing snapping intentionally permits error above machine epsilon.
        self.assertLess(largest_error, 3e-9)

    def test_small_axes_survive_permutation_and_both_sides_of_half_turn(self):
        for axis in ((2e-9, -4e-9, 1), (1, 2e-9, -4e-9),
                     (-4e-9, 1, 2e-9)):
            for angle in (-180.000001, -180, -179.999999, -95.6,
                          95.6, 179.999999, 180, 180.000001):
                with self.subTest(axis=axis, angle=angle):
                    original = rodrigues(axis, angle)
                    recovered_angle, recovered_axis = _axis_angle(original)
                    recovered = rodrigues(recovered_axis, recovered_angle)
                    self.assertLess(max(abs(a-b)
                        for ra, rb in zip(original, recovered)
                        for a, b in zip(ra, rb)), 2e-14)

    def test_nonidentity_moving_frame_and_existing_joint_keep_physical_basis(self):
        moving_rotation = rodrigues((2, -1, 3), 37)
        moving_origin = (.3, -.4, .5)
        fixed_origin = (17, -23, 41)
        for axis, angle in (((0, 0, 1), -95.6),
                            ((2e-9, -4e-9, 1), 179.999999),
                            ((1, -2, 3), 180)):
            with self.subTest(axis=axis, angle=angle):
                expected_rotation = rodrigues(axis, angle)
                fixed_rotation = multiply(expected_rotation, moving_rotation)

                class Part(AssemblyNode):
                    connector = Frame(at=moving_origin,
                        x=tuple(row[0] for row in moving_rotation),
                        z=tuple(row[2] for row in moving_rotation))
                    turn = Revolute(axis=(0, 0, 1))

                class Mount(AssemblyNode):
                    seat = Frame(at=fixed_origin,
                        x=tuple(row[0] for row in fixed_rotation),
                        z=tuple(row[2] for row in fixed_rotation))
                    part = Part()
                    attachment = part.connector.on(seat, part.turn)

                mount = Mount()
                mount.render()
                offset = tuple(a-b for a, b in zip(fixed_origin,
                    apply(expected_rotation, moving_origin)))
                for point in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)):
                    actual = (*point, 1)
                    for operation in mount.part.operations:
                        actual = operation.matrix() @ actual
                    expected = tuple(a+b for a, b in zip(
                        apply(expected_rotation, point), offset))
                    for a, b in zip(actual, expected):
                        self.assertAlmostEqual(a, b, delta=2e-12)
