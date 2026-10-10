# ADR-135: Moving Constraints Attribute Push at Contact

**Status:** Accepted
**Date:** 2026-09-20
**Amends:** ADR-113's net-over-the-stretch pushing test
**Depends on:** ADR-108, ADR-109, ADR-111, ADR-113, ADR-133
**Cites:** ADR-134
**OpenSpec change:** `periodic-lockout-first-contact`
([archived record](../../../openspec/changes/archive/2026-09-20-periodic-lockout-first-contact/))

## Context

Operating Curta at project checkpoint `c76f230` withdraws a selector at crank
120°, leaving its ones shaft at 189.6°. A request to 840° must stop at the
first closing lockout contact, just as a request to 150° does. On framework
`8d2bd71`, the moving-read constraint search finds the obstruction, but its
group test compares the candidate's level only at the whole request's ends.
Two revolutions return the clearance to its starting value, so the sole
pushing input is omitted and the tick raises `StopInvariantError`.

This is not a missed search sample: the locator already found the contact.
Nor is it a new geometry defect. ADR-113 explicitly chose net motion over the
stretch for attribution, although it searched inside the stretch for contact.
The pilot ratified replacing that attribution rule, with actual Curta and
producer-conformance acceptance, before implementation.

## Decision

For a moving-read constraint, retain both ends of the locator's final
inside/outside bracket in a private contact value. The inside end still
determines the committed travel. Each simultaneous constraint carries its
own bracket through earliest-event selection; the existing common commit
boundary and event grouping tolerance are unchanged.

Test each nonzero candidate admission alone at those two fractions, replaying
its determining sub-program from the original stretch origin with other
admissions zero. The constraint's own-coordinate argument remains frozen at
the tick-start committed bank. An admission pushes when its level increases
across this contact bracket, not when its level increases over the entire
untruncated request. Independent time-drive admissions follow the same rule.

The remaining segment is re-evaluated with pushing admissions suppressed.
Relieving, unrelated and disengaged inputs remain free. No all-candidate
fallback is introduced: if no individual candidate pushes, the invariant
still refuses atomically. The bound is not snapped, and the final committed
state is still asserted inside. Command status, admitted travel, no-backlog
behavior, own-only bounds, static-read optimization and idle cost retain
their contracts.

The bracket is ephemeral evidence, not persisted run state or publication.
There is no new API, expression primitive, document field or version. The
producer corpus gains the actual periodic stop and snapshot replay, plus a
guard refusing missing coverage. Restoring the old attribution rule makes
that case fail. Existing corpus scenarios and their documents are unchanged.

## Alternatives considered

- Infer periodic expressions and special-case them: endpoint cancellation
  depends on the path, not its particular expression spelling.
- Probe a new epsilon after contact: risks crossing another branch and adds
  a tolerance when the locator already owns the necessary two-sided evidence.
- Compare only the net contact prefix: still measures from the old origin
  rather than across the obstruction and can hide a reversal near contact.
- Split user requests, cap them to one revolution, or retry after an invariant:
  changes command history or legal travel to conceal a framework failure.
- Stop every candidate: wrongly stops free or relieving inputs.

## Consequences

The Curta four-case reproduction and broader six-test measured lockout suite
pass with the existing model declarations. Long requests can no longer erase
an already found contact merely by ending in a later open window. The full
framework regression suite passes; the candidate test still costs two level
evaluations per moving candidate, now at the contact fractions.

The existing bounded sampling guarantee remains: a forbidden interval wholly
between samples can still be missed. Effects requiring several admissions
together while no single admission pushes remain outside the group rule and
are refused transactionally. Very small brackets inherit floating-point
resolution; no new tolerance or heuristic fallback hides it.

The independent viewer has its own executor. The producer fixture is a
handoff, not a claim of browser parity; any required viewer change is a
separate repository cycle. This decision does not adopt Curta's experimental
general restraint or complete its whole-machine roadmap.
