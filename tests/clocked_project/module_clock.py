# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A module that imported the STDLIB `time`, and a class body in it that
declares no time base and names `time` among a relation's sources.

A Python class body does not see `AssemblyNode.time`, so the name
resolves the way any free name in a class body resolves -- here, to the
MODULE this file imported. The framework's refusal is the reflected `&`
(OpenSpec change ``time-without-running``, design section 5): the group
names the operand and says where a machine's clock comes from.

The class is built inside a function so importing this fixture does not
raise.
"""

import time

from solid_node.math import floor
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, State


def release(sources, targets):
    return lambda time_value, engaged, count: floor(time_value)


def advance(sources, targets):
    return lambda time_value, engaged, count: count + engaged


def stated():
    """State the committing relation that names the stdlib module."""

    class Mistaken(AssemblyNode):
        engaged = Driver(default=1, dtype=int)
        count = State(default=0, dtype=int)

        (time & engaged & count).commits(count, at=release, law=advance)

    return Mistaken
