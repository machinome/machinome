## Why

The animation timeline declares a closed `0..1` domain, but its current
`1 / frames` step divides that domain into `frames + 1` positions while the
browser can expose only the preceding sampled position reliably. On a
twelve-hour clock this prevents the maker from scrubbing to `12:00:00`.

## What Changes

- Make the timeline's declared frame count include both endpoints of its
  `0..1` course.
- Prove that the final slider position is reachable and that a loop-aware
  clock readout reports its complete loop duration there.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: the animation timeline includes its declared end pose
  instead of stopping one sample short.

## Impact

- `solid_node_viewer/widget/src/playback.ts` and `viewer.ts` own the inclusive
  step calculation.
- Widget unit tests and browser tests cover the endpoint and its readout.
- This corrects existing timeline behavior; no document or host API changes.
