# ADR-069: Moving stops attribute push at first contact

**Status:** Accepted

**Date:** 2026-09-20

**Change:** [periodic-first-contact](../../../openspec/changes/archive/2026-09-20-periodic-first-contact/)

**Authority:** The pilot approved the matching viewer correction and autonomous
continuation after Curta's actual exported reproduction failed.

**Amends:** [ADR-054](ADR-054-a-constraint-is-derived-from-the-published-document.md)

**Preserves:** ADR-047 corpus parity and ADR-068 independent time admissions.

**Consumes:** machinome ADR-135, integrated producer e63700e.

## Context

Curta's crank meets a closing locking surface part-way through a request, but
two turns later its endpoint is free again. The viewer located that first
contact correctly and then discarded its bracket; group attribution compared
each candidate at the complete request's endpoints. No input appeared to push,
so the request was refused as a broken invariant instead of stopping there.

## Decision

Keep the search's inside and outside fractions as an ephemeral contact record
through event selection. Commit only at inside, with the same no-snap assertion.
For each candidate, replay its admission alone from the original stretch origin
at both fractions; a positive level change identifies a pushing admission.
The own-coordinate argument stays frozen at tick start. Time-drive admissions
participate by the same rule. Nothing new is persistent or published.

The producer's exact corpus is copied and replayed, with a coverage guard for
the actual periodic stop, blocked outcome, long request and snapshot replay.
An old-algorithm substitution proves that this fixture detects the defect.

Endpoint attribution is rejected by Curta's reproduction. Stopping every
candidate would incorrectly stop relieving and disengaged inputs. Splitting
requests or limiting them to a turn would conceal the consumer disagreement.

## Consequences

Curta's long and short requests meet the same first surface in Python and the
browser. Numeric and static-read stop paths, simultaneous events, record shape,
atomicity and public API remain unchanged. The viewer stays API 23, document
versions 1–10, version 0.2.0 unreleased.

Finite sampling can still miss a contact between samples. A compound push
where no candidate alone raises the level remains a transactional refusal;
this correction neither adds contact dynamics nor broadens that policy.
