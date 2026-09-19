# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The control: an assembly in the SAME package as the leaves it places,
so nothing here has ever needed to travel through the anchoring rule --
the guard against fixing the cross-package case by breaking the ordinary
one."""

from machinome.node import AssemblyNode

from .parts import ExactLeaf, FlexLeaf, RigidLeaf


class SameBench(AssemblyNode):

    def render(self):
        flex = FlexLeaf()
        flex.height = 30.0
        return [RigidLeaf(), ExactLeaf(), flex]
