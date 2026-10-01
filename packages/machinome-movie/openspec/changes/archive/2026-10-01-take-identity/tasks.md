## 0. Preconditions

- [x] 0.1 Base: branch `take-identity` from `addition-warts` at `4833fef`;
  the framework's `main` at 096217f (`Sim.identity`) installed in the
  workspace venv.
- [x] 0.2 The viewer bundle (API 29), passed by path in the environment,
  never written into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. Red first

(Run before any product code; see `evidence.md`.)

- [x] 1.1 Layer 1 (`python/tests/test_take.py`): a copy of the fixture
  project whose counter changed its commit law since its export, and one
  whose state `tens` is renamed, evaluated by the command line, are refused
  naming `Take Turns`, `models.counter:Counter`, the export, both
  identities and `export the model again` (red: the first recorded, the
  second refused about `take.initial`). The faked stale-export test goes
  (D3).
- [x] 1.2 Layer 2 (`fixtures/invalid/take-initial-incomplete.json`): both
  runtimes refuse the count document without `tens` in `take.initial`,
  naming `take.initial`, `tens` and `every driver and state` (red in both:
  the old words).

## 2. Green

- [x] 2.1 `python/machinome_movie/evaluate.py` (`_record`): the identity
  from `sim.identity`, compared before the first step, refused by name
  (D1).
- [x] 2.2 `python/machinome_movie/document.py` and `src/movie.mjs`: the
  `take.initial` refusals in the rule's words (D2).

## 3. Records

- [x] 3.1 ADR-011 amended in place with a dated section; ADR-020 released.
- [x] 3.2 `docs/declaring-a-movie.md`, `docs/architecture-overview.md`,
  `fixtures/README.md`, `CHANGELOG.md`.
- [x] 3.3 Spec delta synced and the change archived with the CLI; the
  archive's work checked.

## 4. Proof

- [x] 4.1 The matching counter evaluates byte-identical to
  `fixtures/documents/count.json` (its take the recipe's
  `fixtures/takes/count/counting.json`): the fixture tests pass unchanged.
- [x] 4.2 The Node suite on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [x] 4.3 `evidence.md`: the identity probe, red-first output, suites,
  findings, what was not done (the Curta: nothing to prove until its export
  is made again).
