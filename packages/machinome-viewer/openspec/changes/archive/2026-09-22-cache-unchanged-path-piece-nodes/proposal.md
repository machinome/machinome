## Why

The OperatingCurta export currently needs about 30 seconds to execute only the first 48 of 480 crank ticks without WebGL. A CPU profile of the actual 213-coordinate document places repeated `PathValue.bind` and `valueAt` among the largest costs: every new path piece re-evaluates its entire expression graph even when most bank inputs are unchanged. That makes the physical crank unusably slow in the browser.

## What Changes

- Reuse a path quantity's node values between adjacent pieces when its relevant inputs have not changed, while re-evaluating the changed node and its dependents in their original order.
- Keep point evaluation, step size, searches, admissions, bank values and replay unchanged.
- Prove the avoided work with the existing expression-resolution counter and remeasure the same OperatingCurta export.

## Capabilities

### New Capabilities

- `incremental-path-piece-evaluation`: Rebinding a path to a subsequent piece evaluates only nodes affected by changed inputs, with exact arithmetic and state preservation.

### Modified Capabilities

None.

## Impact

Viewer-only internals in `machinome_viewer/widget/src/expressions.ts`, its tests and performance evidence. No new document field, API, dependency or producer change.
