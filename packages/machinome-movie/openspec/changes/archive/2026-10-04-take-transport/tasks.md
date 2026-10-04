## 0. Preconditions

- [x] 0.1 Base: branch `take-transport` from `player` at `b86f88b`, which
  carries the campaign's plan and contract
  (`workflow/ongoing/player-campaign/plan.md`).
- [x] 0.2 The viewer bundle (API 29, sha256 `b5fcdb86…`), passed by path in
  the environment, never written into the repository.
- [x] 0.3 The orchestrator, as the campaign's ratification gate, ratified
  the planning artifacts by message on 4 October 2026, before the planning
  commit, with every resolution of the design standing; the take
  document's shape is stated in the spec.

## 1. Layer 4 (red first)

- [x] 1.1 Red: `transport/take.test.ts` (`attachMachine`'s refusals with no
  call made, `pose` with and without a view, up and field of view from API
  28, `bank()`; `attachTake` on `fixtures/documents/count.json`: duration,
  marks, each mark's recorded bank, clamping, mid-step `bankAt`, `time()`,
  refusals; `attachLoop`), `transport/clock.test.ts` (the timer clock with
  an injected `now` and scheduler; the audio clock on a fake element), and
  `tsc --noEmit -p transport/tsconfig.json` among the pure tests. Run,
  record (red by absence).
- [x] 1.2 `vitest.config.mjs`: the `stage` project runs
  `transport/**/*.test.ts`.
- [x] 1.3 `transport/viewer-handle.ts`, `transport/take.ts`,
  `transport/clock.ts`, `transport/tsconfig.json`, `src/take.d.mts`. Green.
- [x] 1.4 `stage/take.test.tsx`: `poseView` through a machine transport;
  `viewMachine`'s proofs moved to `attachMachine`'s.
- [x] 1.5 Mutation: the identity check removed from `attachMachine` turns
  layer 4 red; restored.

## 2. Layer 9 (red first)

- [x] 2.1 Red: `test/transport-boundary.test.mjs` (the import pin over every
  file of `transport/`, its checker's own refusals, the declaration's names
  against `src/take.mjs`'s exports); `test/memo.test.mjs` (every browser
  test's key reads `transport/take.ts` and `src/take.mjs`);
  `test/stage-types.test.mjs` (the second checkout copies `transport/`; the
  bundle names `videomaker/transport/take.ts` and `videomaker/src/take.mjs`).
  Run, record.

## 3. The stage and the bundle

- [x] 3.1 `stage/runtime.tsx` (D7), `stage/types.ts` (D2).
- [x] 3.2 `src/stage-build.mjs` (D8), `test/support/reach.mjs` (D8). Layer 9
  green.

## 4. Layer 5 (red first)

- [x] 4.1 Red: `test/browser/take.test.mjs`, `window.film.transport(key)`
  reports the frame's bank and identity, at a mark the recorded bank, and
  `null` on the tour's loop; `test/browser/transport.test.mjs` with
  `test/support/transport-bundle.mjs`, `attachTake` beside the double at
  every mark, restore then `setView`, A-B-A pixels. Run, record.
- [x] 4.2 Green; the existing layer 5 take proofs green through the
  transport.

## 5. Layer 6 (the API 29 bundle)

- [x] 5.1 `test/viewer/transport.test.mjs`: `attachTake` on the counter's
  export at every mark equal to the record, A-B-A bank and pixels;
  `attachLoop` on the seesaw's export A-B-A. The existing parity proofs
  green through the transport.

## 6. Records

- [x] 6.1 ADR-020 (STAGE), Proposed, indexed.
- [x] 6.2 `docs/stage.md` (the view row, the names of the bundle),
  `docs/movie-document.md` ("The stage": the pose through the transport,
  `transport(key)`), `docs/architecture-overview.md` (the stage paragraph,
  the pipeline, "What is changing"), `AGENTS.md` (layer 4),
  `CHANGELOG.md` (one bullet under `Unreleased`).

## 7. Proof

- [x] 7.1 The Node suite cold on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [x] 7.2 `evidence.md`: every run (command, counts, time, cold or memo),
  red-first output, mutations, findings, what was not done.

## 8. Not in this cycle

The pilot ordered the campaign to stop before sync: the baseline specs are
not synced, the change is not archived and ADR-020 stays Proposed until the
pilot has validated the player in the browser. Human review of the films
and publication are not part of this change.
