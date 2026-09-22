## Why

The Curta `OperatingCurta` still takes tens of CPU seconds for the first 48 default-cadence crank ticks after the Bound standing-cache fix. On frozen project commit `7586002`, 93.9% of path-value binds in a measured tick repeat the immediately previous finite inputs on the *same path object*; a read-only one-entry prototype reduced first-48 tick CPU from 29.088 to 23.685 seconds (18.6%) with identical 213-coordinate bank and all 6,240 ordered Bound samples.

## What Changes

- Reuse a successful numeric first-point bind when the same private path object is rebound with bit-identical finite values for every graph-referenced input.
- Preserve the existing complete eager bind on changed, missing, custom, nonfinite, or otherwise uncertain inputs, including its first error; a failed bind never seeds reuse.
- Keep reuse on the path object for its existing lifetime only. Do not cache across graphs, runs or restored snapshots; do not alter search samples, operators, laws, documents, or public declarations.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: permit the already-required path evaluator to avoid a redundant successful first-point evaluation on the same path instance without changing its observable values, error order, or sample count.

## Impact

Private `machinome/simulation/program.py` path evaluation, focused regression tests, the simulation baseline spec, and the framework architecture/ADR record if the verified implementation changes its synthesis. No project source, viewer source, dependency, document version, or public API changes. The originating project remains the Curta Type I at pinned program identity `be125f4048c8be00ce4e73d646311d4a50ac75a59aa739f93bf2f38c992fa195`.
