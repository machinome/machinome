# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The pin tumbler lock's shape, reduced to two joints and two relations.

A child assembly declares a relation into its OWN leaf's joint, and the
running root declares a relation that READS that joint and drives another
leaf's joint.  Every untimed pose and every `Sim` accepts it; publication
refuses it as doubly bound.
"""

from solid2 import cube, cylinder

from solid_node.motion.joints import Prismatic
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.simulation import Driver


class Key(Solid2Node):
    insert = Prismatic(axis=(1, 0, 0), unit='mm')

    def render(self):
        return cube([20, 4, 4], center=True)


class Pin(Solid2Node):
    lift = Prismatic(axis=(0, 0, 1), unit='mm')

    def render(self):
        return cylinder(r=2, h=12)


class Plug(AssemblyNode):
    """The CHILD assembly: its own relation binds its own leaf's joint."""

    key = Key()
    p1 = Pin()

    key.insert.drives(p1.lift, ratio=0.5)

    def render(self):
        self.p1.translate([0, 0, 10])


class LockBody(AssemblyNode):
    """The ROOT's declarations, with no time base: the untimed twin."""

    push = Driver(default=0.0, unit='mm')

    plug = Plug()
    d1 = Pin()

    push.drives(plug.key.insert)
    plug.p1.lift.drives(d1.lift, ratio=-1)

    def render(self):
        self.d1.translate([20, 0, 0])


class Lock(LockBody):
    """The same machine, running."""

    time = Time.running()


def squared(source, target):
    """A law that does not invert: the same shape, read forward only."""
    return lambda lift: lift * lift


class OpaqueBody(AssemblyNode):
    """The same two relations, with a law the solver cannot read backwards."""

    push = Driver(default=0.0, unit='mm')

    plug = Plug()
    d1 = Pin()

    push.drives(plug.key.insert)
    plug.p1.lift.drives(d1.lift, law=squared)

    def render(self):
        self.d1.translate([20, 0, 0])


class OpaqueLock(OpaqueBody):
    """The same machine, running."""

    time = Time.running()
