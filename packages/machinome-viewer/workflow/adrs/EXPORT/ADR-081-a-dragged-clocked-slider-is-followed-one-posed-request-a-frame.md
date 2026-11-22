# ADR-081: A dragged clocked slider is followed, one posed request a frame

**Status:** Accepted

**Date:** 2026-11-22

**Change:** [follow-the-slider-as-it-is-dragged](../../../openspec/changes/archive/2026-11-22-follow-the-slider-as-it-is-dragged/)

**Amends:** [ADR-065: Every request the clocked panel makes is drawn, over a duration of the viewer's own](ADR-065-every-request-the-clocked-panel-makes-is-drawn.md)
(its section "There is no live-drag exception, because there is no live
drag" and its rejected alternative "Requesting per pointer move during a
drag")

**Extends:** [ADR-064: A clocked instruction is one request, drawn over its duration](ADR-064-a-clocked-instruction-is-one-request-drawn-over-its-duration.md)
(one authority over the pose: a press's own drawn jump is waited for, not
landed),
[ADR-080: A continuous viewer draws a frame only when its picture has changed](ADR-080-a-continuous-viewer-draws-a-frame-only-when-its-picture-has-changed.md)
(a held slider is not motion)

**Builds on:** [ADR-073: A gesture is drawn at the declared tempo](ADR-073-a-gesture-is-drawn-at-the-declared-tempo.md)
(how long a drawn jump takes)

## Context

On the Enigma I page the pilot dragged the slider that opens the case. The
case stood still for as long as the thumb was held; at the release the
thumb went back to where the input stood and the case then swung there in
a fifth of a second. "I want the case to follow the slider as I drag."

The clocked panel's slider listened on `change` alone, so a drag was one
request made at the release, drawn from where the input stood (ADR-065).
It had been written that way on 17 September 2026 and had not changed.
ADR-065 set a request per pointer sample aside on the Curta's cost, by
analogy with the instruction sliced into frames that ADR-064 records the
pilot rejecting; no record shows the pilot being asked about a drag. A
drag's positions are the hand's, not a declared stroke's: there is no
stated transition to draw, and the model that waits for the release shows
nothing the hand did.

A real pointer on the case's slider of the page: twelve `input` events and
no mesh moved; after the release nine frames of drawing. A request rebuilt
the whole panel, so a slider that asked while it was held would be replaced
under the pointer.

## Decision

**While a pointer drags the thumb of a clocked machine's slider, the
machine is asked for the thumb's latest position once per animation frame,
and the model, the readings and the bank follow it. Everything that is not
a drag is one drawn request, as ADR-065 decided.**

1. **A press, a position, and which positions are a drag.** A press begins
   at a `pointerdown` of the primary button on a slider of the clocked
   panel while no clock's transport plays, and records its pointer. Each
   `input` the slider fires while the press is held is a position, in
   design units. The first position of a press is **drawn**, as one
   request over the gesture's duration, when no `pointermove` of the
   press's pointer has come since the `pointerdown` (a press on the track,
   which moves the thumb before the pointer moves) or when the input, as
   the model shows it, stood outside the slider's range (a pinned thumb).
   Every other position is **followed**. The rule reads the order of the
   events and the pointer's id, never where a browser paints the thumb. The
   order was recorded in Chromium with a mouse and with touch, where the
   suite holds it on the viewer's own slider, and in Firefox with a mouse,
   recorded only: the suite's Firefox does not run under its Playwright.
2. **One request a frame, for the latest position.** A followed position is
   kept as the press's one pending position. In each animation frame,
   after the clock's and the drawing's own steps, a pending position that
   differs from the last one asked is asked with one `move(id, { to })`.
   Nothing queues: a later position replaces an earlier one that has not
   been asked. A position is never asked twice in succession, the last
   position is never dropped (whatever ends the press asks it), and a
   thumb held still asks nothing.
3. **Posed, and drawn by the loop.** The request goes through the
   machine's pose hook in a third mode, beside posing-and-drawing and
   judging: it updates the tree and does not draw. The update raises the
   picture's revision and the loop's own decision draws once (ADR-080). A
   held press is not motion: a frame in which nothing was asked draws
   nothing.
4. **A drawn jump is waited for.** A press's own drawn jump is made in its
   `input`'s task, by the press itself, and its drawing runs to its end
   while the thumb stays where the pointer put it. Positions that come
   meanwhile wait; the frame the drawing lands in asks the latest. If the
   pointer is let go first, the drawing still runs to its end. A followed
   position lands any other running drawing, as every gesture does.
5. **Nothing replaces the panel while a press lasts.** A drag writes the
   panel in place: the fields and readings a request moved, the row's
   outcome line where its text changes, and no thumb a pointer holds. The
   slider stays the element the pointer pressed and keeps the focus. A
   press's jump that starts no drawing (a tempo of zero seconds) writes
   what it published the same way. When the press ends the thumb is
   written once where the machine stands.
6. **The row reports the drag as a whole:** the travel admitted since the
   press, with the stops of its latest request, or that request's refusal.
   A stop or a refusal repeated by later positions leaves the report as it
   stands.
7. **What ends a press, its last position asked:** the release of its
   pointer, wherever it is let go; its cancellation; the slider losing the
   pointer's capture; a key on the slider; a press on another slider; and
   every door that would move or repose the machine or replace the panel
   (a typed value, a nudge, a pressed instruction, the panel's Reset, play,
   step and step amount, a change of focus, a reload, an in-place update
   that keeps the machine, and the host's `move`, `restore`, `reset`,
   `trigger` and `setClockPlaying`). The rebuild of the panel ends a press
   itself, so a door added later cannot replace a held slider. The
   release's own `change` is not a request. **Dropped, with nothing
   asked:** a republish that replaces the machine, and `dispose()`. A
   panel's sliders begin a press and commit only for the machine the panel
   was built for. **Ends nothing:** the window losing focus, a hidden
   page, the clock's speed, another pointer.
8. **Nothing stands on the window while no slider is held.** The three
   listeners a press needs there (its pointer's movement, release and
   cancellation) are added at the press and removed at its end.
9. **No press begins while a clock's transport plays.** A slider's gesture
   is then the one drawn request it was. The transport rebuilds the panel
   in every frame it plays, so a slider could not be held there before
   either; no project or fixture carries a clock beside a ranged input,
   and the case is recorded in `workflow/warts.md`, not built.
10. **On demand nothing changes:** that mode presents no clocked panel.
    The viewer API stays 30 and the document versions 1 to 14.

## The bank a drag leaves

A drag is the requests it made, each atomic, each from the bank the one
before it left.

- A travel in one direction leaves the bank one request to the last
  position leaves, commits included.
- A hand that goes back and forth across a commit's level fires the commit
  at each rising crossing, where one request to the last position fires it
  once.
- A whole-number input is asked whole numbers and posed whole at every
  frame.
- A travel the machine refuses whole in one request (more crossings of one
  relation than the document's limit, or a commit that would carry a
  coordinate out of range) can be admitted step by step, and a stop whose
  bound reads a state a commit wrote can hold one and not the other.

## Consequences for hosts

`machine().state()` follows the thumb during a drag, where it held the
bank from before the drag until the release. A host's `move`, `restore`,
`reset`, `trigger` or `setClockPlaying` during a drag acts after the
drag's last position has been asked. A press on the track makes its
request when the button goes down, not when it is let go.

## Alternatives

- **Each position a drawn gesture:** every position drawn over a fifth of
  a second and landed by the next, so the model lags and then jumps; and
  each request rebuilt the panel, replacing the slider the pointer holds.
- **One request per `input`, in the event's task:** several requests a
  frame where a browser does not coalesce, requests queued behind a slow
  one, and a pose a frame might draw twice.
- **Telling a jump by where the thumb is painted, or by the size of the
  first change:** the first depends on the browser's thumb and the page's
  styles; the second confuses a fast hand with a slow press on the track.
- **Landing a press's own jump at its first movement:** the rest of the
  jump shown in one frame, the defect ADR-065 removed.
- **Chasing the thumb with drawn segments:** the model would trail the
  pointer for the whole drag.
- **Rebuilding the panel at the release:** the slider loses the focus and
  the panel its scroll position.
- **Stopping the clock at a press, or ending a press when the window loses
  focus:** struck in review; nothing needs the first, and the second would
  stop following a thumb the hand still holds.
- **A term for a held press among what moves:** a thumb held still would
  draw every frame.
- **A handle method or a mount option:** none is needed.

## Consequences

- A frame of a drag costs one request of the machine, one update of the
  tree, the narrow writes and one draw: about what a frame of a drawn
  request cost, with the machine's solve added. A request that takes
  longer than a frame makes that frame long, and the next frame asks once
  for wherever the thumb is by then.
- After a drawn jump the model joins the thumb in one frame, once the
  jump's drawing has landed: up to the gesture's duration later.
- A pointer let go where the browser reports no release leaves a press
  whose every position has been asked; the next press, key or door ends
  it.
- An arrow key is still a drawn request that rebuilds the panel, so the
  slider loses the focus after one step. Found while proposing, recorded,
  not changed here.

## Proof

A bench that mounts the real viewer in jsdom with a counting renderer,
logs every request the machine is asked, and dispatches on the panel's own
slider the events the browsers dispatch, in their recorded order.
Fifty-five tests, forty-eight of them red before the change; the seven
that pass there assert what the change keeps, and four behaviours were
recorded on the base and are reproduced (a click's drawn path, a slider
beside a playing clock, a key with a typed value and a nudge, and the
on-demand mode). 200 generated sequences of drags, doors and gestures over five documents, each
checked at every frame for the panel against the model, at rest for the
model against the bank, and per drag for what was asked against what the
hand did, replayed on a fresh machine. Browser tests in Chromium with a
real pointer and with touch: the bank against the thumb at every step, a
whole-number input, a press on the track held, the order of the events.
Twenty-five designed mutations and twenty-eight faults planted in review
turn named tests red or are shown equivalent or unreachable; a defect and a
needless rule found in review were corrected first.

**Measured** on the Enigma I page (`enigma-i` at `081f4e6`) with a real
pointer in Chromium; script only, draw calls counted and not executed.
The case's thumb dragged through twelve positions: the machine's
`case_open` equals the thumb at each, twelve requests, twelve draws, 18.6
to 24.2 ms of script in a followed frame (19.9 to 31.9 in a frame of the
drawn request it replaces); sixty frames with the thumb held still, and
the frames after the release: no request, no update, no draw; the slider
the same element, focused. The flap the same, 16.9 to 30.5 ms. A wheel of
whole numbers: six positions, six requests of one tooth, 20.4 to 39.6 ms,
the bank at the end the bank one request of six leaves. A key pressed by
its slider: ten positions each way, 28.4 to 48.0 ms. The wheel's and the
key's sliders stand under the `operation` focus, where the page shows no
part, so their frames draw nothing. A press on the track: the jump drawn
from the press over seven frames with the button down, where it was drawn
after the release; a press on the track then dragged: the machine holds
the jump's end until its drawing lands and follows from the next
position. An arrow key: one drawn request, as before. On the window while
a thumb is held, three listeners more than at rest; none after.
Really drawn in software: what is on screen equals a forced draw in nine
states, two of them with the thumb held in the middle of a drag; and in the
seven states a gesture ends in, the picture outside the panel equals, pixel
for pixel, the previous viewer's picture of the same bank reached by
`restore` (6.7 million pixels compared, none differing). Inside the panel
the two differ by the drag's outcome line and the slider's focus.
Not measured: any GPU, another browser on this page.

[Design](../../../openspec/changes/archive/2026-11-22-follow-the-slider-as-it-is-dragged/design.md) and
[evidence](../../../openspec/changes/archive/2026-11-22-follow-the-slider-as-it-is-dragged/evidence.md)
record the cases, the tests and the measurements. The pilot was told of the
choices this record makes beyond "the case follows the slider" before
integration.
