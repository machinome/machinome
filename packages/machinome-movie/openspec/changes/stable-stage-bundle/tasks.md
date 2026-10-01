## 0. Preconditions

- [x] 0.1 Base: branch `stable-stage-bundle` from `addition-warts` at
  `500ebca` (honest-provenance, serve-what-the-viewer-reads and
  exact-take-times merged).
- [x] 0.2 The viewer bundle (API 29), passed by path in the environment and
  to `--viewer`, never written into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. Before

- [ ] 1.1 `test/pipeline/movie-pipeline.test.mjs` run cold on the base code
  with its fixture renders kept; the frame hashes of every shot generation
  recorded.

## 2. Layer 4, the bytes and the key (red first)

- [ ] 2.1 Red: `test/stage-types.test.mjs`: the tour's stage built from two
  copies of the fixture tour at different depths, by this checkout and by
  a copy of the tool's `src/` and `stage/`, is the same bytes and names no
  machine path; the copy reuses the bundle this checkout built. Run,
  record the differing lines and the `reused` failure.
- [ ] 2.2 `src/stage-build.mjs`: names (D1), the rewrite (D2), the key and
  `inputs.json` by name, reuse by name (D3). Green.

## 3. After

- [ ] 3.1 The same pipeline file run cold on the change with its renders
  kept; every shot generation's frame hashes equal to 1.1's.

## 4. Records

- [ ] 4.1 ADR-013 (PIPELINE), indexed.
- [ ] 4.2 `docs/stage.md` ("Rebuilt by content"),
  `docs/architecture-overview.md`, `CHANGELOG.md`; the module's header
  comment.
- [ ] 4.3 Spec delta synced and the change archived with the CLI; the
  archive's work checked.

## 5. Proof

- [ ] 5.1 The Node suite on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [ ] 5.2 `check` of the Curta film *Addition* from this worktree and from
  `WTs/addition-warts`; the stage built from a second checkout of this
  change's content; the `stageSha256` values compared; nothing written in
  the project but its ignored `_build/`.
- [ ] 5.3 `evidence.md`: red-first output, suites, frame hashes, the film,
  findings, what was not done.
