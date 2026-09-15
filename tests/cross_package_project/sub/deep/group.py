# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""An intermediate assembly, two packages away from the leaf it places
and a different package again from whatever places IT -- so its own
generated `.scad` and the root's above it must each hold a DIFFERENT
spelling of the same import to both resolve (design.md, "What does not
move")."""

from solid_node.node import AssemblyNode

from ...parts import RigidLeaf


class Group(AssemblyNode):
    def render(self):
        return [RigidLeaf()]
