## Why

After ADR-074's incremental bind, `ExpressionPath.bind` still clones the entire 213-coordinate OperatingCurta bank for every path piece solely to restore a path after an expression-generation reset. The post-cache CPU profile places 3,750 of 28,997 self samples (12.9%) in that bind closure, which includes the full-bank copy. The two-second declared crank remains far slower than real time.

## What Changes

- Retain only the unresolved bank inputs a followed expression actually reads for generation-reset reconstruction, including each input's presence and exact value.
- Prove the snapshot survives a generation reset and does not inspect unrelated bank keys.
- Recheck the same pinned export's bank digest and bounded crank cost; do not change dt, samples, admissions, or arithmetic.

## Capabilities

### New Capabilities

- `minimal-path-input-retention`: A path retains only its relevant starting inputs, while reconstructing the same quantity after expression-generation reset.

### Modified Capabilities

None.

## Impact

Viewer expression-path internals and tests only. No document, host API, dependency or producer change.
