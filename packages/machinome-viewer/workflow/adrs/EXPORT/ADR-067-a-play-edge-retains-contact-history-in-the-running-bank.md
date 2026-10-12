# ADR-067: A play edge retains contact history in the running bank

**Status:** Accepted

**Date:** 2026-09-19

**Change:** [execute-running-play](../../../openspec/changes/archive/2026-09-19-execute-running-play/)

**Extends:**
- [ADR-045: The run executes in a worker and the main thread only poses](ADR-045-the-run-executes-in-a-worker.md)
- [ADR-047: The corpus is what makes the two runtimes one algorithm](ADR-047-the-corpus-makes-the-two-runtimes-one-algorithm.md)

**Builds on:**
- [ADR-054: A constraint is derived from the published document, never published](ADR-054-a-constraint-is-derived-from-the-published-document.md)

**Consumes:**
- machinome ADR-131: Play is an explicit running clearance law

## Context

The combination-lock Vault needs a wheel to remain still through clearance,
be collected at either contact flank, and release again on reversal. Encoding
that behavior as a self-read branch preserves the selected relative level and
therefore pulls the wheel through reversal. It conforms to ADR-121; changing
that established interpretation would silently change version-6 documents.

Machinome consequently publishes an opt-in version-9 `play` edge. Its two
needs are the source and retained follower, its give is that follower, and its
finite `low < high` offsets state the two contacts. This viewer must execute
that declaration without inventing a second browser-side controller.

## Decision

The loader accepts the exact producer shape and refuses invalid initial gaps,
cycles, fan-out, a non-driver root, or any second writer of the follower. A
play path is one driver-rooted linear chain. Its retained values live only in
the ordinary running bank; snapshots, restore, reset, worker execution and
in-thread fallback therefore use the existing mechanisms unchanged.

Each pass projects the source endpoint by
`max(source - high, min(retained, source - low))`. Absolute landings are
passed between consecutive play edges so large source offsets cannot erase a
contact value through floating-point cancellation.

A bound on a play follower or its downstream observer is located against the
complete path from the original driver. Affine observers are inverted back
through their held value and then through the contact offsets. Nonlinear
observers replay the complete prefix under the published subdivision and
bisection limits, looking for outward departure; leaving an exact-bound
plateau toward the inside is free. The truncated commit replays the same path.

Document versions become 1 through 9 and viewer API becomes 22. Versions 1
through 8 retain their existing semantics. This is a dedicated unilateral
contact primitive, not a general contact or physics engine.

## Consequences

The Vault can use its dial directly as the play-chain driver and remain
browser-operable after its project migrates to the new declaration. Old
self-read documents are unchanged. Unsupported source graphs are refused at
load rather than approximated, and producer/consumer parity remains pinned by
the framework-owned running corpus copied byte for byte.
