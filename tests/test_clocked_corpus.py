# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The CLOCKED conformance corpus: what pins the two runtimes to each
other.

ADR-111's pattern, repeated for the clocked executor.
`tests/clocked-corpus.json` is written by
`tools/generate_clocked_corpus.py` from the framework's OWN clocked
executor, so every expected value in it is a value the producer PRODUCED
and never one recomputed a second way -- which is what makes a
disagreement mean the consumer drifted. The framework replays it here;
the browser viewer replays the same file in `solid-node-viewer` (cycle
5).

**Agreement is EXACT, bit for bit, floats included.** That is the one
substantive difference from the running corpus, which compares floats
within the run's own `1e-9`. A clocked executor has no such window:
there is no `dt`, every event is SOLVED by division, and two relations
are ONE event exactly when their landings are the SAME float -- so a
consumer agreeing only within a tolerance would merge events this
framework keeps apart and split events it joins. JSON round-trips a
Python float exactly and a JavaScript double IS a Python float, so
exactness is reachable; the file carries `"tolerance": {"float": 0.0}`
so the claim is a field of the file and not a convention of its reader.
"""

import json
import os
from unittest import TestCase

from solid_node.simulation import Sim
from solid_node.simulation.enumeration import bind_declared_defaults

from .base import BaseNodeTest

CORPUS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      'clocked-corpus.json')


def corpus():
    with open(CORPUS) as handle:
        return json.load(handle)


def machine_class(name):
    from tools.generate_clocked_corpus import machine_class as found

    return found(name)


class CorpusReplayTest(BaseNodeTest):
    """(9.6) The framework reproduces its own corpus, step by step, with
    NO tolerance anywhere in the comparison."""

    def setUp(self):
        super().setUp()
        self.corpus = corpus()

    def test_the_fixture_states_exactness_as_a_field_of_its_own(self):
        self.assertEqual(self.corpus['tolerance'], {'float': 0.0})
        self.assertEqual(self.corpus['generated_by'],
                         'tools/generate_clocked_corpus.py')

    def replay(self, entry):
        node = machine_class(entry['name'])()
        bind_declared_defaults(node)
        sim = Sim(node)
        snapshots = {}
        self.assertEqual(len(entry['requests']), len(entry['script']),
                         entry['name'])
        for index, (step, expected) in enumerate(zip(entry['script'],
                                                     entry['requests'])):
            where = f'{entry["name"]} step {index} {step}'
            self.apply(sim, step, snapshots, expected, where)

    def apply(self, sim, step, snapshots, expected, where):
        if 'move' in step:
            request = dict(step['move'])
            input_id = request.pop('input')
            before = dict(sim.state)
            refused = expected.get('refused')
            if refused is not None:
                with self.assertRaises(Exception) as caught:
                    sim.move(input_id, **request)
                self.assertEqual(type(caught.exception).__name__,
                                 refused['kind'], where)
                for name in refused['names']:
                    self.assertIn(name, str(caught.exception), where)
                # A refused request commits NOTHING: the bank after it is
                # the bank before it.
                self.assertEqual(sim.state, before, where)
                self.assertEqual(sim.state, expected['bank'], where)
                return
            result = sim.move(input_id, **request)
            self.exactly(result.admitted, expected['admitted'],
                         f'{where} admitted')
            self.assertEqual(len(result.commits), len(expected['commits']),
                             where)
            for found, want in zip(result.commits, expected['commits']):
                self.assertEqual(list(found.relations), want['relations'],
                                 where)
                self.exactly(found.fraction, want['fraction'],
                             f'{where} fraction')
                self.exactly(found.value, want['value'], f'{where} value')
                self.assertEqual(sorted(found.targets),
                                 sorted(want['targets']), where)
                for identifier, value in want['targets'].items():
                    self.exactly(found.targets[identifier], value,
                                 f'{where} {identifier}')
            self.assertEqual(len(result.stops), len(expected['stops']), where)
            for found, want in zip(result.stops, expected['stops']):
                self.assertEqual(found.coordinate, want['coordinate'], where)
                self.assertEqual(found.side, want['side'], where)
                for name in ('bound', 'value', 'input', 'fraction'):
                    self.exactly(getattr(found, name), want[name],
                                 f'{where} stop {name}')
        elif 'snapshot' in step:
            snapshots[step['snapshot']] = sim.snapshot()
        elif 'restore' in step:
            sim.restore(snapshots[step['restore']])
        elif 'reset' in step:
            sim.reset()
        else:
            self.fail(f'unknown script step {step!r}')
        bank = sim.state
        self.assertEqual(sorted(bank), sorted(expected['bank']), where)
        for identifier, value in expected['bank'].items():
            self.exactly(bank[identifier], value, f'{where} {identifier}')

    def exactly(self, found, want, where):
        """BIT FOR BIT, and not within a window: `assertEqual` on two
        doubles, with the integer/float distinction kept."""
        self.assertEqual(found, want, where)
        self.assertEqual(type(found), type(want), where)

    def test_the_framework_reproduces_its_own_corpus(self):
        for entry in self.corpus['machines']:
            with self.subTest(machine=entry['name']):
                self.replay(entry)

    def test_every_step_is_present_in_order(self):
        """Not a sample: every step the script named is recorded, in the
        order it was applied. A divergence that heals between two samples
        is a divergence."""
        for entry in self.corpus['machines']:
            with self.subTest(machine=entry['name']):
                self.assertEqual(len(entry['requests']),
                                 len(entry['script']))
                self.assertTrue(entry['script'])

    def test_one_representable_value_of_drift_fails_the_replay(self):
        """The exactness claim, PROVED rather than declared: a corpus
        whose recorded landing is moved by ONE representable value is
        rejected, where a `1e-9` window would have accepted it.

        This is the difference between the two corpora. A consumer
        within `1e-9` of a landing would merge events this framework
        keeps apart and split events it joins, and the `ties` fixtures
        are built on surfaces one representable value apart precisely so
        that difference is observable.
        """
        import math

        entry = json.loads(json.dumps(next(
            one for one in self.corpus['machines']
            if one['name'] == 'UlpPair')))
        step = next(one for one in entry['requests'] if one.get('commits'))
        drifted = math.nextafter(step['commits'][0]['value'], math.inf)
        self.assertNotEqual(drifted, step['commits'][0]['value'])
        self.assertLess(abs(drifted - step['commits'][0]['value']),
                        1e-9 * abs(drifted))
        step['commits'][0]['value'] = drifted
        with self.assertRaises(AssertionError):
            self.replay(entry)


class CorpusDocumentTest(BaseNodeTest):
    """(9.6) The fixture carries the document it was run against, so it
    cannot drift from the producer it claims to come from."""

    def test_each_machines_real_document_reproduces_the_fixtures(self):
        from tools.generate_clocked_corpus import DOCUMENT_KEYS, document_of

        for entry in corpus()['machines']:
            with self.subTest(machine=entry['name']):
                published = document_of(entry['name'])
                for key in DOCUMENT_KEYS:
                    self.assertEqual(published.get(key),
                                     entry['document'].get(key),
                                     f'{entry["name"]} {key}')

    def test_every_machine_publishes_version_eight(self):
        for entry in corpus()['machines']:
            self.assertEqual(entry['document']['version'], 8, entry['name'])
            self.assertIn('clocked', entry['document'])
            self.assertIn('states', entry['document'])


class CoverageGuardTest(TestCase):
    """(9.7) The corpus's width is visible without running the
    generator: the guard is under direct test."""

    def test_the_committed_corpus_covers_every_stated_feature(self):
        from tools.generate_clocked_corpus import uncovered_features

        self.assertEqual(uncovered_features(corpus()['machines']), [])

    def without(self, *names):
        return [entry for entry in corpus()['machines']
                if entry['name'] not in names]

    def test_a_corpus_with_no_sign_event_is_refused(self):
        from tools.generate_clocked_corpus import uncovered_features

        self.assertIn('sign', uncovered_features(self.without('Signed')))

    def test_a_corpus_with_no_ceil_event_is_refused(self):
        from tools.generate_clocked_corpus import uncovered_features

        self.assertIn('ceil', uncovered_features(self.without('Ceiling')))

    def test_a_corpus_with_no_tie_is_refused(self):
        from tools.generate_clocked_corpus import uncovered_features

        missing = uncovered_features(
            self.without('SamePair', 'SwappedPair', 'Calculator'))
        self.assertIn('two relations landing on one float', missing)

    def test_a_corpus_with_no_ulp_apart_pair_is_refused(self):
        from tools.generate_clocked_corpus import uncovered_features

        # `Signed` states it too since closure 1 of
        # `publish-the-clocked-machine`: a shuttle crossing its centre
        # takes TWO rising steps of `sign`, at 0.0 and at the float
        # above it, which are one representable value apart.
        self.assertIn('two surfaces one representable value apart',
                      uncovered_features(self.without('UlpPair', 'Signed')))

    def test_a_corpus_with_no_strict_surface_reached_exactly_is_refused(self):
        """Closure 1(a): a request ending exactly on a STRICT surface
        fires nothing, and the request that begins there fires it one
        representable value along."""
        from tools.generate_clocked_corpus import uncovered_features

        self.assertIn('a strict surface reached exactly',
                      uncovered_features(self.without('Strict')))

    def test_a_corpus_with_no_stop_from_zero_is_refused(self):
        """Closure 1(b): a bound stopping a coordinate that stands at
        exactly zero, whose own ulp is a denormal."""
        from tools.generate_clocked_corpus import uncovered_features

        # The Curta-shaped `Calculator` states it too, at the selector
        # knob's own rest: a stop read from a coordinate standing at
        # zero is not rare, which is what made the defect worth
        # closing rather than deferring.
        self.assertIn('a stop from a coordinate at zero',
                      uncovered_features(
                          self.without('Standing', 'Calculator')))

    def test_a_corpus_with_no_clip_is_refused(self):
        """Every machine kept, but no request stopped at a bound: the
        corpus still states the ranges and loses the behaviour they are
        for."""
        from tools.generate_clocked_corpus import uncovered_features

        machines = []
        for entry in corpus()['machines']:
            copy = dict(entry)
            copy['requests'] = [dict(step, stops=[]) if 'stops' in step
                                else step for step in entry['requests']]
            machines.append(copy)
        missing = uncovered_features(machines)
        self.assertIn('a request clipped at a numeric bound', missing)
        self.assertIn('a request clipped at a bound stated as an expression',
                      missing)
        self.assertIn('a request admitted at zero travel', missing)
        self.assertIn('a constraint level partitioned at its own jump '
                      'surfaces', missing)

    def test_a_corpus_with_no_zero_travel_admission_is_refused(self):
        from tools.generate_clocked_corpus import uncovered_features

        machines = []
        for entry in corpus()['machines']:
            copy = dict(entry)
            copy['requests'] = [
                dict(step, admitted=1.0) if step.get('admitted') == 0.0
                else step for step in entry['requests']]
            machines.append(copy)
        missing = uncovered_features(machines)
        self.assertIn('a request admitted at zero travel', missing)
        self.assertNotIn('a request clipped at a numeric bound', missing)

    def test_a_corpus_with_no_conflict_is_refused(self):
        from tools.generate_clocked_corpus import uncovered_features

        self.assertIn('two relations writing one state at one landing',
                      uncovered_features(self.without('Conflict')))

    def test_a_corpus_with_no_exact_half_is_refused(self):
        from tools.generate_clocked_corpus import uncovered_features

        self.assertIn('an integer state whose law lands exactly halfway',
                      uncovered_features(self.without('Calculator')))

    def test_a_corpus_with_no_port_chain_is_refused(self):
        from tools.generate_clocked_corpus import uncovered_features

        self.assertIn('a chain composed through an intermediate port',
                      uncovered_features(self.without('Calculator')))

    def test_a_corpus_with_no_negative_remainder_is_refused(self):
        """Every machine kept, but no bank carrying a negative value:
        the corpus still states the `%` law and loses the operand that
        makes the published remainder a question."""
        from tools.generate_clocked_corpus import uncovered_features

        machines = []
        for entry in corpus()['machines']:
            copy = dict(entry)
            copy['requests'] = [
                dict(step, bank={name: abs(value) for name, value
                                 in step['bank'].items()})
                for step in entry['requests']]
            machines.append(copy)
        self.assertIn('a commit law taking a remainder of a negative '
                      'operand', uncovered_features(machines))

    def test_a_corpus_with_no_clock_is_refused(self):
        from tools.generate_clocked_corpus import uncovered_features

        missing = uncovered_features(
            self.without('Regulator', 'Lift', 'ClockAlone'))
        self.assertIn('a banked clock', missing)
        self.assertIn('an event located on the clock', missing)
        self.assertIn('a time request refused for running backwards', missing)
        self.assertIn('a time request no bound clips', missing)

    def test_a_corpus_with_no_bank_returning_from_outside_is_refused(self):
        from tools.generate_clocked_corpus import uncovered_features

        self.assertIn('a bank standing outside a bound and moving back '
                      'inside it', uncovered_features(self.without(
                          'Standing')))


class NonFiniteGuardTest(TestCase):
    """Follow-up of 2026-09-17: no corpus machine records a value that is
    not a finite number."""

    def test_the_committed_corpus_records_only_finite_values(self):
        from tools.generate_clocked_corpus import non_finite_records

        self.assertEqual(non_finite_records(corpus()['machines']), [])

    def test_a_machine_banking_an_infinity_is_refused(self):
        """The fixture is not edited on disk: one committed machine is
        doctored in memory, exactly as the exactness guard's cases
        are."""
        from tools.generate_clocked_corpus import non_finite_records

        entry = dict(next(one for one in corpus()['machines']
                          if one['name'] == 'Counter'))
        requests = json.loads(json.dumps(entry['requests']))
        banked = sorted(requests[0]['bank'])[0]
        requests[0]['bank'][banked] = float('inf')
        entry['requests'] = requests
        self.assertEqual(non_finite_records([entry]),
                         [('Counter', 0, f'the step.bank.{banked}')])


class ExactnessGuardTest(TestCase):
    """(9.8) A machine whose published machinery is not exactly
    reproducible is refused, naming the operation the claim does not
    cover."""

    def test_the_committed_corpus_carries_no_inexact_operation(self):
        from tools.generate_clocked_corpus import inexact_operations

        self.assertEqual(inexact_operations(corpus()['machines']), [])

    def doctored(self, where, expression):
        """One committed machine with one published expression replaced
        -- the fixture is not edited on disk, and the guard reads the
        fixture."""
        entry = dict(next(one for one in corpus()['machines']
                          if one['name'] == 'Counter'))
        document = json.loads(json.dumps(entry['document']))
        if where == 'law':
            document['clocked']['commits'][0]['law'][0] = expression
        else:
            document['clocked']['commits'][0]['at']['level'] = expression
        entry['document'] = document
        return [entry]

    def test_a_trigonometric_commit_law_is_refused(self):
        from tools.generate_clocked_corpus import inexact_operations

        found = inexact_operations(self.doctored('law', 'sin(units)'))
        self.assertEqual(found, [('Counter', 'a commit law', 'sin')])

    def test_a_trigonometric_event_level_is_refused(self):
        from tools.generate_clocked_corpus import inexact_operations

        found = inexact_operations(self.doctored('level', 'cos(crank)'))
        self.assertEqual(found, [('Counter', 'an event level', 'cos')])

    def test_a_power_is_refused(self):
        from tools.generate_clocked_corpus import inexact_operations

        found = inexact_operations(self.doctored('law', '(units ^ 2)'))
        self.assertEqual(found, [('Counter', 'a commit law', '^')])

    def test_a_square_root_is_admitted(self):
        """IEEE requires `sqrt` correctly rounded, so one double in
        gives one double out in either runtime."""
        from tools.generate_clocked_corpus import inexact_operations

        self.assertEqual(inexact_operations(
            self.doctored('law', 'sqrt(units)')), [])

    def test_what_pins_the_documents_own_remainder_is_not_the_parity_fixture(
            self):
        """Task 9.8 asks what ADR-022's parity fixture already pins for
        the document's own `%`. RECORDED, and it is not what this
        cycle's design assumed: the fixture pins the symbolic VOCABULARY
        -- every name `solid_node.math` may emit, function for function
        across the runtimes -- and `%` is an OPERATOR, not one of those
        names, so no case of it carries a remainder at all.

        What pins the document's `%` is the RUNNING corpus, whose
        feature inventory requires it and whose `Remainder` machine
        states it, within that corpus's own `1e-9` window. This corpus
        pins the DESUGARED form a commit law carries, exactly, and its
        `bindings` tables carry the remainder as well, so the two
        spellings are pinned in two places and neither is pinned by the
        parity fixture (evidence.md, "What the parity fixture pins").
        """
        from solid_node import math as sn_math
        from solid_node.scad_expression import GraphValue, as_node
        from tools.generate_parity_fixture import vocabulary_cases
        from tools.generate_running_corpus import REQUIRED as RUNNING

        cases, _table = vocabulary_cases()
        self.assertNotIn('%', sn_math.SYMBOLIC_BUILTINS)
        written = [str(GraphValue(as_node(case['expression'])))
                   for case in cases]
        self.assertTrue(written)
        self.assertFalse([one for one in written if '%' in one])
        self.assertIn('%', RUNNING)
        remainders = [entry['expression']
                      for machine in corpus()['machines']
                      for entry in machine['document'].get('bindings', ())
                      if '%' in entry['expression']]
        self.assertTrue(remainders)
