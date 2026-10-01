## 0. Preconditions

- [x] 0.1 Base: branch `pose-a-take` from `curta-video` at `fae72ee`, which
  carries the take contract, `declare-a-take` (ADR-011), `reframe-join`
  (ADR-010) and the spike's note. The Node suite is red on that base on two
  tests of `test/movie-document.test.mjs` (no resolved pin for `count`; the
  take fixtures not refused by Node).
- [x] 0.2 The viewer bundle: the API 29 bundle of the viewer cycle
  `on-demand-clocked`, passed by path in the environment and to `--viewer`,
  never written into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. Layer 3 and the document checks (red first)

- [ ] 1.1 Red: `test/take.test.mjs`: the bank rule inside a step, at a step's
  end, at a mark, at the take's end and past it, a commit exactly at its
  fraction, two commits in one step, a step with no commit, the input at
  `end` exactly at `f = 1`, determinism; the replay check refusing a forged
  bank naming the mark and the id; `frameAt` on `count` giving `bank` and no
  `time`, marks resolved in take seconds; `check`'s take line. Run, record.
- [ ] 1.2 `src/take.mjs`; `checkMovie`'s take rules (D1); `viewState` (D4).
  Green; the five take fixtures refused by Node.

## 2. Layer 2

- [ ] 2.1 `scripts/pin-resolved.mjs count`, reviewed; the registered-document
  test green.
- [ ] 2.2 The load: a loop over a clocked export and a running program
  refused by name; a take document loads (`checkProject`).

## 3. Layer 4 (red first)

- [ ] 3.1 Red: `poseView` restores a bank through a stub machine with the
  take's identity, then sets the view, and never calls `setTime`; a loop
  view sets its time; `tsc --noEmit` over the types.
- [ ] 3.2 `stage/runtime.tsx`, `stage/types.ts`. Green.

## 4. Layer 5 (red first)

- [ ] 4.1 The viewer double's machine (D8).
- [ ] 4.2 Red: on `count` with the double, every view poses its frame's bank
  and reports it, A-B-A pixels across two banks, the bank at a mark; a
  double without a machine and one with another identity refused at mount
  naming the view; a forged request table refused before the first frame
  naming the step and the field; a canvas that follows a shrink late is
  waited for, and one that never follows refused, `Viewer canvas exceeds its
  view`. Run, record.
- [ ] 4.3 `src/render.mjs` (D6), the stage's canvas wait. Green.

## 5. Layer 6 (the API 29 bundle)

- [ ] 5.1 `test/viewer/take.test.mjs` over the counter's real export: the
  API, the replay against the recorded take, A-B-A across two banks, the
  banks at the marks, no viewer control shown, `count` through `check`,
  `preview` and `render`, a forged commit target refused naming the step and
  the field.

## 6. Layer 8 (red first)

- [ ] 6.1 Red: `count` through `check` (its take line), `preview` and
  `render` with the double, ffprobe. Run, record.
- [ ] 6.2 `bin/videomaker.mjs` prints the take line. Green.

## 7. Records

- [ ] 7.1 ADR-012 (STAGE), indexed.
- [ ] 7.2 `docs/stage.md` (a view on a take), `docs/movie-document.md` (the
  API sentence), `README.md`, `AGENTS.md` (status line and layer 6),
  `fixtures/README.md`, `docs/architecture-overview.md`, `CHANGELOG.md`, and
  the pins of what the manual tests read.
- [ ] 7.3 Spec deltas synced and the change archived with the CLI; the
  archive's work checked.

## 8. Proof

- [ ] 8.1 The Node suite on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [ ] 8.2 `evidence.md`: red-first output, suites, findings, what was not
  done.
