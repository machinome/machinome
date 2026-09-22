# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Adversarial conformance checks for direct-part-motion."""

from machinome.motion.joints import Free, Prismatic, Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Button, Driver, Instruction, Sim, Slide, Turn
from machinome.simulation.program import ControlError, _published_span

from .base import BaseNodeTest
from .running_project.machine import Crank, SlideKnob
from .running_project.parts import Dial
from .test_running_document import bound, document


class TouchedSlide(AssemblyNode):
    travel = Prismatic(axis=(1, 0, 0))
    hand = Driver(0.0)
    knob = Dial()
    hand.drives(travel)
    controls = {'slide': Slide(knob, hand, coordinate=travel)}


class SiteSlide(AssemblyNode):
    time = Time.running()
    body = TouchedSlide(travel=Prismatic(axis=(0, 0, 1)))


class ChangedSlide(TouchedSlide):
    travel = Prismatic(axis=(0, 1, 0))


class SubclassSlide(AssemblyNode):
    time = Time.running()
    body = ChangedSlide()


class TouchedTurn(AssemblyNode):
    turn = Revolute(axis=(0, 0, 1))
    hand = Driver(0.0)
    knob = Dial()
    hand.drives(turn)
    controls = {'turn': Turn(knob, hand, coordinate=turn)}


class ChangedTurn(TouchedTurn):
    turn = Revolute(axis=(1, 0, 0), at=(0, 2, 3))


class SubclassTurn(AssemblyNode):
    time = Time.running()
    body = ChangedTurn()


class PathSlide(AssemblyNode):
    time = Time.running()
    hand = Driver(0.0)
    body = SlideKnob()
    hand.drives(body.travel)
    controls = {'slide': Slide(body.knob, hand, coordinate=body.travel)}


class ReplacedPathSlide(PathSlide):
    body = SlideKnob(travel=Prismatic(axis=(0, 0, 1)))


class WrongDomainSlide(AssemblyNode):
    time = Time.running()
    body = TouchedSlide(travel=Revolute(axis=(0, 0, 1)))


class ReplacedRelation(TouchedSlide):
    travel = Revolute(axis=(0, 0, 1))
    controls = {}


class RelationRoot(AssemblyNode):
    time = Time.running()
    body = ReplacedRelation()


class PressedBody(AssemblyNode):
    pose = Prismatic(axis=(1, 0, 0))
    hand = Driver(0.0)
    knob = Dial()
    instructions = {'press': Instruction(by={'hand': 1.0}, duration=0.1)}
    controls = {'press': Button(knob, 'press', coordinate=pose)}


class FreeReplacement(AssemblyNode):
    time = Time.running()
    seed = Driver(0.0)
    body = PressedBody(pose=Free())
    seed.drives(body.pose.x)
    seed.drives(body.pose.y)
    seed.drives(body.pose.z)
    seed.drives(body.pose.roll)
    seed.drives(body.pose.pitch)
    seed.drives(body.pose.yaw)


class EffectiveSelectionTest(BaseNodeTest):
    def test_an_inherited_relation_does_not_seed_stale_slot_metadata(self):
        sim = Sim(RelationRoot(), 0.1)
        self.assertEqual(sim.program.declared['body.travel'],
                         ('deg', 'rotational'))
        self.assertEqual(sim.node.body.travel.domain, 'rotational')

    def test_an_inherited_own_selection_uses_the_site_override(self):
        sim = Sim(SiteSlide(), 0.1)
        entry = sim.program.published_controls(dict(sim.initial.bank))['body.slide']
        self.assertEqual(entry['axis'], [0.0, 0.0, 1.0])
        self.assertEqual(entry['coordinate'], 'body.travel')
        sim.move('body.hand', by=3, duration=0.2)
        sim.run(0.2)
        self.assertEqual(sim.state['body.travel'], 3)

    def test_an_inherited_own_selection_uses_the_subclass_override(self):
        published = document(bound(SubclassSlide()))
        self.assertEqual(published['controls']['body.slide']['axis'], [0, 1, 0])

    def test_an_inherited_path_uses_the_effective_child_joint(self):
        published = document(bound(ReplacedPathSlide()))
        entry = published['controls']['slide']
        self.assertEqual(entry['axis'], [0, 0, 1])
        self.assertEqual(entry['coordinate'], 'body.travel')

    def test_an_overridden_pivot_controls_its_actual_placement(self):
        published = document(bound(SubclassTurn()))
        entry = published['controls']['body.turn']
        self.assertEqual(entry['axis'], [1, 0, 0])
        self.assertEqual(entry['origin'], [0, 2, 3])
        self.assertEqual(entry['operation_span'], [0, 3])
        body, = published['root']['children']
        self.assertEqual(body['operations'][:3], [
            ['t', ['-0.0', '-2.0', '-3.0']],
            ['r', 'body.turn', [1, 0, 0]],
            ['t', ['0.0', '2.0', '3.0']],
        ])

    def test_an_override_is_checked_for_the_effective_domain(self):
        with self.assertRaisesRegex(ControlError, 'rotational.*translational'):
            Sim(WrongDomainSlide(), 0.1)

    def test_an_override_does_not_unpack_a_free_joint(self):
        with self.assertRaisesRegex(ControlError, 'ONE coordinate'):
            Sim(FreeReplacement(), 0.1)

    def test_a_foreign_joint_with_the_same_name_is_still_refused(self):
        class Foreign(AssemblyNode):
            travel = Prismatic(axis=(0, 0, 1))

        with self.assertRaisesRegex(TypeError, 'does not declare'):
            class Invalid(AssemblyNode):
                time = Time.running()
                travel = Prismatic(axis=(1, 0, 0))
                hand = Driver(0.0)
                knob = Dial()
                hand.drives(travel)
                controls = {'slide': Slide(knob, hand, coordinate=Foreign.travel)}


class CompleteSelectedPlacementTest(BaseNodeTest):
    def span(self, sim):
        return _published_span(sim.node.crank, type(sim.node.crank).turn,
                               'rotate crank', Crank.controls['rotate crank'],
                               sim.program, 'crank.turn')

    def test_each_truncated_pivot_is_refused_even_if_contiguous(self):
        for missing in range(3):
            with self.subTest(missing=missing):
                sim = Sim(Crank(), 0.1)
                sim.node.crank.operations.pop(missing)
                with self.assertRaisesRegex(ControlError, 'complete'):
                    self.span(sim)

    def test_a_contiguous_reordered_pivot_is_refused(self):
        sim = Sim(Crank(), 0.1)
        ops = sim.node.crank.operations
        ops[0], ops[2] = ops[2], ops[0]
        with self.assertRaisesRegex(ControlError, 'complete'):
            self.span(sim)

    def test_a_contiguous_duplicated_pivot_operation_is_refused(self):
        sim = Sim(Crank(), 0.1)
        ops = sim.node.crank.operations
        ops.insert(1, ops[0])
        with self.assertRaisesRegex(ControlError, 'complete'):
            self.span(sim)

    def test_snapshot_replay_preserves_complete_blocks(self):
        sim = Sim(Crank(), 0.1)
        saved = sim.snapshot()
        sim.move('rotation', by=0.25, duration=0.5)
        sim.run(0.5)
        self.assertEqual(self.span(sim), (0, 3))
        sim.restore(saved)
        self.assertEqual(self.span(sim), (0, 3))
        sim.node.crank.save_checkpoint()
        sim.node.crank.translate([3, 4, 5])
        sim.node.crank.restore_checkpoint()
        self.assertEqual(self.span(sim), (0, 3))
