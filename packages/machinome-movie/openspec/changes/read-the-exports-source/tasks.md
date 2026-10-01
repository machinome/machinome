## 0. Preconditions

- [ ] 0.1 Base: branch `read-the-exports-source` from `addition-warts` at
  `500ebca`; the framework's `main` at 096217f (ADR-158, the export's
  `source`) installed in the workspace venv.
- [ ] 0.2 The viewer bundle (API 29), passed by path in the environment and
  to `--viewer`, never written into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. The fixture exports (D6)

- [ ] 1.1 `scripts/pin-fixture-project.mjs` exports each model from the
  recipe copy (`--machinome`, default `machinome`), replaces the fixture's
  export, refuses unless the manifest records the recipe revision clean,
  and writes no sidecar.
- [ ] 1.2 Run it with the workspace venv's `machinome` and `python`; the
  two manifests gain `source`; any document or resolved pin that moves is
  re-pinned and shown in the evidence.

## 2. Red first

- [ ] 2.1 Layer 1 (`python/tests/test_evaluation.py`, `test_take.py`):
  evaluation opens the manifest and no sidecar; an export whose manifest
  has no `source` is refused naming the manifest, `source.revision` and the
  remedy; the model block's revision is the manifest's. Run, record (red:
  the sidecar is opened, the refusal does not raise).
- [ ] 2.2 Layer 8 (`test/pipeline/movie-pipeline.test.mjs`): `check` of the
  `minimal` fixture movie whose manifest has no `source` is refused by
  name; with `source.revision` other than `model.sourceRevision`, refused
  naming both. Run, record (red: the sidecar is read and `check` passes).
- [ ] 2.3 Layer 8 (`test/pipeline/provenance.test.mjs`): the YAML fixture
  project's `check`, `render` and `preview` print the `Export:` line clean,
  then from an export marked dirty: the line, `exportRevision` and
  `exportDirty` in the manifest, the shots' origin and the preview report,
  the release issue, the same common key and no frame captured; an export
  without `source` refused by name. Run, record (red: no `Export:` line).

## 3. Green

- [ ] 3.1 `src/provenance.mjs`: `exportSource`, `pinnedRevision`,
  `exportLine`, `exportReleaseIssue` (D1 to D4).
- [ ] 3.2 `src/movie.mjs`, `src/episode.mjs`: the revision from the
  manifest, `film.exportSource` (D1, D3).
- [ ] 3.3 `src/render.mjs`, `bin/videomaker.mjs`: the `Export:` line, the
  provenance fields, the release issue, the common key without `source`
  (D4, D5).
- [ ] 3.4 `python/machinome_movie/evaluate.py`: the revision from the
  manifest, the refusal (D1, D2).
- [ ] 3.5 The sidecars deleted; `test/support/fixture-movie.mjs`,
  `test/support/yaml-project.mjs`, `test/project-fixture.mjs` and
  `python/tests/test_repository.py` read or write `source` (D6, D7).

## 4. Records

- [ ] 4.1 ADR-019 (SOURCE), indexed.
- [ ] 4.2 `README.md`, `docs/declaring-a-movie.md`, `docs/FORMAT.md`,
  `fixtures/README.md`, `docs/architecture-overview.md`, `CHANGELOG.md`;
  a layer-9 pin that the manual names no sidecar.
- [ ] 4.3 Spec deltas synced and the change archived with the CLI; the
  archive's work checked.

## 5. Proof

- [ ] 5.1 The Node suite on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [ ] 5.2 `check` of the Curta film *Addition* from this worktree: refused
  by name, its export having no `source`; the refusal quoted.
- [ ] 5.3 `evidence.md`: red-first output, suites, the fixture re-export,
  findings, what was not done.
