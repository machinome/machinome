## Context

`Run.constraintLevel` scales admissions and replays a constraint's compiled prefix at every existing search fraction. The production Curta's paired Follow Bounds have the same three `ProgramEdge` object identities in the same order. Follow's retained output has no determined `Motion`, so both searches take this fallback; 20 searches replayed 768 prefixes in five ticks. The existing v12 Follow certificate makes its source laws affine and its boundary paths piecewise affine, while each Bound expression is evaluated separately after propagation.

## Goals / Non-Goals

**Goals:** Eliminate only duplicate successful prefix propagation for the same stretch, edge sequence and IEEE-identical sample fraction. Preserve all Bound samples and errors, including first-error order, numeric operands, cuts, stops, bank and replay.

**Non-Goals:** Synthesize a Follow `Motion`, change sample resolution or timestep, cache across stretches, or memoize Bound expression evaluation. No new API/document version.

## Decisions

- `reachedBounds` owns a fresh private cache and passes it through its paired Bound searches. Its lifetime ends before the stretch can be retried or committed. A cache entry holds a successful prefix's deltas and optional exact absolute landings. A thrown propagation never enters it.
- Match prefixes by length and ordered `ProgramEdge` identity, not description, text, coordinate or endpoint. Match fractions by JS `Map<number>` only for finite nonzero fractions; zero and signed-zero distinctions remain uncached, and non-finite fractions never occur in prescribed searches. Apply reuse only to the empirical producer shape: zero or more ordinary source laws followed by exactly one terminal Follow. Walk all source, envelope, plan and expanded-binding expression graphs once per stretch and exclude `random` or an indirect/overridden call. An affine-shaped constant call such as `random(1)` is not necessarily deterministic; the shape certificate alone does not establish purity. Every Bound graph remains freshly evaluated.
- Build the cache only around the existing prefix propagation in `constraintLevel`. Let the ordinary prefix propagate successfully before structural cache-eligibility inspection; if that extra inspection fails, disable reuse and continue the ordinary Bound evaluation, so it cannot preempt a prefix error. Neither the sample sequence nor the numerical expression of a level changes. Avoid touching tracing and its standing-value cache.

Alternatives: a reconstructed Follow path is harder to certify across retention and jump sides; a cross-tick cache would require additional invalidation; caching whole Bound levels would conflate low/high graphs and change error timing.

## Risks / Trade-offs

- [Different prefix under a similar Bound] → Require exact ordered edge identity.
- [Stale values after a stop or restore] → Cache scoped to one `reachedBounds` invocation only.
- [Skipped error or stateful expression] → Cache successful certified Follow propagation only; keep Bound graph evaluations separate and test a throwing Bound after one successful sample.
- [Memory under long sample series] → At most one stretch's finite search fractions; discard when the bounds pass returns.

## Migration Plan

Pure internal optimization. Removing the cache restores the old executor with no document or snapshot migration.

## Open Questions

None before implementation; red-first tests must confirm that this exact key matches Curta's production prefix.
