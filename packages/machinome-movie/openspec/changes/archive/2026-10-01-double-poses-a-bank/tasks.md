## 0. Preconditions

- [x] 0.1 Base: branch `double-poses-a-bank` from `addition-warts` at
  `500ebca` (`exact-take-times`, `honest-provenance`,
  `serve-what-the-viewer-reads` and `render-cost` merged).
- [x] 0.2 The viewer bundle: the API 29 bundle passed by path in the
  environment (`VIDEOMAKER_VIEWER_BUNDLE`), never written into the
  repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. Layer 5 (red first)

- [x] 1.1 `test/support/mark-on-a-take.mjs`: the three poses of design D2
  with the ring of D3, and the assertions of D4.
- [x] 1.2 Red: `test/browser/take.test.mjs` calls it with the fixture's
  double, unchanged; run cold, record the failing assertion.
- [x] 1.3 The double's `machine.follows` (D1) and its refusals; the
  fixture's take machine follows `units` over `[0, 9]`; the forged machines
  of `test/browser/take.test.mjs` name what they follow. A test of the
  refusals. Green, cold.

## 2. Layer 6

- [x] 2.1 `test/viewer/take.test.mjs` calls the same helper with the
  selected bundle; green, cold, with the bundle.

## 3. Records

- [x] 3.1 `AGENTS.md` (layer 5 and 6 lines), `fixtures/README.md`,
  `CHANGELOG.md`.
- [x] 3.2 No ADR (design D4); ADR-018 released.
- [x] 3.3 Spec delta synced and the change archived with the CLI; the
  archive's work checked.

## 4. Proof

- [x] 4.1 The Node suite on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [x] 4.2 `evidence.md`: red-first output, green at both layers, suites,
  findings, what was not done.

Implementation note (1 October 2026): 0.3 is left open: the planning commit
was made for the orchestrator's review, which is the campaign's gate and is
not claimed here. The CLI archived the change while 1.1 to 4.2 were still
unticked in this file (it warns and continues under `--yes`); they were
ticked here after the archive, with the work done before it.
