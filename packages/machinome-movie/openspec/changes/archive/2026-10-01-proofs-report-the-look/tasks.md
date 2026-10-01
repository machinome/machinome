## 0. Preconditions

- [x] 0.1 Base: branch `proofs-report-the-look` from `addition-warts` at
  `500ebca` (honest-provenance, serve-what-the-viewer-reads, exact-take-times
  and render-cost merged).
- [x] 0.2 The viewer bundle (API 29), passed by path in the environment and
  to `--viewer`, never written into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. Layer 5, the highlight's images (red first)

- [x] 1.1 Red: `test/browser/render.test.mjs`, the highlight test: the
  report's `highlights` lists under `pawl` the shot, the cue and the three
  images, which exist under `preview/highlights/`; the lit and unlit images
  are the captures; the difference's red pixels are exactly the pixels in
  which they differ, `changedPixels` counts them and `changedBox` holds
  them. Run cold, record.
- [x] 1.2 `src/pixels.mjs` (`differenceImage`, D4); `src/render.mjs`
  (preview's highlight loop, the directory, the names, the index; D1 to D3).
  Green.

## 2. Layer 5, the text the probe measures (red first)

- [x] 2.1 Red: `test/browser/layout.test.mjs`: `measureLayouts` given the
  tour's excerpts returns, per shot, the code's font size and the titles'
  lines; with the headline narrowed in the copy's `stage.css`, `Rise and
  fall` is on 3 lines and `Up. Down.` on 2. Run cold, record.
- [x] 2.2 `stage/runtime.tsx` (`fontSize`, `lines`, `subtitleLines`; D7);
  `src/code.mjs` (`wholeSource`); `src/layout.mjs` (the text frames and
  `textLines`; D6, D8). Green; the stage's jsdom tests still pass.

## 3. Layer 8, the commands' lines

- [x] 3.1 `test/pipeline/movie-pipeline.test.mjs`: the tour's `check`
  prints the text lines in one Chromium; a narrowed headline's `check`
  prints its wrapping; the clocked `count`'s `check` prints the not-measured
  line and launches no browser; its `preview` prints the highlight line.
  Red, then `bin/videomaker.mjs` (D5, D8). Green.

## 4. Layer 6

- [x] 4.1 `test/viewer/real-viewer.test.mjs`: the tour's preview with the
  real viewer lists its highlights under `Stand`, `Beam`, `Beam/Plank` and
  `Beam/Weight`, every image present and every count positive.

## 5. Records

- [x] 5.1 ADR-017 (PIPELINE), indexed.
- [x] 5.2 `README.md` (`check`'s text lines, `preview`'s highlight images),
  `docs/FORMAT.md` (the highlight proof's images), `docs/stage.md`
  (`check`'s text lines, what the shipped elements report),
  `docs/architecture-overview.md`, `CHANGELOG.md`; the manual pin in
  `test/repository.test.mjs`.
- [x] 5.3 Spec deltas synced and the change archived with the CLI; the
  archive's work checked.

## 6. Proof

- [x] 6.1 The Node suite on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [x] 6.2 `check` and `preview` of *Addition* from this worktree, the
  times noted, nothing in the project or its shared `_build/` written,
  restored or deleted: the project's head had moved past the film
  (evidence, finding 5), so on a scratch copy at the film's commit; preview
  twice, the second after D4a; the text lines and the pinion highlight's
  entries quoted.
- [x] 6.3 `evidence.md`: red-first output, suites, findings, what was not
  done.
