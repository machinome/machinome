# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Everything a state and a committing relation refuse, and where.

Each refusal is raised where its FACTS are. The classes are all known in
a class body, so a target that is not a state, a port named as a source
and a missing factory are refused at the line that wrote them; the tree
is known at simulation construction, so a state two relations of two
classes write and a state nothing writes are refused there; and the
root's time base is known where the declared defaults are bound.

Tasks 2.5 and 3.3 of the change `declare-the-state`. The construction
refusals of task 4 and task 6 are in `test_clocked_sim.py`, beside the
simulation that makes them.
"""

from unittest import TestCase

from solid_node.motion.joints import Revolute
from solid_node.motion.ports import RotationalPort, Time
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, State, Turn
from solid_node.simulation.enumeration import bind_declared_defaults

from .clocked_project.counter import Counter, advance, strokes
from .clocked_project.parts import Dial


def one(sources, targets):
    return lambda *values: values[0]


class WriterRefusalTest(TestCase):
    """Task 2.5: who may write a state, and who may not."""

    def test_set_state_refuses_a_state_by_name(self):
        node = Counter()
        bind_declared_defaults(node)
        with self.assertRaises(ValueError) as caught:
            node.set_state(units=3)
        message = str(caught.exception)
        self.assertIn('units', message)
        self.assertIn('State', message)
        self.assertIn('commits', message)
        # Nothing was bound: the state stands where it stood.
        self.assertEqual(node.units, 0)

    def test_set_state_still_binds_the_driver_beside_it(self):
        node = Counter()
        bind_declared_defaults(node)
        node.set_state(crank=90.0)
        self.assertEqual(node.crank, 90.0)

    def test_a_state_is_not_a_driven_end(self):
        with self.assertRaises(TypeError) as caught:
            class Driven(AssemblyNode):
                crank = Driver(default=0)
                units = State(default=0)

                crank.drives(units)
        message = str(caught.exception)
        self.assertIn('units', message)
        self.assertIn('committing relation', message)

    def test_a_state_may_be_a_source_of_drives(self):
        class Posed(AssemblyNode):
            units = State(default=0)
            face = Dial()

            units.drives(face.turn, ratio=2.0)

        self.assertEqual(len(Posed._declared_relations), 1)

    def test_a_turn_refuses_a_state_as_its_input(self):
        with self.assertRaises(TypeError) as caught:
            class Dragged(AssemblyNode):
                units = State(default=0)
                face = Dial()

                controls = {'set units': Turn(face, units)}
        message = str(caught.exception)
        self.assertIn('State', message)
        self.assertIn('committing relation', message)

    def test_two_relations_of_one_body_may_write_one_state(self):
        """Closure 1, C2: a state written at two different events has two
        writers, and a class body cannot see a landing, so it refuses
        nothing here. The one-event conflict is the request's judgement
        (`test_clocked_register.py`)."""
        class Twice(AssemblyNode):
            crank = Driver(default=0)
            ring = Driver(default=0)
            units = State(default=0)

            (crank & units).commits(units, at=strokes, law=one)
            (ring & units).commits(units, at=strokes, law=one)

        self.assertEqual(len(Twice._declared_commitments), 2)

    def test_two_children_of_one_class_are_two_targets(self):
        """Closure 1, C1: `a.digit` and `b.digit` are told apart by their
        PATHS. Keyed on the local name they share, one relation writing a
        register of identical wheels was refused as its own duplicate."""
        class Wheel(AssemblyNode):
            digit = State(default=0)
            face = Dial()

            digit.drives(face.turn, ratio=1.0)

        class Pair(AssemblyNode):
            crank = Driver(default=0)
            a = Wheel()
            b = Wheel()

            (crank & a.digit & b.digit).commits(
                (a.digit, b.digit), at=strokes, law=one)

        commitment, = Pair._declared_commitments
        self.assertEqual(
            [ref.described() for ref in commitment.target_refs()],
            ['a.digit', 'b.digit'])

    def test_one_relation_naming_one_target_twice_is_refused_by_path(self):
        class Wheel(AssemblyNode):
            digit = State(default=0)
            face = Dial()

            digit.drives(face.turn, ratio=1.0)

        with self.assertRaises(TypeError) as caught:
            class Doubled(AssemblyNode):
                crank = Driver(default=0)
                a = Wheel()

                (crank & a.digit).commits((a.digit, a.digit), at=strokes,
                                          law=one)
        message = str(caught.exception)
        self.assertIn('a.digit', message)
        self.assertIn('named twice', message)

    def test_a_state_under_a_looping_base_is_refused(self):
        class Looping(AssemblyNode):
            time = Time(loop=4.0)
            crank = Driver(default=0)
            units = State(default=0)
            face = Dial()

            (crank & units).commits(units, at=strokes, law=one)
            units.drives(face.turn, ratio=1.0)

        with self.assertRaises(TypeError) as caught:
            bind_declared_defaults(Looping())
        message = str(caught.exception)
        self.assertIn('units', message)
        self.assertIn('loop', message)

    def test_a_state_under_a_running_base_is_refused_with_its_meaning(self):
        class Running(AssemblyNode):
            time = Time.running()
            crank = Driver(default=0)
            units = State(default=0)
            face = Dial()

            (crank & units).commits(units, at=strokes, law=one)
            units.drives(face.turn, ratio=1.0)

        with self.assertRaises(TypeError) as caught:
            bind_declared_defaults(Running())
        message = str(caught.exception)
        self.assertIn('units', message)
        self.assertIn('Time.running()', message)
        self.assertIn('NOT implemented', message)


class CommitDeclarationRefusalTest(TestCase):
    """Task 3.3: what a class body decides about a committing relation."""

    def test_a_target_that_is_not_a_state_is_refused(self):
        with self.assertRaises(TypeError) as caught:
            class Posed(AssemblyNode):
                crank = Driver(default=0)
                units = State(default=0)
                face = Dial()

                (crank & units).commits(face.turn, at=strokes, law=one)
        message = str(caught.exception)
        self.assertIn('face.turn', message)
        self.assertIn('State', message)

    def test_a_target_named_twice_is_refused(self):
        with self.assertRaises(TypeError) as caught:
            class Doubled(AssemblyNode):
                crank = Driver(default=0)
                units = State(default=0)

                (crank & units).commits((units, units), at=strokes, law=one)
        self.assertIn('named twice', str(caught.exception))

    def test_a_port_source_is_refused(self):
        with self.assertRaises(TypeError) as caught:
            class Ported(AssemblyNode):
                readout = RotationalPort(unit='deg')
                crank = Driver(default=0)
                units = State(default=0)

                (crank & readout).commits(units, at=strokes, law=one)
        message = str(caught.exception)
        self.assertIn('readout', message)
        self.assertIn('drivers and states', message)

    def test_a_joint_coordinate_source_is_refused(self):
        with self.assertRaises(TypeError) as caught:
            class Jointed(AssemblyNode):
                spin = Revolute(axis=(0, 0, 1), unit='deg')
                crank = Driver(default=0)
                units = State(default=0)

                (crank & spin).commits(units, at=strokes, law=one)
        message = str(caught.exception)
        self.assertIn('spin', message)
        self.assertIn('drivers and states', message)

    def test_a_commits_with_no_at_is_refused(self):
        with self.assertRaises(TypeError) as caught:
            class NoEvent(AssemblyNode):
                crank = Driver(default=0)
                units = State(default=0)

                (crank & units).commits(units, law=one)
        message = str(caught.exception)
        self.assertIn('at', message)
        self.assertIn('event is required', message)

    def test_a_commits_with_no_law_is_refused(self):
        with self.assertRaises(TypeError) as caught:
            class NoLaw(AssemblyNode):
                crank = Driver(default=0)
                units = State(default=0)

                (crank & units).commits(units, at=strokes)
        self.assertIn('law', str(caught.exception))

    def test_a_ratio_with_commits_is_refused(self):
        with self.assertRaises(TypeError) as caught:
            class Affinely(AssemblyNode):
                crank = Driver(default=0)
                units = State(default=0)

                (crank & units).commits(units, at=strokes, law=one, ratio=2.0)
        message = str(caught.exception)
        self.assertIn('ratio=', message)
        self.assertIn('no affine default', message)

    def test_a_broadcast_commits_is_refused(self):
        class Bank(AssemblyNode):
            digit = State(default=0)
            face = Dial()

            digit.drives(face.turn, ratio=1.0)

        with self.assertRaises(TypeError) as caught:
            class Row(AssemblyNode):
                crank = Driver(default=0)
                banks = Bank().repeat(3)

                (crank & banks.digit).commits(banks.digit, at=strokes,
                                              law=one)
        self.assertIn('repeat', str(caught.exception))

    def test_a_commits_outside_a_class_body_is_refused(self):
        with self.assertRaises(TypeError) as caught:
            Counter.crank.commits(Counter.units, at=strokes, law=advance)
        self.assertIn('class body', str(caught.exception))

    def test_a_commits_on_a_leaf_is_refused(self):
        from solid_node.node import Solid2Node

        with self.assertRaises(TypeError) as caught:
            class Leafy(Solid2Node):
                crank = Driver(default=0)
                units = State(default=0)

                (crank & units).commits(units, at=strokes, law=one)

                def render(self):
                    return None
        self.assertIn('not an assembly', str(caught.exception))
