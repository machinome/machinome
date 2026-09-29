## 0. Preconditions

- [x] 0.1 Pilot ratifies this proposal (fields, default `keep`, no overlapping
  cues, the hidden-layer rule D3, format 0.3 and the shared gate D5).
- [x] 0.2 A machinome-viewer bundle declaring API 28 with `highlight` exists
  (the parallel viewer change); record its commit and hash. If its contract
  deviates from design.md's Context, stop and reconcile first.

## 1. Red tests (fail before any implementation; record the failures)

- [x] 1.1 `test/highlight.test.mjs` (new, Node only):
  - a 0.3 fixture passes validation; `frameAt` emits the active cue with layers
    resolved to paths, `others` and `color` explicit (defaults `keep` and the
    accent), `null` outside cues and after a cut;
  - refusals naming the shot: empty `parts`, unknown layer, path absent from
    the manifest, bare path written as layer names, `others: fade`, colour
    `red`, times outside the shot, overlapping cues, a highlighted part inside
    a hidden layer, `highlight` in a 0.2 episode;
  - `requiredViewerApi` is 28 with reason `highlight (shot <id>)`.
- [x] 1.2 `test/render.test.mjs`: a real-browser case with a viewer double
  declaring API 28 whose `highlight` records calls, changes the canvas colour
  and returns a `restore` that puts it back. Preview must pass D6 checks 2 and 3;
  the recorded calls show exactly one `highlight` and one `restore` per cue
  entry and exit in capture order, with `others` and `color` always passed. A
  double whose `restore` leaves the colour changed must fail the replay check.
  The same episode with the double at API 27 is refused with `/Viewer API 28/`.

## 2. Implementation

- [x] 2.1 `src/episode.mjs`: validate `highlight` (D1, D3, D4), paths through the
  manifest walk; add the shared format/requirement pieces if no sibling change
  has (see `annotate-a-part` D5).
- [x] 2.2 `src/timeline.mjs`: emit the active cue (D2).
- [x] 2.3 `src/film.js`: apply and restore by comparison with the applied cue,
  after visibility and before `setTime`/`setView`; refuse below the required API.
- [x] 2.4 `src/render.mjs`: preview's D6 checks and a sample at each cue's
  midpoint; failed comparisons keep their before/after images, as replay does.
- [x] 2.5 `docs/FORMAT.md`: a 0.3 section "Drawing attention to a part" with the
  D1 example, the list-of-lists rule, and the hidden-layer interplay beside the
  `hiddenLayers` paragraph. `README.md`: Viewer API 28 for highlighted episodes.
- [x] 2.6 `npm test` green; record red and green runs in `evidence.md`.

## 3. Consumer verification (implementation evidence)

- [ ] 3.1 In the Leonardo repository (committed there, never here), convert one
  *Revolutions* shot the pilot chooses from hiding to ghosting, the pawls shot
  being the proposed candidate, in format 0.3.
- [x] 3.2 `check` and `preview` with the API 28 bundle: record the D6 results and
  the stills of each cue; confirm the unchanged episodes still pass with the API
  27 bundle and the converted one is refused with it.

## 4. Human review (not claimed by automation)

- [ ] 4.1 The pilot judges whether the ghosted structure reads as translucent
  context and whether the tint draws the eye; automated checks prove only that
  the pixels changed and restored exactly.
- [ ] 4.2 Publication, pushing and final release renders need the pilot's
  explicit request.


Implementation note (29 September 2026): items 3.x marked done were run on a
scratch test episode against the current sawmill export, not in the Leonardo
repository, which this run was not permitted to change; see evidence.md. The
Leonardo authoring items and human review remain open.
