## Why

The maintainer requested the viewer receive the same user-documentation treatment
as mechanics, including discovery from the framework manual. The independent
viewer now has its own complete manual; framework readers need direct links to
its operating, embedding and API guidance.

## What Changes

- Link to the viewer manual from framework navigation and viewer/embedding pages.
- Point host authors to the full viewer reference while preserving existing
  framework-facing explanations and the package/process/licensing boundary.
- Correct the nearby distinction between immediate clocked moves and drawn
  instruction triggers, based on the viewer's implemented handle.
- Keep the viewer's unreleased status explicit; add no runtime behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: Framework users can reach the viewer's own manual.

## Impact

Framework documentation and a focused link regression test only. Viewer source,
manual and OpenSpec records belong to the viewer repository's `user-documentation`
change. The pilot pre-ratified implementation; review approval is required before
this new cycle's spec sync/archive. No integration or push is authorized.
