# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD engine's provider: what the core asks of SolidPython.

The core's seam `machinome.scad_engine` resolves this module and compares
its `CONTRACT` with the version the core speaks. The contract is one
function, `adopt`: the core's symbolic value is its own type
(`machinome.expression_graph.GraphValue`), and a value SolidPython built
-- `solid2.get_animation_time()`, `scad_inline(...)`, or the text
SolidPython's own operators produce when one of its constants is on the
left of a framework value -- is an expression only because this module
reads it as one.
"""

from solid2.core.object_base import OpenSCADConstant

from machinome.core.expressions import ExpressionError, parse
from machinome.expression_graph import ExpressionNode

#: The OpenSCAD engine contract version this provider implements.
CONTRACT = 1

#: Where an adopted value keeps the node read from its text.
_ADOPTED = '_machinome_adopted'


def adopt(value):
    """The expression graph node of a SolidPython scalar, else None.

    A SolidPython scalar constant (`OpenSCADConstant`, which `ScadValue`
    and `scad_inline` produce) is read from its text by the core's own
    parser, which recovers a `let` closure's sharing; text outside the
    parser's language is carried verbatim as a `raw` node, which a law or a
    bound refuses and publication emits with its warning. Anything else --
    a number, a string, the core's own value or node -- is not adopted.
    """
    if not isinstance(value, OpenSCADConstant):
        return None
    # A SolidPython constant is its text, set when it is built. One value
    # is often asked for more than once on its way into one call -- is it
    # symbolic, then its node -- so the node read from that text is kept
    # on the value, and read again only if its text was replaced.
    text = value.value
    try:
        adopted = value.__dict__.get(_ADOPTED)
    except AttributeError:
        adopted = None
    if adopted is not None and adopted[0] is text:
        return adopted[1]
    rendered = str(value)
    try:
        node = parse(rendered)
    except ExpressionError:
        node = ExpressionNode('raw', text=rendered)
    try:
        value.__dict__[_ADOPTED] = (text, node)
    except AttributeError:
        pass
    return node
