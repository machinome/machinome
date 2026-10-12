## 1. Evidence baseline

- [x] 1.1 Record the base: `git -C <bench> log --oneline -1` is the planning commit on the line's head the orchestrator names (after `join-viewer` and `join-skills`), the worktree clean but this change; start `evidence.md` in this change with it.
- [x] 1.2 Record the bench venv the orchestrator synced from the lock (the `__editable__` `.pth` files; no `machinome_movie` importable) and the base counts the orchestrator names for that head without rerunning them: the suite, the lint, the last sweep, `check-dist`'s archives.
- [x] 1.3 Compare this change's MODIFIED requirement (`specs/framework-identity/spec.md`, "Extras select independent Machinome products") with the baseline's at the bench's head: it must equal the baseline plus the movie's sentence, the `movie` names in "The extras keep the Machinome name under a version floor" and the scenario "A user installs the movie extra" (design.md Decision 18). If the baseline moved otherwise, re-derive the requirement from it with those three edits and record the diff; if a scenario title would change, stop and report.
- [x] 1.4 Record the probes of design.md the cycle relies on, by reference: 1 (677 files; 83322ce, a36e32f, ca99a77; no path outside `packages/`), 3 (the reds of the join), 4 (298 at the original layout; 22, 11, then 9 at the new place), 5 (the re-pin), 7 and 8 (the shallow layout; 493 passed, 12 failed of 505), 10 (the member lock), 11 (the installed case), 12 (the seam's reds), 13 (197 packages on the viewer's line), 14 (the timings), 15 (vet), 16 (the projects), 17 (the deltas archived).

## 2. The join (the orchestrator's, after the planning commit)

- [x] 2.1 The orchestrator clones `file:///home/asa/devel/machinome/videomaker` fresh under the scratch directory, makes `live-audio-mixer` and `record-review` local branches from `origin/`, and runs the `git filter-repo` command of design.md Decision 2 in it; `git ls-tree -r --name-only main` lists the 677 paths of `<scratch>/rehearsal-ls-files.txt`, `main` is 83322ce, `live-audio-mixer` a36e32f and `record-review` ca99a77, and `git log --format= --name-only main live-audio-mixer record-review` lists no path outside `packages/`, or each difference is explained.
- [x] 2.2 The orchestrator fetches `main`, `live-audio-mixer:movie-live-audio-mixer` and `record-review:movie-record-review` from that clone into the bench and merges `main` into `v0.9-joins-join-movie` with `git merge --allow-unrelated-histories`, one merge commit, no conflict. Record in `evidence.md`: the merge commit; `git log --format='%h %ad %s' --date=short -- packages/machinome-movie/machinome/movie/js/src/render.mjs | tail -1` reaching the commit of 19 September 2026; `git log --oneline -3` of each fetched branch (two commits on 83322ce's rewrite); `git status --short` clean.
- [x] 2.3 On the joined tree, run `tests/test_repository_layout.py`, `test_release_records.py`, `test_core_names_no_split_words.py` and `test_docs_structure.py` on the bench venv from the framework's directory. Expected red, design.md probe 3: the workspace source, the README, the sibling table and the guide (each naming `machinome-movie`); the numbering (0.0.0), the pin (bare `machinome`) and the bump; the split-word gate (seven `exact_seconds`); the docs' licence wording on `howto/film-a-movie.rst`; and the node workspace's tests on the movie's tracked `package-lock.json`. Record each reason. Anything else red is investigated before group 3.

## 3. Red first, on the joined tree (nothing of the package changes in this group)

- [x] 3.1 `tests/test_repository_layout.py` (design.md Decision 8): the `PRODUCTS` row; `NODE_MEMBERS` as a mapping to the members' names; `OWN_LOCKS`; `test_the_movie_s_own_lock_agrees_with_its_manifest_and_the_root_s`; `test_the_root_installs_each_member_s_dependencies_beside_it`; `.npmrc` among the root's files; the CI tests of Decision 10; the default group with the movie's extra; the docstring. Run it. Expected red: the product's entries (no links, no `MANIFEST.in`), manifest (no licence, `packages` not `include`), README, resolution (`machinome.movie` not importable), the members (one), the locks (the member's names `machinome-videomaker`), the `.npmrc`, the CI steps, and 2.3's. Record each.
- [x] 3.2 `tests/test_release_records.py`: `test_the_movie_s_node_version_files_agree`. Run it. Expected red: `J/package.json` at 0.0.0 and absent from `.bumpversion.cfg`, with 2.3's three.
- [x] 3.3 `tests/test_kernel_extras.py` (`EXTRAS['movie']`) and `tests/test_machinome_identity.py` (`('movie', 'machinome-movie')`). Run them. Expected red: `KeyError: 'movie'` in each.
- [x] 3.4 `tests/test_vet_universe.py`: the contract's tuple and `test_the_movie_is_internal_and_its_former_name_outside`. Run it. Expected red: the contract's tuple, and the model importing `machinome.movie` vetted pure (vet judges a name by its place in the universe, not by whether it is installed, design.md probe 15).
- [x] 3.5 `tests/test_docs_structure.py` (Decision 12): the toctree entries of the three how-tos and `reference/movie/index`, the install page's distribution and its two lines, the CLI section `machinome movie` with its eleven verbs, no "to add" for the videomaker, and no page spelling `bin/videomaker.mjs`, `machinome_movie` (the changelog's one line excepted) or `--viewer`. Run it. Expected red: each.
- [x] 3.6 The package's new `D/tests/test_command.py` (Decision 5), through scratch directories and a fake Node (a script named by `MACHINOME_NODE` that answers `--version` and records its arguments and working directory): `machinome movie -h` lists the eleven verbs; the Node refusals (none, one that cannot run, v20); the missing dependencies' two refusals (installed, workspace); `setup`'s two refusals (workspace member, a linked `node_modules` above) writing nothing; `setup --remove`; the viewer's refusal (`describe` raising `ViewerUnavailable`) for `check`, and `speech` passing none; a directory without a movie and a movie after a file refused; a project and a movie evaluated, its path printed, the fake Node given it; the options passed as given, `--viewer` the report's path; the Node process's exit status returned; an absent extra in the project's model refused in one line; `python -m machinome.movie -h` the same parser. And `D/tests/test_package.py`: the manifest (name, version, the three dependencies, licence, entry point, `include`), `machinome/movie/__init__.py` a file and `machinome/__init__.py` absent, no `machinome_movie` importable, and the lazy root (a fresh interpreter importing `machinome.movie.cli` loads no `jsonschema` and no `machinome.movie.document`). Run them from `D`. Expected red: `ModuleNotFoundError: No module named 'machinome.movie'` at collection (the package is not yet installed or renamed); record it.
- [x] 3.7 Record in `evidence.md` every red of group 3 with its reason.

## 4. The package

- [x] 4.1 The links, from `D`: `ln -s ../../LICENSE LICENSE`, `ln -s ../../LICENSES LICENSES`; `git add` them.
- [x] 4.2 `pyproject.toml`, `README.md`, `MANIFEST.in` and `.gitignore` of design.md Decision 3, verbatim, in place of the product's.
- [x] 4.4 (the orchestrator's ratification, 12 October 2026) A wheel built from `D` in a scratch copy (`python -m build --wheel`) emits no setuptools warning that a `machinome.movie.js` directory, or one below it, is absent from the `packages` configuration (probe 11 saw twenty; setuptools says a later version raises): declare what the wheel ships (`include = ["machinome.movie", "machinome.movie.js*"]` with `exclude` for the test, fixtures and scripts directories, or the remedy the evidence shows works), keep the wheel's 77 entries, and record the build output's warning count, 0.
- [x] 4.3 `J/package.json` edited as Decision 3 says; `J/package-lock.json` regenerated by `npm install --package-lock-only --no-audit --no-fund` in a scratch copy of `J`'s two files outside the workspace, then copied back; `git diff` of the lock shows the name, the version, Playwright and its core, `fsevents`, and the `dev` flags of the three moved packages (design.md probe 10), nothing else.

## 5. The source at its address

- [x] 5.1 The import of Decision 4: `machinome_movie` to `machinome.movie` in `__main__.py`, `stage.py` and `watch.py`, and the comments of `J/src/` naming `python/machinome_movie/`; `git diff` of each file shows those lines.
- [x] 5.2 The lazy root: `__init__.py`'s imports replaced by the name-to-module table and `__getattr__`; its docstring and `__all__` unchanged.
- [x] 5.3 `__main__.py` running the command's parser; `cli.py` with the class `Movie` of Decision 5.
- [x] 5.4 The schema link retargeted (`ln -sfn js/schema/machinome-movie-0.2.json`), its target recorded.
- [x] 5.5 The Node side's three reader-facing messages of Decision 4.

## 6. The npm workspace

- [x] 6.1 The root `package.json`'s second member; the root `.npmrc` of Decision 6.
- [x] 6.2 `npm install --no-audit --no-fund` at the root (never through a linked `node_modules`): record "added N packages", the lock's growth, and that every one of the viewer's resolutions is at its path and version (the comparison script of probe 7); `J/node_modules` holds the movie's direct dependencies, `.bin/tsc` and `.bin/esbuild` among them.
- [x] 6.3 `npm ci --no-audit --no-fund` at the root reproduces it; `git -C <bench> status --short` shows no `node_modules`.
- [x] 6.4 (the orchestrator's ratification, 12 October 2026) The widget under the shallow layout, from the root: `npm run typecheck --workspace packages/machinome-viewer/machinome/viewer/web/widget`, `npm test --workspace ...widget` and `npm run build --workspace ...widget`, each exit 0, the test counts those of `join-viewer` (66 files, 1715 passed, 2 skipped), the bundle's size recorded; and `scripts/check-dist`'s viewer row still green at 11.4 (its sdist hook builds the bundle from this layout).

## 7. The core and the workspace

- [x] 7.1 The core's `pyproject.toml`: the `movie` extra and its comment (Decision 7); `git diff` shows that hunk alone.
- [x] 7.2 The root `pyproject.toml`'s source and dev group; `uv lock` (expected: the line's count plus five, the member and `jsonschema`, `jsonschema-specifications`, `referencing`, `rpds-py`, probe 13; record the line and the diff's size); `uv sync --python 3.12` (one more `__editable__` `.pth`, naming `D`). Then from `/tmp`: `machinome movie -h` lists the eleven verbs, `python -c "import machinome.movie as m; print(m.__file__)"` names `P/__init__.py`, `python -c "import machinome_movie"` raises `ModuleNotFoundError`. If the lock or the sync fails, stop and report.
- [x] 7.3 `machinome/vet/universe.toml`: `"machinome.movie"` in `[contract] deny` with its comment; `tests/test_core_names_no_split_words.py`: the three `ORDINARY` entries of Decision 8.
- [x] 7.4 Groups 3's core tests again (3.1 to 3.5): expected green but the README, guide, CI and manual tests (groups 10 to 12) and anything named there. Record.

## 8. The seam's tests

- [x] 8.1 `tests/contributed_commands.py`: `fake-movie` to `fake-film` and `fake-movie-two` to `fake-film-two` (Decision 9); `tests/test_cli_contributed.py` and `tests/test_cli_lazy_imports.py` follow. Before the edit, on the synced venv, run the three CLI modules: expected red, probe 12's failures on the `movie` fakes (record which remain once `join-skills`'s computed choices are in); after, green.
- [x] 8.2 The conformance walk's red, once: delete `needs_node` from `Movie`, run `test_every_contributed_entry_resolves_and_honours_the_contract` (expected: it names `machinome-movie` and the term), restore; `git diff` of `cli.py` back to the change's.

## 9. The tests at their new place

- [x] 9.1 Python (Decision 13): `machinome_movie` to `machinome.movie` in the tests and the fixture project's five modules; `conftest.py`; `test_take.py`'s path; then `env -C <bench>/packages/machinome-movie <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider`: expected 9 failed, the pinning tests of `test_repository.py` and the fixture revision's (record).
- [x] 9.2 The fixture documents' 77 roots (`../../python/tests/fixtures/project/` to `../../../../../tests/fixtures/project/`), the fourteen path lines of `<scratch>/probe_js_patch.py` (its `stage-build.mjs` part excepted), then the re-pin with `TMPDIR` under the scratch directory: `node scripts/pin-fixture-project.mjs --python <bench>/.venv/bin/python --machinome <bench>/.venv/bin/machinome` from `J` (expected, probe 5: both exports remade, their models unchanged, three documents changed), then `node scripts/pin-resolved.mjs minimal tour count`; record the output and `git diff --stat` of `J/fixtures/` and `D/tests/fixtures/`, and review the resolved pins' diff (expected: the root and the revision).
- [x] 9.3 `D/tests/test_repository.py`'s nine pinning tests and `J/test/repository.test.mjs`'s twelve, rewritten to read the manual's pages, the package's README and changelog and the product's ADR-003 at their new paths, keeping their facts (they turn green with groups 10 and 12).
- [x] 9.4 The Python tests from `D`: no failure; record the count (expected 298 and the new tests of 3.6).
- [x] 9.5 The Node suite from the root, one run, `TMPDIR` under the scratch directory, `VIDEOMAKER_VIEWER_BUNDLE` naming the bench's built viewer bundle: `npm test --workspace packages/machinome-movie/machinome/movie/js -- --cold`, output to a file. Expected: 52 files, 505 tests, none failed (probe 8, its twelve pinning tests now green), the four projects run, none skipped; record the counts and the duration.
- [x] 9.6 `env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest --collect-only -q -p no:cacheprovider | grep -c machinome-movie`: expected 0.

## 10. The manual

- [x] 10.1 Red first: a fresh venv under the scratch directory installing `packages/machinome/docs/requirements.txt` alone, then `sphinx -b html -n -W --keep-going docs <scratch>/html-red`: expected exit 1 (five Markdown pages in no toctree, and their Markdown read as reStructuredText); record the counts.
- [x] 10.2 The four pages converted in place, `reference/movie/index.rst` and `command.rst` written, as design.md Decision 12 says; `index.rst`'s toctrees. The how-to's setup section says to run `machinome movie setup --remove` before `pip uninstall machinome-movie`, since pip leaves what `setup` installed (probe 11); the command reference says the same under `setup` (the orchestrator's ratification, 12 October 2026).
- [x] 10.3 `reference/cli.rst`'s section and sentence, `start/install.rst`'s extra and package, each rewrapped at its width, the rest unchanged.
- [x] 10.4 The build of 10.1 into `<scratch>/html`: exit 0, no warning. Look at the three how-tos and the section; record. `test_docs_structure.py`, `test_docs_exports.py` and `test_node_root_exports_nothing.py` green.

## 11. The version records, `scripts/check-dist` and CI

- [x] 11.1 `.bumpversion.cfg`'s three tables (Decision 8). The bump on a copy: the configuration and the files it names copied under the scratch directory, made a git repository, `bump2version --no-commit --no-tag --new-version 0.9.0 patch`; record that the movie's manifest version, its two pins and `J/package.json` move to 0.9.0. Nothing is written in the bench.
- [x] 11.2 Red first: `scripts/check-dist` fails "machinome-movie has no smoke in scripts/check-dist"; record.
- [x] 11.3 The row and the start's Node check of Decision 11; `flake8 --max-line-length=89 scripts/check-dist`: 0.
- [x] 11.4 Run it: every member built, its archives `twine check --strict` passed, the movie's wheel installed by path, `review` refused before `setup`, `setup` installed, `review` reached Node, `setup --remove` removed, `machinome movie -h` exit 0, the licence files, nothing uploaded. Record the movie's wheel and sdist entries (expected 77 and about 926, probe 11) and `git -C <bench> status --short` afterwards.
- [x] 11.5 `.github/workflows/python-app.yml`: the widget's step named by `--workspace`, the movie's two steps (Decision 10). The layout gate's CI tests green.

## 12. The records

- [x] 12.1 `HISTORY.rst`, `docs/project/changelog.rst` and `D/CHANGELOG.md`: the entries of design.md Decision 14, verbatim. `test_release_records.py` green.
- [x] 12.2 `CREDITS.md`'s section, unless the orchestrator declined it (Open Questions 18); `docs/architecture.md`'s CLI sentence, section, Map row and extras sentence; the root `README.md`'s row; `CONTRIBUTING.rst`'s pip line and sentences; `context7.json`'s folders and rule; `AI-USE.md`'s clause. The layout gate's README, guide, link and index tests and `test_release_records.py`'s context7 test green.
- [x] 12.3 Unless declined (Open Questions 1): ADR-191 as Decision 14 outlines it, Status Proposed; its index line under BUILD after ADR-190's; ADR-182's and ADR-188's dated consequences and index lines.
- [x] 12.4 The product's record of Decision 15, in place; `env -C <bench>/packages/machinome-movie openspec validate --specs --strict` passes (record the report; if the CLI cannot run there, record why).
- [x] 12.5 Grep the tracked files this change and the join added or changed for `machinome_movie`, `bin/videomaker.mjs` as a user's command, `--viewer` and the licence the Leonardo sources carry: found only in the product's archived changes, its workflow notes but `README.md`, its ADRs and `first-rehearsal.md`, the fixture documents' history and the changelog's former-name lines; record the count per file.

## 13. Validation

- [x] 13.1 The whole suite, one process, from the framework's directory on the bench venv: `env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider`, output to a file under the scratch directory. Expected: no failure; the base's skips; the passed count the base's with each added test named.
- [x] 13.2 The package's Python tests (9.4) and Node suite (9.5) on the final tree; record both.
- [x] 13.3 The lint: `flake8 --max-line-length=89 machinome tests` and the `../machinome-*/machinome` paths from the framework's directory; record the count and the movie package's part.
- [x] 13.4 The manual as in 10.4 on the final tree: exit 0.
- [x] 13.5 `scripts/check-dist` as in 11.4 on the final tree, and once on a clean copy of the tracked tree (`git ls-files -z | tar --null -T - -cf -` unpacked under the scratch directory, links kept), recording both runs' counts.
- [x] 13.6 The universe sweep of `join-mechanics` with this bench, before the projects' move: expected identical to the base row for row, no model importing the movie (vet and the loader read no `videos/`, design.md probe 15); any difference reported with its explanation.
- [x] 13.7 Git: `git -C <bench> status --short` shows the edited and added files of groups 3 to 12 and nothing else; `git ls-files -ci --exclude-standard | wc -l` equals its count at the base.
- [x] 13.8 `env -C <bench>/packages/machinome openspec validate join-movie --strict`.
- [x] 13.9 Stop before any commit and report to the orchestrator: the reds of 2.3, group 3, 8.1, 10.1 and 11.2, the counts of 6.2, 7.2, 9.4, 9.5, 10.4, 11.1, 11.4 and 13.1 to 13.6, and anything that departed from the design. Resume only on the orchestrator's message.

## 14. The projects' move and the originating check (the orchestrator's, after the implementation commit)

- [x] 14.1 The move of design.md Decision 16 in each of the five repositories, under its own process, with its commit message; record each repository's commit and its files touched (expected: the 21 Python modules and the film READMEs that show the commands).
- [x] 14.2 The originating check of Decision 16 on the Curta: `machinome movie check <Curta> addition` and `machinome movie preview <Curta> addition` from the bench venv, `TMPDIR` under the scratch directory; record their output and look at the storyboard `preview` writes. A missing take or a refusal is recorded as found.
- [x] 14.3 The universe sweep again after the move: the base's counts row for row; record in `evidence.md`.

## 15. Records closing (after the orchestrator's review)

- [x] 15.1 ADR-191 promoted to Accepted if written; `docs/adrs/README.md` updated; `docs/architecture.md` checked against it.
- [x] 15.2 Re-run 1.3's comparison at the bench's head; then `env -C <bench>/packages/machinome openspec archive join-movie -y` (expected, probe 17), the Purpose of the created `movie-distribution` spec written in place of the CLI's placeholder, then `openspec validate --specs --strict`.
- [x] 15.3 The root's `workflow/ongoing/release-0.9.md`, "Progress": the cycle's entry with its branch, the planning commit, the merge commit, the two fetched branches, the ADR, the suite count, the package's two counts, the manual, `check-dist`, the lock, the projects' move, the originating check and the sweep.
- [x] 15.4 `evidence.md` complete; the implementation commit is the orchestrator's, never amending the planning or the merge commit; nothing pushed.
