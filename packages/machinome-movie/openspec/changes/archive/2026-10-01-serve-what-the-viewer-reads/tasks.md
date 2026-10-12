## 0. Preconditions

- [x] 0.1 Base: branch `serve-what-the-viewer-reads` from `addition-warts`
  at `c8c6309` (the campaign's plan over `main` at 54d64d8).
- [x] 0.2 The viewer bundle: the API 29 bundle passed by path in the
  environment (`VIDEOMAKER_VIEWER_BUNDLE`) and to `--viewer`, never written
  into the repository.
- [ ] 0.3 The orchestrator, as the campaign's ratification gate, reviews the
  planning commit.

## 1. The collection, pure (red first)

- [x] 1.1 Move the extension walk of `stage()` verbatim into
  `src/export.mjs` (`exportFiles(manifestPath)`, returning the URL map),
  `stage()` calling it; behaviour unchanged.
- [x] 1.2 Red: `test/export.test.mjs`: the fixture exports `seesaw` and
  `counter` give exactly their `root` model and marking paths in order, with
  their fields, and the URLs the extension walk gave; a copy whose
  `pieces[0].sources` names an absent `.stl` gives the same files and no
  refusal; a lost model, a lost marking artifact and a model outside the
  export are refused naming the field, the node and the path, and saying
  to export again. Run, record.
- [x] 1.3 `viewerFiles` and `exportFiles` (D1, D2). Green.

## 2. Layer 8 (red first)

- [x] 2.1 Red: `test/pipeline/movie-pipeline.test.mjs`: `minimal` previewed
  and rendered from the command line over an export whose `pieces[0].sources`
  names `STLs/absent.stl`; then, with `Plank`'s model lost, `preview` and
  `render` refused naming the field, the node and the file, before any
  Chromium launches. Run on the base code (1.1 only), record.
- [x] 2.2 Green with 1.3.

## 3. Records

- [x] 3.1 `README.md` (what the loopback asset server exposes),
  `docs/architecture-overview.md` (`src/export.mjs`), `CHANGELOG.md`.
- [x] 3.2 No ADR (design D4); ADR-013 released.
- [x] 3.3 Spec delta synced and the change archived with the CLI; the
  archive's work checked.

## 4. Proof

- [x] 4.1 The Node suite on the final content with the API 29 bundle
  selected; the Python suite; summaries quoted.
- [x] 4.2 The film: in the Curta project's untracked export, the symlink
  `export/clocked_curta/STLs` moved aside, `check` and `preview` of
  *Addition* from this worktree with the bundle, the symlink put back
  exactly as it was; both outcomes recorded. Nothing committed in the
  project.
- [x] 4.3 `evidence.md`: red-first output, suites, the film, findings, what
  was not done.

Implementation note (1 October 2026): 0.3 is left open: the planning commit
was made for the orchestrator's review, which is the campaign's gate and is
not claimed here. The planning design said the shot-cache common key would
change only for exports whose provenance strings were served; it changes for
every film once, because the key hashes `src/render.mjs` (design D3,
implementation note; `evidence.md`, "The shot cache").
