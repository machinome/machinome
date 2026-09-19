# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Owner-scoped delivery of retained coordinates in a running tree."""

import unittest
from unittest import TestCase

import numpy as np

from machinome.core.serializer import serialize_node, symbolic_document
from machinome.motion.joints import Free, Revolute
from machinome.motion.ports import Time, get_coordinate
from machinome.node import AssemblyNode
from machinome.node.base import _compose_world_matrix
from machinome.simulation import Driver, Sim


class Wheel(AssemblyNode):
    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def simulate(self):
        if self.turn.value is None:
            self.turn = -30.0


class Ring(AssemblyNode):
    wheel = Wheel()


class Carrier(AssemblyNode):
    ring = Ring(turn=Revolute(axis=(0, 0, 1), unit='deg'))


class NestedOwners(AssemblyNode):
    time = Time.running()
    carrier_input = Driver(default=10.0, unit='deg')
    ring_input = Driver(default=-20.0, unit='deg')
    carrier = Carrier(turn=Revolute(axis=(0, 0, 1), unit='deg'))

    carrier_input.drives(carrier.turn)
    ring_input.drives(carrier.ring.turn)


class DrivenWheel(Wheel):
    trim = Driver(default=5.0, unit='deg')


class DrivenRing(AssemblyNode):
    wheel = DrivenWheel()


class DrivenCarrier(AssemblyNode):
    ring = DrivenRing(turn=Revolute(axis=(0, 0, 1), unit='deg'))


class DriversAndOwners(AssemblyNode):
    time = Time.running()
    carrier_input = Driver(default=10.0, unit='deg')
    ring_input = Driver(default=-20.0, unit='deg')
    carrier = DrivenCarrier(turn=Revolute(axis=(0, 0, 1), unit='deg'))

    carrier_input.drives(carrier.turn)
    ring_input.drives(carrier.ring.turn)


class DriverClaim(AssemblyNode):
    turn = Driver(default=4.0, unit='deg')


class DriverCollisionCarrier(AssemblyNode):
    ring = Ring(turn=Revolute(axis=(0, 0, 1), unit='deg'))
    claimant = DriverClaim()


class CoordinateDriverCollision(AssemblyNode):
    time = Time.running()
    carrier_input = Driver(default=10.0, unit='deg')
    ring_input = Driver(default=-20.0, unit='deg')
    carrier = DriverCollisionCarrier(turn=Revolute(axis=(0, 0, 1),
                                                   unit='deg'))

    carrier_input.drives(carrier.turn)
    ring_input.drives(carrier.ring.turn)


class SiteWheel(AssemblyNode):
    def simulate(self):
        if self.turn.value is None:
            self.turn = -13.0


class SiteRing(AssemblyNode):
    wheel = SiteWheel(turn=Revolute(axis=(0, 0, 1), unit='deg'))


class SiteCarrier(AssemblyNode):
    ring = SiteRing(turn=Revolute(axis=(0, 0, 1), unit='deg'))


class SiteOwners(AssemblyNode):
    time = Time.running()
    carrier_input = Driver(default=11.0, unit='deg')
    ring_input = Driver(default=-17.0, unit='deg')
    carrier = SiteCarrier(turn=Revolute(axis=(0, 0, 1), unit='deg'))

    carrier_input.drives(carrier.turn)
    ring_input.drives(carrier.ring.turn)


def rest_free(node, values):
    for name, value in values.items():
        coordinate = getattr(node.pose, name)
        if coordinate.value is None:
            setattr(node.pose, name, value)


class FloatingChild(AssemblyNode):
    pose = Free(angle_unit='deg', length_unit='mm')

    def simulate(self):
        rest_free(self, dict(x=7.0, y=8.0, z=9.0,
                             roll=10.0, pitch=11.0, yaw=12.0))


class FloatingParent(AssemblyNode):
    pose = Free(angle_unit='deg', length_unit='mm')
    child = FloatingChild()

    def simulate(self):
        rest_free(self, dict(x=1.0, y=2.0, z=3.0,
                             roll=4.0, pitch=5.0, yaw=6.0))


class MultiCoordinateOwners(AssemblyNode):
    time = Time.running()
    parent = FloatingParent()


class SingleOwner(AssemblyNode):
    time = Time.running()
    child = Wheel()


def coordinate(node, name):
    return get_coordinate(node, name)._value


def rotation(degrees):
    angle = np.deg2rad(degrees)
    cosine, sine = np.cos(angle), np.sin(angle)
    return np.array(((cosine, -sine, 0.0, 0.0),
                     (sine, cosine, 0.0, 0.0),
                     (0.0, 0.0, 1.0, 0.0),
                     (0.0, 0.0, 0.0, 1.0)))


class RetainedCoordinateOwnerTest(TestCase):
    def assert_pose_agrees(self, node, sim):
        expected = {
            'carrier.turn': node.carrier,
            'carrier.ring.turn': node.carrier.ring,
            'carrier.ring.wheel.turn': node.carrier.ring.wheel,
        }
        for identifier, owner in expected.items():
            with self.subTest(identifier=identifier):
                self.assertEqual(coordinate(owner, 'turn'),
                                 sim.state[identifier])

        owners = (node.carrier, node.carrier.ring,
                  node.carrier.ring.wheel)
        accumulated = 0.0
        for identifier, owner in zip(expected, owners):
            accumulated += sim.state[identifier]
            np.testing.assert_allclose(
                _compose_world_matrix(owner), rotation(accumulated),
                rtol=0, atol=1e-12)

    def test_parent_and_child_moves_keep_every_owner_at_its_bank_value(self):
        node = NestedOwners()
        sim = Sim(node, .1)

        sim.move('carrier_input', to=40.0)
        self.assert_pose_agrees(node, sim)
        sim.move('ring_input', to=-70.0)
        self.assert_pose_agrees(node, sim)

    def test_rebinding_the_complete_bank_is_independent_of_mapping_order(self):
        node = NestedOwners()
        sim = Sim(node, .1)
        sim.move('carrier_input', to=35.0)
        sim.move('ring_input', to=-65.0)
        bank = dict(sim.state)

        node.set_state(**bank, time=sim.time)
        normal = [coordinate(node.carrier, 'turn'),
                  coordinate(node.carrier.ring, 'turn'),
                  coordinate(node.carrier.ring.wheel, 'turn')]
        node.set_state(**dict(reversed(tuple(bank.items()))), time=sim.time)
        reverse = [coordinate(node.carrier, 'turn'),
                   coordinate(node.carrier.ring, 'turn'),
                   coordinate(node.carrier.ring.wheel, 'turn')]

        self.assertEqual(normal, [35.0, -65.0, -30.0])
        self.assertEqual(reverse, normal)
        self.assertEqual(sim.tick, 0)

    def test_bare_coordinate_ambiguity_restores_the_complete_pose(self):
        node = NestedOwners()
        sim = Sim(node, .1)
        before_bank = dict(sim.state)
        before_values = [coordinate(node.carrier, 'turn'),
                         coordinate(node.carrier.ring, 'turn'),
                         coordinate(node.carrier.ring.wheel, 'turn')]
        before_world = _compose_world_matrix(node.carrier.ring.wheel).copy()

        with self.assertRaises(ValueError) as caught:
            node.set_state(turn=99.0)

        message = str(caught.exception)
        for identifier in ('carrier.turn', 'carrier.ring.turn',
                           'carrier.ring.wheel.turn'):
            self.assertIn(identifier, message)
        self.assertEqual(sim.state, before_bank)
        self.assertEqual([coordinate(node.carrier, 'turn'),
                          coordinate(node.carrier.ring, 'turn'),
                          coordinate(node.carrier.ring.wheel, 'turn')],
                         before_values)
        np.testing.assert_allclose(
            _compose_world_matrix(node.carrier.ring.wheel), before_world,
            rtol=0, atol=0)

    def test_mixed_bare_and_qualified_coordinates_refuse_in_either_order(self):
        for entries in ({'turn': 99.0, 'carrier.turn': 40.0},
                        {'carrier.turn': 40.0, 'turn': 99.0}):
            with self.subTest(entries=tuple(entries)):
                node = NestedOwners()
                sim = Sim(node, .1)
                before_bank = dict(sim.state)
                before_values = [coordinate(node.carrier, 'turn'),
                                 coordinate(node.carrier.ring, 'turn'),
                                 coordinate(node.carrier.ring.wheel, 'turn')]
                before_world = _compose_world_matrix(
                    node.carrier.ring.wheel).copy()

                with self.assertRaises(ValueError) as caught:
                    node.set_state(**entries)

                message = str(caught.exception)
                for identifier in ('carrier.turn', 'carrier.ring.turn',
                                   'carrier.ring.wheel.turn'):
                    self.assertIn(identifier, message)
                self.assertEqual(sim.state, before_bank)
                self.assertEqual(
                    [coordinate(node.carrier, 'turn'),
                     coordinate(node.carrier.ring, 'turn'),
                     coordinate(node.carrier.ring.wheel, 'turn')],
                    before_values)
                np.testing.assert_allclose(
                    _compose_world_matrix(node.carrier.ring.wheel),
                    before_world, rtol=0, atol=0)

    def test_unambiguous_coordinate_aliases_keep_mapping_order(self):
        for entries, expected in (
                ({'child.turn': 12.0, 'turn': 11.0}, 11.0),
                ({'turn': 11.0, 'child.turn': 12.0}, 12.0)):
            with self.subTest(entries=tuple(entries)):
                node = SingleOwner()
                Sim(node, .1)
                node.set_state(**entries)
                self.assertEqual(coordinate(node.child, 'turn'), expected)

    def test_bare_and_qualified_drivers_and_time_keep_their_reach(self):
        node = DriversAndOwners()
        sim = Sim(node, .1)

        node.set_state(**{'carrier.ring.wheel.trim': 9.0, 'trim': 8.0},
                       time=2.5)

        self.assertEqual(node.carrier.ring.wheel.trim, 8.0)
        node.set_state(**{'trim': 8.0, 'carrier.ring.wheel.trim': 9.0},
                       time=2.5)

        self.assertEqual(node.carrier.ring.wheel.trim, 9.0)
        self.assertEqual(node.carrier.ring.wheel.time, 2.5)
        self.assert_pose_agrees(node, sim)

    def test_coordinate_driver_ambiguity_restores_the_complete_pose(self):
        node = CoordinateDriverCollision()
        sim = Sim(node, .1)
        before_bank = dict(sim.state)
        before_world = _compose_world_matrix(node.carrier.ring.wheel).copy()

        with self.assertRaises(ValueError) as caught:
            node.set_state(turn=99.0)

        message = str(caught.exception)
        for identifier in ('carrier.turn', 'carrier.ring.turn',
                           'carrier.ring.wheel.turn',
                           'carrier.claimant.turn'):
            self.assertIn(identifier, message)
        self.assertEqual(sim.state, before_bank)
        np.testing.assert_allclose(
            _compose_world_matrix(node.carrier.ring.wheel), before_world,
            rtol=0, atol=0)

    def test_site_declared_joints_observe_the_same_owner_boundary(self):
        node = SiteOwners()
        sim = Sim(node, .1)
        sim.move('carrier_input', to=31.0)
        sim.move('ring_input', to=-47.0)

        self.assertEqual(coordinate(node.carrier, 'turn'), 31.0)
        self.assertEqual(coordinate(node.carrier.ring, 'turn'), -47.0)
        self.assertEqual(coordinate(node.carrier.ring.wheel, 'turn'), -13.0)

    def test_multi_coordinate_joint_entries_stop_at_their_owner(self):
        node = MultiCoordinateOwners()
        sim = Sim(node, .1)
        bank = dict(sim.state)
        bank['parent.pose.roll'] = 24.0
        bank['parent.child.pose.roll'] = -36.0

        node.set_state(**bank, time=sim.time)

        self.assertEqual(coordinate(node.parent, 'pose.roll'), 24.0)
        self.assertEqual(coordinate(node.parent.child, 'pose.roll'), -36.0)

    def test_snapshot_restore_and_reset_restore_bank_slots_and_world_pose(self):
        node = NestedOwners()
        sim = Sim(node, .1)
        initial_bank = dict(sim.state)
        initial_world = _compose_world_matrix(node.carrier.ring.wheel).copy()
        sim.move('carrier_input', to=35.0)
        sim.move('ring_input', to=-55.0)
        saved = sim.snapshot()
        saved_bank = dict(sim.state)
        saved_world = _compose_world_matrix(node.carrier.ring.wheel).copy()
        sim.move('carrier_input', to=75.0)
        sim.move('ring_input', to=-5.0)

        sim.restore(saved)
        self.assertEqual(sim.state, saved_bank)
        self.assert_pose_agrees(node, sim)
        np.testing.assert_allclose(
            _compose_world_matrix(node.carrier.ring.wheel), saved_world,
            rtol=0, atol=0)

        sim.reset()
        self.assertEqual(sim.state, initial_bank)
        self.assert_pose_agrees(node, sim)
        np.testing.assert_allclose(
            _compose_world_matrix(node.carrier.ring.wheel), initial_world,
            rtol=0, atol=0)

    def test_symbolic_publication_restores_the_live_numeric_pose(self):
        node = NestedOwners()
        sim = Sim(node, .1)
        sim.move('carrier_input', to=35.0)
        sim.move('ring_input', to=-55.0)
        before_bank = dict(sim.state)
        before_values = [coordinate(node.carrier, 'turn'),
                         coordinate(node.carrier.ring, 'turn'),
                         coordinate(node.carrier.ring.wheel, 'turn')]
        before_world = _compose_world_matrix(node.carrier.ring.wheel).copy()

        with symbolic_document(node):
            published = serialize_node(node, lambda rigid: rigid.name,
                                       graph_values=True)

        carrier = next(child for child in published['children']
                       if child['name'] == 'carrier')
        ring = next(child for child in carrier['children']
                    if child['name'] == 'ring')
        wheel = next(child for child in ring['children']
                     if child['name'] == 'wheel')
        for owner, identifier in (
                (carrier, 'carrier.turn'),
                (ring, 'carrier.ring.turn'),
                (wheel, 'carrier.ring.wheel.turn')):
            rotations = [operation for operation in owner['operations']
                         if operation[0] == 'r']
            self.assertEqual(len(rotations), 1)
            self.assertEqual(rotations[0][1].text, identifier)
        self.assertEqual(sim.state, before_bank)
        self.assertEqual([coordinate(node.carrier, 'turn'),
                          coordinate(node.carrier.ring, 'turn'),
                          coordinate(node.carrier.ring.wheel, 'turn')],
                         before_values)
        np.testing.assert_allclose(
            _compose_world_matrix(node.carrier.ring.wheel), before_world,
            rtol=0, atol=0)


if __name__ == '__main__':
    unittest.main()
