# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""An internal node's children are refused before they are linked.

The framework links an assembly's children after the tree's render() and
simulate() have run, so inside either a read of `children` on an internal
node nothing has linked yet can only answer an empty list, and a loop
over it does nothing. AlbertPro's knees did not bend because
`LowerLeg.simulate()` rotated each of `self.children`; eight
3DPrintedClocks wall clocks coloured each of `self.children` in
render() and published those parts uncoloured. Such a read is refused
naming the assembly, the phase, the read and the declared attributes to
address instead; a read after linking, or outside any phase, answers as
before.
"""

from machinome.node.assembly import AssemblyNode
from machinome.node.declarative import StructureError
from machinome.simulation import Driver

from .base import BaseNodeTest
from .meta_project.parts import Cube

AXIS = [1, 0, 0]


def rotations(node):
    return [op.serialized for op in node.operations
            if op.serialized[0] == 'r']


class LowerLeg(AssemblyNode):
    """AlbertPro's original shin: rotates each of its children."""

    knee = Driver(default=0.0, range=(-90.0, 90.0), unit='deg')
    near = Cube()
    far = Cube()

    def simulate(self):
        for piece in self.children:
            piece.rotate(self.knee, AXIS)


class AddressedLowerLeg(AssemblyNode):
    """The same shin addressing its declared attributes, as AlbertPro's
    `simulation/leg.py` does."""

    knee = Driver(default=0.0, range=(-90.0, 90.0), unit='deg')
    near = Cube()
    far = Cube()

    def simulate(self):
        for piece in (self.near, self.far):
            piece.rotate(self.knee, AXIS)


class Tinted(AssemblyNode):
    """A clock's colour loop over its own children in render()."""

    a = Cube()
    b = Cube()

    def render(self):
        for part in self.children:
            part.color = '#ff0000'


class Islands(AssemblyNode):
    """An assembly that declares no children: its render() builds them."""

    def render(self):
        return [Cube(), Cube()]


class Face(AssemblyNode):
    """Wall clock 12's dial: colours a child's children in render()."""

    islands = Islands()

    def render(self):
        for island in self.islands.children:
            island.color = '#00ff00'


class Inner(AssemblyNode):
    part = Cube()


class Peeking(AssemblyNode):
    """Records a child's children in simulate() when the test asks."""

    inner = Inner()

    def simulate(self):
        if self.__dict__.get('_peek'):
            self.__dict__['_seen'] = self.inner.children


class LeafPeeking(AssemblyNode):
    """Records a leaf's children in simulate()."""

    near = Cube()

    def simulate(self):
        self.__dict__['_seen'] = self.near.children


class SimulatePhaseReadTest(BaseNodeTest):
    """node-model: "A simulate-phase read is refused"."""

    def assertRefusedLikeAlbert(self, refused):
        message = str(refused.exception)
        self.assertIn("LowerLeg 'LowerLeg' read self.children in simulate()",
                      message)
        self.assertIn('the list is not there yet', message)
        self.assertIn('self.near, self.far', message)

    def test_set_state_refuses_the_read(self):
        leg = LowerLeg()
        with self.assertRaises(StructureError) as refused:
            leg.set_state(knee=30.0)
        self.assertRefusedLikeAlbert(refused)
        self.assertEqual(rotations(leg.near), [])

    def test_render_refuses_the_read(self):
        with self.assertRaises(StructureError) as refused:
            LowerLeg().render()
        self.assertRefusedLikeAlbert(refused)

    def test_assemble_refuses_the_read(self):
        with self.assertRaises(StructureError) as refused:
            LowerLeg().assemble()
        self.assertRefusedLikeAlbert(refused)


class RenderPhaseReadTest(BaseNodeTest):
    """node-model: "A render-phase read is refused"."""

    def test_own_children_in_render_are_refused(self):
        tinted = Tinted()
        with self.assertRaises(StructureError) as refused:
            tinted.render()
        message = str(refused.exception)
        self.assertIn("Tinted 'Tinted' read self.children in render()",
                      message)
        self.assertIn('self.a, self.b', message)
        self.assertNotEqual(tinted.a.color, '#ff0000')

    def test_a_childs_children_in_render_are_refused(self):
        with self.assertRaises(StructureError) as refused:
            Face().render()
        message = str(refused.exception)
        self.assertIn("Face 'Face' read islands.children in render()",
                      message)
        self.assertIn('Islands declares no children', message)
        self.assertIn('its own render() returns', message)


class AddressedLoopTest(BaseNodeTest):
    """node-model: "The same loop over the declared attributes works"."""

    def test_the_declared_attributes_rotate(self):
        leg = AddressedLowerLeg()
        leg.set_state(knee=30.0)
        self.assertEqual(rotations(leg.near), [['r', '30.0', AXIS]])
        self.assertEqual(rotations(leg.far), [['r', '30.0', AXIS]])


class UnchangedReadsTest(BaseNodeTest):
    """node-model: "A read after linking, or outside any phase, is
    unchanged"."""

    def test_outside_any_phase_before_linking_is_empty(self):
        self.assertEqual(AddressedLowerLeg().children, ())

    def test_after_assemble_lists_the_linked_children(self):
        leg = AddressedLowerLeg()
        leg.set_state(knee=30.0)
        leg.assemble()
        self.assertEqual(list(leg.children), [leg.near, leg.far])

    def test_a_later_phase_reads_the_linked_children(self):
        node = Peeking()
        node.assemble()
        node.__dict__['_peek'] = True
        node.render()
        self.assertEqual(list(node.__dict__['_seen']), [node.inner.part])

    def test_a_leaf_inside_a_phase_is_empty(self):
        node = LeafPeeking()
        node.render()
        self.assertEqual(node.__dict__['_seen'], ())

    def test_brep_before_linking_keeps_its_refusal(self):
        with self.assertRaises(RuntimeError) as refused:
            AddressedLowerLeg().brep
        self.assertIn('cannot say whether it is a B-rep',
                      str(refused.exception))
