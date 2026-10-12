## Context

The viewer's `kinkBreaks` accepts arbitrary callbacks and deliberately evaluates each kink in postorder at the endpoints of each current sub-interval. Ordinary OperatingCurta running laws call it with expression-backed `kinkLevel` callbacks. A pinned five-tick profile measured 421,392 evaluations, 155,267 repeats of the same kink and fraction, and a 20–22% CPU gain from an in-memory search-local memo. The generic callback may be stateful; expression bindings can include `random()` or indirect calls. The public cut and Bound-search contracts cannot change.

## Goals / Non-Goals

**Goals:** Reuse only successful, deterministic, exact same-kink/same-fraction evaluations during one `kinkBreaks` invocation. Preserve the existing ordered search, error timing, signed-zero/NaN behavior, bank bits and replay. Prove meaningful gain on the pinned Curta export.

**Non-Goals:** No structural expression common-subexpression elimination, cross-search/run memo, reduced sample count, altered cuts/tolerances, new API or document version, or caching arbitrary callbacks.

## Decisions

1. Keep generic `kinkBreaks` uncached by default. Its private expression-backed entry point builds the `kinkLevel` callback itself; no caller can provide an arbitrary callback under an asserted purity flag. Before reuse, a recursive graph/binding provenance walk proves every operand is numeric and each call node is from a closed deterministic numeric-function allowlist. Indirect calls, `random`, binding-shadowed callees, array/object/member/index/coercing shapes, unresolved/custom calls, and uncertain provenance fall back to original evaluation. The proof traverses both operands of every kink, including binding roots, before any callback is invoked. A preflight error also falls back without surfacing a new first error.
2. Allocate the memo inside one `kinkBreaks` call and release it on return or throw. Key by the resolved current kink descriptor and finite fraction with exact signed-zero handling; conservatively bypass nonfinite fractions/results and any uncertain key. Publish only after the callback returns successfully. The first evaluation and all uncached evaluations retain the original order and arithmetic. No historical entries survive to another piece, tick, restore or Run.
3. Bound per-call retention at 2,048 entries. The pinned Curta probe measured a largest search of 1,898 distinct kink/fraction keys, so this retains its complete measured reuse without indefinite growth. At capacity, leave existing entries intact and evaluate new keys normally; no eviction may change computed cuts or error order.
4. Opt in at the expression-backed running-law and Follow cut paths only where the `program`, kink graph and numeric scope are known. The pinned Curta's 768 Follow boundary cut searches account for 129,622 repeats and have 40 or 116 kinks; 225 law-motion searches account for 24,600 repeats and have at least 25 kinks. Searches with fewer than three kinks take the original eager path immediately to avoid proof/Map overhead on small machines; a two-kink synthetic throughput fixture otherwise regressed under load. Keep unknown custom binding/value cases on the original path. Existing pure-expression prefix-cache eligibility is related but not a substitute: kink callbacks have different operand roots and lifetime.

## Risks / Trade-offs

- **False purity admission** → Closed function allowlist and recursive binding walk; negative tests for `random`, indirect/custom calls and changed bindings. Reject uncertain cases even if that loses an optimization.
- **Collapsed IEEE keys** → Distinguish signed zero or bypass it; never cache NaN/nonfinite inputs or outputs. Test exact bits and same fraction under different kink identities.
- **Changed failure order** → Cache successful results only; failures never publish, and generic/stateful callbacks never opt in. Test retry after an error and competing errors.
- **Runtime expression-store reset** → Resolve retained kink descriptors within a `withExpressions` scope; the memo cannot outlive its search and never keys raw node IDs across generations.
- **Performance disappointment** → Require paired CPU timing and exact bank/ordered-bound equality on the same pinned production artifact; abandon or narrow the cycle if the certified path misses the measured opportunity.

## Migration Plan

No serialized or host-facing migration. Keep the old path as fallback, run focused and broad viewer suites plus actual Curta parity, then integrate the isolated verified branch locally. Rollback is reverting this viewer-only implementation commit.

## Open Questions

None remaining before red tests. If the conservative graph proof excludes a material portion of the measured Curta paths, measure that honestly and narrow or reject the cycle rather than weakening eligibility.
