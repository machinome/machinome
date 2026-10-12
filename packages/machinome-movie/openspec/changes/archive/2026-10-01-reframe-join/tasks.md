## 0. Preconditions

- [x] 0.1 Base: branch `reframe-join` from `curta-video` at `ad8f444`
  (the campaign plan on `fix-warts` at `430d3af`).
- [ ] 0.2 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit: the frame of a reframe (D2), where the boxes come from
  (D3), the stage's host and fade (D4), the proofs (D5), the refusals (D6),
  the fixture (D7).

## 1. Declarations and the document (red first, layers 1 and 2)

- [x] 1.1 Red, layer 1: `Reframe(0.8)` declared on a shot evaluates to
  `{"kind": "reframe", "duration": 0.8}` (with `ease` when given); a
  direction or a colour on it is refused; two shots of one chapter that
  share no view are refused at chapter creation naming the chapter, both
  shots and `no view element in both`; a chapter's first shot coming in by
  a reframe is refused at movie creation naming both shots. Record the
  failure (`Reframe` does not exist).
- [x] 1.2 `python/machinome_movie/stage.py` (`Reframe`), `movie.py` (the
  two refusals), `document.py` (the kind and the refusal), `names.py` (the
  shared views and the refusal's words), `__init__.py`.
- [x] 1.3 Layer 2: the invalid fixture `reframe-without-a-shared-view`
  (`must_mention`: the chapter, both shots, `transition`, `no view element
  in both`) refused by both runtimes; `src/movie.mjs` gains the kind and
  the refusal; the unknown-kind refusal lists the reframe in both. (Made
  from the `minimal` document, the smaller one, with a second shot.)
- [x] 1.4 The fixture tour: `question` on `PlaybillSplit` (`right: wide`,
  `left: card`, `headline: title`) with `Reframe(0.8)`; the Python mapping
  test of `question` updated; `scripts/pin-fixture-project.mjs` and
  `scripts/pin-resolved.mjs minimal tour`, the diffs reviewed and recorded.

## 2. The frame (red first, layer 3)

- [x] 2.1 Red, layer 3, in a new `test/reframe.test.mjs` on an inline film
  with measured `reframes`: at the join's first frame the moving view's box
  is its outgoing slot's, at a quarter it is the eased interpolation, the
  other placed elements are named with nothing of the outgoing shot, the
  view's camera and model time are the incoming timeline's (a `move`
  running under the join), the same instant resolves twice to the same
  frame, past the join there is no transition; a film without `reframes` is
  refused naming the shot. Record the failure.
- [x] 2.2 `src/timeline.mjs`: `reframeAt`, the reframe branch of
  `transitionAt`, `joinShows`, `movingViews`, `noViewInBoth`; the
  continuation rules in `src/movie.mjs`, `src/timeline.mjs`,
  `src/render.mjs` and `bin/videomaker.mjs` read `joinShows`.
- [x] 2.3 `src/layout.mjs`: `reframesOf(doc)`, `reframeSets(doc)`,
  `reframeBoxes(doc, layouts)` (refusing a slot sized by what it holds),
  `measureSetsOn(page, doc, kinds)`, `reframeLines`; pure tests of
  `reframeBoxes` on an inline layout.

## 3. The stage (red first, layer 4)

- [x] 3.1 Red, layer 4, `stage/stage.test.tsx`: a frame carrying a reframe
  draws every element but the moving view at the progress's opacity and
  none at progress 1 or without one; `reframeHost` gives the host's inline
  box from the frame's box, snapped to 1/64 px, and clears it without a
  box. Record the failure.
- [x] 3.2 `stage/components.tsx` (`reframeOf`, the fade in `Slot`),
  `stage/runtime.tsx` (`reframeHost`, the host positioned in `poseViews`,
  the box, marks and canvas wait on the host, `opacity` reported during a
  reframe, React's emptied style attribute removed), `stage/types.ts`
  (`ReframeTransition`). `tsc --noEmit` clean.

## 4. In the browser (red first, layer 5)

- [x] 4.1 Red, layer 5, a new `test/browser/reframe.test.mjs` on the tour
  with the viewer double and with the late-canvas double: at the join's
  first frame `opening.wide` reports the box of `playbill`'s `stage` within
  a pixel; at its end, posed at progress 1, the box of `playbill-split`'s
  `right` and pixels identical to the incoming frame without a join; at the
  midpoint the tally and title report the eased progress as opacity, the
  canvas fills the moving box, the headline is drawn above the view, and
  A, B, A give identical pixels. Record the failure. Measure, with the
  late-canvas double, the time per reframe frame against a frame of the
  same shot after the join, and record it.
- [x] 4.2 `src/render.mjs`: reframe frames posed live, the per-frame checks,
  the session's measurement before its first frame; existing tests updated
  for the tour's new `question` (the layout test's sets and slots, the
  preview test's transition checks).

## 5. The pipeline (red first, layer 8)

- [x] 5.1 Red, layer 8: `check` on the tour prints the `Reframe` line and
  the sets in their new order; `preview`'s report has a `reframe`
  transition check for `question` with the first-frame and end boxes, the
  midpoint opacities, the end's pixel equality and the replay; the render
  and its second, cached render pass. Record the failure.
- [x] 5.2 `src/render.mjs` (`preview`'s reframe proof), `src/layout.mjs`
  (`reframeLines`), `bin/videomaker.mjs` (measure for a reframe, refuse,
  print, attach).
- [x] 5.3 A layer 8 refusal: a reframe into a slot sized by what it holds
  is refused by `check` before any take, naming the shot, the view, the
  set and the slot.

## 6. The real viewer (layer 6, gated on the selected bundle)

- [x] 6.1 With the selected bundle: every frame of the tour's reframe, and
  of the same span after it, fills the moving box with the real viewer's
  canvas, and A, B, A give identical pixels; the time per reframe frame
  recorded. (Written after the renderer change; not a red-first proof.)

## 7. Records

- [x] 7.1 ADR-010 (STAGE), indexed; ADR-009 amended in place;
  `docs/declaring-a-movie.md` (the chapter example, the joins, the
  refusals), `docs/stage.md` (a reframe, the view's host, a clipping slot,
  `check`'s line, the renderer's checks), the `transition` sentence of
  `docs/movie-document.md`, `fixtures/README.md` (refusal words),
  `docs/architecture-overview.md`, `README.md` (the proofs), `CHANGELOG.md`.
- [x] 7.2 The Node suite with `VIDEOMAKER_VIEWER_BUNDLE` selected and the
  Python suite on the final content, summaries quoted; the slow files this
  change touches run cold.
- [x] 7.3 `openspec archive reframe-join --yes`; the synced baseline specs
  checked; `evidence.md` in the archived change (red output, suite
  summaries, the per-frame cost, findings, what was not done).
