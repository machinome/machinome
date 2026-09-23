## Why

The Curta Type I's installed reverser trial exposed a false physical stop on a zero-duration absolute withdrawal: `move(to=3.9075)` reported `blocked` although that target equals the inclusive upper bound. The originating public Python/viewer report is `_build_checks/reverser-asymmetric-browser-da9808a-04.json` at project commit `7f56368` (SHA-256 `d0003c7930578f920e9106b86215cc4cc2a417aabb1bdb29736b0436dda2dd04`): eight earlier request statuses agree and only the ninth fails its expected completion. A tiny public Driver → Prismatic model reproduces the fault with both literal and read-dependent bounds: the request's `target - current` rounds to `8.85`, then `current + 8.85` lands one binary64 step above the stated target. The running contract already promises exact absolute landings and completion at an inclusive bound; relabeling the status or adding a tolerance would leave the bank or motion wrong.

## What Changes

- Preserve a `move(to=...)` request's converted native absolute endpoint separately from its travel, and use that endpoint at its full terminal admission before range-stop detection and commit.
- Carry that exact endpoint through its determined motion path where necessary so a directly driven bound sees the requested endpoint, not a reconstructed one-step overshoot; leave `move(by=...)`, rates, intermediate samples, genuine stops, and no-command ticks unchanged.
- Preserve the endpoint through active-command snapshot/restore and replay. Prove static and dynamic bounds, zero- and positive-duration moves, both rounding directions, and a true beyond-bound request.
- Coordinate the same internal runtime behavior in the separately owned viewer; do not change the exported program/document vocabulary, bound tolerance, solver sampling, or project geometry.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: Clarify the existing command/physical-stop rule for representationally exact `move(to=...)` endpoints and snapshot replay, including a target exactly on an inclusive bound.

## Impact

The framework change is scoped to command endpoint representation and running endpoint propagation (`machinome/simulation/driver.py`, `run.py`, and, only as required, the private program/trajectory path). It adds focused public-model and originating Curta oracle regressions. The viewer may need a paired runtime-only change, owned in `machinome-viewer`; no document-version bump, CAD edit, viewer source in this repository, push or release is part of this cycle.
