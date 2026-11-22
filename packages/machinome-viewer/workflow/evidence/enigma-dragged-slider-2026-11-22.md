# What a dragged slider does on a clocked machine, Enigma I, 22 November 2026

Opening evidence for `follow-the-slider-as-it-is-dragged`, written by the
reviewing agent before the proposal. Measured facts with their limits;
nothing here is a design.

## Where the finding comes from

The pilot, on the Enigma I page (`enigma-i` at `081f4e6`, as the project's
own tools build it), in the viewer at framework commit `f6119628`:

> When I drag the slider to, for example, open the case, the case remains
> static while I drag the slider, and only when I release, the slider gets
> back to original and then animation happens. [...] I want the case to
> follow the slider as I drag.

The pilot remembered this as a defect that had been corrected and had come
back. The record does not show that. What it shows is below.

## What the source and the record say

The Enigma's document carries commits, so the viewer runs it as a clocked
machine and its panel is the clocked panel. A ranged input's row there has a
slider that listens on `change` alone (`viewer.ts`, `buildClockedRow`):

    slider.addEventListener('change', () => {
      actions.move(control.id, Number(slider.value));
    });

`move` is `clockedRequest(id, { to }, true)`: one request, judged and not
posed, and the transition it reports drawn over `gestureSeconds`. No
declared instruction states a travel on `case_open` by an amount (`Open
case` and `Close case` state where it lands), so that is the viewer's own
0.2 seconds. The drawing's first frame stands at the origin and the panel
follows the drawing, which is why the thumb goes back to where the input
stood and then travels.

The slider of a document that carries no machine (the posed panel) writes on
`input` and on `change`, so there the model follows the thumb.

`git log -L` over the clocked slider's lines names one commit, `5daeccfc` of
17 September 2026, which wrote them. ADR-065 (`draw-every-request`, the same
day) has a section headed "There is no live-drag exception, because there is
no live drag", and among the alternatives it set aside:

> Requesting per pointer move during a drag (`input` rather than `change`).
> That is the per-frame-request shape ADR-064 measured and the pilot
> rejected; on the Curta it is a 40 ms solve and a pose per pointer sample.

What ADR-064 records the pilot rejecting is slicing a declared instruction
into a request per frame. No record shows the pilot being asked about a
dragged slider.

The Enigma model declared `case_open` on 15 November 2026 (`4db9a50`), when
it already carried the commits of its `operation` branch. On this model the
case's slider has therefore always been a clocked one.

## What was measured

Headless Chromium (Playwright), the page's own files, the viewer built
unminified from the unedited source of `f6119628` (with molejo's `main`) and
a scratch entry that exposes the renderer, the scene and the mounted
handle. WebGL draw calls were counted and not executed, so every time is
script time on the measuring machine (a virtual machine with no GPU). One
page load for each of the two parts.

### A real pointer on the case's slider

The browser's own mouse pressed on the thumb (the input standing at 1),
moved to a quarter of the track in twelve steps with two animation frames
after each, rested for twenty frames, and released.

| | Thumb | Machine's `case_open` | Meshes that moved |
|---|---|---|---|
| Each of the twelve steps | 0.9375, 0.875, ... 0.25 | 1 | 0 |
| Held and at rest | 0.25 | 1 | 0 |
| First frame after the release | 1 | 0.25 | |
| The frames that follow | 0.9374, 0.8125, 0.6876, 0.625, 0.5624, 0.4375, 0.3752, 0.3122, 0.25 | 0.25 | up to 78 in a frame |

The slider received one `pointerdown`, twelve `input` events, one
`pointerup` and one `change`. Nine frames moved something, between 36 and
230 ms after the release, at 15.8 to 24.6 ms of script each.

### One request posed at once in every animation frame

Through the handle a host holds, `machine().move(id, { to })`, which poses
and draws in the call: forty requests over an input's whole travel, one per
animation frame. Milliseconds of script.

| Input, travel | A request, median (least to most) | of it, the pose | of it, the draw | Meshes moved |
|---|---|---|---|---|
| `case_open`, 1 to 0 | 28.3 (22.6 to 36.9) | 4.1 | 20.5 | 80 |
| `case_open`, 0 to 1 | 27.3 (20.7 to 36.5) | 3.7 | 20.0 | 78 |
| `case_open`, 1 to 0 | 28.5 (20.6 to 38.5) | 4.7 | 20.2 | 80 |
| `case_open`, 0 to 1 | 24.7 (19.4 to 30.5) | 3.7 | 18.0 | 78 |
| `hood_open`, 0 to 1 | 26.5 (19.4 to 33.0) | 3.3 | 18.7 | 64 |
| `hood_open`, 1 to 0 | 28.9 (19.5 to 34.9) | 4.0 | 19.7 | 64 |
| `flap_open`, 0 to 100 | 29.8 (22.1 to 33.6) | 5.0 | 20.9 | 6 |
| `flap_open`, 100 to 0 | 28.2 (20.0 to 35.5) | 4.1 | 19.8 | 6 |
| `operation.press`, 0 to 1 | 58.1 (37.3 to 87.4) | 34.4 | 20.0 | 332 |
| `operation.press`, 1 to 0 | 53.8 (37.9 to 68.6) | 31.2 | 19.7 | 332 |

The pose and the draw are means over the forty requests; the request is its
median. No request was refused; every sweep was admitted whole. A request on
`operation.press` visits the 86 flexible parts each time, as a frame of a
played press does. Each request drew once, in its own call, and the frame
loop then drew nothing (0.03 to 0.06 ms a frame).

A request of no travel, twenty times: 18.0 ms median (14.1 to 28.4). It
draws too, since the machine's pose hook draws for every request.

## What the figures say and do not say

- A request posed in a frame costs, on this page, what a frame of the
  drawing after a release costs today (a pose and a draw) plus 3 to 5 ms
  that are the machine's own answer and the panel's rebuild, which the
  handle's `move` does on every call. The two were not separated.
- On `operation.press` it is what a frame of a played key press costs (50 to
  54 ms measured for the previous change).
- Most of every frame is the draw's script for 3,347 draw calls, which any
  frame that changes the picture pays.
- Nothing was measured on a GPU, and no other browser was tried.
- The Curta's figure in ADR-065 (a 40 ms solve for a pointer sample) is from
  September and was not measured again.
- The handle's `move` replaces the panel on every call, and so does the
  panel's own request (`clockedRequest`). A slider that is replaced while a
  pointer holds it is no longer the element the pointer holds; that is read
  from the source and was not tried.
