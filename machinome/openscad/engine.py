# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD engine's provider: what the core asks of SolidPython.

The core's seam `machinome.scad_engine` resolves this module and compares
its `CONTRACT` with the version the core speaks. Version 2 is three
operations:

- `adopt`: the core's symbolic value is its own type
  (`machinome.expression_graph.GraphValue`), and a value SolidPython built
  -- `solid2.get_animation_time()`, `scad_inline(...)`, or the text
  SolidPython's own operators produce when one of its constants is on the
  left of a framework value -- is an expression only because this module
  reads it as one;
- `scad_text`: the SCAD text of the core's presentation description
  (`machinome.node.presentation`), which the core composes and never
  writes as SCAD itself;
- `require_binary`: the OpenSCAD executable, through the binary contract
  `machinome.openscad.binary`.
"""

from solid2 import color, import_stl, rotate, scad_render, translate, union
from solid2.core.object_base import OpenSCADConstant

from machinome.core.expressions import ExpressionError, parse
from machinome.expression_graph import ExpressionNode
from machinome.node.presentation import (ArtifactImport, Authored, Color,
                                         Rotate, Translate, Union)

#: The OpenSCAD engine contract version this provider implements.
CONTRACT = 2

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


def _solid(description):
    """The SolidPython object of one description: the calls the core made
    before the presentation moved here, each value passed as described, so
    SolidPython writes it as it always has -- a number in its own form, any
    other value by its `str()`, which is a symbolic value's closed text."""
    if isinstance(description, ArtifactImport):
        return import_stl(description.path)
    if isinstance(description, Color):
        return color(list(description.rgb), description.alpha)(
            _solid(description.child))
    if isinstance(description, Rotate):
        return rotate(description.angle, description.axis)(
            _solid(description.child))
    if isinstance(description, Translate):
        return translate(description.vector)(_solid(description.child))
    if isinstance(description, Union):
        if not description.children:
            return union()
        return union()([_solid(child) for child in description.children])
    if isinstance(description, Authored):
        return description.geometry
    raise TypeError(f'{description!r} is not a presentation description')


def scad_text(description, fn=None):
    """The SCAD text of a presentation description, byte for byte the text
    the core wrote before it described its presentation: no header, comment
    or whitespace added, nothing re-anchored, rounded or reordered. With
    `fn`, the text begins with `$fn = <fn>;` and a blank line."""
    code = scad_render(_solid(description))
    if fn:
        code = f'$fn = {fn};\n\n{code}'
    return code


def require_binary(needed_by, reason, alternative=None):
    """The OpenSCAD executable's path, or the binary contract's refusal
    (`machinome.openscad.binary.OpenScadUnavailable`), resolved once per
    process. Read at call time, so the binary contract's own resolution
    governs it."""
    from machinome.openscad import binary
    return binary.require_openscad(needed_by, reason, alternative)
