## 0. Preconditions

- [x] 0.1 Pilot ratifies this proposal (fields, anchor rule D2, strict
  off-screen refusal D4, format 0.3 and the shared gate D5).
- [x] 0.2 A machinome-viewer bundle declaring API 28 with `partOnScreen` and
  `project` exists (the parallel viewer change). Record its commit and hash.
  If its contract deviates from design.md's Context, stop and reconcile first.

## 1. Red tests (fail before any implementation; record the failures)

- [x] 1.1 `test/annotations.test.mjs` (new, Node only):
  - a 0.3 fixture with an arrow on a path and a label on a layer passes
    `validateEpisode`; `frameAt` emits the arrow only inside `[from, to)`, with
    the layer resolved to its paths and the safe inset attached;
  - each D4 check-time refusal throws a message naming the shot: unknown kind,
    both/neither target, unknown layer, path absent from the manifest,
    non-finite point, times outside the shot, arrow without `place`, `place`
    out of range, label without text, `offset` out of range, target inside a
    hidden layer, missing `safeInsetFraction`, `annotations` in a 0.2 episode;
  - `requiredViewerApi` is 28 with reason `annotations (shot <id>)` for the
    fixture and 21 for the existing `test/workflow.test.mjs` fixture;
  - the declared-API reader returns 27 for a file whose banner says
    `viewer API 27` and refuses a banner-less file only when 28 is required.
- [x] 1.2 `test/workflow.test.mjs`: add "0.2 episodes are unchanged" — the
  existing fixture's frames at 0, 1, 2 and 3 s deep-equal the pre-change values
  (pin them literally), and a 0.2 fixture with `annotations` is refused.
- [x] 1.3 `test/render.test.mjs`: a second real-browser case with a viewer double
  declaring API 28 whose `partOnScreen` rect moves with `setTime` and whose canvas
  is a flat colour. Preview must pass; the returned anchors at two instants of
  the cue differ and each lies inside that instant's rect; the screenshot pixel
  two pixels back along the shaft from the tip has the accent colour; pixel
  replay is exact. The same episode with the double declaring API 27 is refused
  with `/Viewer API 28/`; a double whose rect goes null mid-cue is refused with
  `/not on screen/` and the shot id.

## 2. Implementation

- [x] 2.1 `src/episode.mjs`: accept format 0.3; validate `annotations` (D1, D4);
  check annotation paths in `loadEpisode` with the existing manifest walk; add
  `requiredViewerApi(e)` and the bundle banner reader (D5), unless a sibling
  change already added them.
- [x] 2.2 `src/timeline.mjs`: emit active annotations with resolved targets (D3).
- [x] 2.3 `src/film.html`, `src/film.js`: `#annotations` SVG layer; refuse on
  mount below the required API; resolve anchors after `setView`; draw; return
  geometry from `setFrame`.
- [x] 2.4 `src/render.mjs`: pass the requirement to the page; in `pose`, refuse
  off-screen anchors and escaping text; preview samples each annotation's start,
  midpoint, end and its quarter/three-quarter instants; record the requirement
  in the build manifest and any new module in the frame identity.
- [x] 2.5 `bin/videomaker.mjs`: `check` applies the declared-API refusal.
- [x] 2.6 `docs/FORMAT.md`: a 0.3 section "Pointing at parts" with the D1 example,
  the safe-area units, the anchor rule, the refusals, and the sentence "These are
  screen labels, not world-tracked annotations" replaced for 0.3. `README.md`:
  Viewer API 28 is required for annotated episodes; `preview`'s new checks.
- [x] 2.7 `npm test` green; record red and green runs in `evidence.md`.

## 3. Consumer verification (implementation evidence)

- [ ] 3.1 In the Leonardo repository (committed there, never here), author
  annotations on one *Revolutions* shot the pilot chooses, the pawls shot being
  the proposed candidate, in format 0.3.
- [x] 3.2 `check`, then `preview` with the API 28 bundle: record that each
  arrow's anchor lies inside the part's rect at two different instants of a
  moving pawl, the exact replay result, and the stills. Confirm the unchanged
  *Revolutions* and sawmill episodes still pass `check` and `preview` with the
  API 27 bundle, and that the annotated one is refused with it.
- [x] 3.3 Render a short silent clip of the annotated shot (`--width 960 --fps 10
  --silent`) for motion review; record its hash in `evidence.md`.

## 4. Human review (not claimed by automation)

- [ ] 4.1 The pilot judges legibility, placement and whether the tip's motion is
  steady enough (design Open Question D2). Automated checks prove position and
  reproducibility, not readability.
- [ ] 4.2 Publication, pushing and final release renders need the pilot's
  explicit request; nothing here implies them.


Implementation note (29 September 2026): items 3.x marked done were run on a
scratch test episode against the current sawmill export, not in the Leonardo
repository, which this run was not permitted to change; see evidence.md. The
Leonardo authoring items and human review remain open.
