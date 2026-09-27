## Why

Curta-Type-I-3x has seventeen register dials whose existing child.turn coordinates are read by register_reading, initialized by guarded defaults and retained by self-targeting arithmetic laws. Fresh mate freedoms name their generated child joints after the assembly mate, so adopting frames would rename or replace these established endpoints; the declaration-reference form currently fails because the mate rejects a PathRef freedom.

## What Changes

- Accept `ones_mount = ones.axle.on(ones_seat, ones.turn)`, where the explicit reference identifies an existing scalar Revolute or Prismatic joint of the directly declared moving child.
- Attach the frames using that joint without creating, renaming, replacing, marking or reordering it; preserve its class/site argument frame, Bound declarer, defaults, bindings and retained history.
- Make the new mate handle a reference and read/write alias of the same physical endpoint for relations, derived expressions, bindings, Bounds, additive constraints and explicit controls. It creates no assembly port, wiring, second bank value or publication address.
- Detect duplicate writers, duplicate reads and self reads using the existing joint's canonical endpoint, while preserving the supported retained-law self-read meaning.
- Keep fresh-freedom and rigid mates unchanged. No string-name keyword, other joint kinds, compound freedoms, loops, moving fixed ends or document/viewer changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mates`: Refer to a moving child's existing scalar joint in an attachment and preserve that joint rather than generating a freedom.
- `ports`: A reused-joint mate handle reads/binds the child slot without owning an assembly slot and preserves its sole binder rules.
- `couplings`: Reused-joint mate references identify the original endpoint in relations and derived coordinates, including canonical writer/alias checks.
- `joints`: Existing-joint mate handles name the original joint in mechanical contracts without shifting its Bound scope.
- `simulation`: Compilation, defaults, retained laws, controls and snapshots keep the original child coordinate once.

## Impact

Mate validation/descriptor handling, coordinate reference resolution, port ownership enumeration, mechanical endpoint normalization, and narrowly necessary relation/compiler endpoint checks. Evidence is project-owned `simulation/docs/mates-refactor-2026-09-27.md`, `simulation/registers.py`, `simulation/running_parts.py:58` and `simulation/running.py:39,223` at `/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x`. Project adoption and Studio API documentation are separately owned follow-through, never staged in this framework repository.

The pilot explicitly ratified the complete declared-reference example on 27 September 2026 and rejected `joint_name="turn"` before proposal. This standalone cycle starts at clean framework main `163afcc868155eba94dac16ab10345662d3ce5bc`, branch `mate-existing-child-joint`, worktree `machinome/WTs/mate-existing-child-joint`, integration target framework main. Proposal by Sol, implementation by a separate Sol, root adversarial review before supported sync/archive; this handoff contains planning only and remains uncommitted for root review.
