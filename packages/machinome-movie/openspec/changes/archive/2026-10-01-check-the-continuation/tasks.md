## 0. Preconditions

- [x] 0.1 Base: branch `check-the-continuation` from `addition-warts` at
  `500ebca` (the merged cycles `exact-take-times`, `honest-provenance`,
  `serve-what-the-viewer-reads` and the `render-cost` investigation).
- [x] 0.2 The viewer bundle (API 29) passed by path in the environment for
  the Node suite's viewer layer, never written into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. Layer 3, the resolver (red first)

- [x] 1.1 Red: `test/take.test.mjs`: the counter's `nine`, resolved,
  carries `model.crossing` (join, duration, into, mark `nine`, step
  `step-3`, the take time its last frame in the dissolve poses, how far
  past) and the sentence verbatim; the take time it records is the one
  `frameAt` poses for the outgoing view on the join's last frame, and every
  frame of the join agrees with the rule; held at the mark it crosses
  nothing; with the mark `nine` removed (a step boundary, not a mark) it
  crosses nothing; a shot ending before a mark and running past it crosses
  it; a fade carries it only through its first half; a continuation that
  leaves the take is still refused with its words. Run, record.
- [x] 1.2 `src/movie.mjs` (D2 to D4, D7). Green.

## 2. Layer 2, the pin

- [x] 2.1 Red: `resolved/count.json` gains, by hand, the expected
  `crossing` on `nine` (one field on one shot); the registered-document
  test fails on the old resolver. Run, record.
- [x] 2.2 Green with 1.2; `scripts/pin-resolved.mjs count` then writes the
  same bytes as the hand-written pin (shown in evidence); `minimal` and
  `tour` unchanged.

## 3. Layer 8, `check` (red first)

- [x] 3.1 Red: `test/pipeline/movie-pipeline.test.mjs`: `check` of the
  fixture movie `count` prints the continuation line after the `Take:`
  line. Run cold, record.
- [x] 3.2 `bin/videomaker.mjs` prints each crossing's report. Green.

## 4. Records

- [x] 4.1 ADR-014 (TIMELINE), indexed.
- [x] 4.2 `docs/movie-document.md` ("Resolution": the resolved shot's
  `model.crossing`), `README.md` (the `check` line), `docs/declaring-a-movie.md`
  (a moving shot runs on through its join), `fixtures/README.md`,
  `CHANGELOG.md`, a clause in `docs/architecture-overview.md`; layer 9 pins
  for the README's words.
- [x] 4.3 Spec delta synced and the change archived with the CLI; the
  archive's work checked.

## 5. Proof

- [x] 5.1 The Node suite whole on the final content with the API 29 bundle
  selected; the Python suite whole; summaries quoted.
- [x] 5.2 The Curta case: the film's evaluated document with `read_23`'s
  model as the project's commit `1567439` declared it
  (`Take.run(5.2, "added_23")`), resolved against the film's cached
  narration in memory, nothing written in the project; the line that
  reports `read-23` quoted; the film's current document's crossings quoted.
- [x] 5.3 `evidence.md`: red-first output, suites, the Curta lines,
  findings, what was not done.

Implementation note (1 October 2026): 0.3 is left open: the planning commit
was made for the orchestrator's review, which is the campaign's gate and is
not claimed here. The test of 1.1 that holds the recorded take time to
`frameAt` was strengthened after its red to compare every frame of the
join, not only the last (`evidence.md`, "Layer 3").
