## 0. Preconditions

- [x] 0.1 Base: branch `viewer-integration-layer` from `fix-warts` at
  `0fb4c2f` (`pose-repaints`, `viewer-instances`, `fixture-hygiene`,
  `narration-end-anchor`, `speech-key-lookup` merged). Probes recorded in
  `design.md`: vitest's per-project workers and global setups; the real
  bundle on the exported seesaw (`check` reads API 28; `preview` refuses a
  highlight on an uncoloured part, and passes once the block declares a
  colour).
- [ ] 0.2 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit: the real export replacing the hand-written one (D1), the
  project and the one Chromium (D2), the gate (D3), the key (D4), what the
  layer proves (D5), the red runs (D6).

## 1. The real export

- [ ] 1.1 `models/seesaw.py`: rest placement, `Time(loop=20)`, the beam's
  tipping, the block's colour, lines 22 to 24 unchanged.
- [ ] 1.2 `machinome export seesaw -o export/seesaw --fps 30 --frames 600
  --no-widget` from the fixture project; `videos/takes.py`'s readiness; the
  re-pin (`scripts/pin-fixture-project.mjs`, `scripts/pin-resolved.mjs`),
  pins reviewed; the readiness in `python/tests/test_evaluation.py` and in
  `docs/declaring-a-movie.md`.

## 2. The gate and the key (red first, pure)

- [ ] 2.1 Red: in `test/memo.test.mjs`, a selected file is keyed by its
  content under its variable's name (other bytes miss, the same bytes at
  another path hit); a skip is never recorded; the memo reporter lists a
  skip by its note and counts it neither passed nor run; the gate's three
  outcomes name the note or the path; `reach.mjs` names the selected bundle
  for `test/viewer/` files only. Record the failures.
- [ ] 2.2 `test/support/reach.mjs` (`SELECTED`, `selectedInputs`),
  `test/support/memo.mjs` (named inputs in the key), `test/support/viewer-bundle.mjs`
  (`viewerTest`, the gate), `test/support/memo-reporter.mjs` (skips).

## 3. The project

- [ ] 3.1 `vitest.config.mjs`: the `viewer` project; the pure project
  excludes `test/viewer/`. `test/support/toolchain.mjs`: one Chromium for
  every project of the run, the browser's PID provided.
- [ ] 3.2 The tripwire test covers `test/viewer/`.

## 4. The layer (red first where a real failure can be shown)

- [ ] 4.1 `test/viewer/real-viewer.test.mjs`: the tests of design D5.
- [ ] 4.2 Red: the layer on the hand-written export (the fixture project's
  base content); the canvas test with the stage's canvas wait disabled
  locally, then restored. Record the failures.
- [ ] 4.3 Green with the bundle; the layer cold; the memory numbers.

## 5. Proof and records

- [ ] 5.1 The whole Node suite with and without the bundle, the Python
  suite; summaries and the skips verbatim in `evidence.md`.
- [ ] 5.2 ADR-008 (RECORDS) and its index row; `AGENTS.md`'s sentences about
  layer 6; `README.md`; `docs/architecture-overview.md` if it lists the
  layers; `CHANGELOG.md` under `Unreleased`.
- [ ] 5.3 Sync the baseline specs and archive the change with the CLI;
  `evidence.md` with the export's provenance.

## 6. Human review (not claimed by automation)

- [ ] 6.1 The pilot looks at a frame of the tour on the real viewer (the
  storyboard of the layer's preview) and decides whether the fixture's
  framing is worth a camera change; the fixture's cameras were written for
  the hand export and frame the seesaw small.
