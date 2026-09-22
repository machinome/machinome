## Why

The production `OperatingCurta` in `projects/Calculators/Curta-Type-I-3x` remains slow at the viewer's default 1/240-second cadence. On frozen project commit `7586002` (program identity `be125f4048c8be00ce4e73d646311d4a50ac75a59aa739f93bf2f38c992fa195`), the first 48 ordinary crank ticks repeatedly bind a 126,032-node lower-bound graph although only 1,479 nodes depend on the moving bell; 124,553 nodes have identical finite standing inputs on successive ticks. A read-only process-local prototype reused those standing results and reduced CPU time from 45.13 to 34.52 seconds (23.5%) with the exact same 213-coordinate bank.

## What Changes

- Reuse a previous successful standing-node bind for the same compiled running constraint only when its graph, moving-name shape, and every graph-referenced standing input have identical finite IEEE-754 values. Recompute moving nodes at the tick's first sample in their existing order.
- Fall back to the existing complete bind when the proof of sameness is unavailable; keep the cache bounded to the run and prevent a failed bind from replacing a successful entry.
- Preserve all samples, operators, errors, crossings, stops, state, and published program/document identity. No author-facing declaration or option is added.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: The existing path-evaluation requirement may reuse numerically unchanged standing subgraphs between running constraint searches while preserving the complete-bind result and error order.

## Impact

Private running constraint evaluation in `machinome/simulation/run.py` and `_PathValue` in `machinome/simulation/program.py`; focused framework tests, Curta numerical/performance evidence, and the accepted ADR-124 no-cross-tick-cache rationale. No public API, dependencies, serialization, geometry, timestep, search resolution, or viewer protocol changes. The pilot's standing authorization for autonomous Sol performance repairs permits this proposal and implementation cycle; the particular cache design was not separately ratified before this planning record.
