"""Both explicit attachment directions retain their supplied precision."""
import inspect
import unittest

import numpy as np

from machinome.node.frames import Frame
from machinome.node.solid2 import Solid2Node
from machinome.node.assembly import AssemblyNode
from machinome.node.frames import resolved_frames
from machinome.parameters import Length, ParameterError
from machinome.motion.joints import Revolute, declared_joints
from machinome.motion.mates import _axis_angle, _SNAP
from .base import BaseNodeTest
from .test_mate_rotation_conversion import rodrigues

X = (-3.2740476996195866e-13, 3.6046641539722035e-10, 1)
Z = (.9999983500045653, .0018165869499783267, -3.2740476996195866e-13)


class Empty(Solid2Node):
    pass


def basis(x, z):
    z = np.asarray(z, dtype=float)
    z = z / np.linalg.norm(z)
    x = np.asarray(x, dtype=float)
    x = x - np.dot(x, z) * z
    x = x / np.linalg.norm(x)
    return np.column_stack((x, np.cross(z, x), z))


class FramePrecisionTest(BaseNodeTest):
    def assertBasis(self, frame, x=X, z=Z):
        np.testing.assert_allclose(frame.rotation(), basis(x, z), atol=2e-16, rtol=0)
        np.testing.assert_allclose(np.asarray(frame.rotation()).T @ frame.rotation(),
                                   np.eye(3), atol=4e-16, rtol=0)

    def test_exact_source_triad_direct_and_cached(self):
        class Part(Solid2Node):
            pin = Frame(x=X, z=Z)
        part = Part()
        self.assertBasis(Part.pin.resolve(part))
        self.assertBasis(resolved_frames(part)['pin'])
        self.assertIs(resolved_frames(part)['pin'], resolved_frames(part)['pin'])

    def test_parameter_formula_and_callable_once_per_instance(self):
        calls = []
        class Part(Solid2Node):
            small = Length(3e-10)
            literal = Frame(z=(0, 0, 1), x=(1, small * 2, 0))
            computed = Frame(z=lambda n: calls.append(('z', n)) or Z,
                             x=lambda n: calls.append(('x', n)) or X)
        first, second = Part(), Part(small=4e-10)
        for part in (first, second):
            self.assertBasis(resolved_frames(part)['computed'])
            self.assertBasis(resolved_frames(part)['literal'],
                             (1, float(part.small) * 2, 0), (0, 0, 1))
            resolved_frames(part)
        self.assertEqual(len(calls), 4)

    def test_explicit_defaults_positional_signature_and_subclass(self):
        expected = '(at=(0, 0, 0), z=(0, 0, 1), x=None)'
        self.assertEqual(str(inspect.signature(Frame)), expected)
        self.assertEqual(str(inspect.signature(Frame.__init__)), '(self, '+expected[1:])
        self.assertEqual(Frame().z, (0, 0, 1))
        self.assertEqual(repr(Frame()), '<Frame  at=(0, 0, 0) z=(0, 0, 1) x=None>')
        with self.assertRaises(TypeError):
            Frame(1, 2, 3, 4)
        with self.assertRaises(TypeError):
            Frame(precision=True)
        class Explicit(Frame):
            def __init__(self):
                super().__init__(z=(0, 0, 1), x=(1, 3e-10, 0))
        for frame in (Frame(z=(0, 0, 1), x=(1, 3e-10, 0)),
                      Frame((0, 0, 0), (0, 0, 1), (1, 3e-10, 0)), Explicit()):
            self.assertBasis(frame.resolve(Empty()), (1, 3e-10, 0), (0, 0, 1))
        self.assertEqual(Frame(x=(1, 3e-10, 0)).resolve(Empty()).x, (1, 0, 0))

    def test_omitted_directions_inference_and_degeneracy_unchanged(self):
        for index in range(3):
            for sign in (-1, 1):
                z = np.eye(3)[index] * sign
                expected = np.eye(3)[(index + 1) % 3] * sign
                for frame in (Frame(z=tuple(z)), Frame(z=tuple(z), x=None)):
                    self.assertEqual(frame.resolve(Empty()).x, tuple(expected))
        self.assertEqual(Frame(z=(3e-10, 0, 1)).resolve(Empty()).z, (0, 0, 1))
        for frame in (Frame(z=(2e-9, 0, 1)), Frame(z=(0, 0, 0), x=(1, 0, 0)),
                      Frame(z=(0, 0, 1), x=(0, 0, 2))):
            with self.assertRaises(ParameterError):
                frame.resolve(Empty())

    def test_public_composition_uses_precise_cached_basis(self):
        moving_x, moving_z = (1, 0, 0), (0, 1, 0)
        class Part(Solid2Node):
            pin = Frame(at=(11, -7, 19), x=moving_x, z=moving_z)
        class Mount(AssemblyNode):
            seat = Frame(at=(3, 5, 29), x=X, z=Z)
            part = Part()
            held = part.pin.on(seat)
        mount = Mount()
        mount.render()
        expected = np.eye(4)
        expected[:3, :3] = basis(X, Z) @ basis(moving_x, moving_z).T
        expected[:3, 3] = (3, 5, 29) - expected[:3, :3] @ (11, -7, 19)
        actual = np.eye(4)
        for op in mount.part.operations:
            actual = op.matrix() @ actual
        # Final Rotation snap remains intentional; the translation must
        # nevertheless use the precise cached frame composition.
        np.testing.assert_allclose(actual[:3, 3], expected[:3, 3], atol=2e-14, rtol=0)
        np.testing.assert_allclose(actual[:3, :3], expected[:3, :3], atol=2e-9, rtol=0)
        self.assertBasis(resolved_frames(mount)['seat'])

    def test_final_mate_snap_and_generated_or_reused_joint_snap_unchanged(self):
        self.assertEqual(_SNAP, 1e-9)
        class FreshPart(Solid2Node):
            pin = Frame(z=(3e-10, 0, 1), x=(1, 0, 0))
        class FreshMount(AssemblyNode):
            seat = Frame()
            part = FreshPart()
            turn = part.pin.on(seat, Revolute())
        fresh = FreshMount()
        self.assertNotEqual(resolved_frames(fresh.part)['pin'].z[0], 0)
        joint = declared_joints(type(fresh.part))['turn']
        self.assertEqual(joint.arguments(fresh.part)[0], (0, 0, 1))
        fresh.render()
        # Angle snap is in degrees, independently of Frame direction units.
        self.assertIsNone(_axis_angle(rodrigues((0, 0, 1), .5e-9)))
        angle, axis = _axis_angle(rodrigues((3e-10, 0, 1), 95.6))
        self.assertEqual((angle, axis), (95.6, [0, 0, 1]))
        class ExistingPart(Solid2Node):
            pin = Frame(z=Z, x=X)
            turn = Revolute(axis=(0, 1, 3e-10))
        class ExistingMount(AssemblyNode):
            seat = Frame()
            part = ExistingPart()
            mounted = part.pin.on(seat, part.turn)
        mounted = ExistingMount()
        self.assertIs(declared_joints(type(mounted.part))['turn'], ExistingPart.turn)
        self.assertEqual(ExistingPart.turn.axis, (0, 1, 3e-10))
        self.assertEqual(ExistingPart.turn.arguments(mounted.part)[0], (0, 1, 0))
