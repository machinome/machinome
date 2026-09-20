## Why

Prusa3-vanilla and Kossel independently divide belt travel by pitch/contact
radius and convert radians to degrees for their pulleys and idlers. InMoov's
drum closure and the Open Robot Actuator tensioner repeat the same inverse
conversion. A named helper removes that arithmetic without owning their phase,
mounting sign or belt geometry.

## What Changes

- Add `rolling_angle(travel, radius)` beside `rolling_travel` and re-export it.
- Document unwrapped degrees, contact radius, caller-owned signs/phase and zero
  radius behavior; test independent values and numeric/symbolic parity red-first.
- Sol agents migrate natural distance-to-angle consumers and record empirical
  results in their own repositories before local integration.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: rotation from signed rolling travel.

## Impact

Additive pure-arithmetic API, tests and manual; no new dependency or geometry
generation. Existing pulley phase, fitted pitch radius, plain-idler contact
radius and inverse motion relations stay project-owned. The pilot's autonomous
per-helper-cycle authority applies; no push or publication. Unresolved helper
blockers are recorded and skipped without archiving incomplete work.
