## Purpose

Avoid redundant certified Follow prefix propagation when paired dynamic Bounds inspect the same fraction of one running stretch, while keeping every observable search and machine result exact.

## ADDED Requirements

### Requirement: Identical certified Follow prefix work may be reused within one stretch

For two running Bounds in the same stretch whose certified Follow prefix comprises the same compiled edges in the same order, the viewer SHALL reuse a successful prefix propagation at an identical finite nonzero search fraction. It SHALL independently evaluate each Bound graph at every prescribed sample and SHALL preserve sample order, first error, one-sided Follow contact, admission, stop, full bank, snapshot, restore and replay exactly. The reuse SHALL not cross a stretch, tick, reset or run.

#### Scenario: Two Bound sides share a prefix
- **WHEN** both Follow Bounds sample the same fraction of one stretch
- **THEN** the shared prefix is propagated once, each Bound is evaluated at its own sample, and the complete result matches independent replay

#### Scenario: Prefix differs or propagation fails
- **WHEN** the compiled edge sequence differs or propagation throws before a successful result
- **THEN** no result from the other sequence or failed sample is reused, and the same first error is reported without committing a partial tick

#### Scenario: Retry starts fresh
- **WHEN** a stopped or refused request is retried or a snapshot is restored
- **THEN** its new stretch computes with fresh inputs and reproduces the uncached result
