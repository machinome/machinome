## Context

The viewer uses `frames` as the number of scrub samples, but currently sets a
range input over `0..1` to `step = 1 / frames`. That describes `frames + 1`
positions. In browser range stepping the declared maximum is therefore not the
last member of the frame sequence, so a 360-frame, twelve-hour clock cannot be
scrubbed reliably to its `12:00:00` endpoint.

## Goals / Non-Goals

**Goals:**

- Make both `0` and `1` reachable among exactly `frames` scrub positions.
- Let a maker enter an exact design-unit driver value in the numeric readout
  beside every bounded slider.
- Keep playback wrapping and externally driven fractional time unchanged.
- Centralize the edge-case arithmetic in a tested pure helper.

**Non-Goals:**

- Adding a distinct thirteenth-hour pose to a looping animation.
- Changing the document schema, frame count, playback rate, or capture CLI.

## Decisions

### D1. Frames count positions, including both ends

Represent the HTML range in integer frame indices, `0..frames - 1` with step
one, and convert to normalized time with `index / (frames - 1)`. This gives a
360-frame document 360 scrub positions from zero through one without asking a
browser to represent the repeating decimal `1 / 359` as an exact range step.
The initially proposed fractional HTML step was rejected by browser evidence:
Chrome snapped an assigned maximum of `1` back to `358 / 359`. Using
`step="any"` was rejected because it would discard the document's declared
sampling precision.

### D2. Keep playback's half-open wrapping behavior

Automatic playback continues to wrap normalized time into `[0, 1)`. The exact
`1` value exists for deliberate scrubbing and host control, where it exposes
the completed loop and readout; it need not become an extra playback frame.

### D3. The driver readout is the numeric input

Render the number beside a bounded range control as an `input[type=number]`
while retaining the unit as adjacent text. On input or change, route the typed
design-unit value through the same `toNative` conversion and `setDriver` door
as the slider. Do not copy the slider's min/max onto the field: ranges bound
slider travel, not machine state. A separate edit dialog was rejected because
the value is already visible in the correct row and calibration benefits from
one-click access.

## Risks / Trade-offs

- [Start and endpoint render the same pose for a periodic machine] → Keep both:
  their mechanical pose is intentionally equal, but their elapsed-time readout
  communicates different points in the course.
- [The DOM slider no longer exposes normalized values directly] → Keep the
  scale private, convert through unit-tested helpers at every boundary, and
  leave the public `setTime` contract normalized to `0..1`.
- [Live ramp updates could fight a maker typing] → Treat focus in the numeric
  field as maker authority and do not rewrite its text until editing commits
  or focus leaves; direct entry uses the same driver update path as dragging.

## Migration Plan

This is an in-place behavior correction. Rebuilding the widget restores the
endpoint; reverting the helper call restores the previous sampling.

## Open Questions

None.
