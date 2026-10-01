## 0. Preconditions

- [x] 0.1 Base: branch `exact-take-times` from `addition-warts` at
  `c8c6309` (the campaign's plan on `main` at 54d64d8).
- [ ] 0.2 The viewer bundle (API 29) passed by path in the environment for
  the Node suite's viewer layer, never written into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. Layer 1, Python (red first)

- [ ] 1.1 Red: `python/tests/test_take.py`: a take of three moves of 1.2 s
  has its steps at 0, 1.2 and 2.4, its marks at 1.2, 2.4 and 3.6 and its
  length 3.6, on the class and in the evaluated document, exactly. Run,
  record.
- [ ] 1.2 `names.py` (`exact`, `written`), `take.py` (`Take._time`). Green.

## 2. Layer 2, the shared fixtures (red first)

- [ ] 2.1 Red: `fixtures/invalid/take-mark-summed-in-floats.json` (three
  steps of 1.2 s, the last mark written `3.5999999999999996`), must mention
  `marks.ten` and `end of a step`; Python's document mutations for a float
  `at` and a float length. Run both suites' fixture tests, record.
- [ ] 2.2 `document.py` (`check_take`) and `src/movie.mjs` (`checkTake`)
  hold the sums exactly (D2). Green; every registered document still
  validates; no pinned document changes (if one does, re-pin with
  `scripts/pin-fixture-project.mjs` and show the diff in evidence).

## 3. Layer 3, Node (red first)

- [ ] 3.1 Red: `test/take.test.mjs`: on an inline take of four steps of
  1.2 s whose fourth has a commit at fraction 0, the bank at the mark 3.6
  is the one the third step ended with; the mark's step is found;
  `markAt` is exact; `check`'s take line gives `3.6 s long`. Run, record.
- [ ] 3.2 `src/take.mjs` (D3), `src/timeline.mjs`. Green.

## 4. Records

- [ ] 4.1 ADR-016 (SOURCE), indexed.
- [ ] 4.2 `docs/movie-document.md` (the one sentence in "The take"),
  `docs/declaring-a-movie.md`, `fixtures/README.md`, `CHANGELOG.md`.
- [ ] 4.3 Spec deltas synced and the change archived with the CLI; the
  archive's work checked.

## 5. Proof

- [ ] 5.1 The Node suite whole on the final content with the API 29 bundle
  selected; the Python suite whole; summaries quoted.
- [ ] 5.2 The Curta film's movie evaluated from this worktree into a
  scratch file, nothing written in the project; its marks and steps
  compared with the document the film was rendered from.
- [ ] 5.3 `evidence.md`: red-first output, suites, the film's check,
  findings, what was not done.
