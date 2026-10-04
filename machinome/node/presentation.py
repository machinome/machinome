# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A node's SCAD presentation, described in the core's own types.

The core does not write SCAD. `assemble()`, `as_scad()`, the operations and
`artifact_import()` compose a small immutable tree of the values below, and
the OpenSCAD engine (`machinome.openscad.engine.scad_text`, reached through
the seam `machinome.scad_engine`) writes its text. The tree holds what the
core already holds and nothing it would have to compute for SCAD:

- `ArtifactImport(path)`: a build artifact, `path` relative to the
  build-wide anchor (`get_build_dir`) until `reanchored` moves it onto the
  directory of the `.scad` about to hold it (ADR-116);
- `Color(rgb, alpha, child)`: a node's colour, three floats and an alpha;
- `Rotate(angle, axis, child)` and `Translate(vector, child)`: the values
  the operation holds, by reference -- numbers, the core's symbolic values
  or a value SolidPython built, unconverted;
- `Union(children)`: a tuple of zero or more descriptions;
- `Authored(geometry)`: the object a SCAD-authored leaf rendered or its
  `as_scad` returned, opaque to the core.

Equality is identity: a field may hold a symbolic value, whose comparison is
an expression rather than a truth. Nothing here imports SolidPython or the
engine.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class ArtifactImport:
    """An `import()` of a build artifact the framework itself emitted.

    What tells a path the framework may re-anchor from a path a project
    wrote in its own `render()`, which is part of `Authored` geometry and is
    never entered."""

    path: str


@dataclass(frozen=True, eq=False)
class Color:
    rgb: tuple
    alpha: object
    child: object


@dataclass(frozen=True, eq=False)
class Rotate:
    angle: object
    axis: object
    child: object


@dataclass(frozen=True, eq=False)
class Translate:
    vector: object
    child: object


@dataclass(frozen=True, eq=False)
class Union:
    children: tuple


@dataclass(frozen=True, eq=False)
class Authored:
    geometry: object


#: Every type of a presentation description.
DESCRIPTIONS = (ArtifactImport, Color, Rotate, Translate, Union, Authored)


def described(value):
    """`value` as a description: itself when it is one, else the geometry a
    SCAD-authored leaf authored, held as `Authored`."""
    if isinstance(value, DESCRIPTIONS):
        return value
    return Authored(value)


def reanchored(description, build_dir, own_build_dir):
    """A description whose every `ArtifactImport` resolves from
    `own_build_dir`, the directory of the `.scad` about to hold it, rather
    than from `build_dir`, the build-wide anchor (ADR-116).

    Every node holding no artifact import is shared, not copied, and the
    input is left unchanged; `Authored` geometry is never entered, so a
    project's own `import_stl` stays exactly as the project wrote it.
    """
    description = described(description)
    if isinstance(description, ArtifactImport):
        return ArtifactImport(os.path.relpath(
            os.path.join(build_dir, description.path), own_build_dir))
    if isinstance(description, Union):
        children = tuple(reanchored(child, build_dir, own_build_dir)
                         for child in description.children)
        if all(new is old
               for new, old in zip(children, description.children)):
            return description
        return Union(children)
    if isinstance(description, (Color, Rotate, Translate)):
        child = reanchored(description.child, build_dir, own_build_dir)
        if child is description.child:
            return description
        if isinstance(description, Color):
            return Color(description.rgb, description.alpha, child)
        if isinstance(description, Rotate):
            return Rotate(description.angle, description.axis, child)
        return Translate(description.vector, child)
    return description
