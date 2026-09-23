## Why

A valid running `Sim` with a square-root law can receive a command that takes the law outside its numeric domain. The producer raises `ValueError: math domain error` and leaves its bank unchanged, but leaves the failed command active and still owning its input. At the same law-result seam, a finite-input `feed*feed` law can instead produce infinity that the producer commits. These are narrow conformance defects, not new authoring features.

## What Changes

- Turn a numeric domain failure or a non-finite result from an actually evaluated running law into the existing named `UnsupportedLaw` tick refusal, retiring commands that moved in the failing tick while leaving bank, tick, records, and pose unchanged from just before that tick.
- Preserve any prior successful ticks and admitted travel of a multi-tick command, the existing law-evaluation/error order, and valid domain endpoints.
- Keep this separate from viewer correction `refuse-nonfinite-running-law-start`; do not broaden `ValueError` handling outside the running law evaluator, change export data, or invent a tolerance.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: Clarify the existing running-tick atomicity and unintegrable-law contract for a domain failure or non-finite law result.

## Impact

`machinome/simulation/` running law evaluation and focused simulation tests. No public method, authored declaration, document version, or package boundary changes. A viewer conformance cycle in its independent repository tests the same valid-start/invalid-endpoint command; parity evidence must be established after both corrections, not assumed from the current corpus.
