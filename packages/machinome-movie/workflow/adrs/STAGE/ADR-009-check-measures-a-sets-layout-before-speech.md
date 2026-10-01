# ADR-009: `check` measures a set's layout before speech

Status: Accepted (OpenSpec change `check-measures-the-stage`, 30 September
2026). Refines [ADR-004](ADR-004-the-stage-is-a-react-template-that-owns-the-screen.md):
the stage still owns layout; `check` reads it from the stage.

## Context

ADR-004 made the template own the screen: a slot's box is whatever the set's
component and stylesheet make it, and nothing in Node knows it. The renderer
refuses, on every posed frame, a picture enlarged beyond its allowance and a
view that leaves the picture, against the box the stage reports, but
`check` could refuse neither for a movie document: it printed "enlargement
checked against its slot's box at preview and render". A YAML episode kept
both refusals at `check`, because its paper sets' boxes are fractions Node
knows. So a still too small for a project's plate was found only after the
narration had been bought and a browser opened for preview (wart 1 of "The
React stage", wart 6 of "Cut and Advance, version 2", `workflow/warts.md`,
30 September 2026; the ruling is the orchestrator's, fix-warts campaign).

## Decision

1. **When a movie document shows a picture, `check` measures the layout of
   every set kind its shots use**, once per kind, after bundling the stage
   and before reading any take, at the output size. A YAML episode and a
   document that shows no picture open no browser.
2. **It measures on the renderer's page, with a stub viewer.** One headless
   Chromium is served `src/film.html`, the movie's bundle and the stage
   config the renderer gives it (without media), and a `/viewer.js` whose
   `MachinomeViewer.mount` throws; each set is posed through
   `window.film.setFrame` with the frame of its first shot emptied of
   elements, so no view mounts. The runtime and the bundle are unchanged:
   nothing is measured by a code path the renderer does not pose through,
   and no film's bundle hash, a common input of every cached shot, moves.
3. **Per slot it measures three things:** the slot's box; the box a picture
   placed there gets (a box with the classes the stage gives a picture's
   element, so the set's rules and the stage's size containment apply);
   and whether the slot's box changes when every slot holds a block three
   times the frame's size. A slot whose box changes is **sized by what it
   holds**, and `check` leaves it, like a slot whose picture box is empty,
   to the live box at preview and render.
4. **`check` refuses what the trusted boxes let it refuse**, in the words
   YAML episodes are refused in: a raster picture whose peak enlargement
   (the fit's scale in the measured box times the largest zoom of its view
   keys) exceeds its allowance, before any take is read; and, once the
   takes resolve its times, a still's view that leaves the picture at any
   output frame of its cue, naming the shot and the video time. It prints
   one `Layout` line per set and each picture's peak and allowance.
5. **Preview and render do not use the measured boxes.** The live box judges
   every frame there, as before.

## Options considered

- **A probe entry in the runtime** (`window.film.layout(set)`). A second path
  through the page that could lay out differently, and a runtime change that
  would recapture every film for nothing drawn.
- **Mount the real viewer, requiring `--viewer` at `check`.** No view is
  placed to measure a layout, and a document's `check` needs no viewer
  bundle unless the movie needs API 28.
- **Compute the boxes in Node from the stylesheets.** A second layout
  engine beside the browser, against ADR-004.
- **Pose the frames of each picture's cue at `check`.** Exact for every
  layout, content-dependent ones included, but it needs the resolved times,
  so the takes, and a pose per frame: it is preview.
- **Give the measured boxes to the renderer as a project set's known
  layout.** The renderer compares an element's box, which a set may pad
  inside its slot, and the boxes would come from another page or another
  run; the live box already judges there.

## Consequences

- A still too small for its slot, in a project's set or a shipped one, is
  refused before `speech`; a view that leaves it, before preview.
- A movie that shows a picture pays one Chromium launch and one pose per set
  kind at `check`: on the fixture tour's four sets, `check` took a median
  1.96 s instead of 0.88 s, alternated on a machine loaded about 20; a movie
  without pictures pays nothing (0.74 s against 0.82 s, noise).
- When the probe runs, what the stage refuses at mount (a set the bundle
  does not register, slots that differ) is refused at `check` too; a movie
  without pictures still meets it at preview.
- The content test is a probe, not a proof: a layout that changes for other
  content than a large block, and not for that block, is trusted wrongly.
  The live check at preview and render still refuses on every frame, and a
  browser test pins the probe's boxes to a posed frame's for the shipped
  `frame` and `split` and the fixture tour's two sets.
- A set component must draw with no element in its slots, which the stage
  already requires of a slot a shot leaves empty.

## Amendment, 1 October 2026 (`reframe-join`, ADR-010)

A movie that comes in by a reframe is measured at `check` as one that shows
a picture is, and a reframe through a slot sized by what it holds is
refused there. Decision 5 is refined: preview and render still judge every
picture against the live box, and each of their sessions now measures, with
the same in-page function on its own page before its first frame, the slots
a reframe moves views between, whose boxes the reframe's frames carry
([ADR-010](ADR-010-a-reframe-is-a-join-that-moves-a-views-box-and-fades-the-rest.md)).
