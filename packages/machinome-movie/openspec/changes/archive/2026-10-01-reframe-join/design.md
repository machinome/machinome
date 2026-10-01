## Context

Four joins exist (`shot-transitions`): `dissolve`, `fade`, `wipe`, `slide`.
`frameAt` (`src/timeline.mjs`) returns the incoming shot's frame with
`transition` naming the join, its eased `progress` and the outgoing shot's
frame under `outgoing`; the renderer's `pose` (`src/render.mjs`) captures
each side picture-only at the same instant and asks the stage to compose
them in its transition layer (`window.film.compose`), under the live chrome
of the incoming set. Nothing on the page moves during a join: two still
pictures are mixed.

A view element is drawn by a viewer instance mounted outside React, in a
host (`div.vm-view-host`, `position: absolute; inset: 0`) appended to the
element's box (`div.vm-element`, which fills its slot). The instance is
leased to the view element while frames place it (ADR-007), whatever slot
holds it, so a view placed in consecutive shots of its chapter keeps its
instance, its camera and its take across the cut; a host moved into another
box, or whose box changed size, is a resize, and the stage waits a bounded
number of animation frames for the canvas to fill before posing (the canvas
wait).

A slot's box is the set's layout: the timeline does not know it. ADR-009
made `check` measure it, for a movie that shows a picture, on the page the
renderer serves, with the bundle and a stub viewer (`src/layout.mjs`,
`measureLayouts`): each set kind the shots use is posed empty, once, and
each slot's box, the box a picture gets there, and whether the box changes
when the slots hold content (`fixed`) are read.

## Goals / Non-Goals

Goals: the join the film needs, its frame a pure function of video time and
the measured layout, drawn live on the page, proved in pixels; refusals
before any take where they can be made. Non-goals: those of the proposal.

## Decisions

### D1. The declaration and the document

`Reframe(duration, *, ease=None)` is a `Transition`, like `Dissolve`: a
positive duration and an easing of the vocabulary; no `direction`, no
`color`. The ruling writes `ease="smooth"`: smooth is the default, written
as every join writes it, left out of the document unless given and read as
`smooth` by the timeline, so `Reframe(0.8)` is `{"kind": "reframe",
"duration": 0.8}`. A direction or a colour on a reframe is refused by the
rules every join already has.

The schema's `join` gives `kind` as a string and leaves the kinds to the two
runtimes' semantic checks, which name the shot and the field
(`transition.kind`); its fields (`kind`, `duration`, `ease`) already cover
the reframe. The schema is therefore unchanged; the ruling allowed amending
it, and nothing in it needs to change. The refusal of an unknown kind now
lists `dissolve, fade, wipe, slide or reframe` in both runtimes.

### D2. What a reframe frame is

For a shot `S` that comes in by a reframe from the shot `P` before it, and
`u` the seconds since `S` started, `u < d`:

- the frame is `S`'s live frame at that instant: the set, slots and
  elements of `S`, every element's state as `S`'s timeline gives it; a view
  element's camera, field of view, up and model time are exactly `S`'s;
- `transition` is `{field: "transition", kind: "reframe", shotId,
  outgoingShotId, start, duration, ease, progress, outgoing: null, boxes}`,
  `progress = ease(u / d)`;
- the **moving views** are the view elements `P` and `S` both place (the
  same element key, so the same chapter); for each, `boxes[key] = (1 −
  progress)·from + progress·to`, component by component, where `from` is
  the box of the slot holding it in `P`'s set and `to` the box of the slot
  holding it in `S`'s set, as `[x, y, width, height]` fractions of the
  frame. The weighted form gives `from` exactly at progress 0 and `to`
  exactly at progress 1;
- every other element `S` places is drawn at opacity `progress`;
- `P`'s elements that `S` does not place are not drawn: the reframe is a
  cut for them (a project that wants them to leave fades them with their
  own `leave` before the cut);
- chrome is `S`'s set's, as for every join.

`outgoing` is null: nothing of `P` is posed, so the review sample plan, the
shot cache and the clip continuation treat the outgoing shot as not seen
past its end (a helper, `joinShows`, gives the seconds a join shows the
outgoing shot: half of a fade, the whole of a dissolve, wipe or slide,
none of a reframe). For the same reason the rule "the outgoing shot cannot
continue past the export" does not apply to a reframe.

Alternative rejected: moving the incoming picture as a capture in the
transition layer (a slide of a cropped capture). It composes pictures, so
the take could not run under it live, a `move` cue could not either, and
the incoming set's other content would move with the view instead of
fading.

### D3. Where the boxes come from

The timeline is pure and cannot measure; the slot boxes belong to the set,
drawn only by the stage. They are measured on the stage, by the probe of
ADR-009, and attached to the loaded film as data, as the pictures' probes
are (`pictureMedia`):

    film.reframes = {<shot id>: {<element key>: {from: {set, slot, box},
                                                to: {set, slot, box}}}}

with `box` in fractions of the frame. `reframeBoxes(doc, layouts)`
(`src/layout.mjs`) builds it from a measured layout and refuses a reframe
whose outgoing or incoming slot is **sized by what it holds** (its box
changes when the set's slots hold content), naming the shot, the view, the
set and the slot: such a slot has no box until it is drawn with its
content, and the reframe needs both boxes before the frame is drawn.

- `check` measures the layouts when the movie shows a picture **or has a
  reframe**, refuses that way before any take, prints one line per reframe
  (`Reframe into question: opening.wide from playbill stage 870.4×576 at
  64,86.4 to playbill-split right …`), and attaches `reframes` to the
  loaded film before the checks that pose frames.
- Every browser session (`preview`, `render`, and the tests' sessions)
  measures the sets its reframes use on its own page, at its own width,
  before its first frame, with the same in-page function (`measureSet`),
  and attaches `reframes` to the film it renders. Fractions are measured at
  the width the film is drawn at, so the stage's arithmetic back to pixels
  meets the layout it measured.
- `frameAt` refuses a reframe frame of a film without `reframes`, naming
  the shot: no box is ever guessed.

Alternatives rejected: the frame carries slot names and the stage measures
the outgoing set while drawing each frame (it would mount a set that is not
on screen inside every frame, a measurement deciding what is drawn, and the
frame would no longer say where the view is); boxes declared in Python (the
layout is the template's, and a set does not know what its CSS draws);
measuring once in `loadMovie` (every load, pure tests included, would need
a browser and the bundle).

### D4. The stage

- **The fade is React's.** `Slot` reads the frame's reframe: an element it
  draws that is not a moving view gets `opacity: progress` on its element
  box while `progress < 1`; at progress 1 no style is written, so the box
  is exactly as without a join. Pure in the frame, tested at layer 4.
- **The host moves; the element stays.** The moving view's host stays in
  its incoming slot's element (so the set's stacking order holds: a
  headline the set draws above the view stays above it), positioned
  `absolute` at the frame's box: `left = snap(x·W) − element.x`, `top =
  snap(y·H) − element.y`, `width = snap(w·W)`, `height = snap(h·H)`, where
  `W`, `H` are the page's size and `snap` rounds to 1/64 px, the layout's
  own unit, so a box measured on the page comes back to the same layout
  unit. Without a reframe, or for a view that does not move, the host's
  inline position is cleared and its stylesheet's `inset: 0` holds. The
  slot's own box stays what the set draws. A slot that clips its content
  clips the moving view: the template's choice, documented.
- **Reports.** The host's rectangle is the element's `box`; the marks are
  drawn over it; the canvas wait compares the canvas with it. During a
  reframe every element reports `opacity`, its box's computed opacity.
- **The canvas wait** runs when the host's size changed since the last
  pose, which a moving host does every frame. Its cost per frame is
  measured with the late-canvas double and recorded in `evidence.md`.

The positioning is a pure helper, `reframeHost(element, page, box)`,
returning the inline style, tested at layer 4.

### D5. The renderer and the proofs

- A reframe frame is posed by `showPicture` like a frame without a join:
  no captures, no `compose`. `show` sends the reframe to the stage (the
  other joins' `transition` stays off the request, as today).
- Each posed reframe frame is checked: a moving view's reported box equals
  the frame's box times the page's size within one pixel (`Reframe box
  differs from the timeline`), every other element's reported opacity
  equals the progress within 0.001 (`Reframe fade differs from the
  timeline`), and the canvas fills the box (the existing check).
- `preview`, per reframe (its `transitionChecks` entry, kind `reframe`):
  stills at the first frame, quarters, midpoint and last frame; at the
  first frame (progress 0) each moving view's box equals its outgoing
  slot's measured box within a pixel; at the midpoint every other
  element's opacity is the eased progress, recorded; at the join's end,
  the reframe at progress 1 (`reframeAt(film, shot, d)`, the timeline's own
  arithmetic) posed at that instant equals, pixel for pixel, the same
  instant posed without a join, and each moving view's box equals its
  incoming slot's within a pixel; the midpoint, another instant and the
  midpoint again give identical pixels. A failure stops preview naming the
  shot, the view and the time and keeps the images.

### D6. Refusals

Before any take, both runtimes (`check_document`, `checkMovie`) and the
Python declarations (`Chapter` for two shots of one chapter, `Movie` for a
chapter's first shot):

- a reframe whose two shots place no view element in both, naming the
  chapter, the incoming shot, the outgoing shot, `transition` and `no view
  element in both`.

At `check`, before any take: a reframe slot sized by what it holds (D3).
After the takes (existing rules): a duration under two frames or longer
than the incoming shot, and a reframe on the film's first shot.

Refusal words added to `fixtures/README.md`: `no view element in both`,
`sized by what it holds`.

### D7. The fixture

The tour's `opening` chapter: `hook` (`Playbill`, `wide` in `stage`, the
tally in `aside`) then `question`, now on `PlaybillSplit` with `wide` in
`right`, the tally in `left` and the title in `headline`, coming in by
`Reframe(0.8)` on the phrase it already cuts on ("How"). The narration and
its take double are unchanged. The tally is in both shots and is not a
view: it fades in, at its new place, as the rule says. `question` keeps its
title fade, so the title's own fade and the reframe's multiply during the
first 0.6 s.

## Risks / Trade-offs

- **Every reframe frame waits for the canvas.** A moving host is a resize
  every frame; with the real viewer, which sizes its canvas on its own
  animation frame, each frame of a join costs at least that wait. Measured
  and recorded; acceptable for joins of a second.
- **CSS opacity on text.** Chromium draws HTML glyphs with grayscale
  antialiasing under CSS opacity; the composed joins avoid it by blending
  captures. A reframe is live by the ruling, so its fading text is drawn
  that way for the join's duration; at progress 1 no opacity is written,
  and the end proof shows the frame is then exactly the incoming one.
- **Boxes measured per session.** A film rendered at another width measures
  its own fractions; they equal the output size's up to the layout unit.
  The shot cache keys the frames, boxes included, so a change of layout
  recaptures the join.
- **`check` opens a browser** for a movie with a reframe, about a second.

## Migration Plan

None: a new kind; documents without one are unchanged. Every film's stage
bundle changes (the runtime), so every film recaptures once.

## Open Questions

None for this change. Whether the real viewer's per-frame canvas wait is
fast enough for the film's join is measured at layer 6 with the selected
bundle and recorded.
