## Context

ADR-124 deliberately gave each `_PathValue` a one-path lifetime: an earlier Curta found only a 5% benefit from cross-tick structure reuse, and avoiding stale cache state was cheaper. The current `OperatingCurta` has a different cost shape. At default `dt=1/240`, a low crank constraint binds a 126,032-node graph on every tick, but only 1,479 nodes depend on the moving bell. Across the frozen project's first 48 ticks, the only changed arguments were bell turn and the crank's held own value; the latter is not referenced by the graph. The first-sample full bind consumed 1.722 CPU seconds in eight ticks, versus 0.199 seconds for all 512 later samples. A process-local value-checked prototype reduced 48-tick total CPU by 23.5% with an exact 213-coordinate bank.

This is internal framework work. A separate viewer implementation needs its own empirical proof and repository cycle. The framework's published program and the fixed search samples do not change.

## Goals / Non-Goals

**Goals:**

- Reuse only the standing numerical values from a prior *successful* bind of the same running constraint when every graph-referenced standing input is exactly unchanged.
- Preserve first-sample postorder and first error, later sample arithmetic, signed-zero behavior, all state/events/refusals, and bounded memory ownership.
- Retain the complete original bind whenever a cache hit cannot be proven.

**Non-Goals:**

- No reuse of moving-node values, path samples, entire constraint results, other law/JumpPlan bindings, or errors.
- No new contact certificate, reduced sample count, changed `dt`, changed law, author option, public cache, or document field.
- No process-global graph registry or persistence across simulations.

## Decisions

1. **Keep one previous bind snapshot per compiled constraint on the owning `Run`.** A fresh `_PathValue` is still created per traced search; the run offers it the prior snapshot at its original `t=0` bind. The cache has at most `len(program.constraints)` entries, replaces an entry rather than appending history, and is discarded with the run. Inactive bounds and prefix-replay searches never consult it. Alternative: a global graph cache or one cache per transient path object; the former leaks graph lifetimes and the latter cannot cross ticks.

2. **Prove standing-input identity from the actual first-sample arguments.** The prior graph root must be the same object, the moving-name frozenset must match, and every graph `name` outside that set must be present, numeric, finite, and bit-identical after the same float conversion as a full bind. Compare IEEE bits, not Python `==`, so `+0.0` and `-0.0` differ; NaN, infinity, missing names, failed conversion, or any mismatch take the original full bind. Names passed but not referenced by the graph do not invalidate it. The cache never keys by mutable source-object identity. Alternative: hash the entire arguments dict or compare source identities; the former loses Curta's win on an unused own argument, and the latter is unsafe when branch placeholders mutate.

3. **Reuse only successfully evaluated standing slots and immutable structure.** The previous full bind supplies the exact standing values, standing-node positions, moving instructions, and graph order. On a hit, evaluate every moving node for the new `t=0` values in the same moving postorder and with the same operators, reading previous standing slots. A standing operation can neither gain a new domain error nor change its value when all its named operands are identical finite floats and the graph/operators are unchanged. Publish the fresh path and replace the run's snapshot only after this first-point evaluation succeeds; otherwise leave the previous entry untouched and propagate the original error. A miss executes the existing full bind in original order and publishes a snapshot only on success. The path's later `at` evaluation remains unchanged. Alternative: reuse the whole previous result, which would miss moving errors and contact.

4. **Make uncertain lifecycle transitions conservative.** Clear the run-owned entries after successful snapshot validation on restore/reset; a new `Sim`/`Run` starts empty. A changed moving-name shape or standing value causes a full bind and replaces the one entry on success. Failure, refusal, and rollback do not publish a partly built entry. Directly altering numeric operator implementations during a live run is outside the immutable compiled-law contract; tests will nevertheless require the cache to use the same selected operators for moving nodes and to fall back on every supported graph/input change.

5. **Record the revised architecture explicitly.** ADR-124's no-cross-tick-cache rationale is amended only for this bound-specific, value-proven case; general `_PathValue` users retain path-local caching. An accepted ADR and architecture synthesis update follow only after numerical/error tests and real Curta evidence.

## Risks / Trade-offs

- **An earlier unchanged node once failed** → A failed full bind never seeds the cache; reuse only follows a complete successful bind, and changed standing input forces the original topological walk.
- **Error precedence changes on a miss** → Cache validation swallows missing/conversion uncertainty and delegates to the existing bind; it does not evaluate graph operations before that bind.
- **Signed zero, NaN, or nonfinite input aliases** → Compare finite IEEE bits; any nonfinite value forces full evaluation.
- **A branch or held coordinate changes despite source-object reuse** → Compare actual numerical first-sample arguments, not object identity; moving-name shape changes miss.
- **A failed hit corrupts the next search** → Stage a fresh path and publish the new snapshot only after `t=0` succeeds; test a failed bind followed by a valid search.
- **Cache retention or stale restore** → One entry per constraint owned by the `Run`, clear on restore/reset, and no shared global state.
- **A large graph's copied standing slots erase the gain** → Reuse immutable positional tuples rather than re-evaluating or duplicating all 124,553 values; benchmark actual 48-tick CPU and the complete Curta turn, not just a microbenchmark.

## Migration Plan

No user migration. A failed conformance or performance gate leaves the framework main branch unchanged; the isolated cycle can be revised or abandoned. No document version or serialized state changes.

## Open Questions

The implementation must confirm that a fresh `_PathValue` can hold a successful prior standing snapshot without retaining a mutable prior path or changing `_visited` accounting, and that full Curta turn/stop replay plus synthetic error-order tests remain exact. If either fails, retain the existing full-bind path and revise the proposal before integration.
