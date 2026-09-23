## Why

The Curta Type I operating positioning ball exposes an OCCT false-empty exact common: at the outer radial position and a 0.2 mm axial perturbation, the source sphere and fitted frame have a native section curve and a point strictly inside both solids, but their valid Boolean common has no solids. The exact comparison path currently interprets that empty result as clearance, so an exact test can pass a physically interfering pair.

## What Changes

- Refuse an exact common reported empty when an independent native-surface and strict-interior witness proves that the operands share material. Do not invent a recovered volume or replace the exact verdict with a faceted one.
- Make the existing exact-shape intersection helper usable by project diagnostics with the same refusal, while keeping ordinary disjoint and zero-volume boundary-contact behavior.
- Record a red-first synthetic Boolean-failure regression and the unchanged Curta source-shape reproduction, including both axial directions, as evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `test-framework`: exact intersection assertions must not silently accept a Boolean empty result contradicted by a strict native shared-interior witness.

## Impact

The exact OCCT comparison seam in `machinome/exact.py`, the assertions that call it, focused exact-geometry tests, and the test-framework specification. There is no viewer change, mesh-kernel substitution, volume epsilon, new project geometry, or claim that all possible OCCT Boolean failures are detected.
