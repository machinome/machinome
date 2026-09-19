# ADR-131: Play Is an Explicit Running Clearance Law

**Status:** Accepted
**Date:** 2026-09-19
**Depends on:** ADR-105, ADR-108, ADR-110, ADR-111, ADR-121
**OpenSpec change:** `unilateral-running-pickup`
([archived record](../../../openspec/changes/archive/2026-09-19-unilateral-running-pickup/))

## Context

The Vault with Combination Lock at checkpoint `78d4ceb` needs a dial to
collect each wheel at either clearance flank, retain it through the gap, and
release it immediately on reversal. ADR-121 self-read switches deliberately
remain engaged when source and follower move together and cannot state this
hysteresis without changing their established meaning.

## Decision

`Play(low, high)` is an immutable running-only relation law for
`(source & retained).drives(retained, law=Play(...))`. For monotonic source
endpoint `x'`, it commits `max(x' - high, min(retained, x' - low))` in the
ordinary run bank.

Play edges form linear chains rooted at a run-owned driver. Cycles, fan-out,
ambiguous writers, invalid initial intervals, and potentially reversing
ordinary sources are refused at construction. Stops replay the complete path
from the originating driver, including permitted downstream observers.

The published edge has `kind: "play"`, ordered source and retained `needs`,
the retained `gives`, and finite `low` and `high`. A document carrying one is
version 9; documents without one are unchanged.

## Consequences

The Vault states measured pickup without project state or a second controller.
Existing callable laws and version 1–8 documents retain their prior semantics
and bytes. Older viewers refuse version 9 rather than guessing.

## Rejected alternatives

- Changing ADR-121's comparison-gate semantics would silently change every
  existing self-read document and still leave clearance implicit.
- A Vault-owned accumulator or clocked `State` would duplicate the wheel bank
  and make the project, rather than its mechanical relation, own pickup.
- Inferring play from an arbitrary expression or a flag on one would hide the
  two flanks and admit source paths whose reversals the runtime cannot prove.
