# Original synthetic native fixtures

Copyright (C) 2026 Luis Henrique Cassis Fagundes.
SPDX-License-Identifier: LGPL-2.1-or-later.

These FCStd documents are original boxes and assembly definitions produced by
`../generate_fixtures.py` in the recorded FreeCAD 1.1.4 runtime. They contain no
Dum-E CAD or other upstream geometry. Parts.FCStd supplies a 4 × 6 × 8 mm box;
the assembly has three distinct occurrences, one revolute and one fixed edge.

The generator records the licence in native document metadata. Assembly and
Maximum120 share the same saved pose and own-frame solids, differing in the
maximum enabled revolute bound. Native FreeCAD automatically adjusts some
contradictory limit edits; ReversedBounds therefore records the editor's native
normalization, not proof that the worker accepted invalid enabled bounds. An
injected resolved-range test separately verifies invalid-range refusal.

## Residual admission variants

`FixedQuarterTurn.FCStd` keeps a saved Fixed connector quarter-turn mismatch
that native solve reports as status 0 without changing the saved pose.
`RevoluteDisplaced.FCStd` and `RevoluteTilted.FCStd` contain incompatible
origin/axis markers. The generator intentionally does not solve away those
authored inconsistencies. `FixedOppositeX/Y/Z.FCStd` preserve the three valid
native Fixed π branches, whose driven poses are tested against native motion.
These are original synthetic box assemblies, not copied Dum-E CAD.
The displaced source is refused for saved-versus-resolved occurrence drift
when native recomputation adjusts it; diagnostics distinguish that pose
residual from the now-consistent resolved joint residuals.
`StaleConnectors.FCStd` has stale cached non-detached Placement1, with valid
references/offsets; authoritative native recomputation admits it without
occurrence drift. Its driven poses are also compared with native simulation.
