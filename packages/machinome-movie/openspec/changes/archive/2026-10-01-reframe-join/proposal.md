## Why

The episode is *Addition*, the Curta film of the curta-video campaign
(`workflow/ongoing/curta-video-campaign/plan.md`, 1 October 2026): the Curta
Type I adds 23 and 145. Its fourth chapter turns from the machine to the
code that declares it, and the pilot wrote how (`workflow/ongoing/curta-video.md`):

> the transition to the code will be: curta will be full screen; in the
> same scenario, its container will shrink to right half of the screen;
> code will fade in a second container; a narration will show some code
> and curta will animate. It's important that the transition in the
> previous item happens with continuity of the camera on the curta model.

The finding: no join does this. A shot comes in by `dissolve`, `fade`, `wipe`
or `slide`, and each is composed from same-instant picture-only captures of
the outgoing and the incoming shot in the stage's transition layer: two
pictures, never a moving container. A cut from the full-frame set into the
split set jumps the model's container from one box to the other. The view
element itself already survives the cut (ADR-007: a view placed in
consecutive shots of a chapter keeps its viewer instance and its camera),
so the camera's continuity is the lease's; what is missing is the
container's motion and the fade of what the incoming set adds.

What the film does with the result: chapter 4 cuts from the Curta in the
whole frame into the split set with `transition=Reframe(...)`; for the
join's duration the Curta's box shrinks from the whole frame to the right
half, its camera and its take running on as the incoming shot's timeline
says (the crank may turn under it), while the source panel fades in on the
left; the narration then lights the code's tokens.

The orchestrator's ruling (curta-video campaign, cycle brief of
1 October 2026): a fifth join, **reframe**, declared `Reframe(duration,
ease="smooth")`, written `{"kind": "reframe", "duration", "ease"}`; it
requires a view element placed in both shots and is refused before any take,
naming both shots and "no view element in both", when none is; during the
join the live page shows the incoming set, each view placed in both shots
drawn in a box moving from its outgoing slot's box to its incoming slot's
box by the eased progress, with the incoming timeline's camera and model
time, every other element of the incoming shot at opacity equal to the
eased progress, and the outgoing shot's other elements not drawn; chrome is
the incoming set's; no captures, no composition; the frame carries the box
of each moving view as fractions of the frame, and the stage hosts the view
over it.

## What Changes

- **A fifth join.** `Reframe(duration, ease=)` in
  `python/machinome_movie/stage.py` beside `Dissolve`, `Fade`, `Wipe` and
  `Slide`, exported by the package; the document's `transition` takes
  `{"kind": "reframe", "duration", "ease"?}`. Python refuses at class
  creation (in the chapter for two shots of one chapter, in the movie for a
  chapter's first shot) a reframe whose two shots place no view element in
  both, naming both shots and `no view element in both`; both runtimes'
  document checks refuse the same, and an invalid fixture pins it.
- **The frame of a reframe** (`src/timeline.mjs`). The incoming shot's live
  frame, with `transition: {kind: "reframe", progress, boxes, outgoing:
  null, …}`; `boxes` gives, for each view element both shots place, the box
  it is drawn in, as fractions of the frame, interpolated between its slot's
  box in the outgoing set and its slot's box in the incoming set by the
  eased progress.
- **Where the boxes come from** (`src/layout.mjs`). A slot's box is the
  set's layout, drawn only by the stage, so the reframe's slot boxes are
  measured on the stage by the probe `check` already runs (ADR-009), and
  attached to the loaded film as `reframes`; `check` measures them for a
  movie with a reframe (as for one with a picture) and refuses a reframe
  whose slot is sized by what it holds, naming the shot, the view, the set
  and the slot; every browser session (`preview`, `render`) measures them on
  its own page before its first frame. `frameAt` refuses a reframe frame of
  a film whose boxes were not measured, naming the shot.
- **The stage** (`stage/components.tsx`, `stage/runtime.tsx`). During a
  reframe, `Slot` draws every element but the moving views at the frame's
  progress as opacity; the runtime positions a moving view's host over the
  frame's box inside its incoming slot's element (so the set's stacking
  order holds), reports that box as the element's `box`, reports every
  element's opacity, and runs the canvas wait whenever the host's size
  changes, which is every frame of a reframe.
- **The renderer** (`src/render.mjs`). A reframe frame is posed live, like a
  frame without a join; each posed reframe frame is checked: a moving view's
  box is the frame's within a pixel, every other element's opacity is the
  progress, the canvas fills the box. `preview` proves each reframe: at its
  first frame each moving view is in its outgoing slot's box, within a
  pixel; at its midpoint the other elements' opacity is the eased progress;
  at its end the reframe at progress 1 is the incoming frame without a join,
  pixel for pixel, each view in its incoming slot's box; the midpoint posed,
  another instant, and the midpoint again gives identical pixels.
- **The fixture tour** gains a reframe: chapter `opening` cuts from
  `Playbill` (the model in `stage`) into `PlaybillSplit` (the same view in
  `right`, the tally in `left`, the title in `headline`) with
  `Reframe(0.8)`, on the phrase it already cuts on, so no speech fixture
  changes. The fixture project and every document are re-pinned; the tour's
  resolved pin is re-made and reviewed.
- **Records**: ADR-010 (STAGE); `docs/declaring-a-movie.md` (the joins),
  `docs/stage.md` (how a view is hosted, the fade), the `transition`
  sentence of `docs/movie-document.md`; `docs/architecture-overview.md`;
  `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shot-transitions`: a shot can come in by a reframe; its refusals; its
  proofs.
- `react-stage`: a moving view's host is drawn over the frame's box, and the
  rest of the incoming shot fades by the progress.
- `declarative-movie`: `Reframe` is declared on a shot and refused without a
  view in both shots.
- `movie-document`: `check` measures the layouts of a movie with a reframe,
  and refuses a reframe slot sized by what it holds.

## Impact

Code: `python/machinome_movie/stage.py`, `movie.py`, `document.py`,
`__init__.py`; `src/movie.mjs`, `src/timeline.mjs`, `src/layout.mjs`,
`src/render.mjs`, `bin/videomaker.mjs`; `stage/components.tsx`,
`stage/runtime.tsx`, `stage/types.ts`. The runtime is bundled into every
film's stage bundle, so every film recaptures once. `check` opens a browser
for a movie with a reframe. The schema is unchanged: its `join` leaves
`kind` a string both runtimes check, and its fields already cover the
reframe (design D1). No viewer change; no change to the four composed joins
or to the lease.

## Non-goals

No reframe of a source, title or picture (only views move); no reframe
across chapters (a view belongs to a chapter, so two chapters' shots never
share one); no change to the dissolve, fade, wipe or slide; no change to the
lease; no YAML episode spelling. No publication, push or paid request.
