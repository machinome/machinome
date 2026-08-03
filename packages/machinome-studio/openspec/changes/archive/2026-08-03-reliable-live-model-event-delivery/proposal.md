## Why

Snowman’s assembly-to-fusion publication was present in the build directory,
but the already-open Floor browser did not apply it until the maker reloaded
the page. The browser can obtain a run snapshot before its live event
subscription is registered, leaving a publication in that hand-off interval
unobserved by the model view.

## What Changes

- Make Floor’s model-publication event stream recover events published after a
  browser’s initial run snapshot and before its live subscription is active.
- Have the Floor browser establish the stream from the snapshot’s latest event
  sequence and apply replayed model-publication events through the existing
  mounted viewer handle.
- Add end-to-end coverage for an already-open browser receiving an
  assembly-to-fusion manifest publication without a page reload.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `functional-model-inspection`: a connected maker must not lose a published
  model update during the initial snapshot-to-stream hand-off.

## Impact

- `floor/app.py` event streaming and its browser-facing event cursor.
- `floor/frontend/src/main.tsx` run subscription and model update handling.
- Floor lifecycle end-to-end tests and the functional-model-inspection spec.
