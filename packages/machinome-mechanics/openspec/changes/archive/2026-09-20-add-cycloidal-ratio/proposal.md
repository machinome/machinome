## Why

CycloidalDrive and OpenCycloid repeat the reverse disk/output rotation
coefficient of their fixed-ring cycloidal reducers. Their eccentric orbits,
positive reduction magnitudes and source phases have different meanings and
must remain separate from that signed coefficient.

## What Changes

- Add one pure helper, `cycloidal_ratio(lobes, pins)`, returning the signed
  disk/output angle increment per eccentric-input angle increment.
- Preserve numeric/deferred arithmetic and distinguish the fixed ring pins
  from output-transfer pins; infer no phases, placement or profile geometry.
- Use Sol agents to migrate the two projects, retain independent angle and
  geometry oracles, and validate bounded CAD/build/image evidence before merge.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: signed output/input ratio for a fixed-ring cycloidal reducer.

## Impact

Independent mechanics gears module, flat export, tests, manual and distribution
smoke; separate project-owned consumer commits and dependency declarations
where applicable. No framework mutation, new runtime dependency, torque model,
profile generator, publication or positive-reduction inverse helper.
Pilot waived per-cycle ratification; empirical evidence gates integration.
