# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The declared set's defaults, for the suite's node doubles (OpenSpec
change `openscad-out`, design.md Decision 5).

The core reads what a node is -- `exact`, `flexible`, its artifact, its base
mesh, its children, its markings -- directly, never through `getattr` with a
default. A double standing in for a node therefore declares the members the
code it stands in for reads, with the meaning of a node that has none: not
exact, not flexible, no artifact and no base mesh (its `mesh` is already its
placed geometry), no children, no source file and no markings. A double
derives from `StandIn` and overrides what it does have.


A double built as a namespace is a `NodeDouble`: a `SimpleNamespace` with
the same answers, whose source is its artifact unless it is given one (it
stands in for a part imported from a mesh).
"""

from types import SimpleNamespace


class StandIn:
    """A node double's answers to the declared set."""

    exact = False
    flexible = False
    stl_file = None
    base_mesh = None
    children = ()
    src = None

    def declared_markings(self):
        return {}

    def kept_artifacts(self):
        return ()


class NodeDouble(StandIn, SimpleNamespace):
    """A namespace standing in for a node, answering the declared set."""

    def __init__(self, **attributes):
        attributes.setdefault('src', attributes.get('stl_file'))
        super().__init__(**attributes)
