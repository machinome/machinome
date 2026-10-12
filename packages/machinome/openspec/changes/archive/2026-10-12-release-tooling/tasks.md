## 1. Evidence baseline

- [x] 1.1 Record the base: `git -C <bench> log --oneline -3` shows this change's planning commit on the line's head the orchestrator names (40087800, or later with `join-movie` integrated); `git -C <bench> status --short` shows nothing else. Start `evidence.md` in this change with it.
- [x] 1.2 Record whether the movie has landed: `ls <bench>/packages/machinome-movie/machinome/movie/js/package.json <bench>/packages/machinome-movie/machinome/movie/js/package-lock.json` and the root `package.json`'s `workspaces`. If it has not, every line of design.md Decision 1 that names the movie is left out of the Makefile and recorded as such; the counts below then drop to fifteen members and 30 archives.
- [x] 1.3 Make the bench venv from the lock if the orchestrator has not: `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12`. Record the line's last suite count from the latest archived evidence on the line (do not rerun it here). One suite at a time, and none while another bench's suite runs (`pgrep -af "WTs/v0.9-joins-.*[p]ytest"`).
- [x] 1.4 Record the lint base as design.md probe 6 ran it, the glob expanded by a shell: `env -C <bench>/packages/machinome sh -c '<bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-*/machinome | wc -l'` and black's last line over the same paths.
- [x] 1.5 Confirm `<bench>/node_modules` is a directory of the bench, not a link (`test -d <bench>/node_modules -a ! -L <bench>/node_modules`); `npm ci` writes through a link into another checkout. If it is a link, stop and report.

## 2. Red first (nothing of the tooling exists yet)

- [x] 2.1 `tests/test_check_dist.py`, new (design.md Decision 12): loads `<repository>/scripts/check-dist` with `importlib.machinery.SourceFileLoader`; `test_the_script_parses`, `test_out_refuses_a_folder_that_is_not_empty`, `test_out_refuses_a_file`, `test_keep_copies_every_archive_flat`, `test_keep_refuses_two_archives_of_one_name`, `test_nothing_is_kept_when_a_check_fails`. Run it. Expected red: every test, `SyntaxError: '{' was never closed` (the module does not load; design.md probe 1).
- [x] 2.2 `tests/test_repository_layout.py` (Decision 12): `TheMakefileTest` with its seven tests and the Makefile-reading helpers of probe 8; `Makefile` out of `FRAMEWORK_ENTRIES`; `/.docs-venv/` in `test_the_root_ignores_the_benches_and_the_venv`; the CI tests in their new form (`test_every_job_calls_the_makefile` in place of `test_every_job_runs_from_the_package_directory`, the products read from `TESTED`, the dist job's `make check`, `test_the_test_job_builds_the_bundles_and_chromium_before_the_tests`, the dist job's Node before `make check`); the module docstring names the Makefile. Run the module. Expected red: every `TheMakefileTest` test (no root Makefile; the framework's present), the `.gitignore` test (`/.docs-venv/` absent), each CI test naming the command its job spells today. Green: every other test. Record each reason.
- [x] 2.3 `tests/test_docs_exports.py`: `ActionsDocsJobBuildsNothingTest` reading the docs job and the Makefile's `docs` recipe (Decision 12). Run the class. Expected red: no root Makefile, then (once it exists, task 4.4) the job's `pip install` and Sphinx lines and no `make docs`.
- [x] 2.4 `tests/test_release_records.py` (Decision 2): `released_version()` from `.bumpversion.cfg`; the core's `pyproject.toml` among the statements in place of the cfg; `test_the_bump_neither_commits_nor_tags`; the docstring. Run it. Expected red: `test_the_bump_neither_commits_nor_tags` (`commit`, `tag`). Then, on a scratch copy of the tracked tree whose cfg reads `current_version = 0.9.0` and whose manifests read 0.8.1, run the module there: `test_every_version_file_agrees_with_pyproject` fails naming `pyproject.toml` (at the base it named the cfg); record both runs.
- [x] 2.5 Run `tests/test_kernel_extras.py::KernelExtrasTest::test_ci_syncs_the_locked_workspace` (or the class holding it): green, before and after task 5.1.
- [x] 2.6 Record in `evidence.md` every red of 2.1 to 2.4 with its reason and each green this group expects.

## 3. `scripts/check-dist`

- [x] 3.1 The line `    },` after the viewer's row's `'commands'` line (Decision 10). Run `tests/test_check_dist.py`. Expected: `test_the_script_parses` green; the `--out` tests red (`TypeError: main() takes 0 positional arguments`, `AttributeError: ... 'keep'`). Record.
- [x] 3.2 `--out` as Decision 10 states: `import argparse`, `keep_out`, `keep`, `main(argv=None)`, the call to `keep` after the last smoke inside the temporary directory, the refusal's wording, the docstring's last paragraph. `git diff scripts/check-dist` shows no row of `SMOKES` changed but the brace. `<bench>/.venv/bin/flake8 --max-line-length=89 scripts/check-dist` from the root: 0 lines. `tests/test_check_dist.py`: green, under a second.
- [x] 3.3 By hand: `<bench>/.venv/bin/python <bench>/scripts/check-dist --help` prints the usage with `--out DIR`; with `--out` naming a scratch folder that holds one file it fails naming the folder in under a second.

## 4. The Makefile

- [x] 4.1 `<bench>/Makefile`, design.md Decision 1 verbatim (the movie's lines per 1.2). `git -C <bench> rm packages/machinome/Makefile`.
- [x] 4.2 `.bumpversion.cfg`: the lines `commit = True` and `tag = True` removed, nothing else. The root `.gitignore`: `/.docs-venv/` after `/dist/`.
- [x] 4.3 Run `tests/test_repository_layout.py`, `tests/test_release_records.py`: `TheMakefileTest`, the `.gitignore` test and the release-records tests green; the CI tests still red (group 5).
- [x] 4.4 The gate's reds after the file exists, each planted in the bench's Makefile, the module run, the plant removed and `git diff Makefile` against 4.1's text empty: a package dropped from `PACKAGES` (fails naming it); a product dropped from `TESTED` (fails naming it); `upload: dist` (fails naming the rule); `.venv` added to `CLEAN` (fails naming it); a target `sweep: ## ...` (fails naming it). Record each.
- [x] 4.5 From the bench root, PATH holding uv and npm: `make` (twelve lines), `make version` (0.8.1), `make test PKG=machinome-engine-brep` and `make test PKG=nope` (each message, make's exit 2), `make bump` and `make bump VERSION=0.8.1` (each refusal), `make -n upload` (prints the twine line, runs nothing). Never `make upload`. Record the outputs.

## 5. CI on the targets

- [x] 5.1 `.github/workflows/python-app.yml` as design.md Decision 11: the job defaults' working directory gone, every setup step unchanged, each job's commands the targets, the `build` job's tag check, `make dist` and `gh release create` with `dist/$GITHUB_REF_NAME/*`. `python -c "import yaml; yaml.safe_load(open('.github/workflows/python-app.yml'))"` parses it.
- [x] 5.2 Run `tests/test_repository_layout.py`, `tests/test_docs_exports.py`, `tests/test_kernel_extras.py`: green.

## 6. The records

- [x] 6.1 `CONTRIBUTING.rst` as design.md Decision 13: the setup, the tests, the pull-request step and the Deploying section by the targets; the install without uv kept; no `requirements.txt`, no `tox`. The layout gate's guide and link tests green.
- [x] 6.2 `HISTORY.rst`: the `Unreleased` bullet of Decision 13, verbatim, after the last bullet of the section (the movie's, if it has landed). `tests/test_release_records.py` green.
- [x] 6.3 `docs/architecture.md`: the "Repository layout" row of Decision 13.
- [x] 6.4 `docs/adrs/BUILD/ADR-192-the-repository-s-steps-are-the-targets-of-one-makefile.md`, Status Proposed, as Decision 13 outlines; its index entry under BUILD after ADR-191 (or after ADR-190 if the movie has not landed) in `docs/adrs/README.md`.
- [x] 6.5 The whole layout gate, the docs-exports, the release-records and the check-dist tests green.

## 7. Validation

- [x] 7.1 `make sync` from the bench root (after 1.5): record uv's resolved and installed counts, npm's, and `git -C <bench> status --short` afterwards (nothing new but this change's files).
- [x] 7.2 `make test` from the bench root, one process, output to a file under the scratch directory, after checking that no other bench's suite runs. Record, per package of `TESTED`, passed, skipped (each reason) and failed, and the whole time. Expected: no failure; the core's count the base's (1.3) with each test this change adds named (`tests/test_check_dist.py`, `TheMakefileTest`, the renamed CI tests, the release-records test).
- [x] 7.3 `make lint`: the counts of 1.4 (the movie's modules added if it landed), make's exit 2 as CI tolerates.
- [x] 7.4 `make docs`: exit 0; record the time; `make docs` again: exit 0.
- [x] 7.5 `make check`: both runs green; record each run's archive count (32 with the movie, 30 without) and the core's sdist and wheel entry counts of each; no `machinome-check-*` directory left under `$TMPDIR` or `/tmp`.
- [x] 7.6 `make dist` on the bench: refused, naming this change's uncommitted files (the guard's evidence); nothing built.
- [x] 7.7 The bump on a copy: the tracked tree copied under the scratch directory, made a Git repository of one commit, `make sync` there, then `make bump VERSION=0.9.0`. Record the files listed (design.md probe 3's twenty, the movie's three tables if landed, `package-lock.json`, the movie's own lock, `uv.lock`), that `git log` shows one commit and `git tag` nothing, and that `make version` prints 0.9.0. Nothing is written in the bench.
- [x] 7.8 The originating check, a dry release rehearsal: the tracked tree copied under the scratch directory, made a Git repository of one commit (a fresh clone's state), then `make sync && make test PKG=machinome && make docs && make dist`. Record the suite count, the archives in `dist/v0.8.1` (32 or 30, listed), `twine check --strict dist/v0.8.1/*` (all PASSED), that no archive holds an entry under `_build/` (`tar tzf` and `unzip -l` of each, grep `_build/`: 0), `make dist` again (refused, the folder not empty), `make -n upload` (the twine line), and `make clean` (the four paths gone; `.venv/`, `node_modules/` and `dist/v0.8.1/` still there; `git status --porcelain` empty). `make upload` is never run.
- [x] 7.9 Git: `git -C <bench> status --short` shows the Makefile and `tests/test_check_dist.py` and ADR-192 added, `packages/machinome/Makefile` deleted, and the edited files; nothing generated is tracked (`git ls-files -ci --exclude-standard | wc -l` equal to its count at 1.1).
- [x] 7.10 `env -C <bench>/packages/machinome openspec validate release-tooling --strict`.
- [x] 7.11 Stop before any commit and report to the orchestrator: the reds of group 2, 3.1 and 4.4, the counts of 7.1 to 7.8, and anything that departed from the design. Resume only on the orchestrator's message.

## 8. Records closing (after the orchestrator's review)

- [x] 8.1 ADR-192 promoted to Accepted; `docs/adrs/README.md` updated; ADR-182's and ADR-183's status lines and index lines note "amended by 192"; `docs/architecture.md` checked against it.
- [x] 8.2 Before the archive, confirm each MODIFIED requirement of the deltas equals the baseline at the bench's head plus this change's edits (design.md Decision 14), re-deriving it if the baseline moved. Then `env -C <bench>/packages/machinome openspec archive release-tooling -y` and `openspec validate --specs --strict` there.
- [x] 8.3 The root's `workflow/ongoing/release-0.9.md`: its Progress gains the entry for `release-tooling` (the branch, the planning commit, ADR-192, the counts of 7.2, 7.5 and 7.8), as the command seam's entry is written.
- [x] 8.4 `evidence.md` complete. The implementation commit and the integration into the line are the orchestrator's; the planning commit is never amended; nothing is pushed, tagged or uploaded.
