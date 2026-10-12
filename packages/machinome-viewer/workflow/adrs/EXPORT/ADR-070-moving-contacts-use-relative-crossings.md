# ADR-070: Moving contacts use relative crossings

**Status:** Accepted

**Date:** 2026-09-21

**Change:** [mixed-threshold-landing](../../../openspec/changes/archive/2026-09-21-mixed-threshold-landing/)

**Amends:** ADR-057's local self-read branch decisions.

**Preserves:** ADR-047 corpus parity, ADR-060 point-evaluation arithmetic,
ADR-069 moving-stop attribution, API 23 and document versions 1–10.

**Consumes:** machinome ADR-136, with an independent implementation here.

## Context

Curta's full exported assembly reproduces two framework executor defects:
a threshold overtaking the carry lever makes the landing search face the
wrong way, and floating-point noise in following contact falsely implies an
impossible sliding mode. A producer-only fix cannot make the browser turn.
The pilot approved both corrections and local integration after validation.

## Decision

At a mixed moving threshold, establish the local incoming/non-incoming
branch bracket with fixed crossing sources, then use its near-to-far
orientation in the unchanged ordinal landing walk. Keep the existing stride
budget and genuine refusal; do not accept an arbitrary opposite-side sample.

Match the producer's conservative constant-relative-level certificate.
Convert finite binary numbers to exact BigInt rationals, compose affine
skeleton increments into the level, and certify only exact zero slope.
Resolve shared bindings through this viewer's own expression DAG. Continuous
`abs`/`min`/`max` branches must hold over an entire interval; exact selection
crossings may split it into separately proved affine pieces. Unknown/curved
expressions or exhausted proof work use the previous executor. No magnitude
epsilon, bank-arithmetic substitution, new state or document field is added.
Stationary-threshold and clocked paths retain their original behavior.

## Alternatives and consequences

Using the part's own travel direction fails Curta's demonstrated relative
crossing. Loosening tolerances, splitting user requests, accepting failed
landings or adjusting print geometry would hide defects rather than make
the published machine execute correctly. Exact arithmetic is restricted to
the branch-decision certificate; it is not a new arithmetic mode for a run.

The producer-generated corpus remains byte-identical between repositories,
with guards for each new case, replay and subsequent motion. Older scenarios
are unchanged. The real full-tree Curta worker carry passes and its pixels
are inspected. Broader regression and obstruction/replay evidence is kept
in the archived change. This correction adds proof cost on mixed contacts,
not general contact dynamics or a claim to certify curved following motion.
Version 0.2.0 remains unreleased; nothing is published or pushed.
