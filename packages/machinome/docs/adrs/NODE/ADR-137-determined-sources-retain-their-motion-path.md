# ADR-137: Determined sources retain their motion path

**Status:** Accepted

**Date:** 2026-09-22

**Amends:** ADR-122's endpoint-increment handoff and unconditional block-stop
search; ADR-123's static-only classification where the active path is known.
Preserves ADR-107 jump removal, ADR-121 landing, ADR-124 point evaluation and
ADR-136 conservative contact certificates.

**Change:** [preserve-carry-across-graph-expansion](../../../openspec/changes/archive/2026-09-22-preserve-carry-across-graph-expansion/)

## Context

Curta's unchanged crank request carries correctly with six result stations
but loses carry with seven and eleven. Later selectors cut the same request
differently. Passing only each predecessor's net increment replaces its
stroke and dwell with a ramp, re-timing the earlier gate. The ordinary frozen
twin also gives 2 instead of 3.5: this is not confined to cyclic blocks.

## Decision

Compose demanded, propagation-local motion paths over the common request
fraction. A source is commanded, held, or determined by the existing law
evaluation and retained walk. Restrict an existing path without replacing it
by a chord. Memoized queries are pure and do not advance state or records.
Keep exact affine fast paths; do not materialize paths nobody reads.

Selected blocks still partition by selectors and order active dependencies
per piece. Forced branches remove inactive dependencies; those not determined
hold their piece-start value. Retained walks expose actual pieces, including
landings, and inherited interior boundaries retain their crossing ownership.
Crossing budgets cover the complete propagated law, not a fresh allowance at
each inherited piece, including record-disabled probes.

Classify the active folded expression against actual source paths, not just
compile-time source affinity. Solve certified affine pieces and retain bounded
search for curves. This classification does not replace floating-point point
evaluation. Range location and contact probes read the same paths as commits;
when a path is unavailable, replay the prefix from the original bank. Preserve
the clearance-aware Play route and its downstream replay, independent time
admissions, tick-start own-coordinate bound arguments and refusal rollback.

## Alternatives and consequences

Omitting unrelated cuts would hide only one manifestation. Smaller ticks,
fixed microsteps, changed Curta laws or a changed oracle would conceal the
defect. A coupled solver is unnecessary. Endpoint chords remain valid only
where they describe the actual affine motion.

Piece retention costs endpoints and caches: the browser's existing carriage
control costs 6277.4 rather than 5913.2 evaluations/tick; affine Train and
Clearing controls are unchanged. Bounded search still cannot guarantee
finding every excursion of an arbitrary curved law. No tolerance or authoring
API changes. The archive records full-bank bulk/partition parity on all four
unchanged Curta diagnostics, not whole-machine geometry acceptance.
