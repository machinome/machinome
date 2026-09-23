# ADR-141: A retained coordinate follows two certified clearance surfaces

**Status:** Accepted

**Date:** 2026-09-23

**Change:** [follow-two-clearance-surfaces](../../../openspec/changes/archive/2026-09-23-follow-two-clearance-surfaces/)

**Ratified:** 23 September 2026. The proposal cited no ratification when the change was applied (recorded in `workflow/warts.md`, review of 23 September); the pilot ratified it by deciding that Machinome 0.7.0 releases with it, document version 12 and viewer API 25 included.

**Depends on:** ADR-105, ADR-108, ADR-113, ADR-121, ADR-123, ADR-124, ADR-131 and ADR-137. Preserves their ordinary law, Play and Bound meanings.

## Context

The Curta Type I radial positioning ball is free between a bell surface and an independently moving carriage collar. Its bell profile is a modulo/piecewise chart; its collar profile is piecewise. A switch law reading the ball's own coordinate pushes it outward but wrongly pulls it back when the bell retreats. `Play` has one source and fixed offsets, not these two independently authored boundaries. Both measured profiles and the two dynamic Bounds already exist in the project.

## Decision

Under a running root, explicit `Follow(lower=, upper=)` projects one banked scalar retained coordinate in relation-source order through the two authored surfaces: `max(lower, min(retained, upper))`. The relation names two distinct scalar sources and the retained target; the lower and upper dynamic Bounds on that target must structurally match the two surface graphs. The output is terminal among program edges. Inputs, held bank values and unbranched ordinary affine-law chains represented by exact `Motion.line` paths are accepted sources. Other ancestry, non-finite values, an invalid rest interval and an uncertified path refuse explicitly. This is not a general contact or dynamics solver.

Each tick uses the source line's original delta, not an endpoint chord, to obtain the producer's jump and kink partitions. Every boundary piece must be certified affine. The projection visits both one-sided piece closures and the exact value at the cut in order; it evaluates the authored graph under the frozen branch, not the increment-integrated path value. Numeric joins, including the Curta bell's one-ULP seam, are never snapped or merged by a tolerance. An inverted interval is provisional: the matching Bounds locate the first admissible contact from their original 64 samples plus certified Follow cuts and cut-side candidates, with their existing bisection and driver attribution. If a strictly positive one-sided closure has no representable positive neighbor, the tick refuses atomically rather than passing an undetectable contact. The landing is absolute, and snapshot/restore and replay preserve it.

The producer publishes `kind: "follow"`, lower and upper graph strings, and nullable producer-compiled jump plans in document version 12. Older documents, self-read switch laws, Play, and no-Follow execution retain their prior identity and behavior. A viewer must opt into version 12 and use the supplied plans; reconstructing them from expression strings would not certify the same branches.

## Alternatives and consequences

An endpoint clamp loses the bell's interior peaks. Recasting either existing Bound or Play changes their meanings. A general unilateral contact solver would exceed this measured Curta requirement. The narrow Follow relation has a higher per-tick path cost and rejects unsupported source ancestry instead of approximating it. The project probe demonstrates outward push, retreat retention, interior stop, relief and exact replay; the archived change records the synthetic one-sided and long-periodic negative controls and framework tests. Geometry itself remains a project-owned obligation.
