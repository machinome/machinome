## 0. Preconditions

- [ ] 0.1 The orchestrator reviews this proposal adversarially after the cycle
  reports (ratification by review; both commits proceed without waiting).
- [x] 0.2 The contract page `docs/movie-document.md` and the validation
  film's draft source are read; deviations are recorded in design.md.

## 1. Package skeleton

- [ ] 1.1 `python/pyproject.toml` (`machinome-movie` 0.0.0, depends on
  `machinome`), an empty `machinome_movie` package, installed editable into
  the workspace venv.
- [ ] 1.2 The fixture project under `python/tests/fixtures/project/`: model,
  hand-written export, still, pyproject tables, `source-revision.txt`.

## 2. Red tests, innermost first (record each failure in evidence.md)

- [ ] 2.1 Layer 1, declarations: every refusal of the spec's list, by name.
- [ ] 2.2 Layer 1, evaluation: the draft's constructs map onto the document
  (D8, D9); twice byte-identical; no I/O beyond manifest, revision and
  pyproject, no clock, randomness or network; part paths refused against the
  export.
- [ ] 2.3 Layer 1, command line: `list` and `evaluate`, and their refusals.
- [ ] 2.4 Layer 2: every registered fixture document equals its movie's
  evaluation; every invalid fixture Python can refuse is refused naming its
  `must_mention`; the resolver-only ones are skipped with the reason.
- [ ] 2.5 Layer 9: every emitted document validates against the schema; the
  subset validator refuses unknown keywords and agrees with a full
  implementation when one exists; the fixture revision matches a
  reproducible commit of the fixture project; the manual page exists and is
  linked from the README.

## 3. Implementation

- [ ] 3.1 Anchors and narration (D4).
- [ ] 3.2 Take: `Loop`, `Camera`, `Layer`, `Source`, `Still`, `run`, `keys`,
  part resolution (D5, D7).
- [ ] 3.3 Stage vocabulary: sets, slots, elements, actions, transitions (D2, D3, D8).
- [ ] 3.4 `Chapter`, `Shot`, `Cue`, `Movie` and their class-creation refusals.
- [ ] 3.5 Evaluation, canonical JSON, the document check (D6, D9-D12).
- [ ] 3.6 Schema and the subset validator (D13).
- [ ] 3.7 Command line and project table (D14).
- [ ] 3.8 Fixture movies, documents, invalid fixtures, `fixtures/manifest.json` (D15).
- [ ] 3.9 Acceptance: the draft source, with D3's correction, evaluates
  against the real Leonardo export from a scratch copy that writes nothing in
  the project; record the result.

## 4. Records

- [ ] 4.1 ADR-002 under `docs/adrs/SOURCE/`, listed in the index; promoted to
  Accepted at archive.
- [ ] 4.2 `docs/declaring-a-movie.md`, linked from `README.md`.
- [ ] 4.3 `docs/architecture-overview.md` gains the Python side.
- [ ] 4.4 `CHANGELOG.md` with an `Unreleased` section and this change's bullet.
- [ ] 4.5 Sync the baseline spec and archive the change; evidence.md carries
  the red-test chronology and the final run.

## 5. Human review (not claimed by automation)

- [ ] 5.1 The film itself: produced in the Leonardo repository by the
  campaign's cycle C once both changes are merged, and inspected by the pilot.
