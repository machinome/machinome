## 0. Preconditions

- [x] 0.1 Base: branch `check-measures-the-stage` from `fix-warts` at
  `0fb4c2f` (`pose-repaints`, `viewer-instances`, `fixture-hygiene`,
  `narration-end-anchor` and `speech-key-lookup` merged).
- [x] 0.2 Measure `check` of the fixture tour from the command line before
  any change (seconds, on a copy of the fixture project with its takes), to
  compare with the same command after (evidence).
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit: when `check` measures (D1), the page and the stub (D2),
  what is measured and trusted (D3), the refusals and their order (D4), the
  report (D5), preview and render unchanged (D6).

## 1. Layer 8, red first

- [x] 1.1 In `test/pipeline/movie-pipeline.test.mjs`: the tour with its
  still's allowance lowered to 1.2 and no take cached is refused by `check`
  naming the still, the shot `still`, the peak 1.40× and the allowance, and
  no take is read; the tour with the still's first view key centred at
  (0.1, 0.5) is refused naming the shot `still` and its start, 16.67 s; the
  tour's `check` prints its `Layout` lines and `peak 1.40×; allowance 1.5×`
  for the plate; `check` of the fixture movie `minimal` (no picture)
  launches no Chromium, and the tour's launches one, counted by a hook
  imported into the command's own process. Run cold and record the
  failures.

## 2. The probe and the command

- [x] 2.1 ~~`src/pictures.mjs`: `enlargementRefusal` and `viewLeavesRefusal`,
  the YAML checks built on them with their wording unchanged.~~ Not done:
  `src/pictures.mjs` is a shot-cache key input (design D7, implementation
  note); the words are written in `src/layout.mjs` in the YAML wording.
- [x] 2.2 `src/layout.mjs`: `picturesShown`, `measureLayouts` (the page, the
  stub viewer, the empty frame per set, the three measurements of D3),
  `layoutLines`, `checkEnlargements`, `checkPictureViews`.
- [x] 2.3 `bin/videomaker.mjs`: on a document that shows a picture, measure
  after the bundle and refuse enlargements before `loadEpisode`; after it,
  refuse a view that leaves the picture; print the `Layout` lines and each
  picture's peak and allowance. The comments that say `check` has no
  browser say what is true.
- [x] 2.4 `test/support/reach.mjs`: `src/layout.mjs` reads `src/film.html`.

## 3. Layer 5

- [x] 3.1 `test/browser/layout.test.mjs`: on the run's one Chromium, the
  probe's boxes for `frame`, `split`, `playbill` and `playbill-split` at the
  tour's 1280×720 equal what a posed frame of each set reports at the same
  size (every trusted slot's box, and for `plate` the picture element's
  box); `headline`, whose box is as tall as the title it holds, is reported
  as sized by what it holds and is not compared. Run cold.

## 4. Proof

- [x] 4.1 The whole Node suite (`npm test`) and the Python suite on the
  final content, summaries quoted; the changed slow files run cold once.
- [x] 4.2 `check` of the tour before (0.2) and after, in seconds.

## 5. Records

- [x] 5.1 ADR-009 (STAGE): `check` measures a set's layout before speech;
  the ADR index.
- [x] 5.2 `docs/movie-document.md` (the frame's picture paragraph and the
  resolution steps), `docs/stage.md` (what `check` builds and measures),
  `README.md` (`check`), `docs/architecture-overview.md`, `CHANGELOG.md`
  under `Unreleased`.
- [x] 5.3 Sync the baseline specs and archive the change with the CLI;
  `evidence.md` in the archived change.

Implementation note (30 September 2026): 0.3 is left open: the planning
commit was made for the orchestrator's review before implementation, and
that review, the campaign's gate, is not claimed here.
