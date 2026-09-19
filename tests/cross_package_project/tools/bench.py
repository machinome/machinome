# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""An assembly in package `tools`, placing leaves declared in the PARENT
package `cross_package_project` -- the cross-package shape
`workflow/warts.md` records for `projects/Robots/Thor` ("A leaf's
artifact is imported into its parent's `.scad` by bare filename...")."""

from machinome.node import AssemblyNode

from ..parts import ExactLeaf, FlexLeaf, RigidLeaf, UnoptimizedLeaf


class Bench(AssemblyNode):
    """One leaf of each artifact-emitting kind, cross-package."""

    def render(self):
        flex = FlexLeaf()
        flex.height = 30.0
        return [
            RigidLeaf(),
            ExactLeaf().translate([20, 0, 0]),
            flex.translate([40, 0, 0]),
        ]


class UnoptBench(AssemblyNode):
    """Cross-package parent of a leaf that declines optimization: no
    import is emitted for it either way, and this is the guard."""

    def render(self):
        return [UnoptimizedLeaf()]
