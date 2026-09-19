# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Controls: which part a person presses, and which part a person turns.

OpenSpec change ``declare-controls-on-parts``. An assembly declares
``controls`` beside ``instructions``; ``Button(part, instruction)`` is a
press and ``Turn(part, input)`` is a drag. The framework finds the
gesture's coordinate by walking up from the part to the nearest ancestor
whose joint the run banks, derives the ratio from the compiled program at
rest, and refuses everything it cannot resolve -- at class definition
where the classes are known, at compile where the program is.

Nothing here moves anything: a control names a request ``trigger``,
``move`` and ``rate`` already accept, and the run, the bank and the
program's identity are exactly what they were.
"""

import hashlib
import math

from machinome.math import sin
from machinome.motion.joints import Free, Prismatic, Revolute
from machinome.motion.ports import RotationalPort, Time
from machinome.node import AssemblyNode
from machinome.node.qualified import instance_path
from machinome.simulation import (Button, Driver, Instruction, Sim,
                                   Slide, Turn)
from machinome.simulation.enumeration import (qualified_controls,
                                               qualified_declarations,
                                               qualified_instructions)

from .base import BaseNodeTest
from .running_project.machine import (AmbiguousCrank, Column, ColumnStack,
                                      Columns, ColumnsBare, Crank, CrankBare,
                                      CrankBody, DeepColumn, DerivedSelected,
                                      DialArbor, FreePosed, FreeSelected,
                                      Gate, GateTouched, KinkedControl,
                                      LoopingControls, NotRunning, OffCentre,
                                      OmittedControl, Register, Selector,
                                      Sideways, SiteTurned, SlideKnob, Sliding,
                                      SlidingTurn, SmoothControl, Stepping,
                                      TwoJoints, Unmoved, Unnamed, Unposed,
                                      Unreached, carried_column)
from .running_project.parts import Block, Dial


def controls_of(program):
    """The compiled controls of `program`, by qualified name."""
    return {control.name: control for control in program.controls}


class DeclarationTest(BaseNodeTest):
    """(2.1) A control is declared beside the instructions and found."""

    def test_a_running_root_with_controls_constructs(self):
        sim = Sim(Columns(), 0.1)
        self.assertTrue(sim.running)
        self.assertEqual(sorted(sim.instructions), ['Add one', 'Add ten'])

    def test_the_trees_qualified_controls_are_the_four_declared(self):
        self.assertEqual(sorted(qualified_controls(Columns())),
                         ['tens dial', 'turn tens', 'turn units',
                          'units dial'])

    def test_one_walk_returns_both_tables(self):
        # THREE tables since the clocked discipline (OpenSpec change
        # ``declare-the-state``): the declared states come from the same
        # pass rather than an additional one, and are empty for a model
        # that declares none.
        instructions, controls, states = qualified_declarations(Columns())
        self.assertEqual(sorted(instructions), ['Add one', 'Add ten'])
        self.assertEqual(sorted(controls),
                         ['tens dial', 'turn tens', 'turn units',
                          'units dial'])
        self.assertEqual(states, {})

    def test_qualified_instructions_keeps_its_shape(self):
        node = Columns()
        found = qualified_instructions(node)
        self.assertEqual(sorted(found), ['Add one', 'Add ten'])
        declaring, path, instruction = found['Add one']
        self.assertIs(declaring, node)
        self.assertEqual(path, ())
        self.assertEqual(instruction.by, {'units_entry': 1.0})

    def test_each_compiled_control_names_its_part_and_its_gesture(self):
        compiled = controls_of(Sim(Columns(), 0.1).program)
        self.assertEqual(sorted(compiled),
                         ['tens dial', 'turn tens', 'turn units',
                          'units dial'])
        for name, part, coordinate, joint in (
                ('units dial', ('units', 'dial'), 'units.turn', ('units',)),
                ('turn units', ('units', 'dial'), 'units.turn', ('units',)),
                ('tens dial', ('tens', 'dial'), 'tens.turn', ('tens',)),
                ('turn tens', ('tens', 'dial'), 'tens.turn', ('tens',))):
            with self.subTest(control=name):
                entry = compiled[name]
                self.assertEqual(entry.part, part)
                self.assertEqual(entry.coordinate, coordinate)
                self.assertEqual(entry.joint, joint)
                self.assertEqual(entry.axis, (1, 0, 0))
                self.assertEqual(entry.origin, (0.0, 0.0, 0.0))

    def test_a_button_names_a_declared_instruction(self):
        sim = Sim(Columns(), 0.1)
        compiled = controls_of(sim.program)
        self.assertEqual(compiled['units dial'].kind, 'button')
        self.assertEqual(compiled['units dial'].instruction, 'Add one')
        self.assertEqual(compiled['tens dial'].instruction, 'Add ten')
        for name in ('units dial', 'tens dial'):
            self.assertIn(compiled[name].instruction, sim.instructions)

    def test_a_turn_names_the_input_the_author_declared(self):
        compiled = controls_of(Sim(Columns(), 0.1).program)
        self.assertEqual(compiled['turn units'].kind, 'turn')
        self.assertEqual(compiled['turn units'].input, 'units_entry')
        self.assertEqual(compiled['turn tens'].input, 'tens_entry')

    def test_a_dial_two_inputs_reach_is_bound_to_the_one_named(self):
        """`tens.turn` is reached by BOTH inputs; the author said which
        one a hand on the tens dial means."""
        program = Sim(Columns(), 0.1).program
        reaching = {program.nodes[key].name: sorted(names)
                    for key, names in program.sources.items()}
        self.assertEqual(reaching['tens.turn'],
                         ['tens_entry', 'units_entry'])
        self.assertEqual(reaching['units.turn'], ['units_entry'])
        self.assertEqual(controls_of(program)['turn tens'].input, 'tens_entry')

    def test_a_control_carries_no_state_and_moves_nothing(self):
        sim = Sim(Columns(), 0.1)
        before = dict(sim.state)
        sim.run(1.0)
        self.assertEqual(dict(sim.state), before)


class QualificationTest(BaseNodeTest):
    """(2.2) A control on a child qualifies through its path."""

    def test_a_childs_control_takes_the_childs_path(self):
        sim = Sim(ColumnStack(), 0.1)
        compiled = controls_of(sim.program)
        self.assertEqual(sorted(compiled), ['column.dial', 'column.turn'])
        self.assertEqual(compiled['column.dial'].part,
                         ('column', 'arbor', 'dial'))

    def test_the_instruction_reference_qualifies_through_the_same_path(self):
        sim = Sim(ColumnStack(), 0.1)
        compiled = controls_of(sim.program)
        self.assertEqual(compiled['column.dial'].instruction, 'column.Add one')
        self.assertIn('column.Add one', sim.instructions)

    def test_the_input_qualifies_through_the_same_path(self):
        sim = Sim(ColumnStack(), 0.1)
        compiled = controls_of(sim.program)
        self.assertEqual(compiled['column.turn'].input, 'column.entry')
        self.assertIn('column.entry', sim.state)


class NearestJointTest(BaseNodeTest):
    """(2.3) The nearest ancestor-or-self the run poses owns the
    coordinate."""

    def test_the_arbor_wins_over_the_root_and_the_dial(self):
        compiled = controls_of(Sim(Columns(), 0.1).program)
        entry = compiled['turn units']
        self.assertEqual(entry.joint, ('units',))
        self.assertNotEqual(entry.joint, ())
        self.assertNotEqual(entry.joint, ('units', 'dial'))

    def test_the_walk_passes_through_an_assembly_declaring_nothing(self):
        node = DeepColumn()
        sim = Sim(node, 0.1)
        compiled = controls_of(sim.program)
        entry = compiled['turn deep']
        self.assertEqual(entry.part, ('deep', 'holder', 'dial'))
        self.assertEqual(entry.joint, ('deep',))
        self.assertEqual(entry.coordinate, 'deep.turn')
        # The intermediate really is in the tree, and really declares
        # no joint of its own.
        from machinome.motion.joints import declared_joints
        holder = node.deep.holder
        self.assertEqual(instance_path(holder, node), ('deep', 'holder'))
        self.assertEqual(declared_joints(type(holder)), {})


class RefusalTest(BaseNodeTest):
    """(2.4) Every refusal the `simulation` delta states, with the facts
    the spec says it carries."""

    def test_a_controls_attribute_that_is_not_a_table_is_refused(self):
        with self.assertRaises(TypeError) as raised:
            class Mistyped(AssemblyNode):
                time = Time.running()
                units = DialArbor()
                controls = {'speed': 3}

        message = str(raised.exception)
        self.assertIn('speed', message)
        self.assertIn('controls', message)

    def test_a_controls_attribute_that_is_not_a_mapping_is_refused(self):
        with self.assertRaises(TypeError) as raised:
            class Listed(AssemblyNode):
                time = Time.running()
                units = DialArbor()
                controls = ['units']

        message = str(raised.exception)
        self.assertIn('controls', message)
        self.assertIn('Listed', message)

    def test_a_part_that_is_not_a_node_is_refused_where_it_is_written(self):
        with self.assertRaises(TypeError) as raised:
            Button(3.0, 'Add one')
        self.assertIn('3.0', str(raised.exception))

    def test_a_coordinate_is_not_a_part(self):
        with self.assertRaises(TypeError) as raised:
            class Jointed(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='digit')
                units = DialArbor()
                entry.drives(units.turn, ratio=-36.0)
                controls = {'turn units': Turn(units.turn, entry)}

        message = str(raised.exception)
        self.assertIn('PART', message)
        self.assertIn('coordinate', message)

    def test_a_joint_of_the_declaring_class_is_not_a_part(self):
        with self.assertRaises(TypeError) as raised:
            class OwnJoint(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='digit')
                spindle = Revolute(axis=(0, 0, 1), unit='deg')
                entry.drives(spindle, ratio=1.0)
                controls = {'turn spindle': Turn(spindle, entry)}

        self.assertIn('PART', str(raised.exception))

    def test_a_driver_is_not_a_part(self):
        with self.assertRaises(TypeError) as raised:
            class DriverPart(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='digit')
                units = DialArbor()
                entry.drives(units.turn, ratio=-36.0)
                controls = {'turn entry': Turn(entry, entry)}

        self.assertIn('PART', str(raised.exception))

    def test_a_repeated_child_names_one_part_per_copy(self):
        with self.assertRaises(TypeError) as raised:
            class Repeated(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='digit')
                bank = DialArbor().repeat(3)
                entry.drives(bank.turn, ratio=-36.0)
                controls = {'press bank': Button(bank, 'Add one')}

        message = str(raised.exception)
        self.assertIn('repeat', message.lower())

    def test_a_list_held_child_is_refused_naming_the_list(self):
        with self.assertRaises(TypeError) as raised:
            class Listed(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='digit')
                bank = [DialArbor(), DialArbor()]
                controls = {'press bank': Button(bank[0], 'Add one')}

        message = str(raised.exception)
        self.assertIn('press bank', message)
        self.assertIn('LIST', message)
        self.assertIn('DialArbor', message)

    def test_a_whole_list_of_children_is_refused(self):
        with self.assertRaises(TypeError) as raised:
            class WholeList(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='digit')
                bank = [DialArbor(), DialArbor()]
                controls = {'press bank': Button(bank, 'Add one')}

        message = str(raised.exception)
        self.assertIn('ONE part', message)
        self.assertIn('2 children', message)

    def test_a_misspelt_part_is_refused_where_it_is_written(self):
        from machinome.node.declarative import SidewaysReadError

        with self.assertRaises(SidewaysReadError) as raised:
            class Misspelt(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='digit')
                units = DialArbor()
                entry.drives(units.turn, ratio=-36.0)
                controls = {'units dial': Button(units.dail, 'Add one')}

        message = str(raised.exception)
        self.assertIn('units.dail', message)
        self.assertIn('DialArbor', message)

    def test_a_part_of_another_class_is_refused_at_class_definition(self):
        class Elsewhere(AssemblyNode):
            other = DialArbor()

        with self.assertRaises(TypeError) as raised:
            class Borrower(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='digit')
                units = DialArbor()
                entry.drives(units.turn, ratio=-36.0)
                controls = {'units dial': Button(Elsewhere.other.dial,
                                                 'Add one')}

        message = str(raised.exception)
        self.assertIn('Borrower', message)
        self.assertIn('units dial', message)
        self.assertIn('other', message)

    def test_an_input_of_another_class_is_refused(self):
        class Elsewhere(AssemblyNode):
            other_entry = Driver(default=0.0, unit='digit')

        with self.assertRaises(TypeError) as raised:
            class Foreign(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='digit')
                units = DialArbor()
                entry.drives(units.turn, ratio=-36.0)
                controls = {'turn units': Turn(units.dial,
                                               Elsewhere.other_entry)}

        message = str(raised.exception)
        self.assertIn('Foreign', message)
        self.assertIn('entry', message)

    def test_an_input_named_by_a_string_is_refused(self):
        with self.assertRaises(TypeError) as raised:
            class Stringly(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='digit')
                units = DialArbor()
                entry.drives(units.turn, ratio=-36.0)
                controls = {'turn units': Turn(units.dial, 'entry')}

        self.assertIn('DECLARATION', str(raised.exception))

    def test_a_button_naming_no_declared_instruction_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Sim(Unnamed(), 0.1)
        message = str(raised.exception)
        self.assertIn('Add two', message)
        self.assertIn('Add one', message)
        self.assertIn('units dial', message)

    def test_a_part_nothing_run_owned_moves_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Sim(Unposed(), 0.1)
        message = str(raised.exception)
        self.assertIn('frame', message)
        self.assertIn('press frame', message)
        self.assertIn('nothing the run owns', message)

    def test_a_turn_on_a_coordinate_that_does_not_turn_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Sim(Sliding(), 0.1)
        message = str(raised.exception)
        self.assertIn('carriage.travel', message)
        self.assertIn('translational', message)
        self.assertIn('rotational', message)

    def test_a_turn_whose_input_does_not_reach_the_part_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Sim(Unreached(), 0.1)
        message = str(raised.exception)
        self.assertIn('units.turn', message)
        self.assertIn('tens_entry', message)
        self.assertIn('units_entry', message)

    def test_a_node_declaring_two_joints_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Sim(TwoJoints(), 0.1)
        message = str(raised.exception)
        self.assertIn('swing', message)
        self.assertIn('lift', message)
        self.assertIn('ONE coordinate', message)

    def test_a_joint_owning_several_coordinates_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Sim(FreePosed(), 0.1)
        message = str(raised.exception)
        self.assertIn('pose', message)
        self.assertIn('yaw', message)
        self.assertIn('ONE coordinate', message)

    def test_a_control_without_a_running_root_is_refused_at_construction(self):
        for factory in (NotRunning, LoopingControls):
            with self.subTest(root=factory.__name__):
                with self.assertRaises(TypeError) as raised:
                    Sim(factory(), 0.1)
                message = str(raised.exception)
                self.assertIn(factory.__name__, message)
                self.assertIn('units dial', message)
                self.assertIn('Time.running()', message)


class IdentityTest(BaseNodeTest):
    """(2.5) A control changes nothing the run computes."""

    def programs(self):
        return Sim(Columns(), 0.1)._run, Sim(ColumnsBare(), 0.1)._run

    def test_the_bank_the_edges_and_the_sources_are_the_same(self):
        controlled, bare = self.programs()
        self.assertEqual(controlled.bank, bare.bank)
        self.assertEqual(
            [program.nodes[key].name
             for program in (controlled.program,) for key in program.nodes],
            [program.nodes[key].name
             for program in (bare.program,) for key in program.nodes])
        self.assertEqual(controlled.program.described().split('\n')[1:],
                         bare.program.described().split('\n')[1:])
        self.assertEqual(
            {controlled.program.nodes[key].name: sorted(names)
             for key, names in controlled.program.sources.items()},
            {bare.program.nodes[key].name: sorted(names)
             for key, names in bare.program.sources.items()})

    def test_described_mentions_no_control(self):
        described = Sim(Columns(), 0.1).program.described()
        for name in ('units dial', 'tens dial', 'turn units', 'turn tens',
                     'control'):
            self.assertNotIn(name, described)

    def test_the_identity_is_the_control_free_twins(self):
        """`described()`'s first line names the ROOT CLASS, so a twin
        under another name necessarily hashes differently; align that
        one line and the digests are equal."""
        controlled, bare = self.programs()
        lines = bare.program.described().split('\n')
        lines[0] = controlled.program.described().split('\n')[0]
        aligned = hashlib.sha256('\n'.join(lines).encode()).hexdigest()
        self.assertEqual(aligned, controlled.program.identity)

    def test_the_two_step_identically(self):
        controlled = Sim(Columns(), 0.1)
        bare = Sim(ColumnsBare(), 0.1)
        for sim in (controlled, bare):
            sim.move('units_entry', by=3.0, duration=0.5)
            sim.run(0.5)
            sim.move('tens_entry', by=-2.0, duration=0.3)
            sim.run(0.5)
        self.assertEqual(dict(controlled.state), dict(bare.state))


class ProgramArithmeticTest(BaseNodeTest):
    """(4.1, 4.2) The measurement and the tick share one implementation.

    `_values` and `_deltas` move off `Run` and onto `Program`, so "the
    bank plus the intermediates" and "one input's displacement" have one
    implementation rather than two to keep in step; `response` is that
    arithmetic with one input displaced and no command, no stop, no
    staging and no record. The cases below are what keeps the two call
    sites honest now that there are two.
    """

    machines = ('Train', 'Carry', 'Columns')

    def factory(self, name):
        from .running_project import machine

        return getattr(machine, name)

    def test_values_of_is_the_runs_own(self):
        for name in self.machines:
            with self.subTest(machine=name):
                sim = Sim(self.factory(name)(), 0.1)
                run = sim._run
                rest = dict(run.bank)
                self.assertEqual(run._values(rest),
                                 run.program.values_of(rest))
                moved = {identifier: value + 3.0
                         for identifier, value in rest.items()}
                self.assertEqual(run._values(moved),
                                 run.program.values_of(moved))

    def test_deltas_of_is_the_runs_own(self):
        for name in self.machines:
            with self.subTest(machine=name):
                sim = Sim(self.factory(name)(), 0.1)
                run = sim._run
                for admissions in ({}, {run.program.inputs[0][0]: 0.5}):
                    self.assertEqual(run._deltas(admissions),
                                     run.program.deltas_of(admissions))

    def test_response_reproduces_the_run_bit_for_bit(self):
        eps = 2.0 ** -20
        for name in ('Columns', 'Carry', 'CarryLead', 'Ranged'):
            factory = self.factory(name)
            reference = Sim(factory(), 0.1)
            rest = dict(reference._run.bank)
            program = reference.program
            for input_id, _declaration in program.inputs:
                for displacement in (eps, -eps):
                    with self.subTest(machine=name, input=input_id,
                                      eps=displacement):
                        measured = program.response(rest, input_id,
                                                    displacement)
                        fresh = Sim(factory(), 0.1)
                        fresh.move(input_id, by=displacement, duration=0)
                        for identifier in sorted(rest):
                            self.assertEqual(
                                measured[identifier],
                                fresh.state[identifier] - rest[identifier],
                                identifier)

    def test_response_seeds_the_banks_own_units(self):
        """The bank of a SCALED or INTEGER driver is native, so
        `response` seeds a native displacement: converted through
        `Driver.native`, exactly as `move` converts a design-unit
        travel, the two agree for that driver too."""
        from .running_project.machine import Stepping

        reference = Sim(Stepping(), 0.1)
        rest = dict(reference._run.bank)
        declaration = dict(reference.program.inputs)['feed']
        for by in (0.0125, -0.0125, 0.025):
            with self.subTest(by=by):
                measured = reference.program.response(
                    rest, 'feed', declaration.native(by))
                fresh = Sim(Stepping(), 0.1)
                fresh.move('feed', by=by, duration=0)
                for identifier in sorted(rest):
                    self.assertEqual(
                        measured[identifier],
                        fresh.state[identifier] - rest[identifier],
                        identifier)

    def test_response_holds_every_other_input_at_zero(self):
        program = Sim(Columns(), 0.1).program
        rest = dict(Sim(Columns(), 0.1)._run.bank)
        forward = program.response(rest, 'tens_entry', 2.0 ** -20)
        self.assertEqual(forward['units.turn'], 0.0)
        self.assertEqual(forward['units_entry'], 0.0)
        self.assertEqual(forward['tens_entry'], 2.0 ** -20)


class GestureGeometryTest(BaseNodeTest):
    """(5.2, 5.3) The gesture's geometry is what `Joint.place` used.

    Asserted against `joint.axes(node)` and `joint.carried_points(...)`
    rather than against the published operations, so the entry cannot
    drift from the placement it describes.
    """

    def placed(self, node, joint):
        """The axis and the anchor `Joint.place` built the placement
        from, carried exactly as `place` carries them."""
        anchor = joint.arguments(node)[1]
        axes = joint.axes(node)
        points = joint.carried_points(node, anchor)
        if joint._declared_at_site:
            axes, points = joint._carry(node, axes, points)
        return tuple(axes[0]), tuple(points[0])

    def test_a_centred_joint_turns_about_its_own_origin(self):
        node = Columns()
        compiled = controls_of(Sim(node, 0.1).program)
        for name, child in (('turn units', 'units'), ('turn tens', 'tens')):
            with self.subTest(control=name):
                arbor = getattr(node, child)
                axis, origin = self.placed(arbor, type(arbor).turn)
                self.assertEqual(compiled[name].axis, axis)
                self.assertEqual(compiled[name].origin, origin)
                self.assertEqual(compiled[name].origin, (0.0, 0.0, 0.0))

    def test_an_off_centre_joint_publishes_the_point_it_turns_about(self):
        node = OffCentre()
        compiled = controls_of(Sim(node, 0.1).program)
        axis, origin = self.placed(node.units, type(node.units).turn)
        for name in ('units dial', 'turn units'):
            with self.subTest(control=name):
                self.assertEqual(compiled[name].axis, axis)
                self.assertEqual(compiled[name].origin, origin)
                self.assertEqual(compiled[name].axis, (1, 0, 0))
                self.assertEqual(compiled[name].origin, (0.0, 3.0, 0.0))

    def test_a_site_declared_joint_publishes_the_carried_values(self):
        """The site wrote `axis=(0, 0, 1), at=(0, 6, 0)` in the PARENT's
        frame; `place` carries both into the child's own before it
        builds the placement, and the entry carries what `place` used.
        """
        node = SiteTurned()
        compiled = controls_of(Sim(node, 0.1).program)
        joint = type(node.holder).turn
        self.assertTrue(joint._declared_at_site)
        axis, origin = self.placed(node.holder, joint)
        entry = compiled['turn holder']
        self.assertEqual(entry.axis, axis)
        self.assertEqual(entry.origin, origin)
        # And they are NOT what the site wrote: the carry is real.
        self.assertNotEqual(entry.axis, (0, 0, 1))
        self.assertNotEqual(entry.origin, (0.0, 6.0, 0.0))
        self.assertEqual(entry.joint, ('holder',))
        self.assertEqual(entry.part, ('holder', 'dial'))


class RatioTest(BaseNodeTest):
    """(6.1-6.4) `per_unit` is measured off the compiled program, at
    rest, in both directions.

    The author would only be restating a relation the program already
    holds, and a number stated twice is a number that drifts. `response`
    seeds its displacement in the BANK's own units -- native for a
    driver that declares a scale or an integer dtype -- and the entry
    publishes coordinate units per DESIGN unit, which is the one
    conversion `Driver.native` already owns.
    """

    def table(self, factory):
        sim = Sim(factory(), 0.1)
        return sim.program.published_controls(dict(sim.initial.bank))

    def test_the_ratio_is_the_exact_affine_factor(self):
        table = self.table(Columns)
        self.assertEqual(table['turn units']['per_unit'], -36.0)
        self.assertEqual(table['turn tens']['per_unit'], 36.0)

    def test_a_button_publishes_no_ratio(self):
        table = self.table(Columns)
        self.assertNotIn('per_unit', table['units dial'])
        self.assertNotIn('input', table['units dial'])

    def test_an_integer_input_measures_over_one_native_unit(self):
        """`Driver.native` rounds a design-unit displacement to whole
        native units ONCE, so anything below half a step is no step at
        all: the measurement displaces by one native unit and divides by
        what that unit is worth in design units."""
        sim = Sim(Stepping(), 0.1)
        rest = dict(sim.initial.bank)
        # The naive displacement moves the part not at all -- which is
        # what the raised one exists to avoid.
        fresh = Sim(Stepping(), 0.1)
        fresh.move('feed', by=2.0 ** -20, duration=0)
        self.assertEqual(fresh.state['units.turn'], rest['units.turn'])
        table = sim.program.published_controls(rest)
        # One native unit is 0.0125 mm and turns the dial -36 degrees.
        self.assertEqual(table['turn units']['per_unit'], -36.0 / 0.0125)
        self.assertEqual(table['turn units']['per_unit'], -2880.0)

    def test_zero_at_rest_is_refused(self):
        """`units_entry` genuinely REACHES `tens.turn` -- the carry
        couples them -- and moves it by nothing where the cam sits
        between its ramps. Reaching is necessary and not sufficient, and
        this is what catches the difference."""
        sim = Sim(Unmoved(), 0.1)
        rest = dict(sim.initial.bank)
        program = sim.program
        reaching = program.sources[program.keys['tens.turn']]
        self.assertIn('units_entry', reaching)
        for eps in (2.0 ** -20, -2.0 ** -20):
            self.assertEqual(program.response(rest, 'units_entry',
                                              eps)['tens.turn'], 0.0)
        with self.assertRaises(ValueError) as raised:
            program.published_controls(rest)
        message = str(raised.exception)
        self.assertIn('turn tens', message)
        self.assertIn('units_entry', message)
        self.assertIn('tens.turn', message)
        self.assertIn('does not move', message)

    def test_a_two_sided_disagreement_is_refused(self):
        sim = Sim(KinkedControl(), 0.1)
        rest = dict(sim.initial.bank)
        with self.assertRaises(ValueError) as raised:
            sim.program.published_controls(rest)
        message = str(raised.exception)
        self.assertIn('turn units', message)
        self.assertIn('units.turn', message)
        self.assertIn('crank', message)
        self.assertIn('5.0', message)
        self.assertIn('-5.0', message)

    def test_a_smooth_non_affine_law_is_admitted(self):
        """The window is the control measurement's own `1e-3`, not the
        program's `1e-9` agreement: a two-sided finite difference over a
        law that curves disagrees by far more than `1e-9`, and a law
        that curves is explicitly permitted -- the pointer leads or lags
        the part and nothing is ever wrong."""
        from machinome.simulation.program import (_CONTROL_AGREEMENT,
                                                   _agreement)

        sim = Sim(SmoothControl(), 0.1)
        rest = dict(sim.initial.bank)
        eps = 2.0 ** -20
        forward = sim.program.response(rest, 'crank', eps)['units.turn'] / eps
        backward = sim.program.response(rest, 'crank',
                                        -eps)['units.turn'] / -eps
        gap = abs(forward - backward) / max(abs(forward), abs(backward))
        self.assertGreater(gap, _agreement())
        self.assertLess(gap, _CONTROL_AGREEMENT)
        table = sim.program.published_controls(rest)
        self.assertEqual(table['turn units']['per_unit'], forward)
        # 90 * sin(a) at 89 degrees, per degree.
        self.assertAlmostEqual(table['turn units']['per_unit'],
                               90 * math.cos(math.radians(89))
                               * math.pi / 180, places=6)

    def test_the_published_reading_is_the_forward_one(self):
        sim = Sim(SmoothControl(), 0.1)
        rest = dict(sim.initial.bank)
        eps = 2.0 ** -20
        forward = sim.program.response(rest, 'crank', eps)['units.turn'] / eps
        table = sim.program.published_controls(rest)
        self.assertEqual(table['turn units']['per_unit'], forward)


class InheritanceTest(BaseNodeTest):
    """(3.2) `controls` inherits exactly as `instructions` does, and
    `_declares_controls` reflects the class's OWN table.

    A subclass that assigns nothing inherits its base's table AND its
    base's flag; a subclass that assigns `controls = {}` replaces the
    table whole and is not refused under a non-running root for a table
    it emptied.
    """

    def test_a_subclass_inherits_the_table_and_the_flag(self):
        self.assertTrue(LoopingControls._declares_controls)
        self.assertEqual(sorted(LoopingControls.controls),
                         sorted(NotRunning.controls))

    def test_a_subclass_that_empties_the_table_declares_none(self):
        class Emptied(NotRunning):
            controls = {}

        self.assertFalse(Emptied._declares_controls)
        self.assertEqual(Emptied.controls, {})
        # Neither door refuses it: it declares no control.
        sim = Sim(Emptied(), 0.1)
        self.assertEqual(sim.controls, {})

    def test_an_emptied_table_publishes_no_controls_key(self):
        from .test_running_document import bound, document

        class EmptiedToo(NotRunning):
            controls = {}

        published = document(bound(EmptiedToo()))
        self.assertNotIn('controls', published)

    def test_a_class_declaring_no_controls_carries_no_flag(self):
        self.assertFalse(getattr(ColumnsBare, '_declares_controls', False))
        self.assertTrue(Columns._declares_controls)


class SlideTest(BaseNodeTest):
    """(1.1, 1.2) `Slide` is the prismatic sibling of `Turn`.

    OpenSpec change ``direct-part-motion``. A drag ALONG the selected
    translational coordinate, declared exactly as a turn is -- part and
    input, no axis, no scale, no law -- because the tree already carries
    the rail and the program already holds the ratio.
    """

    def test_a_slide_over_a_single_prismatic_joint_is_admitted(self):
        compiled = controls_of(Sim(Selector(), 0.1).program)
        entry = compiled['slide selector']
        self.assertEqual(entry.kind, 'slide')
        self.assertEqual(entry.part, ('selector', 'knob'))
        self.assertEqual(entry.joint, ('selector',))
        self.assertEqual(entry.coordinate, 'selector.travel')
        self.assertEqual(entry.input, 'setting')
        self.assertEqual(entry.axis, (0, 1, 0))

    def test_a_press_on_a_sliding_part_names_the_same_instruction(self):
        sim = Sim(Selector(), 0.1)
        entry = controls_of(sim.program)['press selector']
        self.assertEqual(entry.kind, 'button')
        self.assertEqual(entry.instruction, 'One detent')
        self.assertIn('One detent', sim.instructions)
        self.assertEqual(entry.coordinate, 'selector.travel')

    def test_a_slide_over_a_rotational_coordinate_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Sim(SlidingTurn(), 0.1)
        message = str(raised.exception)
        self.assertIn('units.turn', message)
        self.assertIn('rotational', message)
        self.assertIn('translational', message)

    def test_a_slide_names_its_input_by_declaration(self):
        with self.assertRaises(TypeError) as raised:
            class Stringly(AssemblyNode):
                time = Time.running()
                setting = Driver(default=0.0, unit='step')
                selector = SlideKnob()
                setting.drives(selector.travel, ratio=6.0)
                controls = {'slide': Slide(selector.knob, 'setting')}

        self.assertIn('DECLARATION', str(raised.exception))

    def test_a_slides_input_must_be_declared_on_the_declaring_class(self):
        class Elsewhere(AssemblyNode):
            other = Driver(default=0.0, unit='mm')

        with self.assertRaises(TypeError) as raised:
            class Foreign(AssemblyNode):
                time = Time.running()
                setting = Driver(default=0.0, unit='step')
                selector = SlideKnob()
                setting.drives(selector.travel, ratio=6.0)
                controls = {'slide': Slide(selector.knob, Elsewhere.other)}

        message = str(raised.exception)
        self.assertIn('Foreign', message)
        self.assertIn('setting', message)

    def test_a_slide_whose_input_does_not_reach_the_part_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            class Unreaching(AssemblyNode):
                time = Time.running()
                setting = Driver(default=0.0, unit='step')
                spare = Driver(default=0.0, unit='step')
                selector = SlideKnob()
                setting.drives(selector.travel, ratio=6.0)
                controls = {'slide': Slide(selector.knob, spare)}

            Sim(Unreaching(), 0.1)
        message = str(raised.exception)
        self.assertIn('selector.travel', message)
        self.assertIn('setting', message)

    def test_a_coordinate_is_not_a_part_for_a_slide_either(self):
        with self.assertRaises(TypeError) as raised:
            class Jointed(AssemblyNode):
                time = Time.running()
                setting = Driver(default=0.0, unit='step')
                selector = SlideKnob()
                setting.drives(selector.travel, ratio=6.0)
                controls = {'slide': Slide(selector.travel, setting)}

        message = str(raised.exception)
        self.assertIn('PART', message)
        self.assertIn('coordinate', message)


class SelectionTest(BaseNodeTest):
    """(1.2) A control may name the coordinate it means.

    Inference stays exactly what ADR-112 made it; `coordinate=` is the
    escape for the bodies inference cannot serve -- a crank that lifts
    AND turns, a knob whose nearest joint is not the one a hand means.
    """

    def test_one_body_is_lifted_and_turned_independently(self):
        compiled = controls_of(Sim(Crank(), 0.1).program)
        self.assertEqual(sorted(compiled),
                         ['lift crank', 'rotate crank', 'turn crank'])
        for name, kind, coordinate in (
                ('lift crank', 'slide', 'crank.lift'),
                ('rotate crank', 'turn', 'crank.turn'),
                ('turn crank', 'button', 'crank.turn')):
            with self.subTest(control=name):
                entry = compiled[name]
                self.assertEqual(entry.kind, kind)
                self.assertEqual(entry.coordinate, coordinate)
                self.assertEqual(entry.part, ('crank', 'handle'))
                self.assertEqual(entry.joint, ('crank',))

    def test_each_selection_carries_its_own_joints_geometry(self):
        compiled = controls_of(Sim(Crank(), 0.1).program)
        self.assertEqual(compiled['rotate crank'].axis, (0, 0, 1))
        self.assertEqual(compiled['rotate crank'].origin, (0.0, 12.0, 0.0))
        self.assertEqual(compiled['lift crank'].axis, (0, 0, 1))

    def test_each_input_is_the_one_that_reaches_the_selected_coordinate(self):
        compiled = controls_of(Sim(Crank(), 0.1).program)
        self.assertEqual(compiled['rotate crank'].input, 'rotation')
        self.assertEqual(compiled['lift crank'].input, 'elevation')

    def test_ambiguity_is_still_refused_without_a_selection(self):
        with self.assertRaises(ValueError) as raised:
            Sim(AmbiguousCrank(), 0.1)
        message = str(raised.exception)
        self.assertIn('turn', message)
        self.assertIn('lift', message)
        self.assertIn('ONE coordinate', message)

    def test_an_ancestor_coordinate_is_reachable_past_a_nearer_joint(self):
        compiled = controls_of(Sim(Register(), 0.1).program)
        shift = compiled['shift register']
        self.assertEqual(shift.part, ('register', 'marker', 'knob'))
        self.assertEqual(shift.joint, ('register',))
        self.assertEqual(shift.coordinate, 'register.travel')
        # ... and the nearer joint is genuinely the one inference finds.
        turn = compiled['turn marker']
        self.assertEqual(turn.joint, ('register', 'marker'))
        self.assertEqual(turn.coordinate, 'register.marker.turn')

    def test_a_selection_cannot_reach_sideways(self):
        with self.assertRaises(ValueError) as raised:
            Sim(Sideways(), 0.1)
        message = str(raised.exception)
        self.assertIn('lift crank', message)
        self.assertIn('selector.travel', message)
        self.assertIn('crank.handle', message)

    def test_selecting_a_joint_does_not_unpack_it(self):
        with self.assertRaises(ValueError) as raised:
            Sim(FreeSelected(), 0.1)
        message = str(raised.exception)
        self.assertIn('pose', message)
        self.assertIn('yaw', message)
        self.assertIn('ONE coordinate', message)

    def test_a_selection_that_is_not_a_joint_is_refused_where_written(self):
        with self.assertRaises(TypeError) as raised:
            class Numeric(AssemblyNode):
                time = Time.running()
                rotation = Driver(default=0.0, unit='turn')
                crank = CrankBody()
                rotation.drives(crank.turn, ratio=360.0)
                controls = {'rotate': Turn(crank.handle, rotation,
                                           coordinate=3.0)}

        message = str(raised.exception)
        self.assertIn('JOINT', message)
        self.assertIn('3.0', message)

    def test_a_selection_of_another_classs_joint_is_refused(self):
        class Elsewhere(AssemblyNode):
            spare = CrankBody()

        with self.assertRaises(TypeError) as raised:
            class Borrower(AssemblyNode):
                time = Time.running()
                rotation = Driver(default=0.0, unit='turn')
                crank = CrankBody()
                rotation.drives(crank.turn, ratio=360.0)
                controls = {'rotate': Turn(crank.handle, rotation,
                                           coordinate=Elsewhere.spare.turn)}

        message = str(raised.exception)
        self.assertIn('Borrower', message)
        self.assertIn('rotate', message)
        self.assertIn('spare', message)

    def test_a_derived_coordinate_is_not_a_joint(self):
        """A linear formula over coordinates reads as a coordinate and
        poses nothing; a gesture is a JOINT's motion."""
        with self.assertRaises(ValueError) as raised:
            Sim(DerivedSelected(), 0.1)
        message = str(raised.exception)
        self.assertIn('turn body', message)
        self.assertIn('pair.spread', message)
        self.assertIn('not a joint', message)

    def test_a_plain_port_is_not_a_joint(self):
        """A control's gesture is a JOINT's motion: a port an author's
        own render() turns is refused where it is written."""
        from .running_project.parts import Wheel

        with self.assertRaises(TypeError) as raised:
            class Plain(AssemblyNode):
                time = Time.running()
                entry = Driver(default=0.0, unit='deg')
                units = DialArbor()
                spin = Wheel()
                entry.drives(units.turn, ratio=-36.0)
                entry.drives(spin.turn, ratio=1.0)
                controls = {'turn spin': Turn(units.dial, entry,
                                              coordinate=spin.turn)}

        message = str(raised.exception)
        self.assertIn('JOINT', message)
        self.assertIn('spin.turn', message)

    def test_a_selection_changes_neither_the_bank_nor_the_identity(self):
        """The program of a two-freedom body is what it is with no
        control at all: selection is a reading of the tree, and it adds
        no joint, no edge and no source."""
        selected = Sim(Crank(), 0.1)
        bare = Sim(CrankBare(), 0.1)
        self.assertEqual(dict(selected.state), dict(bare.state))
        self.assertEqual(selected.program.described().split('\n')[1:],
                         bare.program.described().split('\n')[1:])
        self.assertEqual(
            {selected.program.nodes[key].name: sorted(names)
             for key, names in selected.program.sources.items()},
            {bare.program.nodes[key].name: sorted(names)
             for key, names in bare.program.sources.items()})
        # The identity itself, with the one line that names the ROOT
        # CLASS aligned -- a twin under another name necessarily hashes
        # differently, and nothing else may.
        lines = bare.program.described().split('\n')
        lines[0] = selected.program.described().split('\n')[0]
        self.assertEqual(
            hashlib.sha256('\n'.join(lines).encode()).hexdigest(),
            selected.program.identity)
        described = selected.program.described()
        for name in ('lift crank', 'rotate crank', 'control'):
            self.assertNotIn(name, described)

    def test_the_two_step_identically(self):
        selected = Sim(Crank(), 0.1)
        bare = Sim(CrankBare(), 0.1)
        for sim in (selected, bare):
            sim.move('rotation', by=0.5, duration=0.5)
            sim.run(0.5)
            sim.move('elevation', by=-2.0, duration=0.3)
            sim.run(0.5)
        self.assertEqual(dict(selected.state), dict(bare.state))


class InterlockedSlideTest(BaseNodeTest):
    """(1.3) A sliding control is a `move` request and nothing else.

    The gate's plug may turn only while both pins stand in the shear
    line, and its key is what lifts them. A request issued through the
    key's sliding control is admitted exactly as the same ordinary move
    is, and it repositions nothing.
    """

    def outcome(self, sim, identifier, by):
        sim.move(identifier, by=by, duration=0.5)
        return sim.run(0.5)

    def test_a_slide_admits_what_the_ordinary_move_admits(self):
        touched = Sim(GateTouched(), 0.1)
        plain = Sim(Gate(), 0.1)
        for sim in (touched, plain):
            self.outcome(sim, 'feed', 4.0)
            self.outcome(sim, 'twist', 30.0)
        self.assertEqual(dict(touched.state), dict(plain.state))

    def test_a_blocked_turn_does_not_move_the_key(self):
        sim = Sim(GateTouched(), 0.1)
        before = dict(sim.state)
        self.outcome(sim, 'twist', 30.0)
        self.assertEqual(sim.state['key.travel'], before['key.travel'])
        self.assertEqual(sim.state['p1.lift'], before['p1.lift'])

    def test_the_controls_do_not_change_the_program(self):
        touched = Sim(GateTouched(), 0.1).program
        plain = Sim(Gate(), 0.1).program
        self.assertEqual(touched.described().split('\n')[1:],
                         plain.described().split('\n')[1:])


class PlacementSpanTest(BaseNodeTest):
    """(2.2) The published block is the placement's OWN, or nothing.

    The indices come from the slot mark every operation a joint places
    carries (ADR-093, ADR-114) -- the thing that placed them -- and
    never from searching a rendered expression for a coordinate's name.
    A block that is not exactly one contiguous run of this coordinate's
    own operations is refused rather than published as a frame the
    producer invented.
    """

    def compiled(self, factory):
        sim = Sim(factory(), 0.1)
        return sim, controls_of(sim.program)

    def test_an_inferred_rotational_control_publishes_no_span(self):
        _sim, compiled = self.compiled(Columns)
        for name in sorted(compiled):
            with self.subTest(control=name):
                self.assertIsNone(compiled[name].span)

    def test_a_translational_coordinate_publishes_one_uninvited(self):
        _sim, compiled = self.compiled(Selector)
        self.assertEqual(compiled['slide selector'].span, (0, 1))
        self.assertEqual(compiled['press selector'].span, (0, 1))

    def test_a_selection_publishes_one_even_where_it_turns(self):
        _sim, compiled = self.compiled(Crank)
        self.assertEqual(compiled['rotate crank'].span, (0, 3))
        self.assertEqual(compiled['turn crank'].span, (0, 3))
        self.assertEqual(compiled['lift crank'].span, (3, 4))

    def test_the_span_is_the_same_wherever_the_run_stands(self):
        """The block is a property of the PLACEMENT, not of the pose:
        a crank that has been lifted and turned publishes the same two
        blocks it published at rest."""
        sim = Sim(Crank(), 0.1)
        at_rest = {name: entry.span
                   for name, entry in controls_of(sim.program).items()}
        sim.move('rotation', by=0.25, duration=0.5)
        sim.run(0.5)
        sim.move('elevation', by=3.0, duration=0.5)
        sim.run(0.5)
        self.assertNotEqual(sim.state['crank.turn'], 0.0)
        self.assertNotEqual(sim.state['crank.lift'], 0.0)
        moved = Sim(Crank(), 0.1, state={'rotation': 0.25,
                                         'elevation': 3.0})
        self.assertEqual(
            {name: entry.span
             for name, entry in controls_of(moved.program).items()},
            at_rest)

    def test_a_placement_that_is_not_there_is_refused(self):
        from machinome.simulation.program import (ControlError,
                                                   _published_span)

        sim = Sim(Crank(), 0.1)
        crank = sim.node.crank
        crank.operations[:] = [
            operation for operation in crank.operations
            if getattr(operation, '_joint_slot', None) != 0]
        with self.assertRaises(ControlError) as raised:
            _published_span(crank, type(crank).turn, 'rotate crank',
                            Crank.controls['rotate crank'], sim.program,
                            'crank.turn')
        message = str(raised.exception)
        self.assertIn('crank.turn', message)
        self.assertIn('turn', message)
        self.assertIn('invented', message)

    def test_a_block_that_is_not_contiguous_is_refused(self):
        from machinome.node.operations import Translation
        from machinome.simulation.program import (ControlError,
                                                   _published_span)

        sim = Sim(Crank(), 0.1)
        crank = sim.node.crank
        intruder = Translation([0.0, 0.0, 1.0], crank)
        intruder._motion = True
        intruder._joint_slot = 1
        crank.operations.insert(1, intruder)
        with self.assertRaises(ControlError) as raised:
            _published_span(crank, type(crank).turn, 'rotate crank',
                            Crank.controls['rotate crank'], sim.program,
                            'crank.turn')
        self.assertIn('contiguous', str(raised.exception))
