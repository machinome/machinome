## Why

The Curta-Type-I-3x `OperatingCurta` now evaluates a larger result-bank restraint graph. In one real station-3 withdrawal stop, 145,224 motion-path samples consume 4.21 of 16.29 profiled CPU seconds while `_PathValue.at` repeatedly hashes immutable expression nodes and builds a dictionary of moving values. The machine's ordinary operations remain too slow for interactive use, so this measured interpreter cost merits a bounded equivalent optimization.

## What Changes

- Compile the moving cone's immutable child references to local positions after a successful first path binding.
- Refresh all standing numeric values at each new piece, and use fresh moving-value storage at each later sample.
- Preserve the existing node and operand order, numeric operators, eager errors, signed-zero/NaN behavior, graph lifecycle, path visit accounting, source timing, and all constraint-search settings; prove exact Curta result-bank parity.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `motion-expression-sharing`: Repeated path samples reuse structure while retaining each piece's current values and exact numerical/error behavior.

## Impact

Private Python `_PathValue` evaluation and its tests/spec only. No public API, viewer document, mechanical law, CAD geometry, dt, constraint sample count, or tolerance change. Originating project: Curta-Type-I-3x `OperatingCurta`, committed runtime graph `7586002` with the higher-result-bank restraint.
