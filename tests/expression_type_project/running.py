# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Running roots whose laws return SolidPython's own values (OpenSpec
change `expression-type`, capability `motion-expression-sharing`, "Supported
legacy expressions retain their behavior").

`LegacyLeft`'s law puts a SolidPython constant on the LEFT of the framework
token it is applied to, so SolidPython's own operator builds the result as
its text, which the framework reads back through the OpenSCAD engine.
`LegacyTime`'s law returns `scad_inline('$t')`: with the engine, an
expression over a source the law does not declare; without it, not an
expression at all.
"""

from solid2.core.object_base import scad_inline

from machinome.motion.ports import Time
from machinome.node.assembly import AssemblyNode
from machinome.simulation import Driver

from tests.running_project.parts import Arbor


def legacy_left(source, target):
    """At rest the run poses the tree with numbers; compiled, the law is
    applied once to a token, and there SolidPython builds the text."""
    def law(angle):
        if isinstance(angle, (int, float)):
            return 2 * angle
        return scad_inline('2') * angle

    return law


def legacy_time(source, target):
    def law(angle):
        if isinstance(angle, (int, float)):
            return angle
        return scad_inline('$t')

    return law


class LegacyLeft(AssemblyNode):
    """A running root whose law is SolidPython text over its source."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    first = Arbor()

    crank.drives(first.turn, law=legacy_left)


class LegacyTime(AssemblyNode):
    """A running root whose law returns SolidPython's own `$t`."""

    time = Time.running()

    crank = Driver(default=0.0, unit='deg')
    first = Arbor()

    crank.drives(first.turn, law=legacy_time)
