## Why

Dragon R1's rack steering and Thor's belt drives independently convert shaft
degrees to linear pitch-circle travel. A shared formula removes repeated unit
conversion without taking ownership of their mounting signs or reference poses.

## What Changes

- Add `rolling_travel(angle, radius)` to a rolling family and the flat API.
- Document degree, pitch-radius, zero and direction conventions.
- Validate numeric and symbolic behavior, then migrate real project consumers
  through Sol agents before completing this cycle.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: rotary-to-linear rolling travel.

## Impact

Additive Python API, tests and manual; no new dependency. Consumer commits stay
in their own repositories. The pilot authorized the entire helper expansion,
individual OpenSpec cycles, Sol-led project migrations and local integration on
2026-09-20, explicitly waiving per-cycle ratification. Empirical validation is
the integration gate; blocked helpers are recorded and skipped, never archived
as complete. Publication and pushes are outside this work.
