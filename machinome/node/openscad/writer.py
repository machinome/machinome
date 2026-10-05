# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD writer: the SCAD text of a presentation the core described,
and its publication as a node's `.scad`.

The core composes a node's presentation in its own types
(`machinome.node.presentation`: `assemble()`, `present()`,
`presentation()`) and writes no SCAD. This module writes it, through
SolidPython, byte for byte the text the framework always wrote: SolidPython's
own `use` and `include` lines, which every `import_scad` of the process
registers, included (OpenSpec change `openscad-out`, design.md Decision 2).

- `scad_text(description, fn=None)`: the text of a description;
- `scad_code(node)`: the text of a node's own presentation, its artifact
  imports resolving from the node's own build directory;
- `generate_scad(node)`: that text published at `<basepath>.scad`, stamped
  and recorded like every artifact, and transient unless the node keeps the
  file (`kept_artifacts()`): a family leaf's own `.scad` is its build
  artifact; any other node's exists only for one process's use, the
  OpenSCAD snapshot renderer's, and every build removes one left behind.
"""

import logging

from solid2 import color, import_stl, rotate, scad_render, translate, union

from machinome import currency
from machinome.node.base import _seconds
from machinome.node.presentation import (ArtifactImport, Authored, Color,
                                         Rotate, Translate, Union)
from machinome.source_generation import current_generation


# The publication's log lines are the ones the node base wrote before the
# family became a package, under the same logger.
logger = logging.getLogger('node.base')


def _solid(description):
    """The SolidPython object of one description: the calls the core made
    before the presentation was described, each value passed as described,
    so SolidPython writes it as it always has -- a number in its own form,
    any other value by its `str()`, which is a symbolic value's closed
    text."""
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
    the framework wrote before it described its presentation: no header,
    comment or whitespace added, nothing re-anchored, rounded or reordered.
    With `fn`, the text begins with `$fn = <fn>;` and a blank line."""
    code = scad_render(_solid(description))
    if fn:
        code = f'$fn = {fn};\n\n{code}'
    return code


def scad_file(node):
    """Where a node's `.scad` is published: beside its STL, at
    `<basepath>.scad`."""
    return f'{node.basepath}.scad'


def scad_code(node):
    """The SCAD text of `node`'s own presentation (`presentation()`), with
    the `$fn` the node declares, if any."""
    return scad_text(node.presentation(), fn=getattr(node, 'fn', None))


def _own_text(node):
    """A family leaf's own text (which `OpenScadNode` composes with its
    source), else the text of the node's presentation."""
    from machinome.node.openscad.leaf import ScadLeafNode
    if isinstance(node, ScadLeafNode):
        return node.scad_code
    return scad_code(node)


def generate_scad(node, code=None):
    """Publish `node`'s `.scad`, unless the same file was already published
    for the same full source identity in this source generation.

    `code`, when given, is called for the text instead of the node's own.
    The file is stamped with the node's `mtime_ns` and recorded with its
    source digest and fingerprint; unchanged text is not replaced
    (`currency.publish_text`). It is published as transient unless the node
    lists it in `kept_artifacts()`.
    """
    path = scad_file(node)
    mtime_ns = node.mtime_ns
    digest = node.source_digest
    fingerprint = node.source_fingerprint
    identity = (mtime_ns, digest, fingerprint)
    generation = current_generation()
    if (node.rigid and generation is not None
            and generation.has_published(path, identity)):
        logger.info('%s reused in this source generation', path)
        return
    content = (code or (lambda: _own_text(node)))()
    transient = path not in node.kept_artifacts()
    currency.publish_text(path, content, mtime_ns, digest, fingerprint,
                          transient=transient)
    if generation is not None:
        generation.remember_published(path, identity)
    logger.info('%s generated with %s!', path, _seconds(mtime_ns))
