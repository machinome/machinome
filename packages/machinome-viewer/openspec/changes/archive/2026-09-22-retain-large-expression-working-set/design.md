## Context

ADR-043's page-scoped, hash-consed expression table reclaims at 50,000 nodes before an outer operation. ADR-043's lifetime amendment made a >50,000-node *single operation* safe, but retained the old threshold. The committed OperatingCurta `7586002` export (SHA256 `c36432b1…`, identity `be125f40…`) prepares 97,474 nodes on load. A direct generation probe recorded generation 0 at load, generation 48 after the 48-tick selector, and generation 49–52 across the first four crank ticks. Each crank tick rebuilt about 94,763 nodes. A V8 profile attributed 13.1% self samples to jokenizer's operator-list getter, 5.5% to DAG interning, additional samples to tokenization, and 5.8% to garbage collection; the first 48 crank ticks took 53.886 seconds with no WebGL.

The already-active `CounterTensOperatingTrial` candidate was exported separately from the current project source (manifest SHA256 `3ccbaf03…`, identity `07d4f8d3…`). Its viewer graph needs 102,580 nodes. Loading both current machines into the same global table under two retained mounts takes 102,690 nodes; disposing the final mount still clears the table. This is a present project use, not an invented future scale target.

## Goals / Non-Goals

**Goals:** Reuse the prepared graph across ordinary ticks for both measured Curta machines and their simultaneous mounts; retain a finite reclamation threshold and disposal semantics; preserve exact numerical, error, event, snapshot and command behavior; quantify time and memory effects.

**Non-Goals:** A new evaluator, compiled JavaScript or `new Function`, lazy piecewise-sector pruning, changed constraint tolerances, a promise that every supported document fits the chosen ceiling, or making the declared two-second turn interactive by this change alone.

## Decisions

1. Raise the shared `EXPRESSION_LIMITS.nodes` default from 50,000 to **125,000**. It is the smallest round finite ceiling with headroom above the measured 102,690-node two-mount union. The threshold remains checked before each outer `withExpressions` operation, so documents or publication history that exceed it still reclaim; scopes, generation reconstruction and final-mount disposal do not change. A simple finite constant is preferable to a dynamically growing ceiling that might retain every historical publication indefinitely or require new per-document ownership accounting.
2. Do not alter parsing, graph evaluation, node order, name resolution, calls or source-motion sampling. The same code executes with fewer cache generations. The exported test-adjustable limit remains available to force pressure, so existing low-limit parity/lifetime tests still test reclamation. A test must fail against 50,000 by requiring a measured large fixture to survive adjacent ticks without a generation change, then pass at the new default. To keep the repository independent of the framework, use a committed viewer fixture or a compact synthetic graph with the same threshold-crossing property, not a project import in the test suite.
3. Benchmark the *same pinned export* before/after on one reserved CPU, without WebGL, 48 individual ticks at `dt=1/240`. Compare all 213 bank values/digests and admissions; record generation counts, wall time, RSS and heap. Validate the current trial's load and adjacent ticks, the two-mount union, low-limit reclamation tests, snapshot/replay corpus, typecheck and a rebuilt primary bundle after integration. A browser pointer/full revolution already passed on the pre-change bundle; the new bundle still needs proportionate current-export browser validation.

## Risks / Trade-offs

- **More retained memory while a large model is mounted** → Report RSS/heap before/after. The ceiling remains finite at 125,000 nodes (2.5× the old trigger); final-mount disposal still releases the table, and publication history beyond the ceiling still reclaims. The threshold is not a hard maximum within one protected operation, as ADR-043 already specifies.
- **Two mounted documents can collectively exceed the ceiling** → The measured current pair fits at 102,690 nodes. The existing low-ceiling two-document tests still force reclamation and prove document-local bindings and numerical parity when a pair does not fit.
- **A future machine or repeated republish still reparses under pressure** → This cycle makes no universal speed claim. The old safe generation reconstruction remains the fallback; a later concrete project may justify a different policy.
- **A cache-only speedup may not make the Curta usable** → Keep the actual 480-tick and browser wall times visible; pursue any subsequent evaluator change only from a new measured hotspot, without weakening mechanical contracts.

## Migration Plan

Build and smoke the viewer bundle, then integrate the viewer-only cycle. Exports embedding the old bundle remain unchanged. The change can be rolled back by restoring the former finite threshold; no document, snapshot or API migration is needed.

## Open Questions

None for this bounded cycle. Additional evaluator work depends on post-change profiling, not on speculative symmetry with framework changes.
