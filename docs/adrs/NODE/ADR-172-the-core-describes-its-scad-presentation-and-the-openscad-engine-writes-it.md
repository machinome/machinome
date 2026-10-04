# ADR-172: The Core Describes Its SCAD Presentation and the OpenSCAD Engine Writes It

**Status:** Accepted
**Date:** 2026-10-04
**Change:** [`scad-presentation`](../../../openspec/changes/scad-presentation/)
**Amends:**
- [ADR-102: Native materialization precedes optional SCAD presentation](ADR-102-native-materialization-precedes-optional-scad-presentation.md) — the compatibility consumer composes a description and writes no SCAD
- [ADR-116: An artifact import is anchored on the build directory](../BUILD/ADR-116-an-artifact-import-is-anchored-on-the-build-directory.md) — re-anchoring is a pure function over the core's description
- [ADR-171: The OpenSCAD engine is `machinome.openscad`](ADR-171-the-openscad-engine-is-machinome-openscad.md) — contract 2, and the core's direct reaches into the package
**Related to:**
- [ADR-162: A resolved provider declares the contract version it implements](ADR-162-a-resolved-provider-declares-the-contract-version-it-implements.md)
- [ADR-170: The core's symbolic value is its own type](../MATH/ADR-170-the-core-s-symbolic-value-is-its-own-type.md)
- [ADR-173: SCAD is written only where it is read](../BUILD/ADR-173-scad-is-written-only-where-it-is-read.md)

## Context and Problem Statement

After ADR-170 and ADR-171 the core's symbolic value was its own, but its SCAD
presentation was still SolidPython's. `node/base.py` imported `scad_render`,
`import_stl` and `color` at module top and built `assemble()`'s result,
`scad_code`, `generate_scad()` and the ADR-116 re-anchoring (a walk of
SolidPython's private `_children` and `_params` over a `copy.deepcopy`) from
SolidPython objects; `node/operations.py`, `node/internal.py` and
`node/flexible.py` imported `rotate`, `translate` and `union`. No node, and so
no build, export, test or document, existed without SolidPython, even for a
project whose every leaf is exact or STL. `node/base.py`,
`viewers/openscad.py` and `manager/snapshot.py` also reached the engine's
package directly for the binary locator, outside the seam.

The lean-core campaign's layer 1 (cycle 6) asks for the presentation behind
the seam, with `assemble()` no longer requiring it.

## Decision Drivers

- No core module composes SCAD or imports SolidPython for presentation.
- Every `scad_code`, and every `.scad` a SCAD-authored leaf writes, byte for
  byte what it was.
- `assemble()` works in an install without SolidPython or the engine.
- Re-anchoring without SolidPython's privates and without a deep copy.
- The core reaches the engine's package only through the seam.

## Considered Options

1. **A core-owned presentation description the engine renders** (chosen)
2. The serializer's published document as the engine's input
3. 4x4 matrices in place of operations
4. Engine-built objects (`engine.rotate(...)`) composed by the core
5. SCAD text composed by the core

## Decision Outcome

**The description.** `machinome/node/presentation.py` holds six immutable
types, with no import of SolidPython or the engine: `ArtifactImport(path)`
(a build artifact, relative to the build-wide anchor), `Color(rgb, alpha,
child)`, `Rotate(angle, axis, child)`, `Translate(vector, child)`,
`Union(children)` and `Authored(geometry)` (what a SCAD-authored leaf rendered
or its `as_scad` returned, opaque to the core). Equality is identity, since a
field may hold a symbolic value whose `==` is an expression. `described(value)`
holds a non-description as `Authored`; `reanchored(description, build_dir,
own_build_dir)` rewrites `ArtifactImport` paths onto the directory of the
`.scad` about to hold them, shares every node holding no artifact import,
never enters `Authored` and leaves its input unchanged.

`assemble()`, `as_scad()`, `artifact_import()`, `import_optimized()` and
`_colorize` build it; `Rotation.scad()`/`Translation.scad()` become
`Rotation.presented(child)`/`Translation.presented(child)`, holding the
operation's own angle, axis and vector objects.

**Expressions travel as values.** A rotation's angle and a translation's
components are passed to SolidPython as the operation holds them, a number,
the core's `GraphValue` or a SolidPython value; SolidPython writes a
non-string scalar by `str()`, which for the core's value is its closed
OpenSCAD text (ADR-170). The engine re-implements no expression syntax and
wraps nothing.

**The engine writes the text: contract 2.** `machinome.scad_engine.CONTRACT`
and `machinome.openscad.engine.CONTRACT` are 2, the operations the core calls:
`adopt(value)` (since 1); `scad_text(description, fn=None)`, which rebuilds
exactly the SolidPython calls the core used to make (`import_stl`,
`color(list(rgb), alpha)`, `rotate(angle, axis)`, `translate(vector)`,
`union()` or `union()([...])`, `Authored` content as is), renders them with
`scad_render`, and prefixes `$fn = <fn>;` and a blank line when given; and
`require_binary(needed_by, reason, alternative=None)`, delegating at call time
to `machinome.openscad.binary.require_openscad`. `scad_code` is the engine's
`scad_text` of the node's re-anchored description; `OpenScadNode.scad_code`
takes its module call from it.

**The binary through the seam.** `generate_stl` and the OpenSCAD snapshot
renderer resolve the binary through `require_scad_engine(...).require_binary(...)`
with the binary refusal's words unchanged; `manager/snapshot.py` catches the
seam's `ScadEngineUnavailable`, of which `OpenScadUnavailable` is a subclass
(ADR-173). Outside the package, only `machinome/scad_engine.py` and the leaf
`machinome/node/solid2.py` (`as_number`, cycle 7) import `machinome.openscad`;
only `node/solid2.py`, `node/openscad.py` and the project template import
`solid2`.

**The leaf contract stays at version 1.** A SCAD-presented leaf's `as_scad`
still returns the SolidPython object it authored, held as `Authored`.
`artifact_import` returns the core's description of an import rather than a
SolidPython `import_stl` subclass; its meaning (the anchored import of the
leaf's own artifact, returned from `as_scad`) is unchanged, its type was never
stated, and no leaf outside the core calls it (projects, machinome-freecad,
machinome-mechanics: grep, 3 October 2026). Accepted by the orchestrator.

### Why not the published document (option 2)

It carries no authored SCAD, no `$fn`, and its operations as graph slots and a
bindings table; the engine would re-derive SolidPython's structure and number
formatting, and byte identity would be a hope rather than a construction.

### Why not matrices (option 3)

A matrix cannot carry `$t`; SCAD presents symbolic motion as `rotate(a =
<text>)`.

### Why not engine-built objects (option 4)

Every `assemble()` would require the engine, and re-anchoring would stay a
walk of SolidPython's privates.

### Why not text composed by the core (option 5)

The core would duplicate SolidPython's formatting of numbers, lists and
indentation, a byte risk for every model, in the responsibility this decision
separates.

## Consequences

- `node/base.py`, `operations.py`, `internal.py` and `flexible.py` import no
  SolidPython; `assemble()`, `build_stls()` and `mesh` work with `solid2` or
  `machinome.openscad` unfindable.
- `assemble()`, `as_scad()` and `artifact_import()` return descriptions;
  `Rotation.scad()` and `Translation.scad()` are removed. No project uses
  them.
- Every node's `scad_code` and the expression golden's 17 values are
  byte-identical (`tests/expression_type_golden.py`,
  `tests/scad_presentation_golden.py`).
- A new presented construct is one description type and one engine mapping.
- Re-anchoring costs no deep copy per `.scad`.

## References

- `machinome/node/presentation.py`, `machinome/node/{base,operations,internal,flexible,openscad,solid2,leaf}.py`
- `machinome/scad_engine.py`, `machinome/openscad/{engine,binary}.py`
- `tests/test_scad_presentation.py`, `tests/test_scad_engine_seam.py`,
  `tests/test_openscad_engine.py`, `tests/scad_presentation_golden.py`
- `openspec/specs/scad-engine-dependency/spec.md`,
  `openspec/specs/openscad-engine/spec.md`, `openspec/specs/leaf-contract/spec.md`
