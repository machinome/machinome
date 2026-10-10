## Why

The engine's one distance measurement, `_distance` in `machinome/engine/brep.py`,
builds `BRepExtrema_DistShapeShape(first, second)` and then calls
`SetMultiThread(True)`; but the two-shape constructor has already performed
the extrema, so the flag is set on a finished computation and every distance
the engine measures runs on one core. Found on 9 October 2026 by the
distance-tier measurement (`workflow/warts.md`, "The overlap question is
asked of a Boolean that is only needed at zero distance", Measured): on the
combination safe lock's 730 placed pairs the same exact distance, loaded,
flagged and then performed, drops from 186 s to 33 s with the identical
value on every pair. Today the helper is called only on a face against a
vertex inside the witness, where the cost is small; the defect is in the
instrument, and the proposed distance tier would lean on it.

## What Changes

- **The distance is asked threaded.** `_distance` builds an empty
  `BRepExtrema_DistShapeShape`, loads both shapes, sets
  `SetMultiThread(True)` and the minimum-only flag, then performs; its value
  is the kernel's minimal distance as before.
- **A seam test pins the order.** A recorder standing in for the kernel
  class sees the flag set before the computation performs; red today.
- No other behaviour changes: the witness's face margins are the same
  numbers.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `brep-engine`: "Measurements are functions of the B-rep geometry" states
  that a distance the engine measures is asked of the kernel with parallel
  execution enabled before the extrema performs.

## Impact

- `machinome/engine/brep.py`: `_distance`.
- `tests/test_brep_geometry.py`: one seam test.
- `openspec/specs/brep-engine/spec.md`: the modified requirement.
- `docs/project/changelog.rst`: one bullet under Unreleased.
- No ADR: the kernel's threading flag decides no architecture.
