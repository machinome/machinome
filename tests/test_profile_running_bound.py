"""Profile contact is a scalar term inside an existing running Bound."""

import json
import struct
import unittest
from pathlib import Path
from unittest.mock import patch

from machinome.motion.joints import Bound, Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver, Sim
from machinome.simulation.profile import ConvexProfile, profile_overlap

from .running_project.parts import Arbor
from .test_running_document import bound, document


SQUARE = ConvexProfile((
    ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)),
))


def profile_bank(profile):
    class ProfileBank(AssemblyNode):
        time = Time.running()
        crank = Driver(default=0.0, unit='deg')
        wheel = Arbor(turn=Revolute(
            axis=(0, 0, 1), unit='deg',
            range=(None, Bound(
                lambda own, crank: 10.0 - 9.5 * profile_overlap(
                    SQUARE, profile, 0.0, 0.0, right_xy=(crank, 0.0)),
                reads=(crank,)))))

        crank.drives(wheel.turn, ratio=1.0)

    return ProfileBank


class ContactBound(AssemblyNode):
    time = Time.running()
    crank = Driver(default=0.0, unit='deg')
    wheel = Arbor(turn=Revolute(
        axis=(0, 0, 1), unit='deg',
        range=(None, Bound(
            lambda own, crank: 10.0 - 9.5 * profile_overlap(
                SQUARE, SQUARE, 0.0, 0.0, right_xy=(crank, 0.0)),
            reads=(crank,)))))

    crank.drives(wheel.turn, ratio=1.0)


class ProfileRunningBoundTest(unittest.TestCase):

    def test_contact_compiles_as_existing_numeric_bound(self):
        sim = Sim(ContactBound(), dt=0.1)
        self.assertIn(('wheel.turn', 'high'), sim._run.program.constraints)
        self.assertIn('profileOverlap', sim._run.program.described())

    def test_stops_at_first_contact_and_replays(self):
        sim = Sim(ContactBound(), dt=0.1, record=8)
        initial = sim.snapshot()
        request = sim.move('crank', by=5.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(request.status, 'blocked')
        self.assertLessEqual(sim.state['wheel.turn'], 0.500001)
        record = json.loads((Path(__file__).parent / 'fixtures' /
                             'profile_overlap_v13_outcome.json').read_text())
        expected = record['expected']
        bits = lambda value: struct.pack('!d', value).hex()
        self.assertEqual(request.status, expected['status'])
        self.assertEqual(bits(request.admitted), expected['admitted_bits'])
        self.assertEqual({key: bits(value) for key, value in sim.state.items()},
                         expected['bank_bits'])
        stop, = sim.stops
        self.assertEqual(dict(tick=stop.tick, coordinate=stop.coordinate,
                              bound=stop.bound, value_bits=bits(stop.value),
                              t_bits=bits(stop.t), inputs=list(stop.inputs),
                              time_drives=list(stop.time_drives)), expected['stop'])
        reached = dict(sim.state)
        sim.restore(initial)
        sim.move('crank', by=5.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state, reached)

    def test_document_carries_one_profile_table_and_v13(self):
        body = document(bound(ContactBound()))
        self.assertEqual(body['version'], 13)
        self.assertEqual(len(body['program']['profiles']), 1)
        self.assertEqual(body['program']['profiles'][0]['polygons'], [[0, 1, 2, 3]])
        expression = body['program']['spans']['wheel.turn']['high']['expression']
        self.assertIn('profileOverlap', expression)
        self.assertIn('0, 0', expression)
        body['root']['mtime'] = 0
        body['root']['children'][0]['mtime'] = 0
        fixture = json.loads((Path(__file__).parent / 'fixtures' /
                              'profile_overlap_v13.json').read_text())
        self.assertEqual(body, fixture)

    def test_profile_content_changes_identity_and_restore_refuses(self):
        wider = ConvexProfile((
            ((0.0, 0.0), (1.1, 0.0), (1.1, 1.0), (0.0, 1.0)),
        ))
        first = Sim(profile_bank(SQUARE)(), dt=0.1)
        second = Sim(profile_bank(wider)(), dt=0.1)
        self.assertNotEqual(first._run.program.identity,
                            second._run.program.identity)
        with self.assertRaisesRegex(ValueError, 'snapshot'):
            second.restore(first.snapshot())
        self.assertEqual(len(second._run.program.profiles), 2)

    def test_no_profile_document_remains_v11_without_table(self):
        from .running_project.machine import Train

        body = document(bound(Train()))
        self.assertEqual(body['version'], 11)
        self.assertNotIn('profiles', body['program'])

    def test_older_viewer_reports_v13_unreadable(self):
        from machinome.viewers import bundle

        with patch.object(bundle, 'describe',
                          return_value={'documentVersions': list(range(1, 13)),
                                        'version': '0.7.0'}):
            warning = bundle.unreadable_document(13)
        self.assertIsNotNone(warning)
        self.assertIn('version 13', warning)


if __name__ == '__main__':
    unittest.main()
