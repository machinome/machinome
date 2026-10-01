## 1. Pin the base

- [ ] 1.1 At the base commit (4d1440a, bench `curta-findings`), export the
  fixture project the new test builds (a `Solid2Node` `cube(1)` under
  `design/part.py`, every source file's mtime set to 1700000000 s, no Git)
  with `machinome export --no-widget`, from two different locations, and
  confirm the two manifests are byte-identical. Commit that manifest as
  `tests/fixtures/export_outside_a_repository.json` in the implementation
  commit.

## 2. Red first

- [ ] 2.1 Add `tests/test_export_source.py`, naming the finding (the clocked
  Curta film, Videomaker's `source-revision.txt`). Each case builds the
  fixture project in a temporary directory, with Git confined to it
  (`GIT_CEILING_DIRECTORIES`, no global or system configuration), and
  exports it through the real `machinome export` command in a subprocess:
  - a committed project: `source == {'revision': <HEAD>, 'dirty': False}`;
  - a modified tracked file: same revision, `dirty` true;
  - an untracked file: `dirty` true;
  - an ignored file and an earlier export's build directory: `dirty` false;
  - outside a repository: no `source`, bytes equal to the pinned manifest.
  In process: a repository with no commit and a `PATH` with no `git` give no
  record and log nothing.
- [ ] 2.2 Run the module on the unchanged code; quote the failures in
  `evidence.md` (the repository cases fail for the missing `source`; the
  non-repository case passes, proving the pin is the base's bytes).

## 3. Implement

- [ ] 3.1 In `machinome/core/export.py`, a private `_source_record(root)`
  running `git rev-parse --verify HEAD` and
  `git status --porcelain --untracked-files=normal` at `root` with
  `GIT_OPTIONAL_LOCKS=0`, returning `{'revision', 'dirty'}` or `None` on any
  nonzero exit or `OSError`.
- [ ] 3.2 In `export_node`, take the record once after clearing the keyframe
  and before the build, from `project_root(node.src)`, and add it as
  `manifest['source']` after `pieces` when it is not `None`.
- [ ] 3.3 Focused tests green: `tests/test_export_source.py`,
  `tests/test_export.py`, `tests/test_pieces.py`, `tests/test_markings.py`.

## 4. Records

- [ ] 4.1 `docs/concepts/publishing.rst`: the document line lists `source?`;
  "An export" says what `source` records and when it is absent.
- [ ] 4.2 `docs/project/changelog.rst`: one bullet under `Unreleased`.
- [ ] 4.3 ADR-158 (EXPORT) if the decision is confirmed architectural; the
  ADR index; `docs/architecture.md`'s export section.
- [ ] 4.4 Docs structure tests (`tests/test_docs_structure.py`,
  `tests/test_release_records.py`) green.

## 5. Prove and close

- [ ] 5.1 The whole suite once on the final content; quote its summary line.
- [ ] 5.2 The caller: export the Curta's `clocked_curta` from its real path
  `/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x` with this
  worktree first on `PYTHONPATH`, a build directory and an output directory
  under this worktree's ignored `build/`, writing nothing in the project;
  quote `source` beside `git -C <project> rev-parse HEAD` and
  `git -C <project> status --porcelain | wc -l`.
- [ ] 5.3 `openspec validate --strict`, archive with the CLI, write
  `evidence.md` in the archived change, commit.
