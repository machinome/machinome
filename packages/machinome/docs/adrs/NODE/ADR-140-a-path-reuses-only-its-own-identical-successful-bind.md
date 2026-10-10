# ADR-140: A Path Reuses Only Its Own Identical Successful Bind

**Status:** Accepted

**Date:** 2026-09-22

**Amends:** [ADR-124](ADR-124-only-what-moves-along-a-tick-s-path-is-evaluated.md)'s statement that every new piece recomputes its standing nodes and its rejected whole-dictionary evaluation cache. This is a path-local first-point exception, not a per-sample or cross-tick cache.

**Extends:** [ADR-139](ADR-139-a-running-bound-reuses-proven-standing-bind-values.md)'s finite IEEE input proof to repeated binds on one path instance. Its separate Run-owned standing Bound snapshot remains unchanged.

**OpenSpec change:** [reuse-identical-path-binds](../../../openspec/changes/archive/2026-09-22-reuse-identical-path-binds/)

## Context

The Curta Type I's `OperatingCurta`, frozen at project commit `7586002`, remained slow after ADR-139. On its default `dt=1/240` crank path, 41,490 of 44,200 `_PathValue.bind` calls in one tick received the same finite IEEE inputs as that *same path object's* immediately preceding call; those repeats accounted for 91.8% of bind node visits. A sample-by-sample whole-dictionary cache, rejected by ADR-124, is not justified. Neither is structural expression deduplication: only 0.66% of measured bind node visits were duplicate subtrees, and only 7 of the crank Bound's 1,479 moving nodes were structurally duplicate. The narrow measured opportunity is to skip an identical successful *rebind* while retaining all search samples.

## Decision

Each private `_PathValue` keeps at most its last successful first-point result. A subsequent `bind` may return that result only when the same path root and moving-name set still apply and every graph-referenced input in a plain dictionary is a builtin finite number with identical IEEE-754 bits, including signed zero. Unreferenced passed keys are irrelevant. A custom mapping, custom-converting scalar, missing input, NaN, infinity, changed bits or other uncertainty takes the original complete eager walk, in its original postorder. The entry is replaced only after a successful complete bind; an error retains the last proven entry and the prior path state. A successful `bind_from` invalidates this path-local entry before publishing its other standing state.

Later `at` samples continue at the same points with their same positional moving program. They do not modify the bind entry. The entry lives on the existing short-lived path object, not on a process, graph registry, run or document. A new path, including after reset or restore, starts unproved. The numeric evaluator has a closed pure degree-math/operator vocabulary; dynamic monkeypatches of its functions during a path are outside the compiled-law contract. This does not transfer to the viewer's independent JavaScript context, which includes `Math.random`.

## Alternatives

- **Structural common-subexpression elimination:** rejected at 0.66% duplicate bind visits and 7 duplicate moving Bound nodes, before any cost of structural hashing or changed error-order proof.
- **Reuse by source/dictionary identity or Python `==`:** rejected because branch dictionaries and source objects mutate, signed zeros compare equal and NaNs do not establish sameness.
- **Hash every passed dictionary value per sample:** the earlier ADR-124 rejection still applies; many Curta argument dictionaries grow to over 100 entries while the small bound graph reads only a few names. The entry is keyed by graph-referenced numeric inputs and checked only for first-point binds.
- **Cross-path, cross-run or unbounded memoization:** rejected because this finding requires only one previous success on one path, and larger lifetime raises graph ownership and stale-state questions without a measured need.
- **Reduce `_SUBDIVISIONS` or change dt:** rejected because it would change the machine's contact search, not avoid redundant arithmetic.

## Consequences and Evidence

No public API, law, source timing, event order, sample count, tolerance, bank arithmetic, document field or version changes. In a paired frozen-Curta first-48 default-cadence run, tick CPU fell from 31.160 to 25.906 seconds (16.9%); on a pinned production Curta program, from 32.213 to 26.602 seconds (17.4%). The complete 360° turn and active stop/restore/replay retained their exact 213-coordinate bank and all ordered Bound input/result IEEE bytes. Focused tests cover signed zero, nonfinite/custom fallback, eager competing errors, failed-bind recovery and `bind_from` invalidation. Commands, hashes, program identities and full framework gates are in the archived change's `evidence.md`.

The cache adds one small tuple to a path object that already holds its graph and positional program. It does not make the Curta interactive on its own; propagation and other complete binds remain substantial. The viewer must prove any analogous optimization under its own evaluator contract.
