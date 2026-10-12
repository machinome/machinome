## 0. Preconditions

- [x] 0.1 The orchestrator reviewed the planning commit 489e658 and ratified
  it, correcting D13 (install and use `jsonschema`).
- [x] 0.2 The contract page `docs/movie-document.md` and the validation
  film's draft source are read; deviations are recorded in design.md.

## 1. Package skeleton

- [x] 1.1 `python/pyproject.toml` (`machinome-movie` 0.0.0, depends on
  `machinome` and `jsonschema`), an empty `machinome_movie` package, installed editable into
  the workspace venv.
- [x] 1.2 The fixture project under `python/tests/fixtures/project/`: model,
  hand-written export, still, pyproject tables, `source-revision.txt`.

## 2. Red tests, innermost first (record each failure in evidence.md)

- [x] 2.1 Layer 1, declarations: every refusal of the spec's list, by name.
- [x] 2.2 Layer 1, evaluation: the draft's constructs map onto the document
  (D8, D9); twice byte-identical; no I/O beyond manifest, revision and
  pyproject, no clock, randomness or network; part paths refused against the
  export.
- [x] 2.3 Layer 1, command line: `list` and `evaluate`, and their refusals.
- [x] 2.4 Layer 2: every registered fixture document equals its movie's
  evaluation; every invalid fixture Python can refuse is refused naming its
  `must_mention`; the resolver-only ones are skipped with the reason.
- [x] 2.5 Layer 9: every emitted document validates against the schema
  with `jsonschema`; the fixture revision matches a
  reproducible commit of the fixture project; the manual page exists and is
  linked from the README.

## 3. Implementation

- [x] 3.1 Anchors and narration (D4).
- [x] 3.2 Take: `Loop`, `Camera`, `Layer`, `Source`, `Still`, `run`, `keys`,
  part resolution (D5, D7).
- [x] 3.3 Stage vocabulary: sets, slots, elements, actions, transitions (D2, D3, D8).
- [x] 3.4 `Chapter`, `Shot`, `Cue`, `Movie` and their class-creation refusals.
- [x] 3.5 Evaluation, canonical JSON, the document check (D6, D9-D12).
- [x] 3.6 Schema, validated with `jsonschema` (D13, as amended).
- [x] 3.7 Command line and project table (D14).
- [x] 3.8 Fixture movies, documents, invalid fixtures, `fixtures/manifest.json` (D15).
- [x] 3.9 Acceptance: the draft source, with D3's correction, evaluates
  against the real Leonardo export from a scratch copy that writes nothing in
  the project; record the result.

## 4. Records

- [x] 4.1 ADR-002 under `docs/adrs/SOURCE/`, listed in the index; promoted to
  Accepted at archive.
- [x] 4.2 `docs/declaring-a-movie.md`, linked from `README.md`.
- [x] 4.3 `docs/architecture-overview.md` gains the Python side.
- [x] 4.4 `CHANGELOG.md` with an `Unreleased` section and this change's bullet.
- [x] 4.5 Sync the baseline spec and archive the change; evidence.md carries
  the red-test chronology and the final run.

## 5. Human review (not claimed by automation)

- [ ] 5.1 The film itself: produced in the Leonardo repository by the
  campaign's cycle C once both changes are merged, and inspected by the pilot.

Implementation note (30 September 2026): 3.9 ran on a scratch copy of the
draft source with its paths made absolute, reading the real export and
writing nothing in the project; see evidence.md. 5.1 remains open.
