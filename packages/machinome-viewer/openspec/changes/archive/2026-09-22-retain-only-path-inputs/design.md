## Context

ADR-074 preserves the original piece's `values` in `ExpressionPath` so a generation reset between `bind` and `at` can re-create its `PathValue`. The owner currently spreads the entire flat bank into a new object for each bind. The actual OperatingCurta bank has 213 keys; its post-cache profile has 3,750 of 28,997 self samples in the bind closure containing this copy. Only the unresolved names reached by that expression's DAG need saving. The document and bank are pinned in `workflow/evidence/operating-curta-path-cache-2026-09-22.md`.

## Goals / Non-Goals

**Goals:** Retain only actually read flat-bank inputs while preserving presence and `Object.is` values across a generation reset. Prove no unrelated bank key is read; remeasure the same 48-tick window and exact bank digest.

**Non-Goals:** Change evaluator arithmetic, samples, dt, branch choice, source timing, nested-scope construction or WebGL rendering. A larger residual bottleneck belongs to another evidenced cycle.

## Decisions

`PathValue` already records unresolved leaf names and their input snapshot during `bind` for ADR-074. Expose a snapshot of those relevant present inputs to `ExpressionPath` after successful bind instead of re-enumerating `values`. On generation change, the new `PathValue` binds from that small immutable snapshot before serving `at`. This is naturally generation-qualified and preserves absent names as absent. Cloning the whole bank and keeping a reference to the mutable bank were considered; the former pays for every unrelated coordinate, the latter could read later mutation as the original piece.

## Risks / Trade-offs

- A binding reaches a name absent from the outer expression → the existing `PathValue` postorder descends into bindings; its unresolved leaves supply the snapshot.
- Context names and absent input names → retain only present bank properties, so context fallback and absence remain exactly as before.
- A reset under a changed binding table → an `ExpressionPath` is document-owned; republishing replaces the owner. Tests cover a table reset with stable binding semantics.

## Migration Plan

No version or schema change. Rebuild the viewer bundle after corpus and actual-export parity checks. Revert this internal cycle if any bank differs.

## Open Questions

How much of the profile's bind-closure cost is the bank copy must be measured; no gain is assumed from the profile alone.
