# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The conformance corpus: what pins the two runtimes to each other.

ADR-022's pattern, repeated for the run. `tests/running-corpus.json` is
written by `tools/generate_running_corpus.py` from the framework's OWN
run, so every expected value in it is a value the producer PRODUCED and
never one recomputed a second way -- which is what makes a disagreement
mean the consumer drifted. The framework replays it here; the browser
worker replays the same file in `solid-node-viewer` (cycle 5).

Agreement is EXACT for discrete state -- tick numbers, statuses, every
coordinate, relation, primitive, bound side and input name, every list
ORDER and a crossing's surface level -- and within `1e-9` RELATIVE for
floats, which is `run.py`'s own `_TOLERANCE`: the window inside which
the run itself declines to distinguish two increments.
"""

import json
import os
from unittest import TestCase

from solid_node.simulation import Sim

from .base import BaseNodeTest

CORPUS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      'running-corpus.json')


def corpus():
    with open(CORPUS) as handle:
        return json.load(handle)


def machine_class(name):
    from .carriage_project import machine as carriage
    from .running_project import machine as module

    found = getattr(module, name, None)
    if found is None:
        found = getattr(carriage, name)
    return found


class CorpusReplayTest(BaseNodeTest):
    """(5.1) The framework reproduces its own corpus, tick by tick."""

    def setUp(self):
        super().setUp()
        self.corpus = corpus()
        self.tolerance = self.corpus['tolerance']['float']

    def close(self, left, right, where):
        window = self.tolerance * max(1.0, abs(left), abs(right))
        self.assertLessEqual(abs(left - right), window, where)

    def replay(self, entry):
        """Construct, script and step one machine exactly as the
        generator did, and compare every tick."""
        sim = Sim(machine_class(entry['name'])(), entry['dt'],
                  record=len(entry['ticks']) + 1)
        script = {}
        for action in entry['script']:
            script.setdefault(action['tick'], []).append(action)
        handles = {}
        snapshots = {}
        crossings_seen = 0
        stops_seen = 0
        for step, expected in enumerate(entry['ticks'], 1):
            # A script entry is applied BEFORE the step it names, in
            # array order. The STEP is the position in the run, not the
            # tick: a restore takes the clock backwards, and what the
            # fixture lists is every step the run took.
            for action in script.get(step, ()):
                self.apply(sim, action, handles, snapshots)
            sim.run(entry['dt'])
            crossings = sim.crossings[crossings_seen:]
            stops = sim.stops[stops_seen:]
            crossings_seen = len(sim.crossings)
            stops_seen = len(sim.stops)
            self.compare(entry['name'], expected, sim, handles,
                         crossings, stops)

    def apply(self, sim, action, handles, snapshots):
        if 'move' in action:
            request = dict(action['move'])
            input_id = request.pop('input')
            handles[action['handle']] = sim.move(input_id, **request)
        elif 'rate' in action:
            request = dict(action['rate'])
            handles[action['handle']] = sim.rate(request['input'],
                                                 request['rate'])
        elif 'trigger' in action:
            issued = sim.trigger(action['trigger'])
            for handle, command in zip(action['handles'], issued):
                handles[handle] = command
        elif 'snapshot' in action:
            snapshots[action['snapshot']] = sim.snapshot()
        elif 'restore' in action:
            sim.restore(snapshots[action['restore']])
        else:
            self.fail(f'unknown script action {action!r}')

    def compare(self, name, expected, sim, handles, crossings, stops):
        where = f'{name} tick {expected["tick"]}'
        self.assertEqual(sim.tick, expected['tick'], where)
        bank = sim.state
        self.assertEqual(sorted(bank), sorted(expected['bank']), where)
        for coordinate, value in expected['bank'].items():
            self.close(bank[coordinate], value, f'{where} {coordinate}')

        self.assertEqual(len(crossings), len(expected['crossings']), where)
        for found, want in zip(crossings, expected['crossings']):
            self.assertEqual(found.relation, want['relation'], where)
            self.assertEqual(found.coordinate, want['coordinate'], where)
            self.assertEqual(found.primitive, want['primitive'], where)
            self.assertEqual(found.level, want['level'], where)
            self.close(found.t, want['t'], f'{where} crossing t')

        self.assertEqual(len(stops), len(expected['stops']), where)
        for found, want in zip(stops, expected['stops']):
            self.assertEqual(found.coordinate, want['coordinate'], where)
            self.assertEqual(found.bound, want['bound'], where)
            self.assertEqual(list(found.inputs), want['inputs'], where)
            self.close(found.value, want['value'], f'{where} stop value')
            self.close(found.t, want['t'], f'{where} stop t')

        self.assertEqual([entry['handle'] for entry in expected['commands']],
                         [handle for handle in handles], where)
        for entry in expected['commands']:
            command = handles[entry['handle']]
            self.assertEqual(command.status, entry['status'],
                             f'{where} {entry["handle"]}')
            self.close(command.admitted, entry['admitted'],
                       f'{where} {entry["handle"]} admitted')

    def test_the_framework_reproduces_its_own_corpus(self):
        for entry in self.corpus['machines']:
            with self.subTest(machine=entry['name'], dt=entry['dt']):
                self.replay(entry)

    def test_every_step_is_present(self):
        """Not a sample: every step the run took is listed, oldest first.

        A divergence that heals between two samples is a divergence, so
        the fixture may never SKIP FORWARD. It may go backwards, at a
        step whose script restores a snapshot -- that is the clock being
        put back, not a tick going unrecorded.
        """
        for entry in self.corpus['machines']:
            with self.subTest(machine=entry['name'], dt=entry['dt']):
                self.assertEqual(len(entry['ticks']), entry['steps'])
                restored = {action['tick'] for action in entry['script']
                            if 'restore' in action}
                previous = 0
                for step, item in enumerate(entry['ticks'], 1):
                    if step in restored:
                        previous = item['tick']
                        continue
                    self.assertEqual(item['tick'], previous + 1,
                                     f'{entry["name"]} step {step}')
                    previous = item['tick']


class CorpusDocumentTest(BaseNodeTest):
    """(5.2) The fixture carries the document it was run against, so it
    cannot drift from the producer it claims to come from."""

    def test_each_machines_real_document_reproduces_the_fixtures(self):
        from .test_running_document import document
        from solid_node.simulation.enumeration import bind_declared_defaults

        for entry in corpus()['machines']:
            with self.subTest(machine=entry['name'], dt=entry['dt']):
                node = machine_class(entry['name'])()
                bind_declared_defaults(node)
                published = document(node)
                for key in ('format', 'version', 'drivers', 'instructions',
                            'bindings', 'program'):
                    self.assertEqual(published.get(key),
                                     entry['document'].get(key), key)


class CoverageGuardTest(TestCase):
    """(5.3) The corpus's width is visible without running the
    generator: the guard is under direct test."""

    def test_the_committed_corpus_covers_every_stated_feature(self):
        from tools.generate_running_corpus import uncovered_features

        self.assertEqual(uncovered_features(corpus()['machines']), [])

    def test_a_corpus_with_no_remainder_law_is_refused(self):
        from tools.generate_running_corpus import uncovered_features

        machines = [entry for entry in corpus()['machines']
                    if entry['name'] != 'Remainder']
        missing = uncovered_features(machines)
        self.assertIn('%', missing)

    def test_a_corpus_with_no_rate_is_refused(self):
        from tools.generate_running_corpus import uncovered_features

        machines = []
        for entry in corpus()['machines']:
            copy = dict(entry)
            copy['script'] = [action for action in entry['script']
                              if 'rate' not in action]
            machines.append(copy)
        self.assertIn('a rate', uncovered_features(machines))

    def test_a_corpus_with_no_bound_reading_another_coordinate_is_refused(self):
        from tools.generate_running_corpus import uncovered_features

        machines = [entry for entry in corpus()['machines']
                    if entry['name'] != 'Captured']
        missing = uncovered_features(machines)
        self.assertIn('a bound reading another coordinate', missing)

    def test_a_corpus_with_no_stop_on_a_standing_coordinate_is_refused(self):
        from tools.generate_running_corpus import uncovered_features

        machines = []
        for entry in corpus()['machines']:
            copy = dict(entry)
            copy['ticks'] = [dict(tick, stops=[]) for tick in entry['ticks']]
            machines.append(copy)
        missing = uncovered_features(machines)
        self.assertIn('a stop reached by the motion of what a bound reads',
                      missing)

    def test_a_corpus_with_no_self_read_law_is_refused(self):
        from tools.generate_running_corpus import uncovered_features

        machines = [entry for entry in corpus()['machines']
                    if entry['name'] not in ('Clearing', 'StoppedClearing',
                                             'ShiftedCarry')]
        missing = uncovered_features(machines)
        self.assertIn('a law that reads the coordinate it drives', missing)
        self.assertIn('a self-read coordinate holding at its gate while '
                      'its input moves on', missing)
        self.assertIn('a tick carrying both a self-read crossing and a stop',
                      missing)

    def test_a_corpus_with_no_block_is_refused(self):
        """OpenSpec change ``select-the-source``: the corpus is the
        contract the browser runtime's own cycle is held to, and a
        version 7 document is the one a version 6 consumer would execute
        in the published ORDER and move by whatever that gives."""
        from tools.generate_running_corpus import uncovered_features

        machines = [entry for entry in corpus()['machines']
                    if entry['name'] not in ('ShiftedCarry', 'RangedBlock')]
        missing = uncovered_features(machines)
        self.assertIn('a switched source', missing)
        self.assertIn('a selection crossing inside a tick', missing)
        self.assertIn('a tick carrying both a selection crossing and a stop',
                      missing)

    def test_a_corpus_with_no_selection_crossing_is_refused(self):
        """Every machine kept, but no tick in which a selector's own
        surface is reached: the corpus still states the block and still
        loses the behaviour the version is for."""
        from tools.generate_running_corpus import uncovered_features

        machines = []
        for entry in corpus()['machines']:
            copy = dict(entry)
            copy['ticks'] = [dict(tick, crossings=[]) if entry['name'] in
                             ('ShiftedCarry', 'RangedBlock') else tick
                             for tick in entry['ticks']]
            machines.append(copy)
        missing = uncovered_features(machines)
        self.assertIn('a selection crossing inside a tick', missing)
        self.assertIn('a tick carrying both a selection crossing and a stop',
                      missing)
        self.assertNotIn('a switched source', missing)

    def test_a_corpus_with_no_in_block_gate_crossing_is_refused(self):
        """OpenSpec change ``pin-the-block-order``: `RangedBlock` still
        carries the block and its own selection crossing, but no
        committed machine but `ShiftedCarry` crosses a GATE of a block
        member strictly inside a tick -- so the two features are shown
        to be independent."""
        from tools.generate_running_corpus import uncovered_features

        machines = [entry for entry in corpus()['machines']
                    if entry['name'] != 'ShiftedCarry']
        missing = uncovered_features(machines)
        self.assertIn('an in-block gate crossing inside a tick', missing)
        self.assertNotIn('a switched source', missing)

    def test_a_corpus_with_no_in_block_gate_movement_is_refused(self):
        """Every machine kept, but `ShiftedCarry`'s crossings blanked:
        the corpus still states its block, and still loses the one
        behaviour a consumer that orders a block by the published
        listing cannot reproduce."""
        from tools.generate_running_corpus import uncovered_features

        machines = []
        for entry in corpus()['machines']:
            copy = dict(entry)
            copy['ticks'] = [dict(tick, crossings=[]) if entry['name'] ==
                             'ShiftedCarry' else tick
                             for tick in entry['ticks']]
            machines.append(copy)
        missing = uncovered_features(machines)
        self.assertIn('an in-block gate crossing inside a tick', missing)

    def test_a_corpus_whose_dial_never_holds_at_its_gate_is_refused(self):
        from tools.generate_running_corpus import uncovered_features

        # Every machine kept, but no tick in which a dial HOLDS while the
        # input that reaches it goes on moving: the corpus still states
        # the law and still loses the one behaviour a version 5 consumer
        # cannot reproduce.
        machines = []
        for entry in corpus()['machines']:
            copy = dict(entry)
            copy['ticks'] = [dict(tick, bank=dict(tick['bank']))
                             for tick in entry['ticks']]
            for index, tick in enumerate(copy['ticks']):
                for identifier in ('wheel.turn', 'carry.travel',
                                   'lower.turn', 'higher.turn'):
                    if identifier in tick['bank']:
                        tick['bank'][identifier] += index
            machines.append(copy)
        missing = uncovered_features(machines)
        self.assertIn('a self-read coordinate holding at its gate while '
                      'its input moves on', missing)
        self.assertNotIn('a law that reads the coordinate it drives', missing)


class BlockOrderTest(TestCase):
    """OpenSpec change ``pin-the-block-order``: the corpus pins the
    block's ORDER and not only its width. ADR-122 declares a block's
    members as an ordered LISTING that a consumer SHALL NOT execute as
    an execution order; this proves the corpus can tell the difference,
    rather than trusting the feature list of `CoverageGuardTest` as a
    proxy for it."""

    def replay_banks(self, entry):
        """Every tick's committed bank, replayed exactly as the
        generator scripted it -- no assertion, so a divergence is
        returned rather than raised."""
        sim = Sim(machine_class(entry['name'])(), entry['dt'],
                  record=len(entry['ticks']) + 1)
        script = {}
        for action in entry['script']:
            script.setdefault(action['tick'], []).append(action)
        handles, snapshots = {}, {}
        banks = []
        for step in range(1, len(entry['ticks']) + 1):
            for action in script.get(step, ()):
                if 'move' in action:
                    request = dict(action['move'])
                    handles[action['handle']] = sim.move(
                        request.pop('input'), **request)
                elif 'rate' in action:
                    handles[action['handle']] = sim.rate(
                        action['rate']['input'], action['rate']['rate'])
                elif 'trigger' in action:
                    issued = sim.trigger(action['trigger'])
                    for handle, command in zip(action['handles'], issued):
                        handles[handle] = command
                elif 'snapshot' in action:
                    snapshots[action['snapshot']] = sim.snapshot()
                elif 'restore' in action:
                    sim.restore(snapshots[action['restore']])
                else:
                    self.fail(f'unknown script action {action!r}')
            sim.run(entry['dt'])
            banks.append(dict(sim.state))
        return banks

    def disagreements(self, entry, banks, tolerance):
        """Every `(tick, coordinate, corpus value, replayed value)`
        whose two values fall outside the corpus's own tolerance
        window."""
        found = []
        for expected, got in zip(entry['ticks'], banks):
            for coordinate, value in expected['bank'].items():
                mine = got[coordinate]
                window = tolerance * max(1.0, abs(value), abs(mine))
                if abs(value - mine) > window:
                    found.append((expected['tick'], coordinate, value, mine))
        return found

    def test_a_consumer_that_executes_the_listing_order_disagrees(self):
        from solid_node.simulation import program as program_module

        fixture = corpus()
        entry = next(one for one in fixture['machines']
                     if one['name'] == 'ShiftedCarry')
        tolerance = fixture['tolerance']['float']

        unpatched = self.disagreements(
            entry, self.replay_banks(entry), tolerance)
        self.assertFalse(
            unpatched,
            'the UNPATCHED replay must reproduce the committed corpus '
            f'exactly, so the first assertion below cannot pass by '
            f'breaking the fixture instead of discriminating the order; '
            f'found {unpatched}')

        original = program_module._Block._order

        def listing_order(self, forced, left, right):
            return tuple(range(len(self.members)))

        program_module._Block._order = listing_order
        try:
            patched = self.disagreements(
                entry, self.replay_banks(entry), tolerance)
        finally:
            program_module._Block._order = original

        self.assertTrue(
            patched,
            'a consumer that executes the block\'s members in the '
            'PUBLISHED LISTING order (Sim ShiftedCarry, dt=0.05) must '
            'disagree with the producer on at least one tick\'s bank '
            '-- for example higher.turn diverging by one sixth of a '
            'turn from tick 2 onward -- and it did not, so the corpus '
            'no longer pins the block\'s order (ADR-122)')
