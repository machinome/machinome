# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""
The operations that can be applied to a solid are represented
here as classes that are able to handle the SCAD presentation and mesh,
other than serializing themselves for the web frontend. This way the same
results can be obtained in browser and in tests.
The operation is also able to revert itself.

An operation presents itself in the core's presentation description
(`machinome.node.presentation`), holding its own values; the OpenSCAD
engine writes the SCAD text of it.
"""

import math
import trimesh
from machinome.expression_graph import GraphValue, scalar, restore_scalar
from machinome.node.presentation import Rotate, Translate, described


def _as_number(node, value):
    """Converts value to a plain number. A symbolic value of the framework
    evaluates itself; otherwise, when a node is available its as_number
    is used, so SolidPython's own animated expressions can be resolved,
    and without one falls back to a plain float() conversion (used when
    an operation was rebuilt through unserialize(), which has no node)."""
    if node is None or isinstance(value, GraphValue):
        return float(value)
    return node.as_number(value)


class Rotation:
    """A rotation operation defined by an angle and an axis"""

    def __init__(self, angle, axis, node=None):
        self.angle = angle
        self.axis = axis
        self.node = node

    @property
    def serialized(self):
        """Returns a serialized rotation as ["r", angle, axis]"""
        return ['r', str(self.angle), self.axis]

    def _graph_serialized(self):
        return ['r', scalar(self.angle, graph=True), self.axis]

    @property
    def reversed(self):
        """Return an operation that reverses the rotation"""
        return Rotation(-self.angle, self.axis, self.node)

    def presented(self, child):
        """The presentation description of `child` rotated, holding this
        operation's own angle and axis"""
        return Rotate(self.angle, self.axis, described(child))

    def matrix(self):
        """The 4x4 world rotation matrix for this operation (skill-repo
        docs/performance-improvement.md fix 1), resolved through the
        node's as_number() AT ACCESS TIME -- never cached, since angle
        can be a symbolic animated expression that changes with the
        keyframe. Used by AbstractBaseNode.mesh to compose a whole
        operation chain into a single world matrix instead of applying
        each operation as a separate mesh pass."""
        return trimesh.transformations.rotation_matrix(
            math.radians(_as_number(self.node, self.angle)),
            self.axis,
        )

    def mesh(self, mesh):
        """Applies a rotation to a mesh"""
        matrix = trimesh.transformations.rotation_matrix(
            math.radians(_as_number(self.node, self.angle)),
            self.axis,
        )
        mesh.apply_transform(matrix)


class Translation:
    """A translation operation defined by a vector"""

    def __init__(self, translation, node=None):
        self.translation = translation
        self.node = node

    @property
    def serialized(self):
        """Returns a serialized translation as ["t", translation_vector]"""
        translation = [ str(x) for x in self.translation ]
        return ['t', translation]

    def _graph_serialized(self):
        return ['t', [scalar(x, graph=True) for x in self.translation]]

    @property
    def reversed(self):
        """Returns an operation that reverts the translation"""
        return Translation(
            [ -x for x in self.translation ],
            self.node,
        )

    def presented(self, child):
        """The presentation description of `child` translated, holding
        this operation's own vector"""
        return Translate(self.translation, described(child))

    def matrix(self):
        """The 4x4 world translation matrix for this operation
        (skill-repo docs/performance-improvement.md fix 1), resolved
        through the node's as_number() AT ACCESS TIME -- never cached,
        for the same reason Rotation.matrix() isn't."""
        translation_n = [ _as_number(self.node, n) for n in self.translation ]
        return trimesh.transformations.translation_matrix(translation_n)

    def mesh(self, mesh):
        """Applies a translation to a mesh"""
        translation_n = [ _as_number(self.node, n) for n in self.translation ]
        mesh.apply_translation(translation_n)


_operations = {
    'r': Rotation,
    't': Translation,
}

def unserialize(serialized):
    """Unserializes a serialized operation"""
    tag = serialized[0]
    if tag == 'r':
        return Rotation(restore_scalar(serialized[1]), list(serialized[2]))
    Operation = _operations[tag]
    return Operation([restore_scalar(x) for x in serialized[1]])
