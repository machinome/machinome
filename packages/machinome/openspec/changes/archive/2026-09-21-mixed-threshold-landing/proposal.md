## Why

Operating Curta's ordinary input-9 crank turn fails with `LandingInvariantError`
when its measured tens-stack restraint observes the actual carry lever. A
CAD-free reduction retaining the source shaft, dial and lever laws passes
without the observer and fails with it: the moving engagement threshold
overtakes the lever, while the landing search follows the lever's own travel
direction instead of the relative crossing.

## What Changes

- Correct running self-read landings for mixed moving thresholds, preserving
  the existing promise of the nearest representable far-side value.
- Prevent round-off in a following contact from being mistaken for a branch
  departure or impossible sliding mode; prove constant relative motion without
  an epsilon, additional clearance or relaxed refusal.
- Pin the failure red through the public running API, including a downstream
  constraint observer, opposite crossing directions, replay and atomic refusal.
- Extend the shared conformance evidence and validate the actual Curta carry
  preparation, lockout requests and neighboring arithmetic/history cases.
- Preserve public declarations, document versions, the tolerance budget and
  behavior of clocked and non-self-reading machines.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: explicitly require mixed-source engagement crossings to remain
  correct when the threshold overtakes a moving part, including observation by
  a mechanical restraint. This clarifies an existing far-side contract rather
  than introducing another motion mode.

## Impact

Framework running integration and its public-API/conformance tests; accepted
architecture records if implementation confirms a changed landing rule.
The originating project is `Calculators/Curta-Type-I-3x`, branch
`direct-operation`, diagnostic `HigherOperatingTrial`, reproduction
`simulation/test_carry_constraint_repro.py`, evidence
`simulation/docs/higher-result-lockout-2026-09-21.md`.

The browser executor is independently owned by `machinome-viewer`; a reproduced
viewer mismatch requires its own repository-local cycle. No viewer source is
added here. Neither Curta print geometry nor its prescribed carry laws may be
changed to conceal the engine error. No push or release is included.
