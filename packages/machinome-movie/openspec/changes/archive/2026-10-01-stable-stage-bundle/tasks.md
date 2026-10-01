## 0. Preconditions

- [x] 0.1 Base: branch `stable-stage-bundle` from `addition-warts` at
  `500ebca` (honest-provenance, serve-what-the-viewer-reads and
  exact-take-times merged).
- [x] 0.2 The viewer bundle (API 29), passed by path in the environment and
  to `--viewer`, never written into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. Before

- [x] 1.1 `test/pipeline/movie-pipeline.test.mjs` run cold on the base code
  with its fixture renders kept; the frame hashes of every shot generation
  recorded.

## 2. Layer 4, the bytes and the key (red first)

- [x] 2.1 Red: `test/stage-types.test.mjs`: the tour's stage built from two
  copies of the fixture tour at different depths, by this checkout and by
  a copy of the tool's `src/`, `stage/` and `package.json`, is the same
  bytes and names no machine path; the copy reuses the bundle this
  checkout built. Run, record the differing lines and the `reused`
  failure.
- [x] 2.2 `src/stage-build.mjs`: names (D1), the rewrite (D2), the key and
  `inputs.json` by name, reuse by name (D3). Green.
- [x] 2.3 A unit test of the rewrite over esbuild's escaped and singly
  quoted forms (written after 2.2; a guard, not a red-first proof).

## 3. After

- [x] 3.1 The same pipeline file run cold on the change with its renders
  kept; every shot generation's frame hashes equal to 1.1's.

## 4. Records

- [x] 4.1 ADR-013 (PIPELINE), indexed.
- [x] 4.2 `docs/stage.md` ("The same bytes from any checkout"),
  `README.md` (the shot cache key), `docs/architecture-overview.md`,
  `CHANGELOG.md`; the module's header comment; the layer 9 pin in
  `test/repository.test.mjs`.
- [x] 4.3 Spec delta synced and the change archived with the CLI; the
  archive's work checked.

## 5. Proof

- [x] 5.1 The Node suite on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [x] 5.2 `check` of the Curta film *Addition* from this worktree and from
  `WTs/addition-warts`: both refuse the film's document before the stage
  is bundled (the project's working tree moved under it; see evidence).
  The stage the film's `check` would build was therefore built with each
  checkout's `buildStage`, as `buildFilmStage` calls it, into build
  directories outside the project: this worktree, a second checkout of
  this change's content, and the campaign worktree. Nothing written in the
  project.
- [x] 5.3 `evidence.md`: red-first output, suites, frame hashes, the film,
  findings, what was not done.
