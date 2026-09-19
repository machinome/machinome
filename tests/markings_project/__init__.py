# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A project whose parts carry markings.

Shaped like the two calculators the `markings` capability was written
for: a dial whose digits are wrapped around it, and a plate carrying a
flat badge. Both leaf kinds are here on purpose -- an exact
`CadQueryNode`, which writes a `.brep` and declares a tessellation
precision of its own, and a faceted `StlNode`, which does neither -- so
every invariant can be read on a part that has the artifacts and on one
that does not.

Each part has a twin of the same class name and the same parameters
declaring NO marking (`plain_dial.py`, `plain_plate.py`), which is what
makes "the solid is byte-identical with and without a marking" a
comparison rather than an assertion about one file.

`label.svg` is the artwork: two closed regions, one of them with its
counter nested as a hole, surrounded by an open rectangular border --
the shape of a real drawing, whose sheet border is a registration mark
and not a glyph. `decals/badge.svg` is a second artwork in the mixin's
own directory, so the rule that an artwork path resolves against the
module that DECLARED the marking is provable and not merely stated.
"""
