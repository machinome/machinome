# ADR-010: A reframe is a join that moves a view's box and fades the rest

Status: Accepted (OpenSpec change `reframe-join`, 1 October 2026). Refines
[ADR-009](ADR-009-check-measures-a-sets-layout-before-speech.md), decision 5
(the renderer's sessions now measure the slots a reframe moves views
between), and builds on
[ADR-007](ADR-007-viewer-instances-are-leased-to-view-elements-per-frame.md)
(the lease, unchanged, keeps the view's instance and camera across the cut).

## Context

The Curta film, *Addition* (the curta-video campaign, 1 October 2026), turns
from the machine to its code by shrinking the Curta's container from the
whole frame to the right half while the code fades in on the left, "with
continuity of the camera on the curta model" (the pilot's goal,
`workflow/ongoing/curta-video.md`). The four joins compose two same-instant
picture-only captures in the stage's transition layer: nothing on the page
moves, and a cut from the full-frame set into the split set jumps the
model's container. The view element already keeps its viewer instance and
its camera across a cut inside its chapter (ADR-007). The ruling is the
orchestrator's, cycle brief of the same day.

## Decision

1. **A fifth join, `reframe`.** `Reframe(duration, ease=)` in Python,
   `{"kind": "reframe", "duration", "ease"?}` in the document, smooth by
   default. It requires a view element placed in both shots, and is refused
   before any take, naming both shots and `no view element in both`, when
   there is none (a view element belongs to its chapter, so a chapter's
   first shot never shares one with the shot before it).
2. **A reframe frame is the incoming shot's live frame.** Its set, slots,
   elements and chrome are the incoming shot's, every element's state the
   incoming timeline's, so a view's camera and model time run through the
   join and a `move` may run under it. The join carries its eased
   `progress` and, for each moving view, the box it is drawn in, `(1 −
   progress)·from + progress·to` in fractions of the frame, `from` and `to`
   the boxes of the slots holding it in the outgoing and incoming sets.
   Every other element of the incoming shot is drawn at opacity `progress`;
   the outgoing shot's other elements are not drawn. No capture, no
   composition.
3. **The boxes are measured on the stage, never computed in Node.** The
   probe of ADR-009 measures the slots; their boxes, as fractions, are
   attached to the loaded film as `reframes` (shot, moving view, both
   slots with their boxes) by `check` at the output size and by every
   browser session on its own page before its first frame; `frameAt`
   refuses a reframe frame of a film without them. A slot sized by what it
   holds has no box before it is drawn with its content, and a reframe
   through one is refused at `check`, naming the shot, the view, the set and
   the slot.
4. **The stage moves the host, not the element.** The moving view's host
   stays inside its incoming slot's element, so the set's stacking order
   holds, positioned over the frame's box in page pixels rounded to the
   layout's 1/64 pixel; its rectangle is the element's reported `box`, the
   marks are drawn over it, and the canvas wait runs whenever its size
   changes. `Slot` gives every other element's box the progress as opacity
   while it is below 1, and nothing at 1.
5. **The proofs.** On every posed reframe frame the renderer refuses a
   moving view's box more than a pixel from the frame's and an element's
   opacity other than the progress. `preview` proves the first frame's
   boxes are the outgoing slots', the end's are the incoming slots' and the
   end's pixels equal the incoming frame without a join, records the
   midpoint's opacities, and replays the midpoint.

## Options considered

- **Compose it like the other joins**: a capture of the incoming picture,
  cropped and slid. The take could not run under it live, the incoming
  set's other content would move with the view, and the camera's continuity
  would be a picture's, not the viewer's.
- **The stage measures the outgoing set while drawing each frame.** It
  would mount a set that is not on screen inside every frame, a measurement
  deciding what is drawn, and the frame would no longer say where the view
  is.
- **Boxes declared in Python.** The layout is the template's (ADR-004); a
  set does not know what its stylesheet draws.
- **Measure in `loadMovie`.** Every load, the pure tests' included, would
  need a browser and the bundle.
- **Move the host to a layer above the set.** It would cover what the set
  draws above the view's slot (a headline) for the join's duration.

## Consequences

- A movie with a reframe pays the layout probe at `check` (one Chromium, one
  pose per set kind) as a movie with a picture does, and each session one
  pose per set kind its reframes use.
- Every frame of a reframe resizes the view's host, so the stage waits for
  the canvas on each: measured on the fixture tour at 640 px, a median of
  about 100 ms per frame of the join against about 67 ms per frame just
  after it, with the late-canvas double and with the real viewer alike.
- The faded elements are drawn under CSS opacity, which Chromium draws with
  grayscale text antialiasing, for the join's duration only; at progress 1
  nothing is written and the end proof shows the frame is the incoming one.
- A slot that clips its content clips a view moving out of it: the
  template's choice, documented in [the stage](../../stage.md).
- Every film's stage bundle changes (the runtime), so every film recaptures
  once.
