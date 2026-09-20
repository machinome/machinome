# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A later free endpoint must not erase the input pushing at first contact."""

from machinome.simulation import Sim
from .base import BaseNodeTest
from .periodic_constraint_project import FixedStop, PeriodicStop, UpperPeriodicStop
from .periodic_constraint_project import RelievingStop, TimePeriodicStop, SimultaneousStop
from .periodic_constraint_project import DisengagedStop, CompoundOnlyStop


class PeriodicConstraintTest(BaseNodeTest):
    def check_stop(self, cls, target, duration=None, turns=0):
        sim = Sim(cls(), .1, record=32, state={'crank': 120 + 360 * turns})
        request = sim.move('crank', to=target + 360 * turns,
                           **({} if duration is None else {'duration': duration}))
        if duration is not None:
            sim.run(duration)
        self.assertEqual(request.status, 'blocked')
        self.assertAlmostEqual(sim.state['crank'], 125.22 + 360 * turns, places=7)
        self.assertAlmostEqual(request.admitted, 5.22, places=7)
        self.assertEqual(sim.commands, ())
        self.assertEqual(sim.stops[-1].inputs, ('crank',))
        return sim

    def test_fixed_surface_stops_long_request(self):
        self.check_stop(FixedStop, 840)

    def test_periodic_surface_stops_short_request(self):
        self.check_stop(PeriodicStop, 150)

    def test_periodic_surface_stops_timed_long_request(self):
        self.check_stop(PeriodicStop, 840, duration=2)

    def test_periodic_surface_stops_long_request(self):
        for cls in (PeriodicStop, UpperPeriodicStop):
            for target in (830, 840):
                for turns in (0, 3):
                    with self.subTest(cls=cls.__name__, target=target, turns=turns):
                        self.check_stop(cls, target, turns=turns)

    def test_retry_relief_and_idle_do_not_resume_a_blocked_request(self):
        sim = self.check_stop(PeriodicStop, 840)
        held = sim.state['crank']
        sim.run(.3)
        self.assertEqual(sim.state['crank'], held)
        retry = sim.move('crank', by=720)
        self.assertEqual(retry.status, 'blocked')
        self.assertAlmostEqual(retry.admitted, 0, places=7)
        self.assertEqual(sim.move('crank', by=-.05).status, 'completed')
        again = sim.move('crank', by=720)
        self.assertEqual(again.status, 'blocked')
        self.assertAlmostEqual(sim.state['crank'], 125.22, places=7)

    def test_independent_motion_and_snapshot_replay(self):
        sim = Sim(PeriodicStop(), .1, record=8)
        snapshot = sim.snapshot()

        def run():
            turn = sim.move('crank', to=840, duration=.1)
            free = sim.move('motor', by=10, duration=.1)
            sim.run(.1)
            self.assertEqual((turn.status, free.status), ('blocked', 'completed'))
            self.assertEqual(sim.state['free.turn'], 10)
            return dict(sim.state), turn.admitted, sim.stops[-1]

        first = run()
        sim.restore(snapshot)
        self.assertEqual(first, run())

    def test_relieving_input_completes_while_crank_stops(self):
        sim = Sim(RelievingStop(), .1, record=8)
        turn = sim.move('crank', to=840, duration=.1)
        relief = sim.move('release', by=10, duration=.1)
        sim.run(.1)
        self.assertEqual((turn.status, relief.status), ('blocked', 'completed'))
        self.assertEqual(sim.state['release'], 10)
        self.assertAlmostEqual(turn.admitted, 720 * 5.22 / 710, places=7)
        self.assertEqual(sim.stops[-1].inputs, ('crank',))

    def test_time_admission_stops_without_stopping_global_time(self):
        sim = Sim(TimePeriodicStop(), .1, record=8)
        sim.run(.1)
        self.assertAlmostEqual(sim.state['bell.turn'], -125.22, places=7)
        self.assertEqual(sim.time, .1)
        self.assertEqual(sim.state['free.turn'], 1)
        stop, = sim.stops
        self.assertEqual(stop.inputs, ())
        self.assertEqual(len(stop.time_drives), 1)
        sim.run(.1)
        self.assertAlmostEqual(sim.state['bell.turn'], -125.22, places=7)
        self.assertEqual(sim.time, .2)
        self.assertEqual(sim.state['free.turn'], 2)

    def test_simultaneous_constraints_keep_both_contacts(self):
        sim = self.check_stop(SimultaneousStop, 840)
        self.assertEqual(len(sim.stops), 2)
        self.assertEqual({s.coordinate for s in sim.stops}, {'bell.turn', 'second.turn'})
        self.assertEqual(sim.stops[0].t, sim.stops[1].t)

    def test_final_inside_assertion_still_refuses_atomically(self):
        from unittest.mock import patch
        from machinome.simulation.run import Run, StopInvariantError
        sim = Sim(PeriodicStop(), .1, record=8)
        before = sim.snapshot()
        command = sim.move('crank', to=840, duration=.1)
        with patch.object(Run, '_assert_inside', side_effect=StopInvariantError('probe')):
            with self.assertRaisesRegex(StopInvariantError, 'probe'):
                sim.run(.1)
        self.assertEqual(sim.snapshot(), before)
        self.assertEqual(sim.stops, [])
        self.assertEqual(command.status, 'refused')

    def test_corpus_guard_requires_periodic_contact(self):
        from tools.generate_running_corpus import uncovered_features
        from .test_running_corpus import corpus
        entries = [e for e in corpus()['machines'] if e['name'] != 'PeriodicStop']
        self.assertIn('a periodic contact before a free endpoint', uncovered_features(entries))

    def test_disengaged_candidate_runs_its_full_request(self):
        sim = Sim(DisengagedStop(), .1, record=8)
        crank = sim.move('crank', to=840, duration=.1)
        idle = sim.move('idle', by=100, duration=.1)
        sim.run(.1)
        self.assertEqual((crank.status, idle.status), ('blocked', 'completed'))
        self.assertEqual(sim.state['idle'], 100)
        self.assertEqual(sim.stops[-1].inputs, ('crank',))

    def test_no_individual_push_still_refuses_the_whole_tick(self):
        from machinome.simulation.run import StopInvariantError
        sim = Sim(CompoundOnlyStop(), .1, record=8)
        before = sim.snapshot()
        first = sim.move('first', by=1, duration=.1)
        second = sim.move('second', by=1, duration=.1)
        with self.assertRaises(StopInvariantError):
            sim.run(.1)
        self.assertEqual(sim.snapshot(), before)
        self.assertEqual(sim.stops, [])
        self.assertEqual((first.status, second.status), ('refused', 'refused'))

    def test_corpus_guard_requires_the_contact_outcome_and_replay(self):
        from copy import deepcopy
        from tools.generate_running_corpus import uncovered_features
        from .test_running_corpus import corpus
        for damage in ('replay', 'stops', 'status', 'target'):
            entries = deepcopy(corpus()['machines'])
            entry = next(e for e in entries if e['name'] == 'PeriodicStop')
            if damage == 'replay':
                entry['script'] = [a for a in entry['script'] if 'restore' not in a]
            elif damage == 'stops':
                entry['ticks'][0]['stops'] = []
            elif damage == 'status':
                entry['ticks'][0]['commands'][0]['status'] = 'completed'
            else:
                next(a for a in entry['script'] if 'move' in a)['move']['to'] = 150
            with self.subTest(damage=damage):
                self.assertIn('a periodic contact before a free endpoint',
                              uncovered_features(entries))

    def test_old_endpoint_attribution_breaks_the_producer_corpus(self):
        from unittest.mock import patch
        from machinome.simulation.run import Run, StopInvariantError
        from .test_running_corpus import corpus, CorpusReplayTest

        def old_group(run, constraint, admissions, values, held, contact):
            own = run.bank[constraint.identifier]
            return [candidate for candidate in constraint.candidates
                    if admissions.get(candidate, 0) and
                    run._constraint_level(constraint, held, values,
                        {candidate: admissions[candidate]}, 1, own) >
                    run._constraint_level(constraint, held, values,
                        {candidate: admissions[candidate]}, 0, own)]

        entry = next(e for e in corpus()['machines'] if e['name'] == 'PeriodicStop')
        replay = CorpusReplayTest()
        replay.tolerance = corpus()['tolerance']['float']
        with patch.object(Run, '_constraint_group', old_group):
            with self.assertRaises(StopInvariantError):
                replay.replay(entry)
        replay.replay(entry)
