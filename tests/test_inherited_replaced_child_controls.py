"""Inherited hand controls through a specialized same-path child."""

from machinome.motion.joints import Prismatic, Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver, Sim, Turn

from .base import BaseNodeTest
from .running_project.machine import DialArbor


class BaseMachine(AssemblyNode):
    time = Time.running()
    hand = Driver(default=0.0, unit='deg')
    body = DialArbor()
    hand.drives(body.turn)
    controls = {'turn dial': Turn(body.dial, hand, coordinate=body.turn)}


class SpecializedArbor(DialArbor):
    turn = Revolute(axis=(0, 1, 0), unit='deg')


class InheritedReplacedChildControlsTest(BaseNodeTest):
    def test_preserved_control_follows_compatible_child_replacement(self):
        class SpecializedMachine(BaseMachine):
            body = SpecializedArbor()
            controls = {**BaseMachine.controls,
                        'turn again': Turn(body.dial, BaseMachine.hand,
                                           coordinate=body.turn)}

        sim = Sim(SpecializedMachine(), 0.1)
        controls = {entry.name: entry for entry in sim.program.controls}
        self.assertEqual(set(controls), {'turn dial', 'turn again'})
        self.assertEqual(controls['turn dial'].part, ('body', 'dial'))
        self.assertEqual(controls['turn dial'].coordinate, 'body.turn')
        self.assertEqual(controls['turn dial'].axis, (0, 1, 0))

    def test_an_explicit_table_still_replaces_its_ancestor(self):
        class OnlyNew(BaseMachine):
            body = SpecializedArbor()
            controls = {'turn again': Turn(body.dial, BaseMachine.hand,
                                           coordinate=body.turn)}

        self.assertEqual(set(Sim(OnlyNew(), 0.1).controls), {'turn again'})

        class NoneAtAll(BaseMachine):
            controls = {}

        self.assertEqual(Sim(NoneAtAll(), 0.1).controls, {})

    def test_a_foreign_same_name_part_or_coordinate_is_not_inherited(self):
        class Foreign(AssemblyNode):
            body = DialArbor()

        with self.assertRaisesRegex(TypeError, 'foreign part'):
            class ForeignPart(BaseMachine):
                body = SpecializedArbor()
                controls = {**BaseMachine.controls,
                            'foreign part': Turn(Foreign.body.dial,
                                                 BaseMachine.hand,
                                                 coordinate=body.turn)}

        with self.assertRaisesRegex(TypeError, 'foreign coordinate'):
            class ForeignCoordinate(BaseMachine):
                body = SpecializedArbor()
                controls = {**BaseMachine.controls,
                            'foreign coordinate': Turn(body.dial,
                                                      BaseMachine.hand,
                                                      coordinate=Foreign.body.turn)}

    def test_a_new_control_cannot_borrow_the_ancestor_child_by_name(self):
        with self.assertRaisesRegex(TypeError, 'turn dial'):
            class BorrowedButNew(BaseMachine):
                body = SpecializedArbor()
                controls = {'turn dial': Turn(BaseMachine.body.dial,
                                             BaseMachine.hand,
                                             coordinate=BaseMachine.body.turn)}

    def test_an_unvalidated_mixin_table_is_not_ancestor_provenance(self):
        class Unvalidated:
            body = BaseMachine.body
            controls = {'turn dial': Turn(body.dial, BaseMachine.hand,
                                         coordinate=body.turn)}

        with self.assertRaisesRegex(TypeError, 'turn dial'):
            class Borrowed(Unvalidated, BaseMachine):
                body = SpecializedArbor()
                controls = {**Unvalidated.controls}

    def test_an_incompatible_same_name_replacement_is_refused(self):
        class OtherBody(AssemblyNode):
            turn = Revolute(axis=(0, 1, 0), unit='deg')
            dial = DialArbor()

        with self.assertRaisesRegex(TypeError, 'turn dial'):
            class Incompatible(BaseMachine):
                body = OtherBody()
                controls = {**BaseMachine.controls}

    def test_effective_joint_domain_is_still_checked(self):
        class SlidingArbor(DialArbor):
            turn = Prismatic(axis=(0, 1, 0), unit='mm')

        class WrongDomain(BaseMachine):
            body = SlidingArbor()
            controls = {**BaseMachine.controls}

        with self.assertRaisesRegex(ValueError, 'turn dial'):
            Sim(WrongDomain(), 0.1)

    def test_effective_selected_joint_must_still_pose_the_part(self):
        class TwoArbors(AssemblyNode):
            left = DialArbor()
            right = DialArbor()

        class Original(AssemblyNode):
            time = Time.running()
            hand = Driver(default=0.0, unit='deg')
            body = TwoArbors()
            hand.drives(body.left.turn)
            hand.drives(body.right.turn)
            controls = {'sideways': Turn(body.left.dial, hand,
                                        coordinate=body.right.turn)}

        class SpecializedTwo(TwoArbors):
            left = SpecializedArbor()

        class Replaced(Original):
            body = SpecializedTwo()
            controls = {**Original.controls}

        with self.assertRaisesRegex(ValueError, 'sideways'):
            Sim(Replaced(), 0.1)

    def test_a_removed_effective_part_does_not_publish_the_old_one(self):
        class Outer(AssemblyNode):
            inner = DialArbor()

        class OuterMachine(AssemblyNode):
            time = Time.running()
            hand = Driver(default=0.0, unit='deg')
            body = Outer()
            controls = {'turn dial': Turn(body.inner.dial, hand,
                                         coordinate=body.inner.turn)}

        class Empty(AssemblyNode):
            pass

        class MissingDial(Outer):
            inner = Empty()

        class Replaced(OuterMachine):
            body = MissingDial()
            controls = {**OuterMachine.controls}

        with self.assertRaisesRegex((TypeError, ValueError), 'turn dial'):
            Sim(Replaced(), 0.1)

    def test_a_removed_effective_selected_joint_is_named(self):
        class Outer(AssemblyNode):
            inner = DialArbor()

        class Original(AssemblyNode):
            time = Time.running()
            hand = Driver(default=0.0, unit='deg')
            body = Outer()
            controls = {'turn inner': Turn(body.inner, hand,
                                          coordinate=body.inner.turn)}

        class Empty(AssemblyNode):
            pass

        class WithoutJoint(Outer):
            inner = Empty()

        class Replaced(Original):
            body = WithoutJoint()
            controls = {**Original.controls}

        with self.assertRaisesRegex(ValueError, 'turn inner'):
            Sim(Replaced(), 0.1)


if __name__ == '__main__':
    import unittest
    unittest.main()
