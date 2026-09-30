## 0. Preconditions

- [ ] 0.1 Base: branch `one-runner` from `react-stage` at `5dae43f`. Run the
  base suite once under `node --test` before any change and record count,
  time and failures in `evidence.md` (the intermittent
  `every incremental PNG equals a separately cold film across the first
  reused-shot gap` recorded if seen).
- [ ] 0.2 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit: the two projects and the slow list (D1), the seam (D3),
  one Chromium per run (D4), the key's inputs and what is left out of it (D5,
  D6), the artefact memo's uses (D7), the memo's place and the cold switch
  (D10), the ADR's category (D12).

## 1. Red tests (written before the code they prove; record each failure)

- [ ] 1.1 `test/memo.test.mjs` (layer 9, pure): every property of D11. Red:
  `test/support/memo.mjs` does not exist.
- [ ] 1.2 `test/browser-seam.test.mjs` (slow): launches counted; two sessions
  on the shared browser launch none, share one asset server origin and leave
  the browser connected; a session without one launches exactly one and closes
  it; a second mount of a standing asset server is refused naming it. Red: the
  seam does not exist (the injected browser is ignored and a launch counted).

## 2. Runner

- [ ] 2.1 `vitest.config.mjs` (D1), `scripts/test.mjs` (D10), `package.json`
  `test` script, `.gitignore` gains `.test-memo/`.
- [ ] 2.2 Convert every `test/*.test.mjs` and `test/project-fixture.mjs` (D2);
  the slow files take `test` from the memo and their browser entry points from
  `test/support/stage.mjs`.
- [ ] 2.3 `experiments/dark-source/README.md` says how to run its test.

## 3. Implementation

- [ ] 3.1 `src/render.mjs`: `CHROMIUM_ARGS`, `assetServer()`, the `browser` and
  `assets` options of `browserSession`, `preview` and `render` (D3).
- [ ] 3.2 `test/support/toolchain.mjs` (D4, D5), `test/support/stage.mjs` (D4),
  `test/support/one-browser.mjs` (D4).
- [ ] 3.3 `test/support/memo.mjs` (D6 to D9) documented at its head, and
  `test/support/memo-reporter.mjs` (D10).
- [ ] 3.4 The artefact memo applied to the review-pack fixture film, the
  render picture media and the pictures media fixture (D7).

## 4. Proof and records

- [ ] 4.1 Green: the whole suite cold (`npm test -- --cold`) with counts and
  time; then a warm run showing memo hits by name; then the honesty and seam
  tests' red-to-green recorded in `evidence.md`.
- [ ] 4.2 ADR-003 under `docs/adrs/RECORDS/`, Accepted at archive, listed in
  `docs/adrs/README.md`; `CHANGELOG.md` bullet; the `AGENTS.md` status
  sentence on the Node suite; `README.md` on running the tests; the
  architecture overview only if the runner appears in it.
- [ ] 4.3 Sync baseline specs and archive the change with the CLI.

## 5. Human review (not claimed by automation)

- [ ] 5.1 The pilot decides whether the slow files move to `test/browser/` and
  `test/pipeline/` in the next cycle, and whether per-test inputs are narrowed
  once the stage's tests exist.
