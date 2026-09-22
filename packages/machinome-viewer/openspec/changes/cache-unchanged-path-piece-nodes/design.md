## Context

`PathValue` already identifies the moving cone of an expression once, then caches standing nodes for `at` samples within a piece (ADR-060). But `bind` clears every standing value and computes every node again on every subsequent piece. The OperatingCurta v11 export (213 coordinates, SHA256 `cdbb284e56672aa905e38a25c7efd1f3169fc8f128cd3195f27baf7745a9c28b`) takes 29.94 s for the first 48 of 480 crank ticks in Node without WebGL; a CPU profile attributes 18.4% of self samples to `bind` and 11.3% to `valueAt`.

## Goals / Non-Goals

**Goals:** Avoid repeated expression node resolution when a path is rebound under equal inputs; maintain bit-identical results; measure work with the existing resolution probe and the same real export.

**Non-Goals:** Change search density, admission rules, the gesture's two-second declaration, tick size, moving-cone calculation, or browser rendering. This cycle need not by itself make the whole crank interactive.

## Decisions

1. Keep a bound value per node and a shallow snapshot of only bank names the graph reads. Compare both own-property presence and `Object.is` at each bind. A fresh object with identical values is equal; `NaN`, `-0` and absent/undefined remain distinguishable. `ExpressionPath` continues to rebuild the entire `PathValue` on expression generation change, so table generations cannot leak.
2. On the first bind, retain the current full postorder and moving-cone classification. On later binds, mark changed name leaves and propagate dirtiness through the graph's original postorder, including through bindings. Recompute only dirty nodes, in that order. Keep the previous bound map separate from `at`'s scratch map, so sampled moving values cannot become the next piece's standing values.
3. Retain the existing `valueAt` operation dispatch and `resolutions` accounting for every actual evaluation. Do not change the program evaluator or its compatibility fallback.

Alternatives: hashing whole values objects would be vulnerable to order and hidden mutation; retaining only full-piece values would not avoid the dominant repeated DAG walk. Comparing all 213 bank keys per expression is unnecessary when a path reads only a subset.

## Risks / Trade-offs

- A bound name can alias a binding expression → include binding roots as dependencies in the existing child graph; compare only unresolved flat-bank leaves.
- Context functions or globals may be mutable → only cache nodes composed of the expression evaluator's existing deterministic functions; reject unsupported node shapes as today. Any context mutation during one step was already outside the current piece-level cache contract.
- Dynamic graph generation invalidates node IDs → `ExpressionPath.current()` already replaces the `PathValue` on generation change; test it.
- A benchmark gain may be insufficient for interactive cranking → record actual before/after and profile the next hotspot separately.

## Migration Plan

No document or API migration. Build a new viewer bundle and exercise the existing conformance corpus and actual export; revert this internal commit if parity fails.

## Open Questions

None for the cache contract. Overall OperatingCurta latency will be judged after measurement.
