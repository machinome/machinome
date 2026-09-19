# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""`State`: a driver the machine writes.

A state takes exactly a driver's arguments with exactly their meanings,
reads off its node exactly as a driver's value does, and qualifies by
exactly a driver's rule. Everything that differs is about WHO WRITES IT,
and every refusal below is one of those.

The originating project is `projects/Calculators/Curta-Type-I-3x`, whose
two registers are the states this declaration exists for; the
requirement note is `workflow/docs/clocked-machine.md`.
"""

from unittest import TestCase

from machinome.node import AssemblyNode
from machinome.simulation import Driver, State
from machinome.simulation.enumeration import (bind_declared_defaults,
                                               declared_states,
                                               qualified_states)
from machinome.node.qualified import DriverIdError, declared_drivers_of

from .base import BaseNodeTest
from .clocked_project.counter import Counter, Stateless
from .clocked_project.parts import Dial


class Bank(AssemblyNode):
    """A class declaring one state and nothing else, for the id rule."""

    digit = State(default=0, range=(0, 9), dtype=int)

    face = Dial()

    digit.drives(face.turn, ratio=36.0)


class TwoBanks(AssemblyNode):
    """Two instances of one state-declaring class: the id rule is the
    driver's, so each carries its own."""

    left = Bank()
    right = Bank()


class StateDeclarationTest(TestCase):
    """Task 2.1: the declaration itself."""

    def test_state_carries_the_declarations_five_fields(self):
        declaration = State(default=3, range=(0, 9), unit='digit',
                            dtype=int, scale=2.0)
        self.assertEqual(declaration.default, 3)
        self.assertEqual(declaration.range, (0, 9))
        self.assertEqual(declaration.unit, 'digit')
        self.assertIs(declaration.dtype, int)
        self.assertEqual(declaration.scale, 2.0)

    def test_a_state_reads_off_the_class_as_the_declaration(self):
        self.assertIsInstance(Counter.units, State)
        self.assertEqual(Counter.units.default, 0)
        self.assertEqual(Counter.tens.range, (0, 9))

    def test_an_integer_state_refuses_a_float_default(self):
        with self.assertRaises(TypeError) as caught:
            State(default=0.5, dtype=int)
        self.assertIn('whole native units', str(caught.exception))

    def test_declared_states_are_not_declared_drivers(self):
        """The two tables are separate: a state is not published in the
        driver table, and a driver is not in the state table."""
        self.assertEqual(sorted(declared_drivers_of(Counter)), ['crank'])
        self.assertEqual(sorted(declared_states(Counter)),
                         ['tens', 'units'])
        self.assertEqual(sorted(declared_states(Stateless)), [])

    def test_a_state_is_read_as_an_attribute_of_its_node(self):
        """The build path binds a declared state exactly as it binds a
        declared driver default, and the pose follows it."""
        node = Counter()
        bind_declared_defaults(node)
        self.assertEqual(node.units, 0)
        self.assertEqual(node.tens, 0)
        self.assertEqual(node.units_dial.turn.value, 0.0)

    def test_the_pose_follows_the_state(self):
        node = Counter()
        bind_declared_defaults(node)
        node._states['units'] = 4
        node.render()
        self.assertEqual(node.units_dial.turn.value, 4 * 36.0)


class StateEnumerationTest(BaseNodeTest):
    """Task 2.3: states enumerate qualified, in the driver's walk."""

    def test_two_children_of_one_class_enumerate_qualified(self):
        found = qualified_states(TwoBanks())
        self.assertEqual(sorted(found), ['left.digit', 'right.digit'])
        for declaration in found.values():
            self.assertEqual(declaration.range, (0, 9))
            self.assertIs(declaration.dtype, int)

    def test_a_root_declared_state_keeps_its_bare_name(self):
        self.assertEqual(sorted(qualified_states(Counter())),
                         ['tens', 'units'])

    def test_a_stateless_tree_enumerates_no_state(self):
        self.assertEqual(qualified_states(Stateless()), {})

    def test_a_driver_and_a_state_claiming_one_id_are_refused(self):
        """A subclass redeclaring an inherited DRIVER as a STATE is the
        one reachable way two declarations claim one id: both tables
        keep their own, and the walk refuses naming the id and both."""
        class Base(AssemblyNode):
            crank = Driver(default=0)
            face = Dial()

            crank.drives(face.turn, ratio=1.0)

        class Clash(Base):
            crank = State(default=0)

        with self.assertRaises(DriverIdError) as caught:
            qualified_states(Clash())
        message = str(caught.exception)
        self.assertIn('crank', message)
        self.assertIn('State', message)
        self.assertIn('Driver', message)
