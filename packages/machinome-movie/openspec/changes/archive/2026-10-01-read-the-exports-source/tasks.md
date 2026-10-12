## 0. Preconditions

- [x] 0.1 Base: branch `read-the-exports-source` from `addition-warts` at
  `500ebca`; the framework's `main` at 096217f (ADR-158, the export's
  `source`) installed in the workspace venv.
- [x] 0.2 The viewer bundle (API 29), passed by path in the environment and
  to `--viewer`, never written into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. The fixture exports (D6)

- [x] 1.1 `scripts/pin-fixture-project.mjs` exports each model from the
  recipe copy (`--machinome`, default `machinome`), replaces the fixture's
  export, refuses unless the manifest records the recipe revision clean,
  and writes no sidecar.
- [x] 1.2 Run it with the workspace venv's `machinome` and `python`; the
  two manifests gain `source`; any document or resolved pin that moves is
  re-pinned and shown in the evidence.

## 2. Red first

(Run before section 1 and before any product code, on the fixtures as they
were; see `evidence.md`.)

- [x] 2.1 Layer 1 (`python/tests/test_evaluation.py`, `test_take.py`):
  evaluation opens the manifest and no sidecar; an export whose manifest
  has no `source` is refused naming the manifest, `source.revision` and the
  remedy; the model block's revision is the manifest's. Run, record (red:
  the sidecar is opened, the refusal does not raise).
- [x] 2.2 Layer 8 (`test/pipeline/movie-pipeline.test.mjs`): `check` of the
  `minimal` fixture movie whose manifest has no `source` is refused by
  name; with `source.revision` other than `model.sourceRevision`, refused
  naming both. Run, record (red: the sidecar is read and `check` passes).
- [x] 2.3 Layer 8 (`test/pipeline/provenance.test.mjs`): the YAML fixture
  project's `check`, `render` and `preview` print the `Export:` line clean,
  then from an export marked dirty: the line, `exportRevision` and
  `exportDirty` in the manifest, the shots' origin and the preview report,
  the release issue, the same common key and no frame captured; an export
  without `source` refused by name. Run, record (red: no `Export:` line).

## 3. Green

- [x] 3.1 `src/provenance.mjs`: `exportSource`, `pinnedRevision`,
  `exportLine`, `exportReleaseIssue` (D1 to D4).
- [x] 3.2 `src/movie.mjs`, `src/episode.mjs`: the revision from the
  manifest, `film.exportSource` (D1, D3).
- [x] 3.3 `src/render.mjs`, `bin/videomaker.mjs`: the `Export:` line, the
  provenance fields, the release issue, the common key without `source`
  (D4, D5).
- [x] 3.4 `python/machinome_movie/evaluate.py`: the revision from the
  manifest, the refusal (D1, D2).
- [x] 3.5 The sidecars deleted; `test/support/fixture-movie.mjs`,
  `test/support/yaml-project.mjs`, `test/project-fixture.mjs` and
  `python/tests/test_repository.py` read or write `source` (D6, D7).

## 4. Records

- [x] 4.1 ADR-019 (SOURCE), indexed.
- [x] 4.2 `README.md`, `docs/declaring-a-movie.md`, `docs/FORMAT.md`,
  `fixtures/README.md`, `docs/architecture-overview.md`, `CHANGELOG.md`;
  a layer-9 pin that the manual names no sidecar.
- [x] 4.3 Spec deltas synced and the change archived with the CLI; the
  archive's work checked.

## 5. Proof

- [x] 5.1 The Node suite on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [x] 5.2 `check` of the Curta film *Addition* from this worktree: refused
  by name, its export having no `source`; the refusal quoted.
- [x] 5.3 `evidence.md`: red-first output, suites, the fixture re-export,
  findings, what was not done.
