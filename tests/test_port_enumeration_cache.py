"""Port enumeration over completed declarative classes."""

import gc
import weakref
from unittest import TestCase

from machinome.motion.joints import Bound, Prismatic, Revolute
from machinome.motion.ports import Port, RotationalPort, declared_ports
from machinome.node import AssemblyNode


class PortEnumerationCacheTest(TestCase):
    def test_completed_class_is_traversed_once_and_returns_independent_maps(self):
        class Probe:
            reads = 0

            def __getattr__(self, name):
                if name in ('coordinates', 'coordinate'):
                    type(self).reads += 1
                raise AttributeError(name)

        class Base(AssemblyNode):
            drive = RotationalPort(unit='deg')

        class Child(Base):
            other = Probe()

        first = declared_ports(Child)
        self.assertEqual(first, {'drive': Base.drive})
        reads = Probe.reads
        self.assertGreater(reads, 0)
        first.clear()
        second = declared_ports(Child)
        self.assertEqual(second, {'drive': Base.drive})
        self.assertEqual(Probe.reads, reads)

    def test_site_joint_is_enumerated_and_specialization_can_be_collected(self):
        class Leaf(AssemblyNode):
            pass

        class Parent(AssemblyNode):
            child = Leaf(turn=Revolute(axis=(0, 0, 1), unit='deg'))

        specialized = Parent.child.node_class
        self.assertIsInstance(declared_ports(specialized)['turn'], Port)
        self.assertNotIn('turn', declared_ports(Leaf))
        reference = weakref.ref(specialized)
        del specialized, Parent
        gc.collect()
        self.assertIsNone(reference())

    def test_bound_read_during_descriptor_naming_does_not_freeze_partial_map(self):
        class Bounded(AssemblyNode):
            turn = Revolute(axis=(0, 0, 1))
            lift = Prismatic(axis=(0, 0, 1), range=(Bound(
                lambda lift, turn: turn, reads=(turn,)), 6))

        self.assertEqual(set(declared_ports(Bounded)), {'turn', 'lift'})
