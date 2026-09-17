# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A module that binds NO `time` at all, and a class body in it that
names `time` among a relation's sources.

Python raises `NameError` before any declaration of the framework is
reached, and this cycle promises no message of its own there (OpenSpec
change ``time-without-running``, design section 5). The blind spot is
RECORDED rather than papered over.
"""

from solid_node.math import floor
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, State


def release(sources, targets):
    return lambda seconds, engaged, count: floor(seconds)


def advance(sources, targets):
    return lambda seconds, engaged, count: count + engaged


def stated():
    """State the committing relation that names a name nothing bound."""

    class Nameless(AssemblyNode):
        engaged = Driver(default=1, dtype=int)
        count = State(default=0, dtype=int)

        (time & engaged & count).commits(count, at=release, law=advance)

    return Nameless
