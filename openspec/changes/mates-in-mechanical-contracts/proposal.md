## Why

Curta-Type-I-3x (`/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x`, HEAD `fb5505d`) declares a crank with a pawl-dependent Bound, additive ancestor stops, and separately selected turn/lift controls (`simulation/running_parts.py:151`, `simulation/running.py:134`). Moving that placement onto a mate currently loses those declarations: mate freedoms reject Bound reads, the generated child joint cannot be named before mate installation, and controls reject the mate because it is not a Joint.

## What Changes

- Accept existing `Bound(expression, reads=(...))` range sides on a moving mate, resolving reads against the assembly declaring the mate.
- Accept moving mate references as Bound reads, additive `constrain(range=...)` targets, and explicit `Turn`, `Slide`, and `Button` coordinate selections, including bare mates in their declaring body and paths from ancestors.
- Resolve these references to the existing generated child joint for mechanical contracts, retaining one bank coordinate and the mate's existing wiring and author binding surface.
- Refuse rigid mates and retain existing scope, self/duplicate read, control ancestry, kind, and single-coordinate checks.
- Preserve existing declarations, caller behavior, document fields and version; no compound freedoms or viewer change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mates`: A moving mate's range may read declared coordinates in its assembly scope; its reference may participate in mechanical contracts.
- `joints`: Bound reads and additive constraints may name moving mates and resolve to their generated joints.
- `simulation`: Explicit control selections and compiled Bound references accept moving mates without duplicate bank entries or altered solver semantics.

## Impact

Narrow changes to `machinome/motion/mates.py`, coordinate reference resolution, `motion/joints.py`, `motion/constraints.py`, `simulation/control.py`, and shared compilation/control resolution as needed; focused regression fixtures and Curta-shaped caller evidence. No change to Curta's repository is part of this cycle. Framework manual examples and architecture/ADR records follow the confirmed implementation. Studio's public API skill is a separately owned companion change at `machinome-studio/WTs/mate-contract-api`, maintained by the root agent after implementation; no studio files belong in this framework change.

Standalone cycle: clean framework `main` base `49a8fc5cb01852a76b878b55788229ef5857b517`, branch/worktree `mates-in-mechanical-contracts` / `machinome/WTs/mates-in-mechanical-contracts`, integration target framework `main`. The pilot explicitly ratified the scope before artifact creation; planning remains uncommitted for root review.
