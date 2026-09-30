## Context

The stage's `setFrame` (`stage/runtime.tsx`) commits the frame with
`flushSync`, poses the views (waiting, when a view was mounted, placed again
or resized, for its canvas to fill its box), draws their marks, decodes the
pictures, and then repaints the whole page: it sets the body's background to
`#010203`, waits two animation frames, restores it and waits two more. The
comment says why: "Chromium otherwise keeps antialiased glyph edges just
outside a changed area." The earlier film page (`src/film.js`, until the
`react-stage` change) did this only for fresh poses, pictures and
source-only frames; its comment added that "the real source-only seek
differed at seven such pixels", and the `source-only-shots` and
`shot-transitions` evidence records the same effect on the code panel's
leftmost column after a second pose. Its plain model frames, where the
viewer's canvas, the marks and the titles changed, were never repainted, and
its replay proofs held for eight real episodes with the real viewer.
`react-stage` design D10 made the repaint unconditional, "simpler and
removes the only order dependence it guarded", and recorded the cost as a
risk: "a few animation frames per pose". The two findings of the proposal
measured it: 55.9 ms of a 150 ms pose on the fixture tour.

What the repaint protects is a property, not a mechanism: after a pose, the
page's pixels are those a whole-page raster of its present content would
give, whatever was drawn before. Chromium rasters only the areas a change
invalidates; where the invalidated area is smaller than what the old or new
content actually painted (a glyph's antialiased edge), pixels of the earlier
content survive. The whole-page repaint invalidates everything, so what
follows it is a fresh raster.

## Goals / Non-Goals

Goals: a pose waits for a repaint exactly when its content can leave pixels
of an earlier pose behind, and for nothing else; no pixel depends on the
order frames are posed in, as the existing proofs and a new one show.
Non-goals: those of the proposal.

## Decisions

### D1. The rule: a pose repaints when the page's drawn content changed

`setFrame` repaints when any of these holds, and otherwise returns without
waiting for an animation frame:

1. the frame is `fresh` (preview's proof poses, which compare the same
   instant drawn several ways);
2. a view was mounted, placed again after shots without it, or its box
   changed size on this pose (the canvas wait already ran; its intermediate
   frames were drawn with the marks of the frame before);
3. the page's content outside the pixels of its canvases differs from what
   it was at the page's last repaint.

"The page's content" is the serialized document
(`document.documentElement.outerHTML`): every element, attribute (inline
styles and classes included) and text node of the set, its slots and
elements, the view hosts and their mark layers, the chrome and the
transition layer. It is not the pixels a canvas holds, which the viewer
draws; a canvas is its own rectangle, and a change to its pixels invalidates
exactly that rectangle and leaves nothing outside it, which is why the old
page could leave every model frame unrepainted. The comparison is taken
against the content at the last repaint, not at the last pose, so a pose
that skips the repaint always stands on content a whole-page raster drew.

Why it keeps "a frame is a pure function of video time": by induction on
the poses of a session. After a repaint, the pixels are the fresh raster of
the present content plus the canvases' pixels. A pose that skips the
repaint has, by the rule, the same content as at that repaint; everything
Chromium re-rasters in between is the same content drawn at the same place
(React writes nothing for unchanged props; the marks are rebuilt identically,
synchronously, between two rasters), so the pixels are again the fresh raster
of that content plus the canvases' present pixels. Neither term depends on
the poses before. Every pose whose content differs repaints, as today.

`compose` and `composeMarkBlend` repaint every time, unchanged: they draw
new captures into the transition layer. The pose after a composition always
repaints, because it empties the transition layer, so its content differs
from the content at the composition's repaint.

### D2. The decision is taken after everything a pose draws

The comparison is made after the commit, the views, the marks and the
picture decodes, immediately before the repaint would start, and the
content is recorded again at the end of every repaint (of a pose or a
composition). Serializing the page cost 0.04 ms a pose on the tour (992
characters at its last frame), measured in the unchanged page.

### D3. The rule is observed through the animation frames a pose requests

A browser test wraps `requestAnimationFrame` in the page and counts what a
pose asks for: none when the same frame is posed again, none when a frame
of the view alone is posed at another instant, some when a title's words
change. No field is added to what `setFrame` reports, and the contract with
the renderer (`docs/movie-document.md`, "The stage") is unchanged: it does
not say that every pose repaints.

### D4. The refusal words

None: the change adds no refusal and changes none. The canvas wait's
refusal ("Viewer canvas does not fill its view") and its bound are
untouched.

## Alternatives considered

- **Always repaint** (today). Correct and simple; its cost is the finding.
- **The brief's type rule**: repaint for fresh poses, shown pictures, and a
  title or source whose text differs from the last pose. Rejected: it names
  the shipped kinds, so a project element's words (the *Cut and Advance*
  template draws its own), a mark's label moving with the model, or a set's
  masthead changing between shots would skip the repaint the glyph edges
  need; and a still held for seconds would repaint on every frame although
  nothing about it changes.
- **The old page's rule** (fresh, pictures, source-only). Rejected for the
  same reason, and the `react-stage` design dropped it as the one order
  dependence it guarded.
- **Repaint when anything mutated since the last repaint** (a
  `MutationObserver`). Rejected: the marks are rebuilt from nothing on every
  frame and the runtime rewrites the body's classes on every pose, so it
  would record a mutation on nearly every pose with the page unchanged.
- **A cheaper repaint** (one flip, fewer frames) or a repaint of the
  changed region only. Not taken: it changes a mechanism the proofs rest
  on, and the finding asks when a pose waits, not how. Recorded for a later
  change if the numbers ask for it.

## Risks / Trade-offs

- [Content the serialization does not see changes between frames: a shadow
  root, a scroll offset, a form control's value] → no shipped component and
  no fixture element uses one; the viewer is reached only through its
  canvas and the handle it declares. A component that draws text inside a
  shadow root would skip a repaint it needs. The exact-bytes incremental
  render proof and the replay proofs are the judge on the fixture; the
  real viewer's evidence is the re-render of *Cut and Advance*.
- [The saving depends on the film] → the fixture tour is dense with cues and
  saves least; the measured numbers are recorded in `evidence.md`, and the
  real film's are owed after the merge.
- [A skipped pose's screenshot sees a stale canvas] → the viewer renders
  synchronously in `setView`, as the old page's unrepainted model frames
  relied on; a screenshot captures a new compositor frame.

## Migration Plan

The stage bundle changes, so every film recaptures once. Rollback is
reverting the commit.

## Open Questions

None.
