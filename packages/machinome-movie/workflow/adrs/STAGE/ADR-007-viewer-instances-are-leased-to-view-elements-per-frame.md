# ADR-007: Viewer instances are leased to view elements per frame

Status: Accepted (OpenSpec change `viewer-instances`, 30 September 2026).
Amends [ADR-004](ADR-004-the-stage-is-a-react-template-that-owns-the-screen.md),
decision 3.

## Context

ADR-004 kept the viewer outside React, "one instance per view element, kept
across the shots of its chapter". The stage mounted an instance the first
time a view element was placed and never released it, so a film mounted as
many viewers as it has view elements: *Cut and Advance* (version 2) six
sawmill viewers, about 1.5 GB in Chromium, and a YAML episode, one chapter
per shot, one viewer per shot that shows the model. No frame of either
shows more than one view at a time. The findings are wart 5 of "The React
stage" and wart 4 of "Cut and Advance, version 2" in `workflow/warts.md`;
the ruling is the orchestrator's, fix-warts campaign, 30 September 2026.

## Decision

1. **Instances are leased per frame.** For each frame, a view element
   placed in it that held an instance at the frame before keeps it; every
   other instance is free; a placed view element without an instance takes
   the lowest-numbered free instance, and a new instance mounts only when
   none is free. A released instance's host leaves the page, as a view
   that left always did. With a viewer at API 28 or later, a film therefore
   mounts no more instances than the largest number of view elements one of
   its frames places.
2. **What an instance holds travels with it.** The layers it hides, the
   highlight standing on it with its restore, and its last box size belong
   to the instance, and each frame's whole state is applied against them:
   a highlight the previous view element left standing is restored, the
   layers it hid are shown again, and a host moved into another box is a
   resize, so the canvas wait runs. A leased instance draws exactly what a
   fresh one would.
3. **Below API 28 an instance keeps its lens.** A viewer below 28 cannot be
   given another up or field of view, and a movie may give two view
   elements different lenses and need only API 21 (a view needs 28 only to
   move to another lens than its own). Such an instance is leased only to a
   view element with the up and field of view it mounted with; for such a
   viewer the bound of decision 1 holds per lens.
4. The lease is a pure function of the mounted instances and the frame's
   placed views (`leaseViews` in `stage/runtime.tsx`); `window.film.views()`
   lists every instance with the view element it serves, or `null` when it
   is free, and `project(key, points)` projects through the instance `key`
   holds.

## Options considered

- **Dispose an instance when its view or chapter is done.** The viewer's
  handle declares no disposal, a chapter's end is not a property of one
  frame (a join poses the outgoing chapter after the incoming one starts),
  and a bounded count needs none.
- **One instance for the whole film.** Wrong for two views side by side.
- **Prefer the instance a returning view last held.** Which instance draws
  a view does not change its pixels (decision 2), and the lowest free one is
  simpler to state and to test.
- **Ignore the lens below API 28, or require 28 whenever two views' lenses
  differ.** The first draws a view through another's lens, and below 28 no
  check reads the lens; the second changes the document contract's rule for
  the required API to serve a runtime choice.

## Consequences

- *Cut and Advance* mounts one viewer instead of six; the fixture tour one
  instead of four when its frames are posed in order, two when a test places
  two views side by side. The memory with the real viewer is measured on the
  film after the change merges.
- Which instance serves a view depends on the frames posed before, and
  nothing drawn does: the instance number appears only in reports and in
  the marks' clip-path ids, which `pose-repaints`' content rule sees, so a
  pose on another instance repaints.
- A join between two chapters' views alternates one instance between them;
  each alternation is a resize with its canvas wait, as each view's
  detached and re-attached host was before.
- Any viewer state the stage does not set on every frame would pass from
  one tenant to the next. It sets time and camera, and from API 28 up and
  field of view, on every frame and diffs visibility and highlight; the
  same assumption held before within a chapter.
