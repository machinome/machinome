## Context

The viewer builds a tick-local `demanded` set from edge `needs` excluding the same edge's `gives`. That exclusion is right for a self-read law's *dependency* but loses a separate consumer: a compiled constraint may read that law's output. On frozen OperatingCurta `7586002`, the crank high bound reads `main_drive.anti_reversal.reverse_rotation_prevention_pawl.turn`; the pawl law both needs and gives this coordinate, so it is not demanded. The propagation path may take the endpoint-only legacy branch, leaving no `Motion` for `searchFromSources` and forcing a program prefix replay at each bound sample. This is a viewer-specific hypothesis pending actual sampled parity and timing.

## Goals / Non-Goals

**Goals:** Preserve exact running outcomes while making constructible constraint-read motions available to stop search. Measure the actual Curta active-stop path and full bank against the frozen baseline. Keep demand metadata scoped to one tick.

**Non-Goals:** Alter the source-timed laws, admissions, sample schedule, convergence tolerances, document format, or the existing fallback when a path cannot be built. No broad graph evaluation rewrite.

## Decisions

1. Form the tick-local demand from its current edge-derived set plus reads of compiled constraints, rather than from all bank coordinates. This follows the actual consumer and avoids making every law construct paths unnecessarily. The bounded coordinate itself is not added merely because it is bounded; only a coordinate read by the bound and constructible through propagation is a new demand.
2. Leave `propagate`, `Motion`, and stop search semantics unchanged. If an existing path is now available, the current `along` path must reproduce the old replay's ordered sampled levels and IEEE-754 results. A synthetic self-read test gates the missing demand red-first; same-export Curta bound-sample traces and the 213-bank digest gate integration.
3. Keep unavailable or untraced paths on the existing replay route. Demand is a request to retain an exact path, not permission to approximate one.

## Risks / Trade-offs

- A newly demanded path may cause different rounding or error order than prefix replay. Capture every actual active-stop bound sample and outcome at the same tick; reject this approach if any bit or error behavior differs.
- More paths cost construction and memory. Count newly demanded keys on the frozen export and compare no-WebGL tick CPU; do not expand demand to all coordinates.
- One tick's demand can affect upstream law choice. Run representative corpus, source-timing and replay tests, including an unsupported/untraced case, before integration.

## Migration Plan

No document migration. Rebuilding the viewer bundle activates the internal optimization; reverting this isolated cycle restores the previous demand construction.

## Open Questions

Does the viewer's sampled bound arithmetic exactly match when the pawl path is retained? Actual baseline/candidate traces decide this before integration.
