## Context

ADR-124 already classifies a tick-local graph into standing and moving nodes. `_PathValue.bind` eagerly evaluates every node in postorder at each piece, and `_PathValue.at` evaluates only the moving cone at later samples. The latter nevertheless reconstructs a dictionary keyed by `ExpressionNode` and hashes each child's key on every sample. A production Curta station-3 withdrawal stop at project `7586002`, framework `6dc07a8`, spent 4.21 of 16.29 profiled CPU seconds in 145,224 path samples. The result-bank restraint remains necessary and all 64 search samples and exact stop semantics are fixed.

## Goals / Non-Goals

**Goals:** Reuse immutable moving-cone child positions within a path value; keep fresh numeric moving storage for every sample and fresh standing values for every piece; reduce the measured Curta cost without changing any result or error.

**Non-Goals:** Skip inactive chart branches, fold errors, cache numeric inputs across pieces or ticks, change evaluator operators, alter constraint search, change public APIs or viewer documents, or change the mechanical project.

## Decisions

1. Compile a path-local tuple of moving nodes and their child references after the first **successful** bind. A child reference names either a position in the moving result array or a position in a standing-value array. Preserve `self.order`'s existing postorder; compile structure only, never evaluate ahead. This removes per-sample node hashing while retaining ADR-124's tick-local lifecycle. A process-wide graph cache and generated Python code are unnecessary and carry lifecycle/code-generation risks.
2. On each successful bind, run the existing complete eager postorder evaluation before replacing the standing-value array. The array is formed from that piece's freshly computed standing dictionary in fixed structural order. A failed bind does not publish new structure or numeric values. At each `at`, allocate a fresh moving result list and dispatch the same operators/call functions after gathering children in original operand order. No arithmetic is precomputed for moving nodes.
3. Keep the existing `_visited(len(self.order))` seam, constant-root path behavior, and missing-input/invalid-call error locations. Red-first tests will prove no `ExpressionNode` key hashing occurs in later samples, standing values refresh on rebind, failed first and later binds preserve previous behavior, and float bits/error ordering match whole-graph evaluation. Use the frozen project `7586002` for a paired active-stop timing and all 213-bank outputs.

## Risks / Trade-offs

- [A standing slot could be stale after a new piece] → Rebuild it only from a complete successful eager bind; test rebinding and failure.
- [Compiled references could reorder operations or errors] → Keep the original postorder and operand tuples; compare signed-zero, NaN, invalid arity, missing inputs, arithmetic exceptions, and exact Curta stop bank.
- [Array/list overhead could erase the gain] → Measure CPU before and after on the same frozen project and search scenario; abandon the optimization if no material gain.
- [Structure could retain discarded graph] → Store it on the tick-local `_PathValue` only and retain GC tests.

## Migration Plan

Internal-only change. Revert the isolated implementation commit if parity or measured benefit fails; no document migration.

## Open Questions

None; the paired Curta measurement is the acceptance gate.
