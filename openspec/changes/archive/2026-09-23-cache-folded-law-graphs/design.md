## Context

Curta Type I's certified Follow path repeatedly folds the same immutable expression roots with identical jump substitutions while locating a Bound. In a five-tick production command, 7,240 folds represented 1,862 exact root/substitution states. A diagnostic 256-entry cache reduced process CPU from 19.744 to 16.423 seconds without changing the 214-coordinate bank. The current `_folded` implementation is pure for finite built-in numeric substitutions, but accepts arbitrary objects via `float`, so reuse needs a narrow eligibility proof.

## Goals / Non-Goals

**Goals:** Avoid repeated structural folding within one running tick; preserve the exact first error, IEEE values, sampled constraint order, stop and bank; bound memory and discard it on success or failure.

**Non-Goals:** Change expression arithmetic, law partitioning, sampling, tolerance, authored APIs, serialization, or cross-tick/run reuse.

## Decisions

- Use a private tick-scoped cache around `_folded`, active only during `Run.advance`. This gives all fold callers in a tick reuse without changing their signatures. A context-local scope is reset in `finally`, so nested or independent runs and failed ticks cannot inherit entries. Direct folding outside a running tick retains its original path. A run-owned persistent cache was considered but retains graphs across ticks and adds restore/reset invalidation for no measured need.
- Key by the original root's identity and the complete substitution mapping, sorted by name. Encode every value as finite IEEE-754 bits; `+0` and `-0` remain distinct. Eligibility requires exact built-in `bool`, `int`, or `float` values and successful finite conversion. A custom object, non-finite value, malformed mapping, or conversion failure falls back to the original fold, which determines its original error. This deliberately avoids invoking custom conversion during a cache lookup.
- Store only the result of a successful original fold in a 256-entry least-recently-used working set. No exception or partial graph is published. Eviction changes only cost; immutable expression roots/results allow identity reuse. The cache performs no numeric evaluation or speculative preflight.

## Risks / Trade-offs

- **An omitted key dimension could reuse a wrong fold** → key the entire mapping and root identity; test distinct roots, signed zero, changed and unused substitutions, and production ordered Bound samples.
- **A cache probe could change the first error** → bypass uncertain/custom/non-finite values without conversion side effects; publish only after success; test failed folds and retry.
- **Cross-run graph retention or nested scope leakage** → one bounded cache per `advance`, context reset in `finally`; test failure, restore, and two runs.
- **The cache may underperform on another workload** → record repeated paired CPU measurements on the unchanged production command; do not claim universal speedup.

## Migration Plan

No migration or document change. Removing the private wrapper restores the original path. Validate red-first, focused and full framework suites, and bit-exact project traces before integration.

## Open Questions

None; the production measurement selects tick-local lifetime and the narrow numeric eligibility.
