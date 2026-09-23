## Why

The viewer's public `Run` can complete a request and bank `NaN` when a square-root law has a non-finite value at the request's endpoint. A version-5 document with a valid authored start reproduces this on viewer main `b976a17`; the running contract requires an unintegrable step to leave its bank and records standing. A separate invalid-start diagnostic exposes the same viewer failure but cannot be produced by the framework's rest render.

## What Changes

- Refuse a running step whose already-evaluated law result is non-finite, including a valid-start/invalid-endpoint request and an accepted document with a non-finite authored start; do not bank or record a partial step.
- Preserve prior successful steps of a multi-step command. At the failing step, use the existing `law` refusal kind and atomic command-retirement path, and preserve valid numeric paths.
- Keep this separate from the running-target-endpoint and performance cycles. No document-field, public method, or viewer API-version change is proposed.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: Clarify the running-step atomicity and unintegrable-law requirements with explicit non-finite law scenarios.

## Impact

The in-thread running engine under `machinome_viewer/widget/src/run/` and its Vitest conformance tests. The same engine is used by the worker transport. No framework source, schema, bundle interface, or independent viewer branch is changed by this proposal.
