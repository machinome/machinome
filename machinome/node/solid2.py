# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`Solid2Node`, a leaf of the OpenSCAD node family rendered with
SolidPython, and the adoption of SolidPython values as the core's
expressions.

A value SolidPython built -- `solid2.get_animation_time()`,
`scad_inline(...)`, or the text SolidPython's own operators produce when one
of its constants is on the left of a framework value -- is an expression of
the core's only because this module reads it as one: `adopt` is registered
with the expression graph (`machinome.expression_graph.register_adopter`)
when this module is imported, which every project using `Solid2Node` does.

SolidPython is installed by the `solid2` extra, which installs the `openscad`
extra; without it this module is refused at its import with the line that
installs it (OpenSpec change `openscad-out`, capability `openscad-node`).
"""

from machinome.extras import require_extra

# A project names this module to render with SolidPython, so without the
# `solid2` extra it is refused here, with the line that installs it, before
# SolidPython or the OpenSCAD node package is imported.
require_extra('solid2', 'machinome.node.solid2 (Solid2Node)', 'solid2')

import os
import re
import tempfile
from subprocess import Popen

from solid2 import scad_render
from solid2.core.object_base import OpenSCADConstant

from machinome.core.expressions import ExpressionError, parse
from machinome.expression_graph import ExpressionNode, register_adopter
from machinome.node.openscad.binary import require_openscad
from machinome.node.openscad.leaf import ScadLeafNode


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


register_adopter(adopt)


class Solid2Node(ScadLeafNode):
    """
    Represents a 3D object created using the SolidPython2 tool.
    """

    namespace = 'solid2'

    def as_number(self, n):
        """Receives a solid2 function result and calculates its number.
        uses an openscad process internally to do the calculation."""
        from machinome.expression_graph import GraphValue
        if isinstance(n, GraphValue):
            return float(n)
        if type(n).__module__.startswith('solid2'):
            # This is very clumsy, but it works. Trimesh cannot load
            # translated / rotated mesh, and transforming meshes after loading
            # requires knowing the final number in python memory.
            # If it's a scad function, then we need to get from OpenScad.

            openscad = require_openscad(
                f'node {self.name}',
                'symbolic value evaluation uses OpenSCAD')
            lines = scad_render(n).split('\n')
            code = []
            while lines[0].startswith('include'):
                code.append(lines.pop(0))
            while not lines[0].strip():
                lines.pop(0)
            code.append('echo(')
            while lines:
                line = lines.pop(0)
                if line.strip():
                    code.append(line)
            code = '\n'.join(code)
            code = re.sub(r";$", ");", code)

            scad_file = tempfile.mktemp(suffix='.scad')
            result_file = tempfile.mktemp('.echo')

            try:
                open(scad_file, 'w').write(code)
                proc = Popen([openscad, '-o', result_file, scad_file])
                proc.wait()
                result = open(result_file).read()
                result = result.replace('ECHO: ', '').strip()
                n = int(result)
            finally:
                if os.path.exists(scad_file):
                    os.remove(scad_file)
                if os.path.exists(result_file):
                    os.remove(result_file)

        return n
