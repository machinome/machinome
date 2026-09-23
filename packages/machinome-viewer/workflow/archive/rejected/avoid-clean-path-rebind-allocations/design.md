## Context

`PathValue.bind` retains a prior piece's input snapshots and graph values. On each later piece it currently creates a dirty `Set`, calls `inputAt` (allocating `{present,value}`) for every input leaf, then often returns before evaluating a node. In the frozen OperatingCurta higher-counter export, 87.7% of 618,561 binds in 12 normal ticks are clean, across 1,062,064 leaf checks. The V8 profile attributes about 3.5 CPU seconds of the first 48 ticks to bind itself and substantial time to GC.

## Goals / Non-Goals

**Goals:** Remove avoidable allocations on a clean rebind while preserving input access and evaluation order, snapshot identity, signed zero, NaN, missing-key semantics and error timing. Demonstrate exact Curta state/sample parity and material CPU reduction.

**Non-Goals:** Change first bind, `at`, graph traversal, operators, tick duration, sampling, paths' lifetime, or program constraints.

## Decisions

Keep the existing ordered input loop. Read each name from the node, check own-key presence once, and read a present value once. Compare the primitive pair against the retained snapshot using the same presence test and `Object.is`. Allocate a replacement snapshot and a local dirty set only on the first difference; update both immediately before moving to the next leaf. If no difference exists, return the retained root without allocating either. On a difference, run the existing full-postorder dirty propagation unchanged. First bind keeps `inputAt` and preflight untouched.

The dirty set stays local rather than a mutable field, avoiding reentrancy and reset-lifetime questions. Caching constraint paths was considered but rejected after instrumentation found only 24 constraint first binds versus 19,357 jump first binds in the first 12 ticks. Flat-bank scope lookup was separately profiled and rejected at a 1.2% paired improvement.

## Risks / Trade-offs

- [Getter or throwing input changes first error] → preserve own-key/read order and test a late throwing getter after an earlier changed leaf.
- [Stale `-0`, `NaN` or missing value] → retain `Object.is` and presence comparisons, with red-first tests and exact Curta state hash.
- [Allocation reduction is too small] → pair CPU15 before/after on one pinned export and reject if not material.

## Migration Plan

Internal-only. No migration; the isolated implementation commit can be omitted from main if parity or performance gates fail.
