## Why

Two findings of 30 September 2026 in `workflow/warts.md`:

- "The React stage", wart 5: **one viewer per view element.** The
  contract's rule; *Cut and Advance* would mount six sawmill viewers in one
  page. Memory with the real viewer is unmeasured (layer 6 has no test).
- "Cut and Advance, version 2", wart 4: **six viewer instances of the
  sawmill cost about 1.5 GB in Chromium** and rendered without trouble; the
  instances are never disposed. A longer film with more chapters mounts one
  per view element.

The episode is *Cut and Advance* (the Leonardo project, version 2,
30 September 2026): six chapters' view elements of one model, each mounting
its own viewer and keeping it for the whole session, although no frame of
the film shows more than one view at a time. The count grows with the
film's chapters, not with what a frame shows.

The orchestrator's ruling (fix-warts campaign, 30 September 2026): a film
mounts no more viewer instances than the largest number of view elements
one of its frames places. Instances are leased: a view element keeps its
instance from one frame to the next while it stays placed; when a frame does
not place it, its instance is free and may be leased to another view element
of that frame or a later one; a view that returns takes a free instance or a
new one. Each frame states each instance's whole state, so a re-leased
instance draws exactly what a fresh one would; the diffs the stage keeps
(hidden layers, the standing highlight and its restore) belong to the
instance and are carried across the lease. Nothing observable changes but
the instance numbers and the count.

What the film does with the result: its next render mounts one sawmill
viewer instead of six (each of its stage frames places one view; a join's
two pictures are two frames posed one after the other), and the memory
with the real viewer is measured on it after the merge (the orchestrator's,
with the `viewer-integration-layer` cycle; owed, not claimed here).

## What Changes

- **View elements lease viewer instances.** `poseViews` in
  `stage/runtime.tsx` keeps a list of mounted instances, each serving at most
  one view element. For a frame, a view element that held an instance at the
  frame before keeps it; every other instance is released (its host
  detached, as today); a placed view without one takes the lowest-numbered
  free instance, and only when none is free does a new one mount. The
  choice is a pure function, `leaseViews`, exported beside `measureElement`.
- **A viewer that cannot change its lens is leased only to its lens.** Below
  Viewer API 28 `setView` cannot set up or field of view, and a movie
  document may give two view elements different lenses and still need only
  API 21; such an instance is leased only to a view element whose up and
  field of view equal those it mounted with (design D3).
- **The instance's state travels with it.** The hidden layers, the standing
  highlight and its restore and the last box size stay on the instance, so
  `pose()` applies a new view element's state against what the instance
  holds: a highlight left standing by the previous tenant is restored,
  layers it hid are shown again, and a host moved into another box is a
  resize, so the canvas wait runs. `mountView()` mounts as it does and
  `pose()` applies what it applies.
- **`window.film.views()`** lists every mounted instance with the key of the
  view element it serves, or `null` when it is free; `project(key, points)`
  projects through the instance the view element holds.
- **Browser tests** (layer 5, the viewer double): a view that leaves frees
  its instance and one that returns is drawn on it, pixels A, B, A
  identical, with a standing highlight restored, hidden layers that differ
  and the late-canvas double; two views side by side mount two instances and
  the six orders of A-only, B-only and A-and-B frames never mount a third
  and give the same pixels for each frame. Layer 4: `leaseViews` over every
  sequence of such frames, and the lens rule.
- **Records**: ADR-007 (STAGE); the three contract sentences
  (`docs/stage.md`'s `view` row, `docs/movie-document.md`'s stage section,
  the `react-stage` requirement renamed and rewritten); ADR-004's decision 3
  pointed at ADR-007; `docs/architecture-overview.md` where it states the
  rule; `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `react-stage`: "A view keeps one viewer across its chapter" becomes "View
  elements lease viewer instances".
- `test-suite`: the browser proofs of the stage include the lease.

## Impact

Code: `stage/runtime.tsx` (`poseViews`, the pool, `views()`, `project()`,
`clearComposition`), `test/browser/stage.test.mjs`, `stage/stage.test.tsx`.
The runtime is bundled into every film's stage bundle, so every film
recaptures once, as every change to it does. No format, document, schema,
refusal, command option or renderer check changes; the renderer does not
read the instance number.

## Non-goals

No disposal API (the count is bounded, so none is needed); no change to the
viewer double's mount, the shot cache or the canvas wait; no change to what
a view's report contains. The memory with the real viewer is the
orchestrator's to measure on *Cut and Advance* after the merge. No
publication, push or paid request.
