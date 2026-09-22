# ADR-072: Source timing is declared as API 24 and document v11

**Status:** Accepted

**Date:** 2026-09-22

**Extends:** ADR-035 capability declarations and ADR-047 producer parity.

**Change:** [preserve-running-source-timing](../../../openspec/changes/archive/2026-09-22-preserve-running-source-timing/)

## Context and decision

The old viewer understands Curta's payload shape but computes the wrong
carry. Declare API 24 and document support 1–11 from the existing single
metadata source. Accept v11 as running, validating optional Play/time-drive
features by content, including mandatory admission mappings for clock reads.
An independent corrected producer emits v11 for every new running export
and includes the source-timing semantic generation in its program identity.

Legacy running files remain loadable with corrected physics, not a separate
endpoint-era executor. Re-export protects users of older viewers: the actual
API-23 bundle rejects v11 before operating in Chromium. Old snapshots refuse
against the newly exported identity, and corrected snapshots replay normally.
Package release numbering, posed/looping and clocked semantics are unchanged.

## Alternatives and consequences

API alone cannot protect portable model exports. A changed payload is not
needed, and a selective static timing detector is not established. Conservative
v11 publication changes even affine models' version and identity. Existing
corpus JSON remains unchanged; new source-hashed fixtures pin the correction.
Both browser transports and the distribution smoke test verify the capability
claim. This decision does not publish, integrate or adopt either package.
