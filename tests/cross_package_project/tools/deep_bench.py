# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A root in package `tools`, over an intermediate assembly declared in
a THIRD package (`sub.deep`), over the leaf it places (in the top
package). The root's own generated `.scad` has always resolved this
import; the intermediate's is the other half of the bug this change
fixes."""

from machinome.node import AssemblyNode

from ..sub.deep.group import Group


class DeepBench(AssemblyNode):
    def render(self):
        return [Group()]
