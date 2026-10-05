# ADR-161: The Core Holds No Kernel Code: the Exact Engine Seam and Its Address

**Status:** Accepted; absent-engine case amended 2026-10-03 by [ADR-167](ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md); extended to the mesh engine 2026-10-04 by [ADR-176](../TEST-FRAMEWORK/ADR-176-the-mesh-engine-is-a-provider-behind-the-seam-installed-by-an-extra.md); the seam's address and names, amended 2026-10-05 by [ADR-180](ADR-180-the-engines-are-named-for-the-representation-each-consumes.md)
**Date:** 2026-10-03
**Change:** [`exact-engine`](../../../openspec/changes/archive/2026-10-03-exact-engine/)
**Related to:**
- [ADR-047: One shared OCCT currency for every exact backend](ADR-047-shared-occt-currency-for-exact-backends.md) — conversion at the adapter boundary, kept; its currency superseded by ADR-160
- [OCCT/ADR-160: The OCCT engine's currency is the kernel's own shape](../OCCT/ADR-160-the-occt-engines-currency-is-the-kernels-own-shape.md)
- [ADR-162: A resolved provider declares the contract version it implements](ADR-162-a-resolved-provider-declares-the-contract-version-it-implements.md)
- [ADR-045: Exact fusion composition](ADR-045-exact-fusion-composition.md) — fusion now resolves the engine for its exact branch only
- [ADR-046: Conditional OpenSCAD dependency](ADR-046-conditional-openscad-dependency.md) — the conditional-dependency shape this seam follows
- [BUILD/ADR-069: Deferred callables for a module's own call sites](../BUILD/ADR-069-deferred-callables-for-a-modules-own-call-sites.md) — no longer used for the exact names of `machinome.test`
- [TEST-FRAMEWORK/ADR-070: Relative placement as the identity of an intersection question](../TEST-FRAMEWORK/ADR-070-relative-placement-as-the-identity-of-an-intersection-question.md) — the placement memo, moved unchanged
- [TEST-FRAMEWORK/ADR-092: Face boxes decide an enclosed pair without a boolean](../TEST-FRAMEWORK/ADR-092-face-boxes-decide-an-enclosed-pair-without-a-boolean.md) — the containment guard, moved into the engine unchanged
- [TEST-FRAMEWORK/ADR-143: Exact booleans preserve their reusable inputs](../TEST-FRAMEWORK/ADR-143-exact-booleans-preserve-their-reusable-inputs.md) — the operand copies, moved into the engine unchanged
- [TEST-FRAMEWORK/ADR-156: A decided verdict outlives the run](../TEST-FRAMEWORK/ADR-156-a-decided-verdict-outlives-the-run.md) — the verdict memo, unchanged

## Context and Problem Statement

`machinome/exact.py` (548 lines) mixed five jobs: OCCT operations
(placement, fuse and common, the empty-common witness, solid counting and
volume, bounding and face boxes, BREP and STL I/O); process identity and
caches over loaded shapes; artifact publication; validation of a node's
declared tessellation precision; and recognition of front-end render
results. It imported cadquery at module top, and through it so did
`node/fusion.py`. The test kernel held the containment guard's OCP code
itself, and bound nine exact names through ADR-069's deferred callables.

The lean-core campaign (`workflow/ongoing/lean-core.md`, item 3) needs exact
geometry to be a kernel package the core resolves. machinome-freecad's exact
leaf showed why: it could not get the engine without importing cadquery, and
had to import the private `machinome.exact._evict`. The pilot ruled on the
first draft of this change that an operation on an OCCT shape is a
capability of the OCCT package, not of the core: "a model that is purely
OpenSCAD based should have no BREP". The core therefore holds no OCCT code
and defines no operation on OCCT shapes under its own name.

## Decision Drivers

- A model with no exact node never imports the engine.
- One name, one path: each operation is defined once, where it lives.
- The engine leaves the core at the cut with its directory, unchanged.
- No behaviour, artifact byte or verdict changes.
- A current exact artifact is reused without resolving the engine.

## Considered Options

1. **A seam module in the core, a known provider, opaque handles; the
   engine at its final address as one module; `machinome.exact` removed**
   (chosen)
2. Keep `machinome.exact` as five thin functions over the engine
3. Split the engine into a provider module and a public module
4. Move the caches, publication and validation into the engine too

## Decision Outcome

**The seam.** `machinome/exact_engine.py` declares the contract the core
speaks -- `CONTRACT`, three Protocols grouping the thirteen operations by
the consumer that calls them (currency I/O, composition, comparison and
measurement) and `ExactEngine` combining them, named as the engine defines
them -- the four error types, and `exact_engine()` /
`require_exact_engine(needed_by, reason)`, the shape of `mesh_engine()`.
Resolution is a try-import of the one known provider, `machinome.occt.engine`,
once per process; an absent provider answers `None` or raises one error
naming the exact engine, the caller, the reason and
`pip install "machinome[occt]"`; a provider that fails to import for another
reason raises its own error. No entry-point group and no registry (the plan's
D2). The seam is the only core module that names the provider.

**The engine.** `machinome/occt/engine.py`, under a `machinome/occt/`
package that exports nothing, is both the provider and the address of the
operations a project calls directly. Every OCCT operation of the old layer
and the containment guard of the test kernel live there, on bare OCP, each
defined once under one name; it imports no front end, no trimesh and no
core internal, and keeps no state. The `occt` extra is declared as metadata
naming the kernel the core already resolves.

**The core keeps what an abstract exact node needs, none of it OCCT code.**
Exact shapes are opaque handles. `machinome/exact_cache.py` holds the memos
over handles and artifact files (`cached_shape`, `shape_identity`,
`shape_load_observation`, `cached_bounding_box`, `cached_face_boxes`,
`cached_placement`, `_evict`, `_reset_placement_cache`), unchanged in keys,
limits and semantics, filling each miss by an engine operation.
`machinome/exact_artifacts.py` publishes artifacts: the engine writes the
bytes to a temporary path, the core stamps, records and publishes them, and
applies the degenerate-triangle cleanup the mesh engine needs. `ExactLeafNode`
converts a render result by its `shape_from_rendered` method, and only inside
the branch that writes a stale artifact, so a leaf prepared on every build
(`optimize = False`) never resolves the engine for current artifacts.
`FusionNode` imports nothing kernel-side at module top and resolves the
engine inside its exact branch; its recipe stays `exact-fusion-occt-v1`.
`machinome.test` keeps the culling order and calls each engine operation and
each memo as an attribute of its defining module at the moment of the call,
so a name patched where it is defined is honoured and `machinome.test` binds
none of them; ADR-069's deferred callables are no longer used here.

**`machinome.exact` is removed.** Its project-facing operations are imported
from `machinome.occt.engine`; its error types from `machinome.exact_engine`,
which the engine and the core both depend on and neither on the other. Vet
denies the exact internals and the engine's file operations.

### Why not five thin functions (option 2)

A core module defining `intersect_shapes` over OCCT shapes is the core
offering the engine's capability, and five functions resolving the engine to
call the same five functions on it are two names at two paths for one
operation.

### Why not two engine modules (option 3)

It forces a provider re-exporting the public functions, two functions per
operation, or a seam resolving two modules. One module is the simplest shape
that keeps one name per operation; its cost is that a project can reach
contract operations it does not need, the file operations among them, which
vet denies.

### Why not move the caches too (option 4)

The engine would import the core privates `machinome.currency` and
`machinome._artifact` across a package and licence boundary, and the next
cycle's fix for `_evict` would have to be made in the engine.

## Consequences

- Importing `machinome.node.fusion`, `machinome.node.exact_leaf`,
  `machinome.exact_cache`, `machinome.exact_artifacts` or `machinome.test`
  imports neither the engine, OCP nor cadquery; a faceted project builds and
  tests with the engine absent; a project whose leaves render the kernel's
  own shape builds, fuses and tests exactly without cadquery or build123d.
- Outside `machinome/occt/`, only the STEP adapter imports OCP and cadquery
  (its reader and `adjust`, which move with their package). The markings'
  SVG reducer keeps importing build123d until the cut.
- 12 project files import `machinome.exact` and move their import line to
  `machinome.occt.engine` (the one-path cycle's rewrite script).
- `_evict` remains private and the shape cache still keys on
  `(path, float mtime)`; the public replacement is the next cycle's, which
  declares the exact-leaf extension contract.
- A second exact engine needs the seam's provider name changed: one string
  in one module, the accepted compromise of D2.
- The verdict store starts afresh once, because its stamp digests the
  package source (ADR-156).

## References

- `machinome/exact_engine.py`, `machinome/exact_cache.py`,
  `machinome/exact_artifacts.py`, `machinome/occt/engine.py`
- `machinome/node/exact_leaf.py`, `machinome/node/fusion.py`,
  `machinome/test.py`, `machinome/manager/test.py`
- `tests/test_exact_engine_seam.py`, `tests/test_exact_engine_dependency.py`,
  `tests/test_front_end_free_exact.py`, `tests/test_core_kernel_free.py`,
  `tests/exact_engine_absent.py`
- `openspec/specs/exact-engine-dependency/spec.md`

## Amendment (2026-10-03)

[ADR-167](ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md)
makes the OCCT binding the `occt` extra's. The engine module is now in every
install and checks for `OCP` before importing it; the seam counts that
refusal as an absent engine, so `exact_engine()` answers `None` and
`require_exact_engine` names `pip install "machinome[occt]"` as before. An
`OCP` found and failing to load is still reported as itself. The engine
imports `machinome.extras` beside the contract module.

## Amendment (2026-10-04)

[ADR-176](../TEST-FRAMEWORK/ADR-176-the-mesh-engine-is-a-provider-behind-the-seam-installed-by-an-extra.md) applies this record to the mesh engine:
the core holds no mesh-engine code either. Its provider
`machinome.manifold.engine` is named only by the seam `machinome.mesh_engine`,
which takes this seam's shape (`CONTRACT = 1`, `PROVIDER`, Protocols by
consumer, an absence rule reading the `manifold` extra's refusal as an absent
engine, `MeshEngineIncompatible` for a contract mismatch), and the core's
mesh solids are opaque handles in core-held caches.
