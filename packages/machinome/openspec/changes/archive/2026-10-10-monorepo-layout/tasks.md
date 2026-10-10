## 1. Evidence baseline

- [x] 1.1 Record the base: `git -C <bench> log --oneline -1` is the planning commit on top of 19c9f83b (or the line's head the orchestrator names), the worktree clean; start `evidence.md` in this change with it. After task 3.1 this change and its `evidence.md` live at `packages/machinome/openspec/changes/monorepo-layout/`.
- [x] 1.2 Record the tree: `git -C <bench> ls-files | wc -l` (expected 3340 plus this change's planning files), `git -C <bench> ls-files | cut -d/ -f1 | sort | uniq -c` (design.md, Context), and `git -C <bench> ls-files -ci --exclude-standard | wc -l` (expected 34, all `.log`). A different count is reported before any edit.
- [x] 1.3 Record the base suite count the orchestrator measured on the line head 19c9f83b, the same tree, with the workspace venv and `PYTHONPATH=<worktree>`: 4768 passed, 4 skipped, 6734 subtests, 849.82 s (10 October 2026). Do not rerun it. One suite at a time.

## 2. Red first, at today's paths (nothing moves in this group)

- [x] 2.1 Write `tests/test_repository_layout.py` (design.md, Decision 6, G1 to G8), with the SPDX header. Run it. Expected red: G1 naming the bench against `machinome/WTs/packages/machinome`, G2 and G4 to G8 on their first missing path under `machinome/WTs`; G3 green (it pins what the move keeps). Record each group's reason.
- [x] 2.2 `tests/test_docs_exports.py` (Decision 8): `PACKAGE` (today's `REPO`) and `REPOSITORY = parents[3]`; `WORKFLOW` at `REPOSITORY`; the Read the Docs install pin compares with the literal `packages/machinome/docs/requirements.txt`, a new `test_configures_the_framework_manual` pins `sphinx.configuration` to `packages/machinome/docs/conf.py`; the CI pins unchanged; `.gitmodules` read at `REPOSITORY`. Run it. Expected red: the three `ActionsDocsJobBuildsNothingTest` tests (`FileNotFoundError` on `machinome/WTs/.github/workflows/python-app.yml`) and the two Read the Docs path pins (the configuration names `docs/...`).
- [x] 2.3 Write the `Unreleased` section at the top of `HISTORY.rst` (at the root, where it stays) with the entry of proposal.md, verbatim. Run `tests/test_release_records.py` and `tests/test_profile_documentation.py`. Expected red: `test_the_history_top_entry_is_the_released_version` and `test_released_status_changelog_and_history`, each finding `unreleased` above the released heading (design.md, Decision 7).
- [x] 2.4 `tests/test_release_records.py`: `REPOSITORY = parents[3]`; `test_context7_states_the_release` reads `REPOSITORY / 'context7.json'`; the history pin admits one `Unreleased` heading above the first released heading and refuses the word anywhere else there, and a second such heading. Run it. Expected: the history pin green; `test_context7_states_the_release` red, `FileNotFoundError` on `machinome/WTs/context7.json`.
- [x] 2.5 `tests/test_profile_documentation.py`: the history line takes the same `replace('\nunreleased\n----------\n', '\n', 1)` its changelog line has. Run it: green.
- [x] 2.6 Record in `evidence.md` every red of 2.1 to 2.4 with its reason, and the greens of 2.4 and 2.5.

## 3. The move

- [x] 3.1 `mkdir -p packages/machinome`, then one `git mv` of the framework's code, suite, manual and records, which read each other: `git mv machinome tests docs openspec tools spike pyproject.toml setup.cfg tox.ini Makefile MANIFEST.in requirements.txt requirements_dev.txt README.rst CREDITS.md .gitignore .readthedocs.yaml packages/machinome/`. Check `git status` shows each as a rename and that this change's `evidence.md` moved with `openspec/`.
- [x] 3.2 The framework's working record: `mkdir -p packages/machinome/workflow/ongoing`, `git mv workflow/README.md workflow/warts.md workflow/archive packages/machinome/workflow/`, and `git mv` every entry of `workflow/ongoing/` but `monorepo-0.9.md` into `packages/machinome/workflow/ongoing/` (Decision 10). `workflow/ongoing/` then holds only the campaign note.
- [x] 3.3 The symlinks, from `packages/machinome/`: `ln -s ../../LICENSE LICENSE`, and the same for `LICENSES`, `HISTORY.rst`, `CONTRIBUTING.rst`, `AI-USE.md`; `git add` them. Check `git ls-files -s packages/machinome | grep ^120000` lists the five with those targets (`git cat-file -p` of each blob).
- [x] 3.4 Run the 42 path-reading test modules (design.md, Context) and the gate from `packages/machinome/` with the fallback recipe: `env -C <bench>/packages/machinome PYTHONPATH=<bench>/packages/machinome /home/asa/devel/machinome/.venv/bin/python -m pytest -q <modules>`. Expected: green but for the gate's G4 to G8 (the root files, the workflow's working directory and the prefixed `context7.json` not yet there) and `test_docs_exports.py`'s two Read the Docs path pins (the configuration not yet prefixed); the three CI tests and `test_context7_states_the_release` now green, since they read the root's unedited files. Anything else red is investigated before group 4.

## 4. The root files

- [x] 4.1 The root `.gitignore` (Decision 1, verbatim).
- [x] 4.2 The root `README.md` (Decision 1, verbatim).
- [x] 4.3 The root `pyproject.toml` (Decision 2, verbatim).
- [x] 4.4 The root `workflow/README.md` (Decision 10, verbatim), and the framework's `packages/machinome/workflow/README.md` gains its one sentence at the end of "Where this fits".
- [x] 4.5 `context7.json`: each of the seven `excludeFolders` prefixed with `packages/machinome/`, and `workflow` added; nothing else changes (Decision 9).
- [x] 4.6 `packages/machinome/.readthedocs.yaml`: the two paths prefixed, the comment stating that Read the Docs reads them from the repository root and that the project's configuration path is `packages/machinome/.readthedocs.yaml` (Decision 9). The two Read the Docs pins of 2.2 green.
- [x] 4.7 `.github/workflows/python-app.yml` (Decision 4): job-level `defaults.run.working-directory: packages/machinome` on `lint`, `test`, `browser-snapshot`, `docs` and `build`; every `cache-dependency-path` prefixed; the `dist` job, verbatim. Check it parses (`python -c "import yaml; yaml.safe_load(open(...))"`). The gate's G6 green and the three CI tests of 2.2 still green.
- [x] 4.8 `scripts/check-dist` (Decision 5), executable, with the SPDX header; `git add --chmod=+x` if the mode is not recorded.

## 5. The workspace environment

- [x] 5.1 `env -C <bench> /home/asa/.local/bin/uv lock`. Expected: about 185 packages resolved (probe 3), `uv.lock` at the root recording `source = { editable = "packages/machinome" }`. A failure naming a distribution no index serves is reported, not worked around beyond Decision 2's list.
- [x] 5.2 `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12`. Expected: `<bench>/.venv` with about 175 packages; `cat <bench>/.venv/lib/python3.12/site-packages/__editable__.machinome-*.pth` is `<bench>/packages/machinome`; `env -C /tmp <bench>/.venv/bin/python -c "import machinome, cadquery, build123d, manifold3d, molejo, solid2; print(machinome.__file__)"` prints the bench's file. If the sync cannot be made to work, stop this group, record the error, and validate group 7 on the fallback recipe; report it, do not hide it.
- [x] 5.3 The gate's G4 green.

## 6. The records

- [x] 6.1 `CONTRIBUTING.rst` at the root: the edits of Decision 9, in place; nothing added.
- [x] 6.2 `AI-USE.md` at the root: the one sentence of Decision 9.
- [x] 6.3 `packages/machinome/README.rst`: the one link of Decision 9; `ReadmeTest` and `LicenceWordingTest` green, the word count unchanged or lower.
- [x] 6.4 `packages/machinome/tests/test_docs_structure.py`: the `.gitmodules` check reads `REPOSITORY` (`parents[3]`). Its blind spot shown red first: with an empty `.gitmodules` planted at `<bench>/.gitmodules`, the check as it was passes (it reads the package directory) and the repointed one fails naming the file; record both, then remove the planted file. The same proof for `test_docs_exports.py::EmbeddedExportsAreCommittedTest::test_no_example_is_pinned` repointed in 2.2.
- [x] 6.5 `packages/machinome/docs/contributor-briefing.md`: the sentence of Decision 9 opening "Layout".
- [x] 6.6 `packages/machinome/docs/reference/api.rst`: the `cd packages/machinome` line of Decision 9.
- [x] 6.7 `packages/machinome/docs/architecture.md`: the identity sentence, the known gap and the Map row of Decision 9.
- [x] 6.8 `packages/machinome/docs/adrs/BUILD/ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md` (Decision 11), Status Proposed; the index entry under BUILD in `docs/adrs/README.md`.
- [x] 6.9 The gate's G7 and G8 green; the whole gate green.

## 7. Validation

- [x] 7.1 The whole suite, one process, from the package directory on the bench venv: `env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs`. Record passed, skipped (each skip's reason) and failed. Expected: no failure; probe 8 measured the moved tree on this recipe at 4748 passed and 20 skipped before this change's test edits, the 16 viewer skips among them (design.md, Context); the passed count is that plus probe 8's four failures turned green, the gate's tests and the new Read the Docs pin, each skip named. Then the same suite on the fallback recipe (`PYTHONPATH=<bench>/packages/machinome` with the workspace venv) if 7.1's skips differ from 1.3's by more than the viewer's tests.
- [x] 7.2 `env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests`; record the count against the base's (the CI step is `continue-on-error`, so the record is the comparison).
- [x] 7.3 The manual: a fresh venv under the scratch directory installing `packages/machinome/docs/requirements.txt` alone, then `env -C <bench>/packages/machinome <venv>/bin/python -m sphinx -b html -W docs <scratch>/html`. Expected: success, as the CI docs job runs it.
- [x] 7.4 `env -C <bench> <bench>/.venv/bin/python scripts/check-dist`. Expected: one member built, `twine check --strict` passed for both archives, each of the five linked entries found in the sdist as a regular file equal to the root's, the wheel installed with `[openscad,stl]` into a venv outside the repository, the version 0.8.1 printed, `License-Expression` and the three licence files listed, `machinome --help` exit 0, the last line saying nothing was uploaded. Record the archives' member counts (probe 4: sdist 1020, wheel 128) and `git -C <bench> status --short` afterwards (nothing new but ignored build leavings).
- [x] 7.5 Git: `git -C <bench> status --short` shows every moved file as a rename (`R`), the five links and the new root files as added; `git ls-files | wc -l` equals 1.2's count plus the root's `.gitignore`, `README.md`, `pyproject.toml`, `uv.lock`, `scripts/check-dist`, `workflow/README.md`, the five links and `tests/test_repository_layout.py`; `git ls-files -ci --exclude-standard | wc -l` is still 34.
- [x] 7.6 `env -C <bench>/packages/machinome openspec validate monorepo-layout --strict`.
- [x] 7.7 Stop before any commit and report to the orchestrator: the reds of group 2, the counts of 3.4, 5.1, 5.2, 7.1 to 7.5, anything that departed from the design. Resume only on the orchestrator's message.

## 8. Records closing (after the orchestrator's review)

- [x] 8.1 ADR-182 promoted to Accepted; `docs/adrs/README.md` updated; `docs/architecture.md` checked against it.
- [x] 8.2 `env -C <bench>/packages/machinome openspec archive monorepo-layout` (the deltas synced into `packages/machinome/openspec/specs/`), then `openspec validate --specs --strict` there.
- [x] 8.3 The root's `workflow/ongoing/monorepo-0.9.md`: cycle 1 marked done with its branch, the suite count of 7.1 and the check-dist result, as the lean-core plan recorded its cycles.
- [x] 8.4 `evidence.md` complete; the implementation commit is the orchestrator's, never amending the planning commit; nothing pushed.
