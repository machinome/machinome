## Context

`Run.searchedConstraint` currently constructs a new `ExpressionPath` per determined Bound search. Its first `PathValue.bind` preflights and evaluates the entire graph even when the bound's standing bank reads have not changed since the preceding tick. The OperatingCurta frozen export shows 47 matching repeats of a 63,252-node graph in the first 48 default ticks; 61,630 nodes stand. `PathValue` already retains bound node values and incrementally rebinds a later piece (ADR-074), but the search-local path is discarded after each search.

## Goals / Non-Goals

**Goals:** Reduce repeated standing-node evaluation in determined Bound searches while preserving the exact first sampled value, ordered later samples, errors, admitted travel, bank and replay. Bound memory to one retained path per declared constraint per run and clear it on reset/restore or expression generation change.

**Non-Goals:** Caching generic `nest` scopes, changing source or constraint laws, changing timestep/subdivisions/bisection, accepting nonfinite bank inputs, exposing a page/API control, or caching searches that use generic fallback.

## Decisions

1. Reuse the existing `ExpressionPath`/`PathValue`, not a second evaluator or a global graph table. A `Run` holds at most one successful path per constraint object. Reuse requires identical moving-name membership, the same expression generation, and a plain finite first-sample scope. `PathValue.bind` itself compares each referenced leaf's presence and `Object.is` value; changed standing leaves and their dependents execute in original postorder. A different shape, generation, nonfinite scope, failed bind, unsupported structure or failed search uses a fresh path and cannot seed the cache. The map is cleared by restore/reset. This reuses the proven ADR-074 mechanism rather than copying its node-value representation.
2. A rebind used for a new search forces evaluation of the moving cone at its first sample, including when its leaf values happen to equal the prior search's first sample. Changed standing dependents and moving nodes are visited once in the original topological order with the same operators. Later prescribed samples continue through `at`. Generic fallback and untraced prefix replay are unchanged.
3. Commit a path to the cache only after its whole search completes without error. If a reused path errors, evict it before propagating the original error. Do not cache `UnsupportedPathNode` fallback. The cache cannot hide first errors from side-effecting caller getters because the searched scope is freshly constructed from ordinary numeric fields, and no externally supplied object is cached.
4. Prove rather than assume benefit: compare pinned frozen Curta first 48 default-dt ticks on the same CPU with exact 213-coordinate bank, ordered Bound sample bits, and source fixture replay. Accept only a material process-CPU reduction without parity loss. The current production export gets a separate equivalent gate before installing the rebuilt bundle.

## Risks / Trade-offs

- **Standing-value reuse hides an error** → cache only a successful prior search with finite ordinary numeric scope, retain the same graph/generation/moving set, run changed and moving nodes through the original operator path, and exercise first-error and unsupported-node regressions.
- **A stale path survives expression reclamation or restore** → generation guard plus explicit map clear on restore/reset; one entry per constraint bounds retained graph data. Two mounted runs own separate maps.
- **A rare branch shape invalidates reuse** → replace the entry and take the original full-bind/fallback path; compare presence and `Object.is` exactly, including signed zero and NaN behavior in the non-cache path.
- **No material speedup** → reject implementation, preserve the measurement in workflow evidence and leave runtime unchanged.

## Migration Plan

No document or API migration. A changed bundle can be rolled back without changing exports or snapshots.

## Open Questions

The measured CPU saving and exact active-stop sample trace are implementation gates, not assumptions of this plan.
