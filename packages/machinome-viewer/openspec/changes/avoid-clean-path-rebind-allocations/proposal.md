## Why

The higher-counter OperatingCurta export takes 20.94 CPU seconds for the first 48 of 480 normal crank ticks without WebGL. A same-export probe found 542,535 of 618,561 `PathValue.bind` calls in the first 12 ticks resolve no expression nodes, yet each allocates a dirty set and one snapshot per input. This measured waste contributes to an unusably slow ordinary crank.

## What Changes

- Avoid allocating a dirty set and replacement input snapshots when a path rebind sees no changed input.
- Preserve exact input-read order, presence and IEEE comparisons, error timing, path samples, admissions, committed coordinates and replay.
- Require a material same-export CPU improvement before integration.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `incremental-path-piece-evaluation`: add an allocation-free clean rebind requirement without changing its numerical behavior.

## Impact

Internal widget expression evaluator only. No document, viewer API, project law, timestep, CSP or dependency change.
