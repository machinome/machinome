## 1. Evidence baseline

- [x] 1.1 Record the base: `git -C <bench> log --oneline -1` is the planning commit on top of 6fb505ed (or the line's head the orchestrator names), the worktree clean but this change; start `evidence.md` in this change with it.
- [x] 1.2 Make the bench venv on the base's tree: `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12`. Expected: 175 packages installed, one `__editable__.machinome-0.8.1.pth` holding `<bench>/packages/machinome` (the first cycle's 5.2). Record the base suite count the first cycle measured on the same tree and recipe (its evidence, 7.1): 4774 passed, 20 skipped, 6799 subtests. Do not rerun it. One suite at a time.
- [x] 1.3 Record the lint base: `env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests | wc -l` (expected 759, design.md probe 6).
- [x] 1.4 Record the sweep base: `root-cleanup`'s counts (design.md, Decision 12): 62 repositories, 129 rows, 121 ok, 0 expected, 2 unexpected, 0 timeout, 6 no-model, 2 skipped. Do not rerun it here.

## 2. Red first, at the base's paths (nothing moves in this group)

- [x] 2.1 `tests/test_repository_layout.py`: group G9 and the generalised G4 of design.md Decision 9, and `test_the_guide_installs_every_member_without_uv`. Run the module. Expected red: every G9 test (the engine directories do not exist; `machinome.engine.brep` and `.mesh` resolve under `packages/machinome/`; the core's `machinome/engine/` holds `brep.py` and `mesh.py`); the guide test (no `editable_mode=compat`, `make test-all` present). `test_every_member_is_a_workspace_source` is green here (one directory, one source); its red is task 3.3's. Record each reason.
- [x] 2.2 `tests/test_kernel_extras.py` (Decision 9): `REPOSITORY`, the version read from the manifest, `EXTRAS['brep']` and `['mesh']` naming the distributions, `ENGINE_REQUIREMENTS` and `test_each_engine_requires_the_core_and_its_kernel`, `test_the_occt_range_is_stated_once`, `test_the_lock_installs_every_kernel`, `test_ci_syncs_the_locked_workspace`; remove `test_ci_installs_every_concrete_requirement_of_all` and `test_tox_installs_every_extra`; the docstring names the manifests and the lock. Run it. Expected red: `test_each_extra_lists_what_its_module_needs` subtests `brep` and `mesh` (the core lists `cadquery-ocp>=7.8.1,<7.9` and `manifold3d`), the engine manifests test (`FileNotFoundError`), the OCCT range test (named in the core's `brep` extra), the lock test (no engine in `uv.lock`), the CI test (no `uv sync --locked`).
- [x] 2.3 `tests/test_core_kernel_free.py` (Decision 9): `REPOSITORY`, `portion_modules()`, the provider exclusions dropped, the core census without the engines, `test_the_engine_packages_import_only_their_kernels`, `EXTRA_OF`'s engine keys as `machinome-engine-<x>/machinome/engine/<x>.py` and the `require_extra` test reading both scans. Run it. Expected red: the core census (it finds `machinome/engine/brep.py` and `mesh.py`), the portion census (empty), the `require_extra` test (`KeyError` on the two portion keys).
- [x] 2.4 `tests/test_release_records.py` (Decision 9): `.bumpversion.cfg` read at `REPOSITORY`, `test_every_member_is_numbered_with_the_core`, `test_every_pin_between_members_is_compatible`, `test_the_version_is_bumped_from_the_root`. Run it. Expected red: `test_every_version_file_agrees_with_pyproject` and `test_the_version_is_bumped_from_the_root` (`FileNotFoundError` on `.bumpversion.cfg`); the member and pin tests green (one member, no pin yet), their red is task 4.1's.
- [x] 2.5 `tests/test_docs_structure.py`: `KernelExtrasTest.test_the_installation_page_names_the_engine_distributions`. Run it. Expected red: `start/install.rst` names neither distribution.
- [x] 2.6 `tests/test_brep_engine.py` and `tests/test_mesh_engine.py`: `ENGINE_SOURCE` through `importlib.util.find_spec(...).origin` (Decision 9). Run both: green. Their red without this edit is design.md probe 5 (`FileNotFoundError` at the move); record it there by reference.
- [x] 2.7 Record in `evidence.md` every red of 2.1 to 2.5 with its reason and each green this group expects.

## 3. The cut

- [x] 3.1 `mkdir -p <bench>/packages/machinome-engine-brep/machinome/engine <bench>/packages/machinome-engine-mesh/machinome/engine`, then `git -C <bench> mv packages/machinome/machinome/engine/brep.py packages/machinome-engine-brep/machinome/engine/brep.py` and the same for `mesh.py`. `git status` shows both as renames with no content change.
- [x] 3.2 The links, from each engine directory: `ln -s ../../LICENSE LICENSE`, `ln -s ../../LICENSES LICENSES`; `git add` them; `git ls-files -s packages/machinome-* | grep ^120000` lists four with those targets.
- [x] 3.3 Run `test_repository_layout.py`, `test_core_kernel_free.py`, `test_brep_engine.py` and `test_mesh_engine.py` on the bench venv (its `.pth` still names the core alone, so the engines are not on the path). Expected: `test_every_member_is_a_workspace_source` red (two directories, no source), the README test red (probe 5), the G9 link and core-engine tests green, the directory, manifest and README tests red (no `pyproject.toml` or `README.md` yet), the resolution test and both engine test modules red (the provider cannot be found until the sync of 4.5). Record each.

## 4. The manifests and the workspace

- [x] 4.1 `packages/machinome-engine-brep/pyproject.toml` and `packages/machinome-engine-mesh/pyproject.toml` (Decision 2, verbatim). Run `test_release_records.py`: `test_every_member_is_numbered_with_the_core` and `test_every_pin_between_members_is_compatible` green, `test_the_version_is_bumped_from_the_root` red (no `.bumpversion.cfg`). Show the pin test's red once: the B-rep manifest's pin edited to `machinome>=0.8.1`, the test run (red naming that requirement), the pin restored (`git diff` of the manifest against 4.1's text empty).
- [x] 4.2 The two `README.md` (Decision 2, verbatim).
- [x] 4.3 The core's `pyproject.toml`: the `brep` and `mesh` extras and the three comments of Decision 3; nothing else in it changes.
- [x] 4.4 `machinome/__init__.py`: the one docstring sentence of Decision 3; its code unchanged (`git diff` shows the docstring alone).
- [x] 4.5 The root `pyproject.toml` sources (Decision 4); `env -C <bench> /home/asa/.local/bin/uv lock` (expected: 187 packages, "Added machinome-engine-brep v0.8.1" and "-mesh"); `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12` (expected: three `__editable__` `.pth` files, each holding its package directory; record them). Then `env -C /tmp <bench>/.venv/bin/python -c` printing `machinome.engine.__path__`, both seams' providers' files and contracts. If the lock or sync fails, stop and report the error.
- [x] 4.6 The root `.gitignore` (Decision 4, verbatim). `git -C <bench> status --short` shows no `*.egg-info` under `packages/machinome-*`.
- [x] 4.7 `tests/test_core_names_no_split_words.py` (Decision 9), its blind spot red first: plant a comment holding the mesh-quality word in the moved `mesh.py`; the gate as it is passes; repoint it to scan `ROOT` and each `packages/machinome-*`; it fails naming `machinome/engine/mesh.py`; remove the plant (`git diff` of `mesh.py` empty); green. Record both runs.
- [x] 4.8 Run the modules of group 2 and `test_engine_package.py`, `test_brep_engine_seam.py`, `test_mesh_engine_seam.py`, `test_brep_engine_dependency.py`, `test_mesh_engine_dependency.py` on the bench venv. Expected green but `test_release_records.py`'s bumpversion tests (group 5), `test_kernel_extras.py`'s CI test (group 6), the layout README and guide tests and `test_docs_structure.py`'s page test (group 8). Anything else red is investigated before group 5.

## 5. One version for the set

- [x] 5.1 The root `.bumpversion.cfg` (Decision 5, verbatim); the `[bumpversion]` and `[bumpversion:file:...]` tables removed from `packages/machinome/setup.cfg`, its `[flake8]` kept; the comment in `machinome/vet/universe.toml` naming the root's `.bumpversion.cfg`.
- [x] 5.2 The dry run: `env -C <bench> <bench>/.venv/bin/bump2version --dry-run --allow-dirty --verbose --new-version 0.9.0 patch 2>&1`; record that it would change the nine statements of design.md probe 7 and nothing else. Nothing is written.
- [x] 5.3 `test_release_records.py` green.

## 6. CI, the lint and the retirements

- [x] 6.1 `.github/workflows/python-app.yml` (Decision 6): the `lint`, `test` and `browser-snapshot` jobs take the `Setup uv` and `Sync the workspace` steps verbatim in place of `actions/setup-python` and the requirements install; the browser-snapshot install step and the lint steps verbatim; the `build` job's install becomes `pip install build`; `docs` and `dist` unchanged. Check it parses (`yaml.safe_load`). `test_kernel_extras.py`'s CI test, `test_docs_exports.py` and the layout gate's CI group green.
- [x] 6.2 `packages/machinome/setup.cfg`'s two engine per-file ignores spelled `../machinome-engine-brep/machinome/engine/brep.py:E402` and the mesh one (Decision 8). `env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-engine-brep/machinome ../machinome-engine-mesh/machinome | wc -l`: expected 759, the base's; `grep -c E402` of the same over the two engine paths: 0.
- [x] 6.3 The Makefile: `test-all` and the `.tox/` line removed; `lint/flake8` and `lint/black` over `machinome tests ../machinome-*/machinome`. `make -C <bench>/packages/machinome lint/flake8` runs with the venv's `bin/` on `PATH` over the three packages; record its line count (it exits non-zero on the base's warnings, as before).
- [x] 6.4 `git -C <bench> rm packages/machinome/requirements.txt packages/machinome/requirements_dev.txt packages/machinome/tox.ini`. `grep -rn "requirements_dev\|tox" <bench>/packages/machinome --include=*.py --include=*.cfg --include=*.toml --include=Makefile --include=*.yml` and the same over the root's `.github`, `CONTRIBUTING.rst` and `scripts`: no hit but the layout gate's list of entries the root must not hold and the changelog's history.

## 7. `scripts/check-dist`

- [x] 7.1 Red first: `env -C <bench> <bench>/.venv/bin/python scripts/check-dist` fails "machinome-engine-brep has no smoke in scripts/check-dist" (or the mesh one first by sort order); record it.
- [x] 7.2 The two rows, the `through` install and the shared licence template of Decision 7; the core's row unchanged (`git diff` shows no line of it changed).
- [x] 7.3 Run it. Expected: three members built; `twine check --strict` passed for six archives; each member's linked files in its sdist as regular files equal to the root's; the install naming the core's wheel with `[openscad,stl]` and `machinome[brep]`, `machinome[mesh]` with three `--find-links`; each engine's line printing its version 0.8.1, its provider file inside the venv, its contract and its operation's result (1000 and 24.0); the three licence files listed for each; `machinome --help` exit 0; the last line saying nothing was uploaded. Record the archives' member counts (probe 3: core sdist 1019 on a clean tree, wheel 126; each engine 18 and 8) and `git -C <bench> status --short` afterwards (nothing new but ignored leavings).

## 8. The records

- [x] 8.1 `HISTORY.rst`: the `Unreleased` bullet of Decision 10, verbatim, after the first cycle's.
- [x] 8.2 `docs/project/changelog.rst`: the `Unreleased` section of Decision 10, verbatim, above `Machinome 0.8.1`. `test_release_records.py` and `test_profile_documentation.py` green.
- [x] 8.3 `docs/start/install.rst`: the two rows and the section of Decision 10. `test_docs_structure.py` green.
- [x] 8.4 The root `README.md`: the two rows of Decision 10. The layout gate's README test green.
- [x] 8.5 `CONTRIBUTING.rst`: the edits of Decision 10, in place. The layout gate's guide and link tests green.
- [x] 8.6 `docs/architecture.md`: the Map rows and the sentences of Decision 10.
- [x] 8.7 `docs/adrs/BUILD/ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md` (Decision 10), Status Proposed; the index entry under BUILD and the OCCT heading in `docs/adrs/README.md`.
- [x] 8.8 The whole layout gate green.

## 9. Validation

- [x] 9.1 The whole suite, one process, from the framework's directory on the bench venv: `env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider`, output to a file under the scratch directory. Record passed, skipped (each reason) and failed. Expected: no failure; 20 skips, the base's (16 the viewer, networkx, the `jscad` command, two vendor STEP); the passed count the base's 4774 less the two removed tests of 2.2, plus the tests this change adds, each named. The fallback recipe is not run (design.md, Risks).
- [x] 9.2 The lint of 6.2 again on the final tree; record the count.
- [x] 9.3 The manual: a fresh venv under the scratch directory installing `packages/machinome/docs/requirements.txt` alone, then `env -C <bench>/packages/machinome <venv>/bin/python -m sphinx -b html -W docs <scratch>/html`. Expected: success.
- [x] 9.4 `scripts/check-dist` as in 7.3 on the final tree, and once on a clean copy of the tracked tree (`git ls-files -z | tar --null -T - -cf -` unpacked under the scratch directory, links kept), recording the archives' counts from both.
- [x] 9.5 The universe sweep with the command of design.md Decision 12 (`--timeout 300`, the ten tables, `--json` under the scratch directory). Expected: the counts of 1.4; any row that differs is reported with its explanation, not worked around.
- [x] 9.6 Git: `git -C <bench> status --short` shows the two modules as renames, the two package directories' five files each as added (the links with mode 120000), `.bumpversion.cfg` added, the three retired files deleted, and the edited files; `git ls-files -ci --exclude-standard | wc -l` still 34.
- [x] 9.7 `env -C <bench>/packages/machinome openspec validate cut-the-engines --strict`.
- [x] 9.8 Stop before any commit and report to the orchestrator: the reds of groups 2 to 4 and 7.1, the counts of 1.2, 4.5, 5.2, 6.2, 7.3 and 9.1 to 9.6, and anything that departed from the design. Resume only on the orchestrator's message.

## 10. Records closing (after the orchestrator's review)

- [x] 10.1 ADR-183 promoted to Accepted; `docs/adrs/README.md` updated; `docs/architecture.md` checked against it; ADR-167's and ADR-180's index lines note "amended by 183" where the ADR says it amends them.
- [x] 10.2 `env -C <bench>/packages/machinome openspec archive cut-the-engines` (the deltas synced into `packages/machinome/openspec/specs/`), then `openspec validate --specs --strict` there.
- [x] 10.3 The root's `workflow/ongoing/monorepo-0.9.md`: cycle 2 marked done with its branch, the suite count of 9.1, the check-dist result and the sweep's counts, as cycle 1 is recorded.
- [x] 10.4 `evidence.md` complete; the implementation commit is the orchestrator's, never amending the planning commit; nothing pushed.
