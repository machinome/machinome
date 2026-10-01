## 0. Preconditions

- [x] 0.1 Base: branch `honest-provenance` from `addition-warts` at
  `c8c6309`, the campaign's plan on `main` at 54d64d8.
- [x] 0.2 The viewer bundle (API 29), passed by path in the environment and
  to `--viewer`, never written into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. Layer 8, the Stage line (red first)

- [x] 1.1 Red: `test/pipeline/movie-pipeline.test.mjs`: `check` the tour,
  change only `videos/tour/stage.css`, `check` again; the two `Stage:`
  lines differ, the stylesheet's hash is the file's, the script's is
  unchanged. Run, record (red: the lines are identical).
- [x] 1.2 `bin/videomaker.mjs` prints both hashes (D7); the two existing
  `Stage:` patterns of the file follow. Green.

## 2. Layer 8, the trees (red first)

- [x] 2.1 Red: `test/pipeline/provenance.test.mjs` (and its `READS` entry):
  a YAML fixture project committed with its export and build ignored and
  its release links set; `check` and `render` on the command line clean,
  then `render` with an untracked `notes.txt` (dirty, not release-ready,
  the reason named, the same common key, no frame captured), then `check`
  and `preview` with a tracked file changed. Run, record.
- [x] 2.2 `src/provenance.mjs` (D1, D5); `src/render.mjs` (D2, D3, D4,
  D6); `bin/videomaker.mjs` (`check`'s lines). Green.
- [x] 2.3 `.gitignore`: `/WTs/` (D8).

## 3. Records

- [x] 3.1 ADR-015 (PIPELINE), indexed.
- [x] 3.2 `README.md` (`check`'s lines, the manifest, `releaseReady`),
  `docs/stage.md` (the `Stage:` line), `docs/architecture-overview.md`
  (`src/provenance.mjs`), `CHANGELOG.md`.
- [x] 3.3 Spec deltas synced and the change archived with the CLI; the
  archive's work checked.

## 4. Proof

- [x] 4.1 The Node suite on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [x] 4.2 `check` of the Curta film *Addition* from this worktree; its
  lines quoted, the project tree's state reported.
- [x] 4.3 `evidence.md`: red-first output, suites, findings, the common
  key, what was not done.
