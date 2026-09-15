# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Schema v5: a running root's document publishes the compiled program.

OpenSpec change ``publish-the-mechanical-program``, cycle 4 of the
open-run campaign. Cycles 1 to 3 built a machine that runs in Python and
nothing of it reached the browser: a running root's document was
BYTE-IDENTICAL to an untimed root's, so its pose expressions were the law
evaluated ABSOLUTELY at the driver values -- the reading the whole
campaign exists to replace.

Under version 5 the document carries two new things and one changed rule.
`program` is what COMPILE TIME decided about the machine: the coordinate
table with each bank id's kind, rest value, unit and domain, the
intermediates, the edges in program order with their expressions and jump
plans, the spans, the candidate table, the identity, the clock name and
the algorithm's limits. The poses name BANK IDS, because a committed bank
is what poses the geometry. And the instructions table publishes both
forms, which versions 2 to 4 may not.

An untimed or looping root's document is unchanged in every byte, which
`ByteIdentityTest` pins against documents captured from the cycle's base
commit rather than against a re-derivation.
"""

import json
import os
import shutil
import tempfile
from unittest.mock import patch

from solid_node.core.builder import Builder
from solid_node.core.export import export_node
from solid_node.core.expressions import parse
from solid_node.core.serializer import (
    DOCUMENT_FORMAT, drivers_table, instructions_table, serialize_node,
    symbolic_document,
)
from solid_node.expression_graph import postorder
from solid_node.motion.ports import Time, get_coordinate
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, Instruction, Sim, Slide
from solid_node.simulation.enumeration import bind_declared_defaults
from solid_node.simulation.program import (_BISECTION_ROUNDS,
                                           _CROSSING_TOLERANCE,
                                           _MAX_CROSSINGS, _SUBDIVISIONS)
from solid_node.simulation.run import _TOLERANCE

from .base import BaseNodeTest
from .running_project.machine import (Captured, ClassGate, Clearing, Clocked,
                                      ClockedBody, Columns, ColumnsBare,
                                      Crank, Derived, Gate, Gauged, Guarded,
                                      LoopingTrain, NotRunning, OffCentre,
                                      OmittedControl, Optional, OptionalRead,
                                      PlainClearing,
                                      PortDrivenJoint, PortDrivenSmooth,
                                      Ratchet, Register, Remainder, Selector,
                                      Sixbound, Sixfree, SlideKnob, SpringBank,
                                      StatedBelow, StatedBelowBody,
                                      StatedBelowOpaque, StoppedDifferential,
                                      Swept, ThreeCarries, Tilted, Train,
                                      TrainBody, Window, Wired)

BASE_DOCUMENTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'base_documents')


def document(node):
    """The document a producer assembles for `node`, minus the two keys
    a producer owns: the model paths it resolves, and `pieces`.

    The sequence is `export_node`'s and `_write_viewer_snapshot`'s, called
    here directly so the schema can be read without building an artifact.
    """
    from solid_node.core.serializer import (compiled_controls,
                                            compiled_program, document_body)

    program, initial = compiled_program(node)
    with symbolic_document(node) as (declarations, instructions):
        root = serialize_node(node, lambda rigid: rigid.name,
                              graph_values=True)
        drivers = drivers_table(declarations)
        events = instructions_table(instructions, running=program is not None)
    body = document_body(node, root, drivers, events, program, initial,
                         controls=compiled_controls(program, initial))
    body['root'] = root
    return body


def bound(node, prepared=None):
    """`node` with its declared defaults bound, ready to serialize."""
    bind_declared_defaults(node)
    return node


def operations_of(document, *path):
    node = document['root']
    for name in path:
        node = next(child for child in node['children']
                    if child['name'] == name)
    return node['operations']


def resolved(document, text):
    """`text` with every bindings entry substituted, so a test can read
    what an expression says without walking the table by hand."""
    table = {entry['name']: entry['expression']
             for entry in document.get('bindings', ())}
    changed = True
    while changed:
        changed = False
        rewritten = []
        for token in _tokens(text):
            if token in table:
                rewritten.append(f'({table[token]})')
                changed = True
            else:
                rewritten.append(token)
        text = ''.join(rewritten)
    return text


def _tokens(text):
    token = ''
    for character in text:
        if character.isalnum() or character in '_$.':
            token += character
        else:
            if token:
                yield token
                token = ''
            yield character
    if token:
        yield token


def free_names_of(text):
    """Every free name an expression reads, off the document's own
    parser."""
    return {item.text for item in postorder([parse(text)])
            if item.kind == 'name'}


def names_in(document):
    """Every free name every operation and `params` expression of the
    document's tree reads."""
    found = set()

    def visit(node):
        for operation in node['operations']:
            if operation[0] == 'r':
                found.update(free_names_of(operation[1]))
            else:
                for component in operation[1]:
                    found.update(free_names_of(component))
        if 'flexible' in node:
            for expression in node['flexible']['params'].values():
                found.update(free_names_of(expression))
        for child in node.get('children', ()):
            visit(child)

    visit(document['root'])
    return found


class VersionTest(BaseNodeTest):
    """(1) The version is a property of the ROOT'S DECLARATION."""

    def setUp(self):
        super().setUp()
        self.temporary = tempfile.mkdtemp(prefix='solid-running-document-')
        self.addCleanup(shutil.rmtree, self.temporary, ignore_errors=True)

    def exported(self, node):
        bind_declared_defaults(node)
        output = os.path.join(self.temporary, 'export')
        export_node(node, output, widget=False)
        with open(os.path.join(output, 'manifest.json')) as handle:
            return json.load(handle)

    def built(self, node):
        bind_declared_defaults(node)
        build_dir = os.path.join(self.temporary, 'build')
        os.makedirs(build_dir, exist_ok=True)
        node.assemble()
        node.build_stls()
        builder = Builder('model.py', build_dir=build_dir, watch=False)
        builder.node = node
        builder._write_viewer_snapshot()
        with open(os.path.join(build_dir, 'viewer.json')) as handle:
            return json.load(handle)

    def test_a_running_export_declares_version_five(self):
        manifest = self.exported(Train())
        self.assertEqual(manifest['version'], 5)
        self.assertIn('program', manifest)

    def test_a_running_build_declares_version_five(self):
        published = self.built(Train())
        self.assertEqual(published['version'], 5)
        self.assertIn('program', published)

    def test_an_untimed_document_carries_no_program(self):
        self.assertNotIn('program', document(bound(TrainBody())))
        self.assertNotIn('program', document(bound(LoopingTrain())))

    def test_a_running_root_with_nothing_shared_is_still_version_five(self):
        """The ladder below 5 is content-derived; 5 is not."""
        published = document(bound(Window()))
        self.assertEqual(published['version'], 5)


class InstructionTableTest(BaseNodeTest):
    """(1.3, 1.4, 6.2) Both forms under 5, and neither change under 4."""

    def test_a_running_document_publishes_both_forms(self):
        table = document(bound(Train()))['instructions']
        self.assertEqual(sorted(table), ['Advance', 'Park', 'Wind'])
        self.assertEqual(table['Park'], {'targets': {'crank': 40.0},
                                         'duration': 0.5})
        self.assertEqual(table['Advance'], {'by': {'crank': 10.0},
                                            'duration': 0.5})
        self.assertEqual(table['Wind'], {'by': {'crank': 10.0, 'lever': 5.0},
                                         'duration': 0.5})
        for name, entry in table.items():
            self.assertEqual(('targets' in entry) + ('by' in entry), 1, name)

    def test_an_untimed_document_still_omits_a_relative_instruction(self):
        table = document(bound(TrainBody()))['instructions']
        self.assertEqual(sorted(table), ['Park'])
        self.assertEqual(table['Park'], {'targets': {'crank': 40.0},
                                         'duration': 0.5})


class ByteIdentityTest(BaseNodeTest):
    """(1.2, 10.2) Every document but a running one is unchanged.

    Compared against files captured from the cycle's base commit
    (`tests/base_documents/`), not against a second derivation of the
    same code. One field is normalized on both sides: each node's
    `mtime`, which is its SOURCE FILE's modification time and therefore a
    property of the checkout rather than of the document.
    """

    trees = {
        'driverless': 'tests.deep_project.third_level:ThirdLevel',
        'drivers': 'tests.meta_project.machine:Machine',
        'flexible': 'tests.flexible_project.spring:Engine',
        'sharing': 'tests.expression_project.sharing:SharedValueTree',
        'looping': 'tests.running_project.machine:LoopingTrain',
        'untimed_train': 'tests.running_project.machine:TrainBody',
        # A RUNNING tree too, captured at the base of the
        # `declare-controls-on-parts` cycle: a version 5 document whose
        # tree declares no control must stay byte-identical, which is
        # what makes "the table is ADDITIVE" true by construction.
        'running_train': 'tests.running_project.machine:Train',
    }

    def factory(self, reference):
        from importlib import import_module
        module, _colon, name = reference.partition(':')
        return getattr(import_module(module), name)

    def normalized(self, root):
        root['mtime'] = None
        for child in root.get('children', ()):
            self.normalized(child)
        return root

    def test_every_document_with_no_control_is_unchanged_in_every_byte(self):
        for name, reference in sorted(self.trees.items()):
            with self.subTest(tree=name):
                node = self.factory(reference)()
                bind_declared_defaults(node)
                published = document(node)
                self.normalized(published['root'])
                with open(os.path.join(BASE_DOCUMENTS,
                                       f'{name}.json')) as handle:
                    expected = handle.read()
                self.assertEqual(json.dumps(published, indent=2) + '\n',
                                 expected)


class PoseTest(BaseNodeTest):
    """(2) A committed bank poses the geometry."""

    def test_a_joints_placement_is_its_coordinates_name(self):
        published = document(bound(Train()))
        self.assertEqual(operations_of(published, 'first'),
                         [['r', 'first.turn', [0, 0, 1]]])

    def test_a_plain_port_follows_the_bank(self):
        published = document(bound(Gauged()))
        rotation = operations_of(published, 'gauge', 'hand')[0]
        self.assertEqual(rotation[0], 'r')
        self.assertEqual(free_names_of(resolved(published, rotation[1])),
                         {'first.turn'})

    def test_a_guarded_rest_default_is_published_as_its_own_id(self):
        published = document(bound(Guarded()))
        self.assertEqual(operations_of(published, 'slide')[0],
                         ['t', ['slide.travel', '0', '0']])

    def test_a_free_joint_reads_its_six_coordinate_ids(self):
        published = document(bound(Sixbound()))
        operations = operations_of(published, 'chassis')
        names = set()
        for operation in operations:
            if operation[0] == 'r':
                names |= free_names_of(operation[1])
            else:
                for component in operation[1]:
                    names |= free_names_of(component)
        self.assertTrue({'chassis.pose.yaw', 'chassis.pose.pitch',
                         'chassis.pose.roll', 'chassis.pose.x',
                         'chassis.pose.y', 'chassis.pose.z'} <= names,
                        sorted(names))

    def test_a_flexible_part_follows_the_bank(self):
        from .running_project.flexible import Valvegear

        published = document(bound(Valvegear()))

        def find(node, name):
            if node['name'] == name:
                return node
            for child in node.get('children', ()):
                found = find(child, name)
                if found is not None:
                    return found
            return None

        spring = find(published['root'], 'spring')
        self.assertIsNotNone(spring)
        self.assertIn('flexible', spring)
        self.assertEqual(spring['flexible']['tech'], 'molejo')
        height = spring['flexible']['params']['height']
        self.assertEqual(free_names_of(resolved(published, height)),
                         {'lifter.travel'})

    def test_every_free_name_the_document_reads_is_declared(self):
        for factory in (Train, ThreeCarries, Sixbound, Guarded, Gauged,
                        SpringBank, Optional, PortDrivenSmooth):
            with self.subTest(machine=factory.__name__):
                published = document(bound(factory()))
                declared = (set(published['drivers'])
                            | set(published['program']['coordinates'])
                            | set(published['program']['intermediates'])
                            | {published['program']['clock']})
                table = {entry['name']
                         for entry in published.get('bindings', ())}
                names = names_in(published)
                self.assertTrue(names <= declared | table, sorted(names))
                # And once the table is resolved away, nothing but the
                # declared ids is left.
                left = set()
                for name in names:
                    left |= free_names_of(resolved(published, name))
                self.assertTrue(left <= declared, sorted(left - declared))

    def test_the_tree_is_left_as_it_was_found(self):
        node = Train()
        bind_declared_defaults(node)
        node.set_state(crank=10.0, lever=110.0, time=0.0)
        before = {name: get_coordinate(owner, coordinate)._value
                  for name, (owner, coordinate)
                  in _coordinates(node).items()}
        binders = {name: get_coordinate(owner, coordinate).binder
                   for name, (owner, coordinate) in _coordinates(node).items()}

        document(node)

        after = {name: get_coordinate(owner, coordinate)._value
                 for name, (owner, coordinate) in _coordinates(node).items()}
        self.assertEqual(after, before)
        self.assertEqual({name: get_coordinate(owner, coordinate).binder
                          for name, (owner, coordinate)
                          in _coordinates(node).items()}, binders)
        self.assertEqual(operations_of(document(node), 'first'),
                         [['r', 'first.turn', [0, 0, 1]]])


def _coordinates(node):
    from solid_node.simulation.program import qualified_coordinates

    return qualified_coordinates(node)


class LiveRunTest(BaseNodeTest):
    """(2.0c) Publication over a tree a live run owns leaves no trace."""

    def test_publishing_mid_move_does_not_disturb_the_run(self):
        node = Train()
        sim = Sim(node, 0.1)
        command = sim.move('crank', by=20.0, duration=1.0)
        sim.run(0.5)
        state = sim.state
        tick = sim.tick
        admitted = command.admitted
        binders = {name: get_coordinate(owner, coordinate).binder
                   for name, (owner, coordinate) in _coordinates(node).items()}

        published = document(node)

        self.assertEqual(published['version'], 5)
        self.assertEqual(sim.state, state)
        self.assertEqual(sim.tick, tick)
        self.assertEqual(command.admitted, admitted)
        self.assertEqual(command.status, 'active')
        self.assertEqual({name: get_coordinate(owner, coordinate).binder
                          for name, (owner, coordinate)
                          in _coordinates(node).items()}, binders)

        sim.run(0.5)
        self.assertEqual(command.status, 'completed')
        self.assertAlmostEqual(sim.state['crank'], 20.0)
        self.assertAlmostEqual(sim.state['first.turn'], 40.0)


class StatedBelowTest(BaseNodeTest):
    """A relation a CHILD states and the ROOT only READS.

    `a-read-is-not-a-binding`: the pin tumbler lock states "the key lifts
    the pins inside the plug" in the plug's own body and reads those lifts
    from the root. Every pose and every `Sim` accepts it; publication over
    a tree an ENUMERATION posed refused it as doubly bound, naming a
    relation's SOURCE as one of its binders, because the producer's
    epilogue put the coordinates back without the record of what had bound
    them.
    """

    def test_a_posed_running_tree_of_that_shape_publishes(self):
        node = bound(StatedBelow())
        node.set_state(push=1.0)

        published = document(node)

        self.assertEqual(published['version'], 5)
        self.assertEqual(operations_of(published, 'd1')[0],
                         ['t', ['0', '0', 'd1.lift']])
        self.assertIn('plug.p1.lift', published['program']['coordinates'])

    def test_a_law_that_does_not_invert_publishes_too(self):
        """The root's relation then DEFERS instead of stepping backward,
        and the enumeration's own fixpoint refused it against its own
        previous binding: the same stale value, surfacing the other way."""
        node = bound(StatedBelowOpaque())
        node.set_state(push=1.0)

        published = document(node)

        self.assertEqual(published['version'], 5)
        self.assertEqual(operations_of(published, 'd1')[0],
                         ['t', ['0', '0', 'd1.lift']])

    def test_a_posed_tree_poses_again_after_publication(self):
        """The re-pose half of the promise: what the publication put back
        has to let the NEXT enumeration clear and re-solve, not merely let
        the tree be read."""
        node = bound(StatedBelow())
        node.set_state(push=1.0)

        document(node)
        node.set_state(push=2.0)

        values = {name: get_coordinate(owner, coordinate)._value
                  for name, (owner, coordinate) in _coordinates(node).items()}
        self.assertEqual(values, {'plug.key.travel': 2.0,
                                  'plug.p1.lift': 1.0,
                                  'd1.lift': -1.0})
        self.assertEqual(
            {name: repr(get_coordinate(owner, coordinate).binder)
             for name, (owner, coordinate) in _coordinates(node).items()},
            {'plug.key.travel':
                 '<relation push drives plug.key.travel solved forward>',
             'plug.p1.lift':
                 '<relation key.travel drives p1.lift solved forward>',
             'd1.lift':
                 '<relation plug.p1.lift drives d1.lift solved forward>'})

    def test_the_untimed_twin_is_unchanged(self):
        """The reference behaviour: the same declarations with no time
        base always published, and this change moves nothing there."""
        node = bound(StatedBelowBody())
        node.set_state(push=1.0)

        published = document(node)

        self.assertEqual(published['version'], 4)
        placement = operations_of(published, 'd1')[0]
        self.assertEqual(placement[0], 't')
        self.assertEqual(
            free_names_of(resolved(published, placement[1][2])), {'push'})

    def test_posed_or_not_publishes_the_same_document(self):
        posed = bound(StatedBelow())
        posed.set_state(push=1.0)

        self.assertEqual(json.dumps(document(posed), sort_keys=True),
                         json.dumps(document(StatedBelow()), sort_keys=True))


class CoordinateTableTest(BaseNodeTest):
    """(3.1, 3.2, 2.0b) The bank, published."""

    def test_the_table_is_the_bank_with_kinds_units_and_rest_values(self):
        node = Train()
        bind_declared_defaults(node)
        published = document(node)
        table = published['program']['coordinates']
        initial = dict(Sim(Train(), 0.1).initial.bank)
        self.assertEqual(sorted(table), sorted(initial))
        self.assertEqual([name for name, entry in table.items()
                          if entry['kind'] == 'input'],
                         ['crank', 'lever'])
        self.assertEqual(list(table)[:2], ['crank', 'lever'])
        for name, entry in table.items():
            with self.subTest(coordinate=name):
                self.assertEqual(entry['initial'], initial[name])
        self.assertEqual(table['first.turn']['unit'], 'deg')
        self.assertEqual(table['slide.travel']['unit'], 'mm')
        self.assertNotIn('unit', table['crank'])

    def test_the_intermediates_are_the_plain_ports_the_program_computes(self):
        """`Train`'s only plain port, `wheel.turn`, is a wiring OUT of
        the bank that nothing reads back -- `_reaching_the_bank` drops
        the edge, and, under ``publish-only-what-runs``, the program's
        own table agrees: a port no compiled edge determines is not an
        intermediate. `PortDrivenSmooth`'s `register` is a plain port a
        KEPT edge does determine, and it is what the definition means."""
        self.assertEqual(document(bound(Train()))['program']['intermediates'],
                         [])
        self.assertEqual(
            document(bound(PortDrivenSmooth()))['program']['intermediates'],
            ['register'])

    def test_the_drivers_table_is_the_one_declaration(self):
        published = document(bound(Train()))
        inputs = {name for name, entry
                  in published['program']['coordinates'].items()
                  if entry['kind'] == 'input'}
        self.assertEqual(inputs, set(published['drivers']))
        for name in inputs:
            entry = published['program']['coordinates'][name]
            self.assertEqual(set(entry) & {'unit', 'dtype', 'scale',
                                           'range', 'default'}, set())

    def test_every_entry_carries_its_domain(self):
        published = document(bound(Train()))
        table = published['program']['coordinates']
        self.assertEqual(table['first.turn']['domain'], 'rotational')
        self.assertEqual(table['spindle']['domain'], 'rotational')
        self.assertEqual(table['slide.travel']['domain'], 'translational')
        for name, entry in table.items():
            self.assertIn('domain', entry, name)

    def test_a_prismatic_fixture_reads_translational(self):
        published = document(bound(Swept()))
        table = published['program']['coordinates']
        self.assertEqual(table['rack.travel']['domain'], 'translational')
        self.assertEqual(table['wheel.turn']['domain'], 'rotational')

    def test_no_dt_is_published(self):
        published = document(bound(Train()))
        self.assertNotIn('dt', published['program'])
        self.assertNotIn('dt', published)


class NothingLeftOfADroppedEdgeTest(BaseNodeTest):
    """OpenSpec change ``publish-only-what-runs``: a coordinate no
    compiled edge computes is not part of the program, so it cannot
    refuse the document, however its node is named."""

    def test_a_repeated_ports_document_publishes(self):
        """`SpringBank` drives three `.repeat()` copies' plain port,
        whose list-held names (`springs-0`, ...) are not legal id
        segments. The relation onto them reaches no bank coordinate, so
        it is dropped, and none of the three copies' names may appear
        anywhere in the published program."""
        published = document(bound(SpringBank()))
        self.assertEqual(published['program']['intermediates'], [])
        self.assertEqual(published['program']['sources'],
                         {'lift': ['lift'], 'slider.travel': ['lift']})
        text = json.dumps(published['program'])
        for needle in ('PenSpring', 'height', 'springs-0'):
            self.assertNotIn(needle, text)
        names = [child['name'] for child in published['root']['children']
                 if child['name'].startswith('springs')]
        self.assertEqual(sorted(names), ['springs-0', 'springs-1',
                                        'springs-2'])

    def test_an_omitted_parts_driven_coordinate_publishes(self):
        """`Optional` drives both arbors from one crank; `render()` omits
        `spare` when `fitted` is false. Fitted, both coordinates are in
        the bank; unfitted, `spare.turn` is not published anywhere --
        the relation onto it reaches no bank coordinate once `spare` is
        gone, and the document that publishes it fitted is the one that
        never mentions it unfitted."""
        fitted = document(bound(Optional(fitted=True)))
        self.assertIn('spare.turn', fitted['program']['coordinates'])
        self.assertEqual(fitted['program']['intermediates'], [])

        unfitted = document(bound(Optional(fitted=False)))
        self.assertNotIn('spare.turn', unfitted['program']['coordinates'])
        self.assertEqual(unfitted['program']['intermediates'], [])
        self.assertNotIn('spare.turn', unfitted['program']['sources'])
        text = json.dumps(unfitted['program'])
        self.assertNotIn('spare', text)
        self.assertNotIn('Arbor.turn', text)

    def test_a_plain_port_a_kept_edge_computes_is_untouched(self):
        """`PortDrivenSmooth`'s `register` IS a coordinate the program
        computes -- a continuous law drives it and it drives a bank
        coordinate in turn -- so the reduction that drops `wheel.turn`
        and `gauge.angle` must not touch it."""
        published = document(bound(PortDrivenSmooth()))
        self.assertEqual(published['program']['intermediates'], ['register'])
        self.assertEqual(published['program']['sources']['register'],
                         ['crank'])
        gives = [name for edge in published['program']['edges']
                 for name in edge['gives']]
        self.assertIn('register', gives)

    def test_a_wiring_a_kept_edge_computes_is_untouched(self):
        """`Gauged` (`gauge.angle`) and `PortDrivenJoint` (`register`)
        each drive a plain port FROM a bank coordinate, so no edge in
        either program determines it -- the same shape as `wheel.turn`,
        which is why the reduction removes both."""
        gauged = document(bound(Gauged()))
        self.assertEqual(gauged['program']['intermediates'], [])
        self.assertNotIn('gauge.angle', gauged['program']['sources'])

        port_driven_joint = document(bound(PortDrivenJoint()))
        self.assertEqual(port_driven_joint['program']['intermediates'], [])
        self.assertNotIn('register', port_driven_joint['program']['sources'])


class EdgeTableTest(BaseNodeTest):
    """(3.3, 3.4, 3.5) The edges, in program order, with their plans."""

    def edges(self, factory):
        node = factory()
        bind_declared_defaults(node)
        published = document(node)
        return published, Sim(factory(), 0.1).program

    def test_the_edges_match_the_compiled_program_one_for_one(self):
        published, program = self.edges(Train)
        edges = published['program']['edges']
        self.assertEqual(len(edges), len(program.edges))
        for entry, edge in zip(edges, program.edges):
            with self.subTest(edge=edge.description):
                self.assertEqual(entry['kind'], edge.kind)
                self.assertEqual(entry['needs'],
                                 [program.nodes[key].name
                                  for key in edge.needs])
                self.assertEqual(entry['gives'],
                                 [program.nodes[key].name
                                  for key in edge.gives])
                self.assertEqual(entry['description'], edge.description)
                self.assertEqual(entry['stated_by'], edge.stated_by)
                if edge.kind == 'law':
                    self.assertEqual(entry['affine'], list(edge.affine))
                    self.assertEqual(len(entry['expressions']),
                                     len(edge.gives))
                    self.assertEqual(len(entry['plans']), len(edge.gives))

    def test_a_wiring_publishes_its_factor(self):
        published, program = self.edges(Wired)
        wirings = [entry for entry in published['program']['edges']
                   if entry['kind'] == 'wiring']
        self.assertEqual(len(wirings), 1)
        self.assertEqual(wirings[0]['needs'], ['relay'])
        self.assertEqual(wirings[0]['gives'], ['first.turn'])
        self.assertEqual(wirings[0]['factor'], 1.0)

    def test_a_formula_publishes_its_coefficients(self):
        published, program = self.edges(Derived)
        formulas = [entry for entry in published['program']['edges']
                    if entry['kind'] == 'formula']
        self.assertEqual(len(formulas), 1)
        self.assertEqual(formulas[0]['needs'], ['wrist', 'tool'])
        self.assertEqual(formulas[0]['gives'], ['left'])
        self.assertEqual(formulas[0]['factors'], [1.0, 2.0])
        self.assertEqual(formulas[0]['constant'], 0.0)
        self.assertEqual(formulas[0]['slot'], 'left')

    def test_a_check_publishes_what_it_predicts(self):
        published, program = self.edges(StoppedDifferential)
        checks = [entry for entry in published['program']['edges']
                  if entry['kind'] == 'check']
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0]['gives'], [])
        self.assertEqual(checks[0]['needs'], ['left', 'wrist', 'tool'])
        self.assertEqual(checks[0]['factors'], [0.0, 1.0, 2.0])
        self.assertEqual(checks[0]['slot'], 'left')

    def test_a_jump_publishes_its_plan(self):
        published, program = self.edges(Window)
        edge = published['program']['edges'][0]
        self.assertEqual(edge['affine'], [False])
        plan = edge['plans'][0]
        self.assertEqual(len(plan['jumps']), 1)
        jump = plan['jumps'][0]
        self.assertEqual(jump['primitive'], 'floor')
        self.assertTrue(jump['affine'])
        self.assertIn(jump['name'], plan['skeleton'])
        self.assertEqual(free_names_of(resolved(published, jump['level'])),
                         {'crank'})

    def test_a_remainder_is_written_out_in_the_skeleton(self):
        published, program = self.edges(Remainder)
        plan = published['program']['edges'][0]['plans'][0]
        jump = plan['jumps'][0]
        self.assertEqual(jump['primitive'], '%')
        skeleton = resolved(published, plan['skeleton'])
        self.assertIn(jump['name'], skeleton)
        self.assertIn('-', skeleton)

    def test_three_laws_mint_three_distinct_placeholders(self):
        published, program = self.edges(ThreeCarries)
        plans = [plan for entry in published['program']['edges']
                 if entry['kind'] == 'law'
                 for plan in entry.get('plans', ()) if plan is not None]
        self.assertEqual(len(plans), 3)
        names = [jump['name'] for plan in plans for jump in plan['jumps']]
        self.assertEqual(len(names), 3)
        self.assertEqual(len(set(names)), 3)
        table = {entry['name']: entry['expression']
                 for entry in published.get('bindings', ())}
        for name, expression in table.items():
            with self.subTest(binding=name):
                reads = free_names_of(expression) & set(names)
                self.assertLessEqual(len(reads), 1, expression)
        for plan, expected in zip(plans, names):
            self.assertEqual(
                free_names_of(resolved(published, plan['skeleton']))
                & set(names), {expected})


class SpansAndLimitsTest(BaseNodeTest):
    """(3.6) Spans, sources, identity and limits."""

    def test_an_expression_bound_travels_as_an_expression(self):
        published = document(bound(Ratchet()))
        spans = published['program']['spans']
        self.assertEqual(sorted(spans), ['wheel.turn'])
        self.assertIsNone(spans['wheel.turn']['high'])
        self.assertEqual(
            free_names_of(resolved(published,
                                   spans['wheel.turn']['low']['expression'])),
            {'wheel.turn'})

    def test_a_bound_reading_other_coordinates_names_them(self):
        for cls, expected in ((Gate, {'p1.lift', 'p2.lift'}),
                              (ClassGate, {'plug.p1.lift', 'plug.p2.lift'})):
            with self.subTest(cls=cls.__name__):
                published = document(bound(cls()))
                self.assertEqual(published['version'], 5)
                spans = published['program']['spans']
                span = spans['plug.turn']
                self.assertEqual(span['low'], 0.0)
                names = free_names_of(
                    resolved(published, span['high']['expression']))
                self.assertEqual(names, expected)
                coordinates = published['program']['coordinates']
                for name in names | {'plug.turn'}:
                    self.assertIn(name, coordinates)

    def test_a_capture_bound_publishes_the_coordinate_it_reads(self):
        published = document(bound(Captured()))
        spans = published['program']['spans']
        self.assertEqual(spans['key.travel']['high'], 20.0)
        names = free_names_of(
            resolved(published, spans['key.travel']['low']['expression']))
        self.assertEqual(names, {'plug.turn'})

    def test_a_numeric_bound_travels_as_a_number(self):
        published = document(bound(Swept()))
        spans = published['program']['spans']
        self.assertEqual(spans['rack.travel']['high'], 50.0)
        self.assertIsNone(spans['rack.travel']['low'])

    def test_the_candidate_table_and_the_identity_are_the_programs(self):
        published = document(bound(Train()))
        program = Sim(Train(), 0.1).program
        self.assertEqual(
            published['program']['sources'],
            {program.nodes[key].name: sorted(names)
             for key, names in program.sources.items()})
        self.assertEqual(published['program']['identity'], program.identity)

    def test_the_limits_are_the_constants_the_algorithm_declares(self):
        published = document(bound(Train()))
        self.assertEqual(published['program']['limits'], {
            'crossing_tolerance': _CROSSING_TOLERANCE,
            'subdivisions': _SUBDIVISIONS,
            'bisection_rounds': _BISECTION_ROUNDS,
            'max_crossings': _MAX_CROSSINGS,
            'agreement': _TOLERANCE,
        })


class SharingTest(BaseNodeTest):
    """(3.7, 3.8) One bindings table, one order, twice the same bytes."""

    def test_no_program_expression_carries_producer_local_sharing(self):
        for factory in (Train, Window, ThreeCarries, Ratchet):
            with self.subTest(machine=factory.__name__):
                published = document(bound(factory()))
                text = json.dumps(published['program'])
                self.assertNotIn('let(', text)
                for entry in published.get('bindings', ()):
                    self.assertNotIn('let(', entry['expression'])

    def test_a_law_and_its_plan_share_one_binding(self):
        published = document(bound(Window()))
        edge = published['program']['edges'][0]
        level = edge['plans'][0]['jumps'][0]['level']
        self.assertIn(level, [entry['name']
                              for entry in published['bindings']])
        self.assertIn(level, edge['expressions'][0])

    def test_publishing_twice_is_byte_identical(self):
        first = json.dumps(document(bound(ThreeCarries())), indent=2)
        second = json.dumps(document(bound(ThreeCarries())), indent=2)
        self.assertEqual(first, second)


class ClockTest(BaseNodeTest):
    """(4.1) `time` under a running root leaves the document."""

    def test_a_running_document_carries_no_animation_variable(self):
        published = document(bound(Clocked()))
        self.assertEqual(published['program']['clock'], 'time')
        self.assertNotIn('$t', json.dumps(published))
        self.assertIn('time', names_in(published))

    def test_an_untimed_document_still_carries_the_animation_variable(self):
        published = document(bound(ClockedBody()))
        self.assertIn('$t', json.dumps(published))

    def test_a_running_document_publishes_no_loop(self):
        published = document(bound(Train()))
        self.assertEqual(published['animation'], {'fps': 30, 'frames': 360})


class RefusalTest(BaseNodeTest):
    """(3.9) What publication refuses."""

    def test_a_root_the_run_refuses_cannot_be_published(self):
        """The program a document publishes is the program the run
        executes, so a root the run cannot be constructed over has none
        to publish, and publication says exactly what the run says."""
        node = Sixfree()
        bind_declared_defaults(node)
        with self.assertRaises(ValueError) as raised:
            document(node)
        self.assertIn('chassis.pose.pitch', str(raised.exception))
        self.assertIn('rest render leaves', str(raised.exception))

    def test_an_id_that_cannot_be_qualified_is_refused(self):
        """A node the walk could not qualify carries the
        `<ClassName>.<name>` FALLBACK and says so; publication refuses
        it, because that name is not unique across two instances of one
        class. Corrupted onto `PortDrivenSmooth`, whose `register` a
        kept edge genuinely computes and the reduction of
        ``publish-only-what-runs`` therefore leaves in `program.nodes`
        -- unlike `Train`'s `wheel.turn`, which the reduction now drops
        before this refusal ever sees it.
        """
        from solid_node.core.serializer import compiled_program
        from solid_node.simulation import program as program_module

        node = PortDrivenSmooth()
        bind_declared_defaults(node)
        program, initial = compiled_program(node)
        for entry in program.nodes.values():
            if entry.kind == 'intermediate':
                entry.name = 'Register.register'
                entry.qualified = False
                break
        else:
            self.fail('the fixture has no intermediate to unqualify')
        with self.assertRaises(program_module.UnsupportedLaw) as raised:
            program.published(initial)
        self.assertIn('Register.register', str(raised.exception))
        self.assertIn('class name', str(raised.exception))

    def test_an_omitted_part_a_kept_edge_still_reads_is_refused(self):
        """`OptionalRead` chains its relations through `spare`, so both
        edges reach the bank and are kept: `spare.turn` is a coordinate
        the program genuinely computes, and omitting `spare` leaves it
        unqualified rather than absent. Publication must go on refusing
        this one -- the reduction removes only what no kept edge
        touches."""
        from solid_node.simulation import program as program_module

        self.assertEqual(
            document(bound(OptionalRead(fitted=True)))['version'], 5)
        with self.assertRaises(program_module.UnsupportedLaw) as raised:
            document(bound(OptionalRead(fitted=False)))
        self.assertIn('Arbor.turn', str(raised.exception))


class AcceptanceShapeTest(BaseNodeTest):
    """(3.10) The acceptance project's own shape, pinned HERE.

    The Pascaline module lives in another repository, and the framework's
    suite may not depend on it -- so what the module's own document is
    asserted to be is a PROBE, run against the module and pasted into the
    change's `evidence.md`. What is pinned here is the same shape, built
    from the framework's own fixtures: a chain of registers, one carry law
    per column each carrying a single `floor`, every register's angle
    published as its own coordinate's name, and every coordinate
    rotational.
    """

    def setUp(self):
        super().setUp()
        self.published = document(bound(ThreeCarries()))

    def test_every_register_is_posed_by_its_own_coordinate(self):
        for column in ('units', 'tens', 'hundreds', 'trail'):
            with self.subTest(column=column):
                self.assertEqual(operations_of(self.published, column)[0],
                                 ['r', f'{column}.turn', [0, 0, 1]])

    def test_the_carry_laws_are_in_the_program_and_nowhere_else(self):
        text = json.dumps(self.published['root'])
        self.assertNotIn('floor', text)
        plans = [plan for edge in self.published['program']['edges']
                 for plan in edge.get('plans', ()) if plan is not None]
        self.assertEqual([jump['primitive'] for plan in plans
                          for jump in plan['jumps']],
                         ['floor', 'floor', 'floor'])

    def test_every_coordinate_is_rotational_at_its_rest_value(self):
        table = self.published['program']['coordinates']
        initial = dict(Sim(ThreeCarries(), 0.1).initial.bank)
        for name, entry in table.items():
            with self.subTest(coordinate=name):
                self.assertEqual(entry['initial'], initial[name])
                if entry['kind'] == 'coordinate':
                    self.assertEqual(entry['domain'], 'rotational')
                    self.assertEqual(entry['unit'], 'deg')

    def test_the_dials_reach_the_registers_through_the_program(self):
        sources = self.published['program']['sources']
        self.assertEqual(sources['units.turn'], ['units_entry'])
        self.assertEqual(sources['tens.turn'],
                         ['tens_entry', 'units_entry'])
        self.assertEqual(sources['hundreds.turn'],
                         ['hundreds_entry', 'tens_entry', 'units_entry'])


class ControlsTableTest(BaseNodeTest):
    """(7) The version 5 document publishes the controls its parts carry.

    OpenSpec change ``declare-controls-on-parts``. The table is
    top-level, beside ``instructions``, ADDITIVE within version 5, and
    absent when empty -- so a document that declares no control is the
    document the producer published before it existed, byte for byte.
    """

    def setUp(self):
        super().setUp()
        self.temporary = tempfile.mkdtemp(prefix='solid-controls-document-')
        self.addCleanup(shutil.rmtree, self.temporary, ignore_errors=True)
        self.published = document(bound(Columns()))

    def exported(self, node):
        bind_declared_defaults(node)
        output = os.path.join(self.temporary, 'export')
        export_node(node, output, widget=False)
        with open(os.path.join(output, 'manifest.json')) as handle:
            return json.load(handle)

    def built(self, node):
        bind_declared_defaults(node)
        build_dir = os.path.join(self.temporary, 'build')
        os.makedirs(build_dir, exist_ok=True)
        node.assemble()
        node.build_stls()
        builder = Builder('model.py', build_dir=build_dir, watch=False)
        builder.node = node
        builder._write_viewer_snapshot()
        with open(os.path.join(build_dir, 'viewer.json')) as handle:
            return json.load(handle)

    def walk(self, document, path):
        """The node `path` names, walked from the document's own tree by
        `name` -- the walk a consumer performs."""
        node = document['root']
        for name in path:
            found = [child for child in node.get('children', ())
                     if child['name'] == name]
            self.assertEqual(len(found), 1,
                             f'{name} of {node["name"]} in {path}')
            node = found[0]
        return node

    def test_both_producers_publish_the_table(self):
        for label, produced in (('built', self.built(Columns())),
                                ('exported', self.exported(Columns()))):
            with self.subTest(producer=label):
                self.assertEqual(sorted(produced['controls']),
                                 ['tens dial', 'turn tens', 'turn units',
                                  'units dial'])

    def test_the_table_sits_beside_the_instructions(self):
        keys = list(self.published)
        self.assertEqual(keys[keys.index('instructions') + 1], 'controls')
        self.assertLess(keys.index('controls'), keys.index('program'))

    def test_each_entrys_fields_are_in_the_specs_order(self):
        table = self.published['controls']
        self.assertEqual(list(table['units dial']),
                         ['kind', 'part', 'instruction', 'joint',
                          'coordinate', 'axis', 'origin'])
        self.assertEqual(list(table['turn units']),
                         ['kind', 'part', 'input', 'per_unit', 'joint',
                          'coordinate', 'axis', 'origin'])

    def test_a_button_names_a_key_of_its_own_instructions_table(self):
        table = self.published['controls']
        for name, instruction in (('units dial', 'Add one'),
                                  ('tens dial', 'Add ten')):
            with self.subTest(control=name):
                self.assertEqual(table[name]['kind'], 'button')
                self.assertEqual(table[name]['instruction'], instruction)
                self.assertIn(instruction, self.published['instructions'])

    def test_a_turn_names_a_key_of_its_own_drivers_table(self):
        table = self.published['controls']
        for name, driver, ratio in (('turn units', 'units_entry', -36.0),
                                    ('turn tens', 'tens_entry', 36.0)):
            with self.subTest(control=name):
                self.assertEqual(table[name]['kind'], 'turn')
                self.assertEqual(table[name]['input'], driver)
                self.assertIn(driver, self.published['drivers'])
                self.assertEqual(table[name]['per_unit'], ratio)

    def test_every_coordinate_is_a_key_of_the_program(self):
        coordinates = self.published['program']['coordinates']
        for name, entry in self.published['controls'].items():
            with self.subTest(control=name):
                self.assertIn(entry['coordinate'], coordinates)
                self.assertEqual(
                    coordinates[entry['coordinate']]['domain'], 'rotational')
                self.assertNotIn('domain', entry)
                self.assertNotIn('unit', entry)

    def test_the_part_and_joint_paths_resolve_by_walking_the_tree(self):
        """The walk a viewer will follow, performed here on the same
        document: `part` and `joint` are node-NAME paths from the
        document's own root."""
        for name, entry in self.published['controls'].items():
            with self.subTest(control=name):
                part = self.walk(self.published, entry['part'])
                self.assertEqual(part['name'], entry['part'][-1])
                joint = self.walk(self.published, entry['joint'])
                self.assertEqual(joint['operations'][0],
                                 ['r', entry['coordinate'], [1, 0, 0]])

    def test_the_geometry_is_the_joints_own(self):
        table = self.published['controls']
        self.assertEqual(table['turn units']['axis'], [1.0, 0.0, 0.0])
        self.assertEqual(table['turn units']['origin'], [0.0, 0.0, 0.0])
        self.assertEqual(table['turn units']['joint'], ['units'])
        self.assertEqual(table['turn units']['part'], ['units', 'dial'])

    def test_an_off_centre_joint_publishes_the_point_it_turns_about(self):
        table = document(bound(OffCentre()))['controls']
        self.assertEqual(table['turn units']['origin'], [0.0, 3.0, 0.0])
        self.assertEqual(table['turn units']['axis'], [1.0, 0.0, 0.0])

    def test_a_part_two_inputs_reach_publishes_the_declared_one(self):
        """`tens.turn` is reached by both entries. The entry names the
        one the author declared, and `per_unit` is measured against that
        input ALONE — the other's contribution held at zero, which is
        why the tens dial reads the same `36.0` the units dial reads
        `-36.0`, rather than a number the carry has leaked into."""
        sources = self.published['program']['sources']
        self.assertEqual(sources['tens.turn'],
                         ['tens_entry', 'units_entry'])
        entry = self.published['controls']['turn tens']
        self.assertEqual(entry['input'], 'tens_entry')
        self.assertEqual(entry['per_unit'], 36.0)

        program = Sim(Columns(), 0.1).program
        rest = dict(Sim(Columns(), 0.1).initial.bank)
        held = program.response(rest, 'tens_entry', 2.0 ** -20)
        self.assertEqual(held['units_entry'], 0.0)
        self.assertEqual(held['tens.turn'] / 2.0 ** -20, entry['per_unit'])

    def test_publication_is_refused_when_the_part_does_not_move(self):
        """The export delta's refusal, at the door a build goes
        through."""
        from .running_project.machine import Unmoved

        with self.assertRaises(ValueError) as raised:
            document(bound(Unmoved()))
        message = str(raised.exception)
        self.assertIn('tens.dial', message)
        self.assertIn('units_entry', message)
        self.assertIn('tens.turn', message)

    def test_a_document_with_no_control_omits_the_key(self):
        for factory in (Train, TrainBody, LoopingTrain, ColumnsBare):
            with self.subTest(root=factory.__name__):
                self.assertNotIn('controls', document(bound(factory())))

    def test_the_version_does_not_move(self):
        self.assertEqual(self.published['version'], 5)
        self.assertEqual(document(bound(ColumnsBare()))['version'], 5)
        self.assertEqual(self.built(Columns())['version'], 5)
        self.assertEqual(self.exported(Columns())['version'], 5)

    def test_a_control_under_a_non_running_root_is_refused_at_publication(self):
        with self.assertRaises(TypeError) as raised:
            document(bound(NotRunning()))
        message = str(raised.exception)
        self.assertIn('NotRunning', message)
        self.assertIn('units dial', message)
        self.assertIn('Time.running()', message)

    def test_the_program_is_unchanged_by_the_presence_of_a_control(self):
        """`ColumnsBare` is `Columns` minus the controls, so the two
        programs differ only where the ROOT CLASS's own name is
        published: each edge's `stated_by`, and `identity`, whose first
        described line names the class. Align that one name and
        everything else is equal, key by key."""
        bare = document(bound(ColumnsBare()))
        for key in ('coordinates', 'spans', 'sources', 'limits',
                    'intermediates', 'clock'):
            with self.subTest(key=key):
                self.assertEqual(self.published['program'][key],
                                 bare['program'][key])
        renamed = [dict(edge, stated_by='Columns')
                   for edge in bare['program']['edges']]
        self.assertEqual(self.published['program']['edges'], renamed)

    def test_republishing_is_byte_identical(self):
        first = json.dumps(document(bound(Columns())))
        second = json.dumps(document(bound(Columns())))
        self.assertEqual(first, second)
        self.assertEqual(list(first), list(second))

    def test_the_bindings_table_is_the_same_with_and_without_controls(self):
        bare = document(bound(ColumnsBare()))
        self.assertEqual(self.published.get('bindings'), bare.get('bindings'))

    def test_no_control_expression_enters_the_binding_pass(self):
        text = json.dumps(self.published['controls'])
        for entry in self.published.get('bindings', ()):
            self.assertNotIn(entry['name'], text)

    def spare_children(self, published):
        return [child['name']
                for child in self.walk(published, ['spare'])
                .get('children', ())]

    def test_an_omitted_part_drops_its_control(self):
        fitted = document(bound(OmittedControl(fitted=True)))
        self.assertEqual(sorted(fitted['controls']),
                         ['spare dial', 'turn units', 'units dial'])
        self.assertEqual(self.spare_children(fitted), ['dial'])

        dropped = document(bound(OmittedControl(fitted=False)))
        # The document genuinely does not contain that part.
        self.assertEqual(self.spare_children(dropped), [])
        self.assertEqual(sorted(dropped['controls']),
                         ['turn units', 'units dial'])
        # ... and the other entries are published unchanged.
        for name in ('units dial', 'turn units'):
            self.assertEqual(dropped['controls'][name],
                             fitted['controls'][name])

    def test_an_omitted_part_does_not_refuse_the_build(self):
        published = self.built(OmittedControl(fitted=False))
        self.assertEqual(published['version'], 5)
        self.assertEqual(sorted(published['controls']),
                         ['turn units', 'units dial'])


class SelectedPlacementTest(BaseNodeTest):
    """(2.1, 2.2) A sliding control, and a control that says which
    placement its gesture belongs to.

    OpenSpec change ``direct-part-motion``. Where inference over a
    single rotational joint published the joint node's own frame and
    nothing else, a translational or explicitly selected coordinate
    publishes `operation_span` too: the half-open pair of indices into
    the joint node's own `operations` identifying the COMPLETE block
    that coordinate placed. Everything outside and after that block
    carries the gesture's frame into the world; nothing inside it, and
    nothing before it, does.
    """

    def controls(self, factory):
        return document(bound(factory()))['controls']

    def node_of(self, published, path):
        node = published['root']
        for name in path:
            found = [child for child in node.get('children', ())
                     if child['name'] == name]
            self.assertEqual(len(found), 1, name)
            node = found[0]
        return node

    def block(self, published, entry):
        """The operations the entry's span selects, read out of the
        document's own tree exactly as a consumer reads them."""
        start, end = entry['operation_span']
        return self.node_of(published, entry['joint'])['operations'][start:end]

    ##############################################
    # A sliding selector

    def test_a_sliding_selector_publishes_its_physical_direction(self):
        entry = self.controls(Selector)['slide selector']
        self.assertEqual(entry['kind'], 'slide')
        self.assertEqual(entry['input'], 'setting')
        self.assertEqual(entry['per_unit'], 6.0)
        self.assertEqual(entry['coordinate'], 'selector.travel')
        self.assertEqual(entry['axis'], [0.0, 1.0, 0.0])

    def test_a_slide_entrys_fields_are_in_the_specs_order(self):
        table = self.controls(Selector)
        self.assertEqual(list(table['slide selector']),
                         ['kind', 'part', 'input', 'per_unit', 'joint',
                          'coordinate', 'axis', 'origin', 'operation_span'])
        self.assertEqual(list(table['press selector']),
                         ['kind', 'part', 'instruction', 'joint',
                          'coordinate', 'axis', 'origin', 'operation_span'])

    def test_a_slides_span_selects_the_actual_prismatic_placement(self):
        published = document(bound(Selector()))
        entry = published['controls']['slide selector']
        self.assertEqual(entry['operation_span'], [0, 1])
        self.assertEqual(self.block(published, entry),
                         [['t', ['0', 'selector.travel', '0']]])

    def test_a_press_on_a_prismatic_part_needs_no_rotation(self):
        published = document(bound(Selector()))
        entry = published['controls']['press selector']
        self.assertEqual(entry['instruction'], 'One detent')
        self.assertEqual(entry['operation_span'],
                         published['controls']['slide selector']
                         ['operation_span'])
        self.assertEqual(self.block(published, entry)[0][0], 't')

    def test_the_domain_stays_the_programs_to_publish(self):
        published = document(bound(Selector()))
        coordinates = published['program']['coordinates']
        for name, entry in published['controls'].items():
            with self.subTest(control=name):
                self.assertEqual(
                    coordinates[entry['coordinate']]['domain'],
                    'translational')
                self.assertNotIn('domain', entry)
                self.assertNotIn('unit', entry)

    ##############################################
    # Two placements on one body

    def test_two_controls_identify_two_placements_on_one_body(self):
        published = document(bound(Crank()))
        lift = published['controls']['lift crank']
        rotate = published['controls']['rotate crank']
        self.assertEqual(lift['part'], rotate['part'])
        self.assertEqual(lift['joint'], rotate['joint'])
        self.assertNotEqual(lift['coordinate'], rotate['coordinate'])
        self.assertNotEqual(lift['operation_span'],
                            rotate['operation_span'])

    def test_each_span_is_the_complete_block_of_its_own_coordinate(self):
        """The crank's pivot is off its own origin, so the turn's block
        is the two centring translations with the rotation between
        them -- one unit, at one slot, and the slide's own translation
        outside it."""
        published = document(bound(Crank()))
        turn = published['controls']['rotate crank']
        lift = published['controls']['lift crank']
        self.assertEqual(turn['operation_span'], [0, 3])
        self.assertEqual(self.block(published, turn),
                         [['t', ['-0.0', '-12.0', '-0.0']],
                          ['r', 'crank.turn', [0, 0, 1]],
                          ['t', ['0.0', '12.0', '0.0']]])
        self.assertEqual(lift['operation_span'], [3, 4])
        self.assertEqual(self.block(published, lift),
                         [['t', ['0', '0', 'crank.lift']]])

    def test_the_pivot_the_turn_names_is_the_one_it_turns_about(self):
        turn = self.controls(Crank)['rotate crank']
        self.assertEqual(turn['axis'], [0.0, 0.0, 1.0])
        self.assertEqual(turn['origin'], [0.0, 12.0, 0.0])

    def test_a_selected_button_carries_the_span_of_what_it_names(self):
        table = self.controls(Crank)
        self.assertEqual(table['turn crank']['operation_span'],
                         table['rotate crank']['operation_span'])
        self.assertEqual(table['turn crank']['coordinate'], 'crank.turn')

    def test_an_inner_motion_does_not_rotate_an_outer_joints_axis(self):
        """`swing` is inner and turns about X; `shift` is outer and
        slides along Y. The document distinguishes the two blocks, so
        the outer axis is never carried through the inner rotation --
        which is exactly what the whole body's world matrix would do.
        """
        published = document(bound(Tilted()))
        swing = published['controls']['swing stack']
        shift = published['controls']['shift stack']
        self.assertEqual(swing['axis'], [1.0, 0.0, 0.0])
        self.assertEqual(shift['axis'], [0.0, 1.0, 0.0])
        self.assertEqual(swing['operation_span'], [0, 1])
        self.assertEqual(shift['operation_span'], [1, 2])
        self.assertEqual(self.block(published, swing),
                         [['r', 'stack.swing', [1, 0, 0]]])
        self.assertEqual(self.block(published, shift),
                         [['t', ['0', 'stack.shift', '0']]])
        # The operations after the SHIFT block are the rest placement
        # alone: the outer joint's frame is its parent's, and no joint
        # of its own body stands between them.
        operations = self.node_of(published, shift['joint'])['operations']
        self.assertEqual(operations[shift['operation_span'][1]:],
                         [['t', ['0.0', '0.0', '15.0']]])

    def test_an_ancestors_placement_is_the_one_a_selection_names(self):
        published = document(bound(Register()))
        shift = published['controls']['shift register']
        self.assertEqual(shift['joint'], ['register'])
        self.assertEqual(self.block(published, shift),
                         [['t', ['register.travel', '0', '0']]])
        turn = published['controls']['turn marker']
        self.assertEqual(turn['joint'], ['register', 'marker'])
        self.assertEqual(self.block(published, turn),
                         [['r', 'register.marker.turn', [0, 0, 1]]])

    ##############################################
    # What does not move

    def test_an_inferred_rotational_entry_gains_no_field(self):
        for name, entry in document(bound(Columns()))['controls'].items():
            with self.subTest(control=name):
                self.assertNotIn('operation_span', entry)

    def test_the_inferred_document_is_the_one_published_at_the_base(self):
        """`touched_columns.json` is `Columns`' whole document as the
        producer published it before this change: the controls table,
        the program and every other byte."""
        published = document(bound(Columns()))

        def normalized(root):
            root['mtime'] = None
            for child in root.get('children', ()):
                normalized(child)

        normalized(published['root'])
        with open(os.path.join(BASE_DOCUMENTS,
                               'touched_columns.json')) as handle:
            expected = handle.read()
        self.assertEqual(json.dumps(published, indent=2) + '\n', expected)

    def test_the_version_does_not_move_for_a_span(self):
        for factory in (Selector, Crank, Tilted, Register):
            with self.subTest(root=factory.__name__):
                self.assertEqual(document(bound(factory()))['version'], 5)

    def test_a_span_carries_no_expression_into_the_bindings(self):
        published = document(bound(Crank()))
        text = json.dumps(published['controls'])
        for entry in published.get('bindings', ()):
            self.assertNotIn(entry['name'], text)

    def test_republishing_a_selected_document_is_byte_identical(self):
        self.assertEqual(json.dumps(document(bound(Crank()))),
                         json.dumps(document(bound(Crank()))))

    def test_a_signed_slide_ratio_keeps_its_sign(self):
        """`reach` drives the outer slide at `-2.5`: a gesture scaled by
        a signed number carries the sign, or a drag runs backwards."""
        table = self.controls(Tilted)
        self.assertEqual(table['shift stack']['per_unit'], -2.5)
        self.assertEqual(table['shift stack']['input'], 'reach')

    def test_a_slide_that_does_not_move_its_part_is_refused(self):
        """The export delta's refusal, reached through a SLIDE."""
        class Disengaged(AssemblyNode):
            time = Time.running()
            setting = Driver(default=0.0, unit='step')
            spare = Driver(default=0.0, unit='step')
            selector = SlideKnob()
            (setting & spare).drives(selector.travel,
                                     law=lambda source, target:
                                     lambda a, b: 6.0 * a)
            instructions = {
                'One detent': Instruction(by={'setting': 1.0}, duration=1.0),
            }
            controls = {'slide selector': Slide(selector.knob, spare)}

        with self.assertRaises(ValueError) as raised:
            document(bound(Disengaged()))
        message = str(raised.exception)
        self.assertIn('slide selector', message)
        self.assertIn('spare', message)
        self.assertIn('does not move', message)


class SelfReadDocumentTest(BaseNodeTest):
    """Schema v6: a program carrying a law that reads the coordinate it
    drives.

    OpenSpec change ``read-the-driven-coordinate``. The shape of the
    document does not change: the self-read is ``needs`` intersected with
    ``gives``, no key is added for it, and a law edge's expressions still
    read exactly the ids in ``needs``. The VERSION changes, because a
    version 5 consumer would evaluate such an edge as the difference of
    its two endpoint evaluations, freeze the branch that reading selects
    and move the part by a different mechanism in silence.
    """

    def clearing(self):
        return document(bound(Clearing()))

    def law_edge(self, published, coordinate):
        for entry in published['program']['edges']:
            if entry['kind'] == 'law' and coordinate in entry['gives']:
                return entry
        raise AssertionError(f'no law edge gives {coordinate}')

    def test_a_program_with_a_self_read_law_is_a_version_6_document(self):
        published = self.clearing()

        self.assertEqual(published['version'], 6)
        edge = self.law_edge(published, 'wheel.turn')
        self.assertEqual(edge['needs'], ['setter', 'ring', 'wheel.turn'])
        self.assertEqual(edge['gives'], ['wheel.turn'])

    def test_the_expressions_free_names_are_exactly_the_needs(self):
        published = self.clearing()
        edge = self.law_edge(published, 'wheel.turn')

        names = free_names_of(resolved(published, edge['expressions'][0]))
        self.assertEqual(names, set(edge['needs']))

    def test_no_key_was_added_to_the_program_for_the_read(self):
        reading = self.clearing()['program']
        plain = document(bound(PlainClearing()))['program']

        self.assertEqual(sorted(reading), sorted(plain))
        self.assertEqual(sorted(reading['edges'][0]),
                         sorted(plain['edges'][0]))

    def test_the_plan_skeleton_does_not_name_the_driven_coordinate(self):
        published = self.clearing()
        edge = self.law_edge(published, 'wheel.turn')
        plan = edge['plans'][0]

        skeleton = free_names_of(resolved(published, plan['skeleton']))
        self.assertNotIn('wheel.turn', skeleton)
        levels = [free_names_of(resolved(published, jump['level']))
                  for jump in plan['jumps']]
        self.assertTrue(any('wheel.turn' in names for names in levels))

    def test_a_program_with_no_self_read_law_is_still_version_5(self):
        self.assertEqual(document(bound(PlainClearing()))['version'], 5)
        self.assertEqual(document(bound(Train()))['version'], 5)

    def test_the_document_is_the_committed_version_6_fixture(self):
        published = self.clearing()
        published['root']['mtime'] = None
        for child in published['root'].get('children', ()):
            child['mtime'] = None
        with open(os.path.join(BASE_DOCUMENTS, 'clearing.json')) as handle:
            expected = handle.read()
        self.assertEqual(json.dumps(published, indent=2) + '\n', expected)

    def test_the_viewer_warning_names_the_version_written(self):
        from solid_node.viewers import bundle

        with patch.object(bundle, 'describe',
                          return_value={'documentVersions': [1, 2, 3, 4, 5],
                                        'version': '0.1.0'}):
            message = bundle.unreadable_document(6)
        self.assertIn('version 6', message)
        self.assertIn('1, 2, 3, 4, 5', message)
        self.assertIn('solid-node-viewer 0.1.0', message)
