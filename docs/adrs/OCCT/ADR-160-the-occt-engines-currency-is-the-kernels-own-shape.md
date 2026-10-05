# ADR-160: The OCCT Engine's Currency Is the Kernel's Own Shape

**Status:** Accepted; the provider's address, amended 2026-10-05 by [ADR-180](../NODE/ADR-180-the-engines-are-named-for-the-representation-each-consumes.md)
**Date:** 2026-10-03
**Change:** [`exact-engine`](../../../openspec/changes/archive/2026-10-03-exact-engine/)
**Supersedes:** the chosen option of [ADR-047: One shared OCCT currency for every exact backend](../NODE/ADR-047-shared-occt-currency-for-exact-backends.md), adopting its option 2; its conversion-at-the-boundary rule stands
**Related to:**
- [ADR-161: The core holds no kernel code](../NODE/ADR-161-the-core-holds-no-kernel-code.md) — the seam this engine is resolved through
- [ADR-162: A resolved provider declares the contract version it implements](../NODE/ADR-162-a-resolved-provider-declares-the-contract-version-it-implements.md) — the `CONTRACT` this engine declares
- [ADR-057: The flexible leaf, whose geometry travels as a spec](../NODE/ADR-057-the-flexible-leaf-and-spec-carried-geometry.md) — its sentence on recasting molejo's solid is now historical

This is the engine package's own ADR. It lives in `docs/adrs/OCCT/`, a
directory of its own, so that the cycle cutting the engine into the
machinome-occt repository moves the directory whole and the ADR keeps its
number, as the viewer-owned ADRs did.

## Context and Problem Statement

ADR-047 made one type flow through the exact layer whatever exact backend
produced a shape, and chose CadQuery's `Shape` for it because it was the type
`exact.py` already used; it recorded raw `TopoDS_Shape` as a rejected option,
mainly because it "does not remove the cadquery dependency anyway".

The lean-core campaign (`workflow/ongoing/lean-core.md`) removes exactly that
dependency from the exact path. Every operation of the exact layer moved into
the OCCT engine, `machinome.occt.engine`, rewritten on bare OCP with no
cadquery import (ADR-161), so the reason to keep CadQuery's type is gone and
the engine has to say what it passes around. The originating evidence is
machinome-freecad's exact leaf, which reads a FreeCAD BREP into a bare
`TopoDS_Shape` with OCP and imports cadquery for one reason only: to cast it
into the exact layer's currency.

The pilot ruled that the currency is the engine's decision, not the core's,
and stated the expectation of the bare shape; the core's specs name no OCCT
type and require only that every exact node returns the one type the engine
declares.

## Decision Drivers

- The engine imports OCP and numpy, never a CAD front end.
- Every exact node returns one type, so a fusion, a molejo solid and a leaf
  are interchangeable to every consumer.
- The kernel object is already what every producer holds: OCCT, OCP,
  CadQuery (`.wrapped`), build123d (`.wrapped`), molejo (`result.solid`) and
  FreeCAD's BREP transfer.
- Artifacts built before the change and after it must be byte-identical.

## Considered Options

1. **The bare `OCP.TopoDS.TopoDS_Shape`, or a subtype** (chosen)
2. A thin engine-owned wrapper holding the `TopoDS_Shape`
3. Each front end's own type from `shape()`, `TopoDS_Shape` from a fusion
4. Keep CadQuery's `Shape` this cycle and change it at the cut

## Decision Outcome

Chosen option: **the kernel's own shape**. The engine passes exact geometry
as an `OCP.TopoDS.TopoDS_Shape` or one of its subtypes and adds no type
around it. Every engine operation that returns geometry returns one; every
operation that takes geometry accepts one. `as_shape(obj)` admits a value as
the currency: the object itself when it is a `TopoDS_Shape`, else the
`TopoDS_Shape` it carries as `.wrapped` (the convention CadQuery and
build123d share), else a `TypeError` naming its type. It never copies,
heals or tessellates. The five operations a project calls directly
(`intersect_shapes`, `fuse_shapes`, `placed_shape`, `solid_count`,
`solid_volume`) accept whatever `as_shape` admits.

ADR-047's other decision stands: conversion happens once, at the adapter
boundary, and is a rewrap. `ExactLeafNode.shape_from_rendered` admits by
`as_shape`; `CadQueryNode` and `StepNode` add a `Workplane`'s values,
`Build123dNode` a builder's finished part; `MolejoNode` returns molejo's own
solid. A consumer that wants CadQuery's methods wraps the shape itself with
`cadquery.Shape.cast(node.shape())`.

Each CadQuery method the old layer called has a plain OCP equivalent, taken
from cadquery 2.7.0's own source (design.md Decision 4), so results are
unchanged: on a fused solid, the engine's BREP and STL writers produce the
same SHA-256 as CadQuery's `exportBrep` and `exportStl` in separate
processes, and seven characterization fixtures (CadQuery, build123d, sheet,
STEP, two fusions, molejo) keep every BREP and STL digest, volume, solid
count, bounding box and face-box array they had on the unmodified tree.

### Why not a wrapper (option 2)

It costs projects exactly what the bare shape costs -- it cannot offer
CadQuery's methods without re-implementing CadQuery -- and adds a second
type every front end, molejo and FreeCAD must wrap and unwrap, and a type
the engine contract must version. Its one advantage, an owned identity in
place of the core's `id()`-keyed memo, is not needed: the core's cache
already owns identity.

### Why not front-end types (option 3)

A fusion's shape and its children's would differ in type, breaking the
substitutability every exact consumer relies on.

### Why not later (option 4)

The engine would import cadquery to cast, an interim shape that exists only
to be replaced.

## Consequences

- The engine knows no front end, and depends on cadquery-ocp alone.
- Project code that calls CadQuery methods on `shape()` or on an engine
  result wraps it: 29 project files on 2 October 2026, migrated by the
  one-path cycle's rewrite script; OpenAstroMount was migrated by hand to
  validate this change.
- `StepNode.adjust` still receives a CadQuery `Shape` in this cycle; whether
  it receives the bare shape is decided when the STEP package is cut.
- ADR-057's sentence that `shape()` "returns the OCCT solid, recast to the
  CadQuery `Shape` the exact layer trades in" is historical: a molejo solid
  is now the currency as molejo returns it.
- The verdict memo (ADR-156) is unaffected: its identities are cache keys
  and artifact bytes, neither of which involves the shape's type.

## References

- `machinome/occt/engine.py` — `as_shape`, `compound` and every operation
- `machinome/node/exact_leaf.py` — `ExactLeafNode.shape_from_rendered`
- `machinome/node/adapters/cadquery.py` — `workplane_shape`
- `machinome/node/adapters/build123d.py` — `build123d_shape`
- `tests/test_occt_engine.py`, `tests/test_exact_currency.py`,
  `tests/exact_engine_golden.py`, `tests/data/exact_engine_golden.json`
- `openspec/specs/occt-engine/spec.md` — "The engine's currency is the
  kernel's own shape"
