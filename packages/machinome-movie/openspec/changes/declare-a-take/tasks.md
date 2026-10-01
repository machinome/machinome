## 0. Preconditions

- [x] 0.1 Base: branch `declare-a-take` from `curta-video` at `4ecbc51`, which
  carries the take contract (`docs/movie-document.md`, "The take"; the
  schema's `take` block). The spike's note is not on the base; this change
  does not depend on it.
- [ ] 0.2 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit: the base (D1), how steps name the machine (D2), marks
  (D3), the recording (D5, D6), the document check and the replay (D7).

## 1. The fixture

- [ ] 1.1 `models/counter.py` and `models/digits.svg` copied from the
  framework tutorial with the header; `counter` in the fixture project's
  models table; `export/counter/` written by `machinome export counter -o
  export/counter --no-widget`.
- [ ] 1.2 `Turns(Take)` in `videos/takes.py`; `videos/count/movie.py`;
  `count` in the movies table and in `fixtures/manifest.json`.

## 2. Declarations (layer 1, red first)

- [ ] 2.1 Red: tests that a `Take` declares its steps, computes `at`,
  `length` and `marks`, resolves a `Driver` declaration and an instruction
  to the framework's names, and refuses by name every case of D2 and D3,
  and that a shot's model time outside the take is refused; run, record the
  failure.
- [ ] 2.2 `take.py`: `_Take`, `Loop`, `Take`, `Move`, `Trigger`, `Mark`;
  `stage.py` and `evaluate.py` ask for a take where they asked for a
  `Loop`; the package exports. Green.

## 3. Evaluation and the document check (layers 1 and 2, red first)

- [ ] 3.1 Red: the count movie evaluates to the take block (identity,
  initial, steps with the requests verbatim, banks), twice identically,
  reading no clock, randomness or network and building no CAD; a request
  the framework refuses and a step stopped before travelling are refused
  naming the step and the framework's words; an export without a clocked
  block is refused; the document check's take rules (D7) each refuse a
  mutated document by name, the replay included. Run, record the failure.
- [ ] 3.2 `evaluate.py` records the take through `Sim`; `document.py`
  checks take documents. Green.
- [ ] 3.3 The shared fixtures: `fixtures/documents/count.json` evaluated by
  the pin script, `fixtures/takes/count/` by the recipe, the five invalid
  documents of the design's refusal words; `scripts/pin-fixture-project.mjs`
  writes every export's revision; `minimal` and `tour` re-pinned and their
  resolved pins rewritten by `scripts/pin-resolved.mjs` and reviewed
  (`sourceRevision` only).
- [ ] 3.4 Show the new tests are not vacuous: remove the replay comparison,
  the stop refusal, the framework-refusal wrapping and the model-time check
  one at a time, run, record what fails, restore.

## 4. Records (layer 9)

- [ ] 4.1 ADR-011 (SOURCE), indexed in `docs/adrs/README.md`.
- [ ] 4.2 `docs/declaring-a-movie.md`: "The take, clocked" after "The
  take", its examples the fixture's own lines; what evaluation reads; the
  refusals. `README.md`'s status line; `fixtures/README.md`;
  `docs/architecture-overview.md`; `CHANGELOG.md`; pins of the new manual
  sentences and of the changelog bullet.
- [ ] 4.3 Spec deltas synced and the change archived with the CLI; the
  archive's work checked and repaired.

## 5. Proof

- [ ] 5.1 The Python suite green on the final content, its summary quoted.
- [ ] 5.2 The Node suite on the final content with the viewer bundle
  selected, its summary quoted, and each red named with its cause: the
  tests that load the registered `count` document and refuse the new
  invalid documents, red until `pose-a-take`.
- [ ] 5.3 `evidence.md` in the archived change: the red-first output, the
  mutations, the suites, the findings, and what was not done.

## 6. Owed, not claimed by automation

- [ ] 6.1 `pose-a-take` makes the Node side read the take document and
  turns the red of 5.2 green.
