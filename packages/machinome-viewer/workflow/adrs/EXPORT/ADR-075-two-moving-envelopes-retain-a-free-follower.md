# ADR-075: Two moving envelopes retain a free follower

**Status:** Accepted

**Date:** 2026-09-23

**Change:** `follow-two-moving-envelopes`

**Extends:** [ADR-067: A play edge retains contact history in the running bank](ADR-067-a-play-edge-retains-contact-history-in-the-running-bank.md)

**Builds on:** [ADR-054: A constraint is derived from the published document](ADR-054-a-constraint-is-derived-from-the-published-document.md), [ADR-061: A kink is a cut in the viewer too](ADR-061-a-kink-is-a-cut-in-the-viewer-too.md)

## Context

The OperatingCurta's positioning ball is free between the bell and carriage collar. The project's old self-read switch law pulled the ball backward when the bell retreated, and a raised-carriage crank stopped at zero. Play retains a follower but has one source and two fixed clearances; it cannot express these two independently moving measured surfaces. The framework producer has now published a narrow version-12 Follow declaration for the actual project trial.

## Decision

The viewer accepts the producer-authored `follow` edge only in running document version 12. It requires ordered lower and upper sources, one retained bank target, two graph expressions and their authored jump plans, matching dynamic lower and upper Bounds, a feasible finite rest interval, unique writing, and a terminal target. Each source must be rooted in an input or held bank through an unbranched affine determiner chain. Older versions and ordinary self-read laws retain their prior meanings.

During a request, the viewer partitions both certified source paths using their original increments, not endpoint chords, and evaluates the frozen authored boundary graph at actual source values. It visits exact and left-sided values at every cut. The follower is projected in producer order, `max(lower, min(retained, upper))`, with first-operand tie selection to preserve Python's signed-zero bits. Its absolute landing is retained across prefix replay and committed to the bank.

Separate dynamic Bounds still own admission and attribution. The Follow-associated search preserves the old uniform probes and adds certified boundary cut-side candidates, so a narrow between-sample inversion is not silently passed. A positive analytic closure that no representable probe can witness is refused atomically as unsupported precision. Curved, ambiguous, mismatched or unsupported paths are refused rather than approximated; the first Follow target cannot feed another compiled edge.

The viewer's source capability is API 25 and document versions 1–12. That is not a package release.

## Consequences

The producer's frozen v12 command corpus and the actual read-only Curta Follow trial matched the viewer's complete 214-coordinate bank through push, blocked crank, restore/replay, relief and return. A mesh-enabled trial export also mounted in Chromium and matched all eight Python bank stages, with no page errors and an inspected assembled screenshot. The project's production adoption is separate: its ball/ring fit is still under mechanical investigation. Neither this decision nor a green trial claims that production Curta is finished or that its declared two-second crank is interactive in wall time.
