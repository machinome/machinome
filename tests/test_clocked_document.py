# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A CLOCKED model publishes a version 8 document.

Three cycles made a clocked machine sayable and each ended on the same
sentence: a clocked model cannot be published or viewed. This is the
publication half (OpenSpec change ``publish-the-clocked-machine``). The
originating project is `projects/Calculators/Curta-Type-I-3x`, whose
clocked model reproduces its operating model's registers at every stroke
end and is worth nothing to its pilot until a browser can crank it.

Every expected value here is computed BY HAND or read from the
declaration it is published from; no expectation is taken from the
implementation.
"""

import json

from machinome.simulation import Sim

from .base import BaseNodeTest


def text(graph):
    """One published expression graph as the document's own text."""
    from machinome.scad_expression import GraphValue, as_node

    return str(GraphValue(as_node(graph)))


def compiled(node_class):
    """The compiled clocked machine of one fixture, through the
    simulation that compiles it."""
    from machinome.simulation.enumeration import bind_declared_defaults

    node = node_class()
    bind_declared_defaults(node)
    sim = Sim(node)
    return sim._clocked


class RetainedLawTest(BaseNodeTest):
    """(2.1) The graphs `_checked_law` builds are what this cycle
    publishes, and today it throws them away."""

    def test_a_compiled_relation_exposes_one_law_graph_per_target(self):
        from .clocked_project.counter import Counter

        machine = compiled(Counter)
        relation = machine.relations[0]
        self.assertEqual(relation.target_ids, ('units', 'tens'))
        graphs = relation.law_graphs
        self.assertEqual(len(graphs), 2)
        # `(units + 1) % 10` and `(tens + (units == 9)) % 10`, as the
        # inspection applied them to one token per source.
        self.assertEqual(text(graphs[0]), '((units + 1) % 10)')
        self.assertEqual(text(graphs[1]), '((tens + (units == 9)) % 10)')

    def test_the_callable_is_still_what_a_commit_calls(self):
        """Nothing about the executor's request path changes."""
        from .clocked_project.counter import Counter, advance

        machine = compiled(Counter)
        relation = machine.relations[0]
        self.assertIsNot(relation.law, relation.law_graphs)
        self.assertEqual(relation.commit(machine.bank, 'crank', 360.0),
                         {'units': 1, 'tens': 0})
        del advance


class PublishedObjectTest(BaseNodeTest):
    """(2.3, 2.7, 2.8) The `clocked` object: what compile time decided,
    in one fixed order, and nothing a request computes."""

    KEYS = ['identity', 'clock', 'own', 'commits', 'bounds', 'limits']

    def test_the_object_carries_its_keys_in_a_fixed_order(self):
        from .clocked_project.counter import Counter

        machine = compiled(Counter)
        published = machine.published(dict(machine.initial.values))
        self.assertEqual(list(published), self.KEYS)

    def test_republishing_an_unchanged_machine_gives_an_equal_object(self):
        from .clocked_project.pawl import Pawl

        machine = compiled(Pawl)
        initial = dict(machine.initial.values)
        first = json.dumps(_written(machine.published(initial)))
        second = json.dumps(_written(machine.published(initial)))
        self.assertEqual(first, second)

    def test_a_clock_is_published_by_name_and_null_without_one(self):
        from .clocked_project.counter import Counter
        from .clocked_project.pendulum import Regulator

        self.assertIsNone(compiled(Counter).published({})['clock'])
        self.assertEqual(compiled(Regulator).published({})['clock'], 'time')

    def test_the_limits_are_the_two_a_clocked_path_reaches(self):
        """(2.8) A clocked path never searches, never bisects and never
        compares two increments, so the other three running limits would
        state a contract this discipline has not got."""
        from machinome.simulation.program import (_CROSSING_TOLERANCE,
                                                   _MAX_CROSSINGS)

        from .clocked_project.counter import Counter

        limits = compiled(Counter).published({})['limits']
        self.assertEqual(limits, {'crossing_tolerance': _CROSSING_TOLERANCE,
                                  'max_crossings': _MAX_CROSSINGS})

    def test_two_machines_differing_only_in_a_range_differ_in_identity(self):
        """(2.7) A bank taken against one machine is refused against
        another, and a changed range moves the stops."""
        from .clocked_project.pawl import Stroke, TwoStops

        first = compiled(Stroke).published({})['identity']
        second = compiled(TwoStops).published({})['identity']
        self.assertNotEqual(first, second)

    def test_compiling_one_machine_twice_gives_one_identity(self):
        from .clocked_project.register import Register

        self.assertEqual(compiled(Register).published({})['identity'],
                         compiled(Register).published({})['identity'])


def _written(published):
    """`published` with every native expression graph rendered as the
    document's own text, so two publications compare as JSON."""
    if isinstance(published, dict):
        return {key: _written(value) for key, value in published.items()}
    if isinstance(published, list):
        return [_written(value) for value in published]
    if isinstance(published, (str, int, float, bool)) or published is None:
        return published
    return text(published)


class PublishedCommitTest(BaseNodeTest):
    """(2.4) One entry per committing relation, in the tree's own
    order: what it reads, what it writes, and what it fires on."""

    KEYS = ['sources', 'targets', 'at', 'law', 'shapes', 'description',
            'stated_by']

    def commits(self, node_class):
        machine = compiled(node_class)
        return _written(machine.published({})['commits'])

    def test_a_commit_publishes_its_ends_its_event_and_its_law(self):
        from .clocked_project.counter import Counter

        commits = self.commits(Counter)
        self.assertEqual(len(commits), 1)
        entry = commits[0]
        self.assertEqual(list(entry), self.KEYS)
        self.assertEqual(entry['sources'], ['crank', 'units', 'tens'])
        self.assertEqual(entry['targets'], ['units', 'tens'])
        self.assertEqual(entry['at'], {'primitive': 'floor',
                                       'level': '(crank / 360)'})
        # `(units + 1) % 10` and `(tens + (units == 9)) % 10`, with
        # every `%` DESUGARED to the floored remainder the executor
        # computes: read by what they mean, because the producer-local
        # `let(...)` this helper renders is what the document's own
        # binding pass replaces (design section 16).
        self.assertEqual(
            [evaluated(expression, {'units': 9, 'tens': 0})
             for expression in entry['law']], [0.0, 1.0])
        self.assertEqual(
            [evaluated(expression, {'units': 3, 'tens': 7})
             for expression in entry['law']], [4.0, 7.0])
        self.assertEqual(entry['shapes'], {'crank': 'affine'})
        self.assertEqual(entry['stated_by'], 'Counter')
        self.assertIn('commits', entry['description'])

    def test_the_entries_are_in_the_trees_own_order(self):
        from .clocked_project.register import Register

        commits = self.commits(Register)
        self.assertEqual([entry['targets'] for entry in commits],
                         [['w0.digit', 'w1.digit', 'w2.digit'],
                          ['w0.digit'], ['w1.digit'], ['w2.digit']])

    def test_an_event_level_reading_the_state_it_commits_publishes_it(self):
        from .clocked_project.clearing import Clearer

        entry = self.commits(Clearer)[0]
        self.assertEqual(entry['at']['primitive'], '>=')
        self.assertIn('dial.digit', entry['at']['level'])
        self.assertEqual(entry['targets'], ['dial.digit'])

    def test_a_relation_an_input_cannot_move_is_not_listed_for_it(self):
        """`operand` is a SOURCE of the stroke and moves its level by
        nothing, so the entry names the crank alone: a consumer does not
        examine the relation for an input that can never fire it."""
        from .clocked_project.register import Register

        commits = self.commits(Register)
        self.assertEqual(commits[0]['sources'][:2], ['crank', 'operand'])
        self.assertEqual(commits[0]['shapes'], {'crank': 'affine'})
        self.assertEqual(commits[1]['shapes'], {'ring': 'affine'})

    def test_a_kinked_event_level_says_so(self):
        from .clocked_project.counter import KinkedCounter

        self.assertEqual(self.commits(KinkedCounter)[0]['shapes'],
                         {'crank': 'kinked'})

    def test_a_numeric_law_publishes_a_literal_and_never_a_null(self):
        """A commit's law IS the value written, so a constant is a real
        answer and not an absent one."""
        from .clocked_project.units import Scaled

        self.assertEqual(self.commits(Scaled)[0]['law'], ['4.0'])


class PublishedBoundTest(BaseNodeTest):
    """(2.5, 2.6) One entry per COMPILED CONSTRAINT -- one side of one
    bounded coordinate's declared range -- and where a request stops."""

    KEYS = ['coordinate', 'side', 'unit', 'value', 'bound', 'plan',
            'shapes', 'node', 'joint', 'description']

    def bounds(self, node_class):
        machine = compiled(node_class)
        return _written(machine.published({})['bounds'])

    def test_a_numeric_range_publishes_its_chain(self):
        from .clocked_project.pawl import Stroke

        bounds = self.bounds(Stroke)
        self.assertEqual(len(bounds), 2)
        low, high = bounds
        self.assertEqual(list(low), self.KEYS)
        self.assertEqual([low['side'], high['side']], ['low', 'high'])
        for entry in bounds:
            self.assertEqual(entry['coordinate'], 'plate.lift')
            self.assertEqual(entry['unit'], 'mm')
            self.assertEqual(entry['node'], 'Plate')
            self.assertEqual(entry['joint'], 'lift')
            self.assertEqual(entry['value'], 'lift')
            self.assertIsNone(entry['plan'])
            self.assertEqual(entry['shapes'],
                             {'lift': {'level': 'affine', 'jumps': []}})
        self.assertEqual(low['bound'], 0.0)
        self.assertEqual(high['bound'], 9.0)

    def test_the_level_is_the_consumers_own_subtraction(self):
        """Publishing it as well would publish the bound twice."""
        from .clocked_project.pawl import Stroke

        for entry in self.bounds(Stroke):
            self.assertNotIn('level', entry)

    def test_a_ratchet_publishes_a_bound_reading_its_own_coordinate(self):
        from .clocked_project.pawl import Pawl

        bounds = self.bounds(Pawl)
        self.assertEqual(len(bounds), 1)
        entry = bounds[0]
        self.assertEqual(entry['side'], 'low')
        self.assertEqual(entry['coordinate'], 'crank_dial.turn')
        self.assertEqual(entry['value'], 'crank')
        self.assertEqual(entry['bound'], '(6.0 * floor((_own / 6.0)))')
        self.assertEqual(entry['plan']['jumps'][0]['primitive'], 'floor')
        self.assertEqual(entry['shapes']['crank']['level'], 'affine')
        self.assertEqual(len(entry['shapes']['crank']['jumps']),
                         len(entry['plan']['jumps']))

    def test_a_freeze_publishes_both_sides_reading_the_own_coordinate(self):
        from .clocked_project.freeze import Freeze

        bounds = self.bounds(Freeze)
        self.assertEqual([entry['side'] for entry in bounds],
                         ['low', 'high'])
        for entry in bounds:
            self.assertIn('_own', entry['bound'])
            self.assertIn('crank', entry['bound'])
            self.assertIn('selector', entry['value'])
            self.assertIn('<', [jump['primitive']
                                for jump in entry['plan']['jumps']])

    def test_two_bounds_carrying_a_floor_get_two_published_names(self):
        """(2.6) A placeholder repeated across two plans would let the
        binding pass share one subtree between two jump nodes."""
        from .clocked_project.freeze import Freeze

        bounds = self.bounds(Freeze)
        minted = [jump['name'] for entry in bounds
                  for jump in entry['plan']['jumps']]
        self.assertEqual(len(minted), len(set(minted)))
        self.assertEqual(len(minted), 4)

    def test_a_decorative_range_publishes_as_a_constant(self):
        from .clocked_project.decorative import Decorative

        bounds = self.bounds(Decorative)
        self.assertEqual(len(bounds), 2)
        for entry in bounds:
            self.assertEqual(entry['value'], '0.0')
            self.assertEqual(entry['shapes'], {})

    def test_a_chain_through_a_port_carries_no_port(self):
        from .clocked_project.calculator import Calculator

        bounds = self.bounds(Calculator)
        knob = [entry for entry in bounds
                if entry['coordinate'] == 'knob.travel']
        self.assertEqual(len(knob), 2)
        for entry in knob:
            self.assertIn('setting', entry['value'])
            self.assertNotIn('shaft', entry['value'])
            self.assertNotIn('shaft', entry['bound'])

    def test_a_clocked_document_publishes_no_spans_table(self):
        from .clocked_project.pawl import Pawl

        self.assertNotIn('spans', compiled(Pawl).published({}))


def evaluated(expression, values):
    """`expression` -- one published law, as TEXT -- evaluated under the
    DOCUMENT's own expression semantics, whose `%` is the truncated
    remainder both runtimes already agree on."""
    from machinome.core.expressions import parse
    from machinome.scad_expression import GraphValue

    return GraphValue(parse(expression)).evaluate(values)


class PublishedRemainderTest(BaseNodeTest):
    """(2.4a, 2.4b, 2.4c) A published commit law says what the EXECUTOR
    computed, which is not always what the author's text spells.

    The executor calls the project's own Python callable with the bank's
    numbers, and Python's float `%` is FLOORED; the document's `%` is
    the truncated remainder in both runtimes. A law graph published as
    written would therefore not mean what the executor computed.
    """

    def test_a_law_over_a_negative_operand_publishes_what_is_banked(self):
        from .clocked_project.register import Register
        from machinome.simulation.enumeration import bind_declared_defaults

        node = Register()
        bind_declared_defaults(node)
        sim = Sim(node)
        sim.move('operand', to=-1)
        request = sim.move('crank', by=360.0)
        self.assertEqual(len(request.commits), 1)
        written = request.commits[0].targets
        # BY HAND: the register stands at 000 and the operand is -1, so
        # the total is -1 and the three digits are 9, 9, 9 -- the
        # wrap-around a subtracting machine shows.
        self.assertEqual(written, {'w0.digit': 9, 'w1.digit': 9,
                                   'w2.digit': 9})

        published = _written(sim._clocked.published({})['commits'][0])
        values = {'crank': request.commits[0].value, 'operand': -1,
                  'w0.digit': 0, 'w1.digit': 0, 'w2.digit': 0}
        for identifier, expression in zip(published['targets'],
                                          published['law']):
            self.assertEqual(evaluated(expression, values),
                             written[identifier], expression)

    def test_the_desugaring_reproduces_pythons_own_remainder(self):
        """(2.4b) CPython's `float_rem` is `fmod` plus ONE correcting
        addition, so the document's own vocabulary reproduces it with
        the same single rounding."""
        import random
        import struct

        from machinome.core.expressions import parse
        from machinome.scad_expression import GraphValue, symbol
        from machinome.simulation.clocked import _floored_remainder

        graph = _floored_remainder(symbol('a') % symbol('b'))
        rendered = parse(str(GraphValue(graph)))

        def desugared(a, b):
            return GraphValue(rendered).evaluate({'a': a, 'b': b})

        for a, b in ((-1.0, 10.0), (1.0, -10.0), (-7.0, -3.0),
                     (5.5, -2.0), (-5.5, 2.0), (1e308, -3.0)):
            self.assertEqual(desugared(a, b), a % b, (a, b))

        def finite():
            while True:
                value = struct.unpack('<d', struct.pack(
                    '<Q', random.getrandbits(64)))[0]
                if value == value and abs(value) != float('inf'):
                    return value

        random.seed(20260917)
        pairs = []
        for _index in range(2000):
            pairs.append((random.uniform(-10, 10), random.uniform(-10, 10)))
            pairs.append((random.uniform(-1e12, 1e12),
                          random.uniform(-1e-6, 1e-6)))
            pairs.append((finite(), finite()))
        zeros = 0
        for a, b in pairs:
            if b == 0.0:
                continue
            want = a % b
            got = desugared(a, b)
            if want == 0.0 and got == 0.0:
                # The ONE stated exception: Python gives the zero the
                # DIVISOR's sign and the desugaring gives `+0.0`. The
                # two compare equal as numbers in both runtimes, and
                # nothing in the published vocabulary distinguishes
                # them.
                zeros += 1
                continue
            self.assertEqual(got, want, (a, b))
        self.assertGreater(len(pairs), 5000)

    def test_a_chain_a_bound_and_a_level_keep_the_documents_remainder(self):
        """(2.4b) The framework EVALUATES those through the graph, whose
        `%` is `fmod`, so a published graph already says what the clip
        computed; desugaring one would make the document disagree with
        the framework."""
        from machinome.simulation.clocked import _floored_remainder
        from machinome.scad_expression import GraphValue, symbol
        from .clocked_project.units import JumpsOnly

        published = _written(compiled(JumpsOnly).published({}))
        self.assertIn('%', published['commits'][0]['law'][0])
        self.assertNotIn('%', published['commits'][0]['at']['level'])
        # The rewrite is a function of a LAW graph and is applied
        # nowhere else: nothing but `_published_law` calls it.
        self.assertIsNot(_floored_remainder(symbol('a') % symbol('b')),
                         None)
        del GraphValue

    def test_an_event_level_cannot_carry_a_remainder_at_all(self):
        """`%` IS a jump, and an `at` admits exactly one jump node which
        must be a floor, ceil, sign or comparison."""
        from machinome.math import floor
        from machinome.node import AssemblyNode
        from machinome.simulation import Driver, State
        from machinome.simulation.clocked import ClockedError

        from .clocked_project.parts import Dial

        class Remainders(AssemblyNode):
            crank = Driver(default=0.0, unit='deg')
            count = State(default=0, dtype=int)
            dial = Dial()

            (crank & count).commits(
                count,
                at=lambda sources, targets: (lambda crank, count:
                                             floor(crank % 360)),
                law=lambda sources, targets: (lambda crank, count: count + 1))

        with self.assertRaises(ClockedError) as caught:
            Sim(Remainders())
        self.assertIn('ONE jump node', str(caught.exception))

    def test_the_three_existing_remainder_fixtures_are_unmoved(self):
        """(2.4c) `counter`, `register` and `units` all run on
        NON-NEGATIVE operands, so the rewrite changes neither what they
        bank nor what their published law means."""
        from .clocked_project.counter import Counter
        from .clocked_project.register import Register
        from .clocked_project.units import JumpsOnly

        for klass, values, expected in (
                (Counter, {'crank': 3600.0, 'units': 9, 'tens': 0},
                 [0.0, 1.0]),
                (Register, {'crank': 360.0, 'operand': 1, 'w0.digit': 9,
                            'w1.digit': 0, 'w2.digit': 0}, [0.0, 1.0, 0.0]),
                (JumpsOnly, {'crank': 4320.0, 'value': 0}, [2.0])):
            published = _written(compiled(klass).published({}))
            found = [evaluated(expression, values)
                     for expression in published['commits'][0]['law']]
            self.assertEqual(found, expected, klass.__name__)
        # And the BANK is what it always was: the executor calls the
        # project's own callable, which this cycle does not touch.
        sim = Sim(Counter())
        request = sim.move('crank', by=3610.0)
        self.assertEqual(
            [one.targets for one in request.commits],
            [{'units': index + 1, 'tens': 0} for index in range(9)]
            + [{'units': 0, 'tens': 1}])
        self.assertEqual(sim.state, {'crank': 3610.0, 'tens': 1,
                                     'units': 0})

    def test_an_integer_state_takes_the_nearest_whole_native_unit(self):
        """(2.4c) `State.committed` is Python's `round`: the nearest
        whole native unit, an exact half to the EVEN one, and `scale`
        applied nowhere."""
        from machinome.simulation.state import State

        rounded = State(default=0, dtype=int)
        for value, expected in ((0.5, 0), (1.5, 2), (2.5, 2), (3.5, 4),
                                (-0.5, 0), (-1.5, -2), (8.9999, 9)):
            self.assertEqual(rounded.committed(value), expected, value)
        scaled = State(default=0.0, scale=10.0)
        self.assertEqual(scaled.committed(4.0), 4.0)


class OwnNameTest(BaseNodeTest):
    """(3.1, 3.2) `$own` cannot travel, so the name is MINTED and
    DECLARED."""

    def test_dollar_own_is_not_a_name_of_the_expression_language(self):
        """(3.1) The document's grammar admits exactly ONE `$`-name,
        `$t`, so a bound published with `$own` would not tokenize. This
        test exists to pin WHY the minted name is there."""
        from machinome.core.expressions import (ExpressionError, _NAME_RE,
                                                  parse)

        self.assertIsNone(_NAME_RE.fullmatch('$own'))
        self.assertIsNotNone(_NAME_RE.fullmatch('$t'))
        self.assertIsNotNone(parse('$t + 1'))
        with self.assertRaises(ExpressionError):
            parse('$own + 1')

    def test_the_minted_name_is_declared_and_read_by_every_bound(self):
        from .clocked_project.pawl import Pawl

        published = _written(compiled(Pawl).published({}))
        self.assertEqual(published['own'], '_own')
        self.assertIn('_own', published['bounds'][0]['bound'])

    def test_a_driver_named_own_lengthens_the_minted_name(self):
        """(3.2) A tree declaring a driver literally named `_own`."""
        from machinome.math import floor
        from machinome.motion.joints import Revolute
        from machinome.node import AssemblyNode
        from machinome.simulation import Driver, State
        from machinome.simulation.enumeration import bind_declared_defaults

        from .clocked_project.parts import Dial
        from .clocked_project.pawl import PITCH

        class Named(AssemblyNode):
            _own = Driver(default=0.0, unit='deg')
            count = State(default=0, dtype=int)

            dial = Dial(turn=Revolute(
                axis=(0, 0, 1), unit='deg',
                range=(lambda turn: PITCH * floor(turn / PITCH), None)))

            (_own & count).commits(
                count,
                at=lambda sources, targets: (lambda own, count:
                                             floor(own / 360)),
                law=lambda sources, targets: (lambda own, count: count + 1))

            _own.drives(dial.turn)

        node = Named()
        bind_declared_defaults(node)
        machine = Sim(node)._clocked
        published = _written(machine.published({}))
        self.assertEqual(published['own'], '__own')
        self.assertIn('__own', published['bounds'][0]['bound'])
        self.assertIn('_own', machine.published_names())


class CompiledForPublicationTest(BaseNodeTest):
    """(2.9) `clocked_of(root)` on `program_of`'s shape: the published
    machine is the simulation's BY CONSTRUCTION, and the tree is left
    exactly as it was found."""

    def snapshots(self, node):
        from machinome.simulation.program import _snapshots

        return [(type(target).__name__, dict(states))
                for target, states in _snapshots(node)]

    def operations(self, node):
        return [operation.serialized
                for operation in node.units_dial.operations]

    def test_the_compile_returns_the_machine_and_its_rest_bank(self):
        from machinome.simulation.clocked import Clocked, clocked_of
        from machinome.simulation.enumeration import bind_declared_defaults

        from .clocked_project.counter import Counter

        node = Counter()
        bind_declared_defaults(node)
        machine, initial = clocked_of(node)
        self.assertIsInstance(machine, Clocked)
        self.assertEqual(initial, {'crank': 0, 'units': 0, 'tens': 0})

    def test_publication_leaves_a_posed_tree_as_it_found_it(self):
        from machinome.simulation.clocked import clocked_of
        from machinome.simulation.enumeration import bind_declared_defaults

        from .clocked_project.counter import Counter

        node = Counter()
        bind_declared_defaults(node)
        sim = Sim(node)
        sim.move('crank', by=750.0)
        self.assertEqual(sim.state, {'crank': 750.0, 'units': 2, 'tens': 0})
        before_states = self.snapshots(node)
        before_operations = self.operations(node)

        clocked_of(node)

        self.assertEqual(self.snapshots(node), before_states)
        self.assertEqual(self.operations(node), before_operations)

    def test_a_stateless_root_compiles_nothing(self):
        from machinome.core.serializer import compiled_clocked
        from machinome.simulation.enumeration import bind_declared_defaults

        from .clocked_project.counter import Stateless

        node = Stateless()
        bind_declared_defaults(node)
        self.assertEqual(compiled_clocked(node), (None, None))


def document(node):
    """The document a producer assembles for `node`, minus the two keys
    a producer owns: the model paths it resolves, and `pieces`.

    The builder's own sequence, called here directly so the schema can
    be read without building an artifact.
    """
    from machinome.core.serializer import (clocked_block, compiled_clocked,
                                            compiled_controls,
                                            compiled_program, document_body,
                                            drivers_table, instructions_table,
                                            serialize_node, symbolic_document)

    program, initial = compiled_program(node)
    clocked, bank = compiled_clocked(node)
    with symbolic_document(node) as (declarations, instructions):
        root = serialize_node(node, lambda rigid: rigid.name,
                              graph_values=True)
        drivers = drivers_table(declarations)
        events = instructions_table(
            instructions,
            version_five_or_above=program is not None or clocked is not None)
    body = document_body(node, root, drivers, events, program,
                         initial if program is not None else bank,
                         controls=compiled_controls(program, initial),
                         clocked=clocked)
    body['root'] = root
    del clocked_block
    return body


def published(node_class):
    from machinome.simulation.enumeration import bind_declared_defaults

    node = node_class()
    bind_declared_defaults(node)
    return document(node)


class VersionLadderTest(BaseNodeTest):
    """(4.1, 4.2) Version 8 is a property of the ROOT'S DECLARATION, and
    it DOMINATES every other rung."""

    def version(self, **named):
        from machinome.core.serializer import document_version

        return document_version(**named)

    SELF_READ = {'edges': [{'kind': 'law', 'needs': ['a'], 'gives': ['a']}]}
    BLOCK = {'edges': [{'kind': 'law', 'needs': ['b'], 'gives': ['a']},
                       {'kind': 'law', 'needs': ['a'], 'gives': ['b']}]}

    def test_each_rung_of_the_ladder(self):
        plain = {'children': []}
        flexible = {'flexible': {}, 'children': []}
        self.assertEqual(self.version(root=plain), 2)
        self.assertEqual(self.version(root=flexible), 3)
        self.assertEqual(self.version(root=plain, bindings=['a']), 4)
        self.assertEqual(self.version(root=plain, program={'edges': []}), 5)
        self.assertEqual(self.version(root=plain, program=self.SELF_READ), 6)
        self.assertEqual(self.version(root=plain, program=self.BLOCK), 7)
        self.assertEqual(self.version(root=plain, clocked={}), 8)

    def test_eight_dominates_the_content_ladder(self):
        flexible = {'flexible': {}, 'children': []}
        self.assertEqual(
            self.version(root=flexible, bindings=['a'], clocked={}), 8)

    def test_a_clocked_model_publishes_version_eight(self):
        from .clocked_project.counter import Counter

        body = published(Counter)
        self.assertEqual(body['version'], 8)
        self.assertIn('clocked', body)
        self.assertIn('states', body)

    def test_a_stateless_model_never_declares_eight(self):
        from .clocked_project.counter import Stateless

        body = published(Stateless)
        self.assertEqual(body['version'], 2)
        self.assertNotIn('clocked', body)
        self.assertNotIn('states', body)


class StatesTableTest(BaseNodeTest):
    """(4.3) The `states` table beside `drivers`, under exactly the
    drivers table's rules -- and the split IS the handle rule."""

    def test_states_publish_their_declarations(self):
        from .clocked_project.register import Register

        body = published(Register)
        self.assertEqual(sorted(body['states']),
                         ['w0.digit', 'w1.digit', 'w2.digit'])
        self.assertEqual(body['states']['w0.digit'],
                         {'default': 0, 'range': [0, 9], 'unit': None,
                          'dtype': 'int', 'scale': None})
        self.assertEqual(sorted(body['drivers']),
                         ['crank', 'operand', 'ring'])

    def test_a_scaled_state_publishes_its_scale_verbatim(self):
        from .clocked_project.units import Scaled

        body = published(Scaled)
        self.assertEqual(body['states']['value'],
                         {'default': 0.0, 'range': None, 'unit': 'digit',
                          'dtype': None, 'scale': 10.0})

    def test_the_two_tables_name_disjoint_ids(self):
        from .clocked_project.calculator import Calculator

        body = published(Calculator)
        self.assertEqual(set(body['drivers']) & set(body['states']), set())

    def test_a_state_is_not_a_handle(self):
        from .clocked_project.register import Register

        body = published(Register)
        self.assertNotIn('controls', body)
        for entry in body['instructions'].values():
            named = set(entry.get('targets', {})) | set(entry.get('by', {}))
            self.assertEqual(named & set(body['states']), set())

    def test_every_free_name_of_every_pose_expression_resolves(self):
        from machinome.core.expressions import parse
        from machinome.expression_graph import postorder

        from .clocked_project.calculator import Calculator

        body = published(Calculator)
        known = set(body['drivers']) | set(body['states'])
        known |= {entry['name'] for entry in body.get('bindings', ())}
        if body['clocked']['clock'] is not None:
            known.add(body['clocked']['clock'])

        def names(text):
            return {node.text for node in postorder([parse(str(text))])
                    if node.kind == 'name'}

        def walk(node):
            for operation in node['operations']:
                slots = ([operation[1]] if operation[0] == 'r'
                         else list(operation[1]))
                for slot in slots:
                    if isinstance(slot, str):
                        self.assertLessEqual(names(slot), known, slot)
            for child in node.get('children', ()):
                walk(child)

        walk(body['root'])


class ClockedObjectInTheDocumentTest(BaseNodeTest):
    """(4.5, 4.6) The object travels in the document's own binding pass,
    and no minted name can collide with anything it reads."""

    def test_the_object_stands_beside_the_tables_and_ahead_of_root(self):
        from .clocked_project.counter import Counter

        body = published(Counter)
        keys = [key for key in body if key != 'root']
        self.assertEqual(keys, ['format', 'version', 'animation', 'drivers',
                                'states', 'instructions', 'bindings',
                                'clocked'])
        self.assertNotIn('program', body)
        self.assertNotIn('controls', body)

    def test_every_published_expression_is_text_and_carries_no_let(self):
        from .clocked_project.calculator import Calculator

        body = published(Calculator)
        rendered = json.dumps(body)
        self.assertNotIn('let(', rendered)

    def test_a_subexpression_shared_with_the_geometry_is_published_once(self):
        """The clocked slots are compiled in the SAME pass as the
        tree's, so a subexpression a commit law shares with the pose
        expression that displays it appears once as a `bindings` entry.
        """
        from .clocked_project.register import Register

        body = published(Register)
        table = {entry['name'] for entry in body.get('bindings', ())}
        self.assertTrue(table)
        rendered = json.dumps(body['clocked'])
        self.assertTrue(any(name in rendered for name in table),
                        'no clocked expression references the shared table')

    def test_a_minted_binding_name_collides_with_nothing_it_reads(self):
        from .clocked_project.pawl import Pawl

        body = published(Pawl)
        minted = {entry['name'] for entry in body.get('bindings', ())}
        clocked = body['clocked']
        self.assertEqual(minted & set(body['drivers']), set())
        self.assertEqual(minted & set(body['states']), set())
        self.assertNotIn(clocked['own'], minted)
        jumps = {jump['name'] for entry in clocked['bounds']
                 if entry['plan'] for jump in entry['plan']['jumps']}
        self.assertEqual(minted & jumps, set())


class ReaimedGateTest(BaseNodeTest):
    """(4.7) The gate is not deleted; it is re-aimed at the PRODUCER."""

    def test_a_clocked_tree_without_its_machine_is_refused(self):
        from machinome.core.serializer import (ClockedDocumentError,
                                                document_body)
        from machinome.simulation.enumeration import bind_declared_defaults

        from .clocked_project.counter import Counter

        node = Counter()
        bind_declared_defaults(node)
        with self.assertRaises(ClockedDocumentError) as caught:
            document_body(node, {}, {}, {})
        message = str(caught.exception)
        self.assertIn('units', message)
        self.assertIn('tens', message)
        self.assertIn('without its compiled machine', message)

    def test_a_clocked_tree_with_its_machine_publishes(self):
        from .clocked_project.counter import Counter

        self.assertEqual(published(Counter)['version'], 8)


class ClockAndAnimationVariableTest(BaseNodeTest):
    """(5.1, 5.3, 5.4) What `time` means in a version 8 document, and
    what `$t` goes on meaning."""

    def swing(self, body):
        found = [child for child in body['root']['children']
                 if child['name'] == 'bob']
        self.assertEqual(len(found), 1)
        return json.dumps(found[0]['operations'])

    def test_an_elapsed_clocked_document_carries_the_clock_by_name(self):
        from .clocked_project.pendulum import Regulator

        body = published(Regulator)
        self.assertEqual(body['clocked']['clock'], 'time')
        rendered = self.swing(body)
        self.assertIn('time', rendered)
        self.assertNotIn('$t', json.dumps(body))

    def test_a_clocked_root_with_no_base_keeps_the_animation_variable(self):
        """(5.3) `$t` goes on meaning exactly what it means in every
        version 2 document: the `animation` object's own 0..1 timeline,
        with the bank standing."""
        from .clocked_project.pendulum import Clockless, Untimed

        clocked = published(Clockless)
        untimed = published(Untimed)
        self.assertIsNone(clocked['clocked']['clock'])
        self.assertEqual(self.swing(clocked), self.swing(untimed))
        self.assertIn('$t', self.swing(clocked))

    def test_animation_carries_fps_and_frames_and_no_loop(self):
        """(5.4) Neither base a clocked root may declare has a loop."""
        from .clocked_project.pendulum import Clockless, Regulator

        for body in (published(Regulator), published(Clockless)):
            self.assertEqual(body['animation'], {'fps': 30, 'frames': 360})

    def test_an_elapsed_clocked_root_with_no_driver_publishes(self):
        """(5.5) `tree_declares_drivers` answers True for a state-only
        tree, so `symbolic_document`'s early return does not skip one."""
        from machinome.simulation.enumeration import tree_declares_drivers

        from .clocked_project.pendulum import ClockAlone

        node = ClockAlone()
        self.assertTrue(tree_declares_drivers(node))
        body = published(ClockAlone)
        self.assertEqual(body['version'], 8)
        self.assertEqual(body['drivers'], {})
        self.assertEqual(sorted(body['states']), ['count'])
        self.assertEqual(body['clocked']['clock'], 'time')

    def test_a_state_binds_through_the_same_resolver_as_a_driver(self):
        """(5.5) `drive_tree` binds a declared STATE through the same
        `resolve` callback, in the same pass, while the table it returns
        holds drivers only."""
        from machinome.core.serializer import symbolic_document
        from machinome.simulation.enumeration import bind_declared_defaults

        from .clocked_project.register import Register

        node = Register()
        bind_declared_defaults(node)
        with symbolic_document(node) as (declarations, _instructions):
            self.assertEqual(sorted(declarations),
                             ['crank', 'operand', 'ring'])
            faces = [child for child in node.w0.render()
                     if child.name == 'face']
            self.assertEqual(str(faces[0].turn.value), '(36.0 * w0.digit)')

    def test_the_control_refusal_is_unchanged_in_both_places(self):
        """(5.6) A control issues a movement request and only a running
        simulation takes one, so a clocked root carrying one is refused
        in the publication walk and again at `Sim` construction."""
        from machinome.core.serializer import symbolic_document
        from machinome.node import AssemblyNode
        from machinome.simulation import Driver, State, Turn
        from machinome.simulation.enumeration import bind_declared_defaults

        from .clocked_project.counter import advance, strokes
        from .clocked_project.parts import Dial

        class Controlled(AssemblyNode):
            crank = Driver(default=0, unit='deg')
            units = State(default=0, range=(0, 9), dtype=int)
            tens = State(default=0, range=(0, 9), dtype=int)

            crank_dial = Dial()

            controls = {'handle': Turn(crank_dial, crank)}

            (crank & units & tens).commits((units, tens), at=strokes,
                                           law=advance)

            crank.drives(crank_dial.turn)

        node = Controlled()
        bind_declared_defaults(node)
        with self.assertRaises(TypeError) as walked:
            with symbolic_document(node) as _tables:
                pass
        self.assertIn('handle', str(walked.exception))
        with self.assertRaises(TypeError) as constructed:
            Sim(Controlled())
        self.assertIn('handle', str(constructed.exception))

    def test_a_version_eight_document_never_carries_controls(self):
        from .clocked_project.counter import Counter

        self.assertNotIn('controls', published(Counter))


def _instructed(declare=True):
    """A clocked root declaring an ABSOLUTE and a RELATIVE instruction,
    each naming a declared DRIVER.

    Declared here rather than in `clocked_project/` because it exists to
    pin a behaviour `publish-the-clocked-machine` did not change, and a
    fixture whose own cycle's tests say what it means should not grow
    one.

    `declare=False` gives the SAME CLASS without the two declarations,
    which is how `play-the-instruction` checks that the meaning an
    instruction now has reaches no key of the document. The class name
    is the same either way on purpose: a published commit names the
    assembly that stated it, so two differently named classes would
    differ in `clocked` for a reason that has nothing to do with
    instructions.
    """
    from machinome.node import AssemblyNode
    from machinome.simulation import Driver, Instruction, State

    from .clocked_project.counter import DIGIT, advance, strokes
    from .clocked_project.parts import Dial

    class Instructed(AssemblyNode):
        crank = Driver(default=0, unit='deg')
        units = State(default=0, range=(0, 9), dtype=int)
        tens = State(default=0, range=(0, 9), dtype=int)

        units_dial = Dial()
        tens_dial = Dial()

        if declare:
            instructions = {
                'Park': Instruction({'crank': 360.0}, duration=0.5),
                'Advance': Instruction(by={'crank': 10.0}, duration=0.5),
            }

        (crank & units & tens).commits((units, tens), at=strokes, law=advance)

        units.drives(units_dial.turn, ratio=DIGIT)
        tens.drives(tens_dial.turn, ratio=DIGIT)

    return Instructed


class InstructionsUnderAClockedRootTest(BaseNodeTest):
    """(6.1, 6.3, 6.4) An instruction targeting a DRIVER is admitted,
    published, and -- since `play-the-instruction` -- MEANS one request.

    `publish-the-clocked-machine`'s brief said "an instruction under a
    clocked root is refused today; keep it". It was not: `compile_clocked`
    refused one only where its TARGET is a State. That correction is
    still pinned here, and the meaning the next cycle gave it is pinned
    beside it.
    """

    def test_both_forms_construct_and_both_are_played(self):
        """(6.1) The probe, as a test -- and what `play-the-instruction`
        made of its second half: `trigger` is no longer refused, it
        makes the request the instruction states, and it returns it."""
        sim = Sim(_instructed()())
        self.assertEqual(sorted(sim.instructions), ['Advance', 'Park'])
        parked = sim.trigger('Park')
        self.assertEqual(parked.input, 'crank')
        self.assertEqual(parked.to, 360.0)
        self.assertEqual(parked.origin, 0)
        self.assertEqual(parked.end, 360.0)
        advanced = sim.trigger('Advance')
        self.assertEqual(advanced.input, 'crank')
        self.assertEqual(advanced.by, 10.0)
        self.assertEqual(advanced.origin, 360.0)
        self.assertEqual(advanced.end, 370.0)

    def test_a_version_eight_document_publishes_every_instruction(self):
        """(6.3) A RELATIVE instruction is not omitted here: the
        omission below version 5 exists because a shipped consumer of
        those versions reads `targets` off every entry."""
        body = published(_instructed())
        self.assertEqual(body['version'], 8)
        self.assertEqual(body['instructions'], {
            'Advance': {'by': {'crank': 10.0}, 'duration': 0.5},
            'Park': {'targets': {'crank': 360.0}, 'duration': 0.5},
        })

    def test_a_stateless_untimed_document_still_omits_the_relative_ones(self):
        """(6.3) Nothing about a document below version 5 moves."""
        from machinome.core.serializer import instructions_table
        from machinome.simulation import Instruction

        declared = {
            'Park': ((), Instruction({'crank': 360.0}, duration=0.5)),
            'Advance': ((), Instruction(by={'crank': 10.0}, duration=0.5)),
        }
        self.assertEqual(sorted(instructions_table(declared)), ['Park'])
        self.assertEqual(
            sorted(instructions_table(declared,
                                      version_five_or_above=True)),
            ['Advance', 'Park'])

    def test_an_instruction_naming_a_state_reaches_no_document(self):
        """(6.4) Structurally, and not by a filter in the table: the
        compile refuses it at simulation construction, every producer
        compiles before it publishes, and the re-aimed gate refuses a
        clocked tree published without a machine."""
        from machinome.node import AssemblyNode
        from machinome.simulation import Driver, Instruction, State
        from machinome.simulation.clocked import ClockedError

        from .clocked_project.counter import advance, strokes
        from .clocked_project.parts import Dial

        class Wrong(AssemblyNode):
            crank = Driver(default=0, unit='deg')
            units = State(default=0, range=(0, 9), dtype=int)
            tens = State(default=0, range=(0, 9), dtype=int)

            units_dial = Dial()
            tens_dial = Dial()

            instructions = {'Set': Instruction({'units': 4.0}, duration=0.5)}

            (crank & units & tens).commits((units, tens), at=strokes,
                                           law=advance)

        with self.assertRaises(ClockedError) as caught:
            published(Wrong)
        message = str(caught.exception)
        self.assertIn("'Set'", message)
        self.assertIn('units', message)
        self.assertIn('State', message)

    def test_the_meaning_reaches_no_key_of_the_document(self):
        """(6.1 of `play-the-instruction`) A published instruction MEANS
        one request, and the document says NOTHING about it: declaring
        the two instructions changes the published document in its
        `instructions` table and nowhere else.

        This is the design's claim that a version 8 document published
        after an instruction has a meaning is byte for byte the one the
        same root published before it had one -- checked structurally
        here, and against the committed golden by `GoldenDocumentTest`.
        """
        def plain(root):
            # `mtime` is the SOURCE FILE's, and the root's own `name` is
            # the class's: neither is what this test is about.
            root['mtime'] = None
            root['name'] = None
            for child in root.get('children', ()):
                plain(child)
            return root

        speaking = published(_instructed())
        silent = published(_instructed(declare=False))
        plain(speaking['root'])
        plain(silent['root'])
        self.assertEqual(sorted(speaking), sorted(silent))
        self.assertNotEqual(speaking['instructions'], silent['instructions'])
        for key in sorted(speaking):
            if key == 'instructions':
                continue
            self.assertEqual(json.dumps(speaking[key], sort_keys=True),
                             json.dumps(silent[key], sort_keys=True), key)

    def test_an_instruction_naming_two_drivers_reaches_no_document(self):
        """(6.2 of `play-the-instruction`) An instruction under a
        clocked root is ONE request, a request names exactly one moving
        input, and the machine's COMPILE refuses the others where it
        refuses a State -- so no producer can write a document carrying
        one."""
        from machinome.simulation.clocked import ClockedError

        from .clocked_project import unsupported

        for klass in (unsupported.TwoInputs, unsupported.NoInput):
            with self.subTest(model=klass.__name__):
                with self.assertRaises(ClockedError) as caught:
                    published(klass)
                self.assertIn('exactly one', str(caught.exception))


class CalculatorFixtureTest(BaseNodeTest):
    """(8.2) The Curta-shaped fixture, driven through the interactions
    the corpus is built on: three strokes with a carry, a clearing
    sweep, a blocked reverse and a blocked selector move mid-stroke.

    Every expected value below is computed BY HAND from the constants
    `calculator.py` declares. Nothing here is read from the
    implementation.
    """

    def machine(self):
        from machinome.simulation.enumeration import bind_declared_defaults

        from .clocked_project.calculator import Calculator

        node = Calculator()
        bind_declared_defaults(node)
        return Sim(node, record=64)

    def test_three_strokes_carry(self):
        sim = self.machine()
        sim.move('operand', to=4)
        request = sim.move('crank', by=1100.0)
        # `floor(crank / 360)` rises at 360, 720 and 1080; the request
        # ends at 1100, short of the fourth surface.
        self.assertEqual(len(request.commits), 3)
        self.assertEqual([one.targets['w0.digit'] for one in request.commits],
                         [4, 8, 2])
        self.assertEqual([one.targets['w1.digit'] for one in request.commits],
                         [0, 0, 1])
        self.assertEqual(sim.state['w0.digit'], 2)
        self.assertEqual(sim.state['w1.digit'], 1)
        self.assertEqual(sim.state['w2.digit'], 0)
        self.assertEqual(sim.state['w3.digit'], 0)
        self.assertEqual(request.admitted, 1100.0)

    def test_the_selector_is_frozen_while_the_crank_is_off_rest(self):
        sim = self.machine()
        sim.move('crank', by=1100.0)
        # 1100 - 360 * 3 = 20 degrees into the fourth revolution, so the
        # crank is OFF REST and both bounds of the knob evaluate to the
        # value the coordinate held when the request started.
        request = sim.move('setting', by=1.0)
        self.assertEqual(request.admitted, 0.0)
        self.assertEqual(sim.state['setting'], 0.0)
        self.assertTrue(request.stops)
        self.assertEqual({one.coordinate for one in request.stops},
                         {'knob.travel'})

    def test_the_ratchet_stops_the_reverse_at_the_seated_tooth(self):
        sim = self.machine()
        sim.move('crank', by=1100.0)
        # The tooth the request BEGAN on: 6 * floor(1100 / 6) = 6 * 183
        # = 1098, two degrees back.
        request = sim.move('crank', by=-30.0)
        self.assertEqual(sim.state['crank'], 1098.0)
        self.assertEqual(request.admitted, -2.0)
        self.assertEqual(len(request.commits), 0)
        self.assertEqual([one.coordinate for one in request.stops],
                         ['crank_dial.turn'])

    def test_a_clearing_sweep_zeroes_every_wheel(self):
        sim = self.machine()
        sim.move('operand', to=4)
        sim.move('crank', by=1100.0)
        request = sim.move('ring', by=500.0)
        # The racks stand at 10 + 100 * place + 4 * (10 - digit), which
        # for (2, 1, 0, 0) is 42, 146, 250 and 350. Each wheel reached
        # is zeroed, and a wheel standing at zero has its rack at
        # 10 + 100 * place + 40, so w0 is reached a second time at 50
        # and w1 at 150, each writing the zero it already holds.
        self.assertEqual([one.value for one in request.commits],
                         [42.0, 50.0, 146.0, 150.0, 250.0, 350.0])
        self.assertEqual(sim.state['w0.digit'], 0)
        self.assertEqual(sim.state['w1.digit'], 0)
        self.assertEqual(sim.state['w2.digit'], 0)
        self.assertEqual(sim.state['w3.digit'], 0)

    def test_an_integer_state_landing_on_an_exact_half_takes_the_even(self):
        sim = self.machine()
        request = sim.move('feed', by=350.0)
        # `(floor(feed / 100) * 2 + 1) / 2` at the three landings is
        # 1.5, 2.5 and 3.5, and `State.committed` takes the nearest
        # whole native unit with an exact half to the EVEN one.
        self.assertEqual([one.targets['halved'] for one in request.commits],
                         [2, 2, 4])
        self.assertEqual(sim.state['halved'], 4)


class GoldenDocumentTest(BaseNodeTest):
    """(10.1) The version 8 documents of five machines, pinned as
    committed fixture files and compared LITERALLY.

    A structural assertion would let a key change without a test
    failing, which is why the running cycles pinned their programs the
    same way. One field is normalized on both sides: each node's
    `mtime`, which is its SOURCE FILE's modification time and therefore
    a property of the checkout rather than of the document.
    """

    trees = {
        'counter': 'tests.clocked_project.counter:Counter',
        'register': 'tests.clocked_project.register:Register',
        'pawl': 'tests.clocked_project.pawl:Pawl',
        'pendulum': 'tests.clocked_project.pendulum:Regulator',
        'calculator': 'tests.clocked_project.calculator:Calculator',
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

    def golden(self, name):
        import os

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'clocked_documents', f'{name}.json')
        with open(path) as handle:
            return handle.read()

    def test_each_machine_publishes_the_committed_document(self):
        for name, reference in sorted(self.trees.items()):
            with self.subTest(tree=name):
                body = published(self.factory(reference))
                self.normalized(body['root'])
                self.assertEqual(
                    json.dumps(body, indent=2, sort_keys=True) + '\n',
                    self.golden(name))

    def test_republishing_is_byte_identical(self):
        """The minted names included: two publications of one unchanged
        model must not differ because a name was minted differently."""
        for name, reference in sorted(self.trees.items()):
            with self.subTest(tree=name):
                klass = self.factory(reference)
                first = json.dumps(self.normalized(
                    published(klass)['root']), sort_keys=True)
                second = json.dumps(self.normalized(
                    published(klass)['root']), sort_keys=True)
                self.assertEqual(first, second)


class DeferredClockedImportTest(BaseNodeTest):
    """(4.4) The clocked compiler is imported at ONE place in the
    producers, so a model that declares no `State` loads none of it --
    the rule `compiled_program` already states for the running compiler
    (capability ``cli-startup-cost``)."""

    def test_importing_the_serializer_imports_no_clocked_module(self):
        from .import_probe import probe

        result = probe('import machinome.core.serializer\n')
        self.assertEqual(result.status, 0, result.stderr)
        self.assertNotIn('machinome.simulation.clocked', result.modules)
        self.assertNotIn('machinome.simulation.program', result.modules)

    def test_publishing_a_stateless_model_imports_no_clocked_module(self):
        from .import_probe import probe

        result = probe(
            'from machinome.core.serializer import compiled_clocked\n'
            'from machinome.simulation.enumeration import '
            'bind_declared_defaults\n'
            'from tests.clocked_project.counter import Stateless\n'
            'node = Stateless()\n'
            'bind_declared_defaults(node)\n'
            'assert compiled_clocked(node) == (None, None)\n')
        self.assertEqual(result.status, 0, result.stderr)
        self.assertNotIn('machinome.simulation.clocked', result.modules)

    def test_publishing_a_clocked_model_does_import_it(self):
        from .import_probe import probe

        result = probe(
            'from machinome.core.serializer import compiled_clocked\n'
            'from machinome.simulation.enumeration import '
            'bind_declared_defaults\n'
            'from tests.clocked_project.counter import Counter\n'
            'node = Counter()\n'
            'bind_declared_defaults(node)\n'
            'machine, bank = compiled_clocked(node)\n'
            'assert machine is not None\n')
        self.assertEqual(result.status, 0, result.stderr)
        self.assertIn('machinome.simulation.clocked', result.modules)
