## Context

`_PathValue.bind` eagerly walks every node on each first-point bind, even when an existing path object is rebound with the identical inputs it just evaluated. The frozen Curta program `be125f4048c8be00ce4e73d646311d4a50ac75a59aa739f93bf2f38c992fa195` performs 44,200 such binds in one ordinary default-cadence tick: 41,490 repeat the same path object's immediately preceding IEEE input tuple, representing 91.8% of bind node visits. Structural common-subexpression elimination is not the remedy: just 0.66% of these bind visits are duplicate subtrees within a graph, and the crank Bound's moving cone duplicates only 7 of 1,479 nodes. The read-only path-local prototype reduced first-48 tick CPU by 18.6% with exact bank and ordered Bound-level parity.

## Goals / Non-Goals

**Goals:** Avoid only a redundant, successful first-point numeric walk on the same path instance; preserve the original eager first error and publication on every uncertainty or change; keep the path's existing short lifetime and all sample points.

**Non-Goals:** No structural interning, cross-path or cross-run cache, JIT, new operator, lazy branch, changed sample count, tolerance, timestep, document, project law, or viewer behavior.

## Decisions

1. Give each private `_PathValue` one last-successful-bind entry, containing the graph root identity, fixed moving-name set, names actually referenced by its graph, their finite IEEE-754 bits, and the result. The path instance fixes graph and moving shape; checking them also prevents an accidentally modified private path from receiving a stale hit. A fresh path or reset/new Run has no such entry. A successful `bind_from` invalidates any local entry before publishing its different standing state.
2. On `bind`, compare the entry before evaluating graph nodes only for an exact plain `dict` of builtin `bool`, `int`, or `float` values. Missing, custom, nonfinite and conversion-uncertain values take the existing complete walk. Signed zero has distinct bits. Unreferenced keys do not invalidate a valid result. The cache check never invokes user-defined conversion or expression operations.
3. A hit returns the last successful result without touching path structure or standing state. `at` is read-only with respect to that state, so an intervening sample cannot stale the entry. On a miss, perform the original eager walk and publish the new entry only after the complete bind succeeds. An exception leaves the previous successful entry and existing path state intact; subsequent changed input still full-binds, while returning to the earlier proven input remains safe.

The numeric expression vocabulary is the framework's closed pure degree-math/operator set (ADR-139), not the viewer's independent context with `Math.random`. The decision is about a private path object already local to a tick (ADR-124), not an additional Run-owned cache.

## Risks / Trade-offs

- **Key checking outweighs a small bind** → Measure a default-cadence 48-tick Curta pair in process CPU time and retain the change only with a material net gain. Use graph-referenced names, not the growing branch-argument dictionary.
- **Different inputs compare equal as Python numbers** → Compare finite IEEE bits, including signed zero; reject nonfinite or custom values.
- **Cache validation changes earliest error** → Reject custom mappings/values without conversion, and route every miss to the original eager walk; exercise competing missing/domain/arithmetic failures and failed-bind recovery red-first.
- **A later state or graph uses old standing values** → Keep one entry on the path instance only; invalidate on successful `bind_from`; test new path, restore/reset/new Run and changed moving or graph identity.

## Migration Plan

No migration: the cache is private and ephemeral. Reverting the implementation restores full binds without changing authored models or serialized documents.

## Open Questions

None; the originating project's speed and exact ordered-level parity are implementation gates, not a request to change semantics.
