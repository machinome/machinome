## Context

The viewer uses `frames` as the number of scrub samples, but currently sets a
range input over `0..1` to `step = 1 / frames`. That describes `frames + 1`
positions. In browser range stepping the declared maximum is therefore not the
last member of the frame sequence, so a 360-frame, twelve-hour clock cannot be
scrubbed reliably to its `12:00:00` endpoint.

## Goals / Non-Goals

**Goals:**

- Make both `0` and `1` reachable among exactly `frames` scrub positions.
- Keep playback wrapping and externally driven fractional time unchanged.
- Centralize the edge-case arithmetic in a tested pure helper.

**Non-Goals:**

- Adding a distinct thirteenth-hour pose to a looping animation.
- Changing the document schema, frame count, playback rate, or capture CLI.

## Decisions

### D1. Frames count positions, including both ends

Use `1 / (frames - 1)` when `frames > 1`, and `1` for the degenerate
single-frame case. This gives a 360-frame document 360 scrub positions from
zero through one. Using `step="any"` was rejected because it would discard the
document's declared sampling precision.

### D2. Keep playback's half-open wrapping behavior

Automatic playback continues to wrap normalized time into `[0, 1)`. The exact
`1` value exists for deliberate scrubbing and host control, where it exposes
the completed loop and readout; it need not become an extra playback frame.

## Risks / Trade-offs

- [Start and endpoint render the same pose for a periodic machine] → Keep both:
  their mechanical pose is intentionally equal, but their elapsed-time readout
  communicates different points in the course.
- [Floating-point step strings vary] → Derive one deterministic number in a
  unit-tested helper and retain the explicit range maximum of `1`.

## Migration Plan

This is an in-place behavior correction. Rebuilding the widget restores the
endpoint; reverting the helper call restores the previous sampling.

## Open Questions

None.
