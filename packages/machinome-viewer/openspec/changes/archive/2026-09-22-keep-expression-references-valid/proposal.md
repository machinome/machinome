## Why

The Curta Type I remaining-result-bank operating trial cannot open in the
viewer: its valid published document triggers an expression-store reset
while program validation still holds node references from the previous
generation. This blocks browser acceptance of the nine remaining result
restraints before the first request; the originating reproduction and
identities are recorded in `evidence.md`.

## What Changes

- Keep expression roots, binding roots and derived node references valid
  throughout their preparation and use, including when one document's
  working set crosses the current cache-reclamation threshold.
- Preserve numeric results, document-local bindings, existing malformed
  document refusals, and reclamation of obsolete expression state.
- Add deterministic reset-pressure regressions and validate the repaired
  bundle against the originating Curta export and its Python state banks.
- Clarify the existing viewer contract: cache reclamation cannot prevent a
  supported machine from opening or change how it operates.

Status: **ratified for implementation, 2026-09-22**. The pilot explicitly
instructed: “Implement the prepared viewer repair”. This approves this
proposal, design and delta, extending the Curta continuation into the
viewer repository. No fix or speedup is claimed before acceptance.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: make correct loading and operation under expression
  cache pressure an explicit requirement, preserving bounded retention
  relative to live work rather than accumulated publication history.

## Impact

Viewer-owned `expressions.ts`, `bindings.ts`, their consumers in document
validation, running/clocked evaluation and posing, and associated tests.
ADR-043/044 lifetime details need a narrowly scoped amendment after approval.
No new host option, document field, API capability, dependency, or version
bump is planned. No framework, Curta mechanism, contact tolerance, sampling
count, or conformance expected value changes are included.

The separate read-only investigation of Python runner performance remains
outside this change. This proposal neither authorizes framework work nor
promises to shorten Python arithmetic tests. Publication and integration
are not implied by approval to implement.
