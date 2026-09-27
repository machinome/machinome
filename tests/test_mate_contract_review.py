"""Adversarial ownership checks for mechanical endpoint normalization."""

import unittest

from machinome.node import AssemblyNode, Frame
from machinome.motion.joints import Bound, Revolute


class Rotor(AssemblyNode):
    origin = Frame()
    turn = Revolute(axis=(0, 0, 1))


class ForeignAssembly(AssemblyNode):
    key = Rotor()


class End(AssemblyNode):
    origin = Frame()


class MateUnit(AssemblyNode):
    seat = Frame()
    body = End()
    turn = body.origin.on(seat, Revolute())


class MateContractReviewTest(unittest.TestCase):
    def test_same_named_child_cannot_launder_a_foreign_bound_read(self):
        with self.assertRaises(TypeError):
            class Bad(AssemblyNode):
                key = Rotor()
                rotor = Rotor(turn=Revolute(axis=(0, 0, 1), range=(0,
                    Bound(lambda own, other: 10 + other,
                          reads=(ForeignAssembly.key.turn,)))))

    def test_same_named_child_cannot_launder_a_foreign_constraint_read(self):
        with self.assertRaises(TypeError):
            class Bad(AssemblyNode):
                key = Rotor()
                rotor = Rotor()
                rotor.turn.constrain(range=(0, Bound(
                    lambda own, other: 10 + other,
                    reads=(ForeignAssembly.key.turn,))))

    def test_inferred_child_joint_cannot_hide_a_mate_self_read(self):
        with self.assertRaisesRegex(TypeError, 'OWN'):
            class Bad(AssemblyNode):
                unit = MateUnit()
                unit.turn.constrain(range=(0, Bound(
                    lambda own, other: 10 + other, reads=(unit.body,))))

    def test_inferred_child_joint_cannot_duplicate_a_mate_read(self):
        for reverse in (False, True):
            with self.subTest(reverse=reverse), self.assertRaisesRegex(TypeError, 'twice'):
                class Bad(AssemblyNode):
                    unit = MateUnit()
                    rotor = Rotor()
                    reads = (unit.turn, unit.body)
                    if reverse:
                        reads = reads[::-1]
                    rotor.turn.constrain(range=(0, Bound(
                        lambda own, a, b: 10 + a + b, reads=reads)))
