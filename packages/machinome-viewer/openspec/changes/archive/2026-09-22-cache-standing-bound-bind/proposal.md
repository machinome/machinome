## Why

The published OperatingCurta runs correctly in the browser but a declared two-second crank turn still takes minutes at the default 1/240-second tick. A pinned 213-coordinate export repeats the same large constraint-bound graph across adjacent ticks: in the first 48 ticks its 63,252-node bound was first-bound 48 times, 47 with identical finite standing inputs and moving-name shape. Re-evaluating those standing nodes prevents the physical control from responding at its declared tempo.

## What Changes

- Reuse a successful constraint-bound path's standing node values across searches in one run only when its graph, moving-name classification, expression generation, and referenced standing inputs match exactly.
- Preserve first-sample evaluation of every moving node, all later search samples, search order and limits, float operations, error behavior, committed bank, snapshot/restore and replay.
- Keep the cache finite and owned by the run; do not add a public API, document field, timestep option or dependency.
- Reject the optimization if the paired JavaScript benchmark does not show a material benefit with exact Curta parity.
- Record the source-only correction in the reader-facing Unreleased changelog, explicitly keeping API 24 and document versions 1–11 unchanged; leave the 0.7.0 release entry intact.

## Capabilities

### New Capabilities

- `standing-bound-bind-cache`: Exact reuse of successful standing bound values across adjacent constraint searches, with safe fallback and bounded lifetime.

### Modified Capabilities

- `user-documentation`: Keep the post-release source correction separate from the released manual's version claims in the changelog.

## Impact

Viewer-owned TypeScript expression-path and running-search internals, focused tests, a changelog note, and OperatingCurta performance/parity evidence. The originating project and framework are unchanged. The bundle and public API/document versions remain unchanged.
