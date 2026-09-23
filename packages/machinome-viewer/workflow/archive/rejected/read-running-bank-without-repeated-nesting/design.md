## Context

The running program passes a fresh flat coordinate map to `evaluateExpression` or `kinkLevel` at every path sample. Those adapters call `nest(values)` even when the expression reads one exact qualified coordinate. On the frozen higher-counter OperatingCurta export, V8 assigns 2.97 of the first 48 ticks' 22.08 CPU seconds directly to `nest`; GC takes another 2.46 seconds. The loader already rejects strict-prefix bank identifiers.

## Goals / Non-Goals

**Goals:** Avoid repeated nested-tree construction for exact running-bank reads; retain the existing scope semantics and evaluator pass invalidation; prove same-export parity and a material CPU reduction.

**Non-Goals:** Alter dt, search samples, motion demand, arithmetic operators, parsing, public widget scope semantics, CSP, or document/API versions.

## Decisions

Only running adapters will opt into an internal flat bank. Name resolution keeps `$t` and binding-head precedence, then reads an own exact key from that bank. On a miss it constructs the old nested tree lazily and follows the old member-chain implementation, including context fallback and native errors. A scope with this flat bank compares flat values and presence with the existing `Object.is` map rule; mixed flat/nested scopes do not share a pass. Each evaluation still creates a fresh scope, so memoized values cannot survive changed bank data.

This is preferable to a global nested-scope cache, which would need a mutation/lifetime policy across path samples. It also avoids broader compiled-operation work while the profile names scope construction as a measurable hotspot.

## Risks / Trade-offs

- [Binding or context collision] → retain head precedence and exercise collision/partial-name cases against the old path.
- [Signed zero, NaN, or missing-key stale memo] → compare value and presence with the existing `Object.is` map rule and assert bit-level parity.
- [Extra scope branches hurt simple documents] → opt in only from the running adapters and compare a pinned Curta window before integration.
- [Nested fallback could rebuild often for partial reads] → accepted as the conservative correctness path; no speculative document-wide rewrite.

## Migration Plan

Internal-only change; no migration. Revert the implementation commit if the paired performance/parity gate fails.
