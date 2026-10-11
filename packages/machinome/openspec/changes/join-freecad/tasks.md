## 1. Evidence baseline

- [ ] 1.1 Record the base: `git -C <bench> log --oneline -1` is the planning commit on top of cf631645 (or the line's head the orchestrator names), the worktree clean but this change; start `evidence.md` in this change with it.
- [ ] 1.2 Record the bench venv the orchestrator synced from the lock (187 packages; eleven `__editable__` `.pth` files, each holding its package directory) and the base counts measured by `cut-the-mesh-nodes` on the same tree and recipe, without rerunning them: suite 4796 passed, 20 skipped, 7029 subtests; lint 759 lines (`flake8 --max-line-length=89 machinome tests` and the ten `../machinome-*/machinome` paths, named, from the framework's directory); sweep 63 repositories, 130 rows, 121 ok, 0 expected, 3 unexpected, 0 timeout, 6 no-model; the clean copy's framework sdist 1006 entries and wheel 114.
- [ ] 1.3 Record the probes of design.md that the cycle relies on, by reference: probe 1 (4 collection errors), probe 2 (80 passed, 1 failed, 1 skipped; the seam variant 31 passed), probe 3 (55 failed, 6 errors, 20 passed, 1 skipped), probe 4 (51 files; 7e5b228a), probe 6 (the reds of the join), probe 7 (Dum-E), probe 8 (82 passed on regenerated fixtures).

## 2. The join (the orchestrator's, after the planning commit)

- [ ] 2.1 The orchestrator clones `file:///home/asa/devel/machinome/machinome-freecad` fresh under the scratch directory and runs the `git filter-repo` command of design.md Decision 2 in it; `git ls-tree -r --name-only lean-core-validation` lists the 51 paths of `<scratch>/rehearsal-ls-files.txt`, no commit of any branch touches a path outside `packages/`, and the branch's head is 7e5b228a or the difference is explained.
- [ ] 2.2 The orchestrator fetches `lean-core-validation` from that clone into the bench and merges it into `v0.9-joins-join-freecad` with `git merge --allow-unrelated-histories`, one merge commit, no conflict. Record in `evidence.md`: the merge commit; `git log --follow --format='%h %ad %s' --date=short -- packages/machinome-node-freecad/machinome/node/freecad/adapter.py` reaching the commit of 1 October 2026 that wrote it; `git log` on `packages/machinome/workflow/archive/native-freecad-assembly-2026-10-01/dume-native-freecad.md` reaching the product's first commit; `git status --short` clean.
- [ ] 2.3 On the joined tree, run `tests/test_repository_layout.py`, `test_release_records.py`, `test_core_kernel_free.py`, `test_core_names_no_split_words.py` and `test_node_root_exports_nothing.py` on the bench venv from the framework's directory. Expected red, design.md probe 6: `test_every_member_is_a_workspace_source`, `test_every_sibling_is_in_the_table`, `test_the_guide_installs_every_member_without_uv`, `test_the_readme_links_every_package_and_states_the_licence`; `test_every_member_is_numbered_with_the_core`, `test_every_pin_between_members_is_compatible`, `test_the_version_is_bumped_from_the_root`; `test_the_extension_packages_import_only_their_kernels`; the split-words gate on `adapter.py` (three names) and `worker.py` (`'occt'`); the root-import scan on `adapter.py` line 17. Record each reason. Anything else red is investigated before group 3.

## 3. Red first, on the joined tree (nothing of the package changes in this group)

- [ ] 3.1 `tests/test_repository_layout.py`: the `EXTENSIONS` and `PACKAGE_PORTIONS` rows of design.md Decision 10, the docstring. Run it. Expected red: the package's directory, manifest and README subtests (no links; the product's manifest; no install line or licence), the portion's resolution (not installed), and 2.3's four. Record each reason.
- [ ] 3.2 `tests/test_kernel_extras.py` (Decision 10). Run it. Expected red: the `freecad` and `all` extras subtests, the requirements and B-rep-engine tests on the product's manifest, the lock test (no `machinome-node-freecad` in `uv.lock`), the refusal of `machinome.node.freecad` with `OCP` blocked (the package does not refuse).
- [ ] 3.3 `tests/test_core_kernel_free.py` (Decision 10). Run it. Expected: the extension census green (its expectation now names `adapter.py`'s `OCP`, the red of 2.3), and `test_each_kernel_module_checks_its_kernel_first` red for the package's `__init__` (no `require_extra`).
- [ ] 3.4 `tests/test_supported_node_types.py` and `tests/test_node_root_exports_nothing.py` (Decision 10), the new skip test included. Run them. Expected red: the table test (no `freecad` row), `AbsentPackageTest`'s four `freecad` doors (no row, so the doors meet a plain `ModuleNotFoundError` with no extra), the table's new names, and the skip test (the module's tests fail without the runtime).
- [ ] 3.5 `tests/test_core_names_no_split_words.py`: `ZONES` gains the worker (Decision 10). Run it: red on `adapter.py` alone.
- [ ] 3.6 `tests/test_docs_structure.py` (Decisions 10 and 12). Run it. Expected red: the installation page's `machinome[freecad]` and `machinome-node-freecad`, and `test_the_freecad_guide_is_a_how_to` (the page is Markdown and in no toctree).
- [ ] 3.7 Record in `evidence.md` every red of group 3 with its reason.

## 4. The package

- [ ] 4.1 The links, from `packages/machinome-node-freecad/`: `ln -s ../../LICENSE LICENSE`, `ln -s ../../LICENSES LICENSES`; `git add` them; `git ls-files -s packages/machinome-node-freecad | grep ^120000` lists two with those targets.
- [ ] 4.2 The manifest and the README of Decision 3, verbatim, in place of the product's.
- [ ] 4.3 `machinome/node/freecad/__init__.py` of Decision 4, verbatim; the headers of Decision 4 on `adapter.py`, `runtime.py` and `worker.py`, the worker's third line kept and its fourth replaced.
- [ ] 4.4 The four edits of Decision 5 in `adapter.py`; `git diff` of the module shows them and the header, nothing else.

## 5. The core and the workspace

- [ ] 5.1 `machinome/node/supported.py`: the row of Decision 6; `git diff` shows one line.
- [ ] 5.2 The core's `pyproject.toml`: the `freecad` extra, `all` and the comment of Decision 6; `git diff` shows those three hunks.
- [ ] 5.3 The root `pyproject.toml`'s source of Decision 7; `env -C <bench> /home/asa/.local/bin/uv lock` (expected: 188 packages, "Added machinome-node-freecad v0.8.1"; record the line); `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12` (expected: twelve `__editable__` `.pth` files; record them). Then from `/tmp`, `<bench>/.venv/bin/python -c` printing `machinome.node.freecad.__file__` and `machinome.node.freecad.FreeCADAssemblyNode.__module__`. If the lock or the sync fails, stop and report. `git -C <bench> status --short` shows no build leaving under `packages/machinome-node-freecad`.
- [ ] 5.4 Run groups 3's modules again. Expected green but `test_docs_structure.py`'s (group 7), `test_release_records.py`'s bumped-from-root test (group 8), the guide and README tests of the layout gate (group 9) and the skip test (group 6). Record.
- [ ] 5.5 By hand on the bench venv, from `/tmp`, with `machinome-node-freecad` uninstalled (`uv pip uninstall --python <bench>/.venv/bin/python machinome-node-freecad`): `python -c "from machinome.node.freecad import FreeCADAssemblyNode"` prints the refusal naming `machinome[freecad]`; then `uv sync --python 3.12` restores it ("Installed 1 package"). Record both.

## 6. The tests and the fixtures

- [ ] 6.1 `tests/freecad_support.py` of Decision 10, verbatim.
- [ ] 6.2 The four test modules and the three helpers: the headers of Decision 4, the guard call, the imports and paths of Decision 10, `leaf.exact` to `leaf.brep`; `git diff` of each shows those lines and nothing else.
- [ ] 6.3 The fixtures of Decision 11: the generator's `out` and its three assignments; the fixtures' README's three edits; then, if the orchestrator has not declined it (design.md Open Questions 4), from the framework's directory `MACHINOME_FREECAD_ROOT=<freecad> PYTHONPATH="<freecad>/usr/lib" "<freecad>/AppRun" python tests/freecad_generate_fixtures.py` (the generator reads the variable), the `.FCBak` backups deleted, and for each of the 27 documents its count of the former licence string in `Document.xml` before and after recorded (expected 2 and 0) and of the set's expression after (expected 1).
- [ ] 6.4 Without the runtime: `env -u MACHINOME_FREECAD_ROOT -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider tests/test_freecad_public.py tests/test_freecad_constraints.py tests/test_freecad_diagnostics.py tests/test_freecad_freshness.py`: expected 4 skipped, each reason naming `MACHINOME_FREECAD_ROOT`, nothing failed. The skip test of 3.4 green.
- [ ] 6.5 With the runtime: the same four modules with `MACHINOME_FREECAD_ROOT=<freecad>` and `MACHINOME_FREECAD_DUME_SOURCE=/home/asa/devel/machinome/projects/Robotic-Arms/Dum-E/upstream/MA_Dum_E_v2_Assembly.FCStd`: expected 82 passed (probe 8); then without the Dum-E variable: 81 passed, 1 skipped naming it. Record both, with their times. One suite at a time.

## 7. The manual

- [ ] 7.1 Red first: a fresh venv under the scratch directory installing `packages/machinome/docs/requirements.txt` alone, then `env -C <bench>/packages/machinome <venv>/bin/python -m sphinx -b html -W --keep-going docs <scratch>/html-red`. Expected: exit 1, the imported Markdown page in no toctree (and whatever else it reports; record it).
- [ ] 7.2 `docs/howto/freecad-assemblies.rst` converted in place to the outline of Decision 12; `index.rst`'s how-to toctree gains it after `howto/simulate-existing`.
- [ ] 7.3 `docs/start/install.rst`, `docs/howto/backends.rst` and `docs/reference/api.rst` as Decision 12 says, each rewrapped at its page's width, the rest of each page unchanged.
- [ ] 7.4 The build of 7.1 into `<scratch>/html`: success. Look at the rendered guide and the reference entries (the two classes and the attribute present); record. `test_docs_structure.py` green.

## 8. One version and `scripts/check-dist`

- [ ] 8.1 The root `.bumpversion.cfg`: the two tables of Decision 8. `test_release_records.py` green.
- [ ] 8.2 The bump on a copy, as `cut-the-mesh-nodes` did: the root's `.bumpversion.cfg` and the files it names copied under the scratch directory, made a git repository, `bump2version --no-commit --no-tag --new-version 0.9.0 patch`; record that `git diff -U0` changes the new manifest's version and its two pins with the rest, and nothing else. Nothing is written in the bench.
- [ ] 8.3 Red first: `env -C <bench> <bench>/.venv/bin/python scripts/check-dist` fails "machinome-node-freecad has no smoke in scripts/check-dist"; record it.
- [ ] 8.4 The row of Decision 9 and the template's docstring sentence; `git diff` shows no line of another row changed. `flake8 --max-line-length=89 scripts/check-dist`: 0.
- [ ] 8.5 Run it without `MACHINOME_FREECAD_ROOT`: twelve members built, 24 archives `twine check --strict` passed, the package installed through `machinome[freecad]` from the built archives, its line printing 0.8.1, its `__init__.py` inside the venv and "refused without MACHINOME_FREECAD_ROOT, as documented", the licence files listed, nothing uploaded. Then with `MACHINOME_FREECAD_ROOT=<freecad>`: the package's line "blocked at its enabled limit, 120 degrees, through FreeCAD". Record the archives' member counts and `git -C <bench> status --short` afterwards.

## 9. The records

- [ ] 9.1 `HISTORY.rst` and `docs/project/changelog.rst`: the bullets of Decision 13, verbatim. `test_release_records.py` and `test_profile_documentation.py` green.
- [ ] 9.2 `CREDITS.md`: the subsection, the two table rows and the date of Decision 13.
- [ ] 9.3 `docs/architecture.md`: the extras sentence and the Map row of Decision 13.
- [ ] 9.4 The root `README.md`'s row, `CONTRIBUTING.rst`'s pip block and `context7.json`'s rule of Decision 13. The layout gate's README, guide and link tests green; `test_release_records.py`'s context7 test green.
- [ ] 9.5 Unless the orchestrator declined it (design.md Open Questions 1): `docs/adrs/NODE/ADR-185-a-node-type-may-read-a-whole-assembly-through-an-external-program.md` as Decision 13 outlines it, Status Proposed; its index line in `docs/adrs/README.md` under NODE after ADR-184; ADR-183's dated consequence. If declined: ADR-183's consequence alone, and the HISTORY bullet's "(ADR-185)" becomes "(ADR-183 amended)".
- [ ] 9.6 `workflow/warts.md`: the section of Decision 14, verbatim, at its end.
- [ ] 9.7 Grep the bench's tracked files changed or added by this change and the join (`git diff --name-only <planning commit>` and the 51 joined paths) for the former licence identifier and the framework's former licence: found only in the verbatim archives (`openspec/changes/archive/2026-10-01-native-freecad-assembly/`, `workflow/archive/native-freecad-assembly-2026-10-01/`), in `CREDITS.md`'s two third-party entries and table rows, and nowhere else; record the count per file.

## 10. Validation

- [ ] 10.1 The whole suite, one process, from the framework's directory on the bench venv, without `MACHINOME_FREECAD_ROOT`: `env -u MACHINOME_FREECAD_ROOT -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider`, output to a file under the scratch directory. Record passed, skipped (each reason) and failed. Expected: no failure; 24 skips, the base's 20 and the four FreeCAD modules; the passed count the base's 4796 with each test this change adds or renames named.
- [ ] 10.2 The four FreeCAD modules with the runtime and the Dum-E variable, as 6.5, on the final tree: 82 passed.
- [ ] 10.3 The lint of 1.2 with `../machinome-node-freecad/machinome` added; record the count and the part the joined package and tests contribute.
- [ ] 10.4 The manual as in 7.4 on the final tree: success.
- [ ] 10.5 `scripts/check-dist` as in 8.5 on the final tree, and once on a clean copy of the tracked tree (`git ls-files -z | tar --null -T - -cf -` unpacked under the scratch directory, links kept), recording the archives' counts from both (the framework's sdist grows by the joined tests, fixtures and page; record by how much).
- [ ] 10.6 Dum-E, by the orchestrator, as design.md Decision 15 says: the project's edits in its own repository; its seven tests, the posed snapshot looked at and its SHA-256 compared with `40f8d56813970cbfc958c9e7e532646d2e31b20d754989271b42c20aecf3b804`, `machinome vet`'s exit and verdict; record each in `evidence.md`.
- [ ] 10.7 The universe sweep with the command of design.md Decision 17 after 10.6, `MACHINOME_FREECAD_ROOT` set. Expected: the base's counts but Dum-E's row ok (122 ok, 2 unexpected); any other difference reported with its explanation, not worked around.
- [ ] 10.8 Git: `git -C <bench> status --short` shows the edited and added files of groups 4 to 9 and nothing else; `git ls-files -ci --exclude-standard | wc -l` equals its count at the base.
- [ ] 10.9 `env -C <bench>/packages/machinome openspec validate join-freecad --strict`.
- [ ] 10.10 Stop before any commit and report to the orchestrator: the reds of 2.3, group 3, 7.1 and 8.3, the counts of 5.3, 6.3 to 6.5, 8.2, 8.5 and 10.1 to 10.7, and anything that departed from the design. Resume only on the orchestrator's message.

## 11. Records closing (after the orchestrator's review)

- [ ] 11.1 ADR-185 promoted to Accepted if written; `docs/adrs/README.md` updated; ADR-183's status and index lines note "amended by 185"; `docs/architecture.md` checked against it.
- [ ] 11.2 `env -C <bench>/packages/machinome openspec archive join-freecad -y` (the deltas synced into `openspec/specs/`, the renamed requirement applied), then the Purpose of `openspec/specs/native-freecad-assembly/spec.md` replaced by the text of design.md Decision 16, then `openspec validate --specs --strict`.
- [ ] 11.3 The root's `workflow/ongoing/joins-0.9.md`, "Progress": the cycle's entry with its branch, the planning commit, the merge commit, the ADR, the suite count of 10.1, the FreeCAD count of 10.2, the manual, `check-dist` with the clean copy's counts, the lock, Dum-E's result and the sweep's counts.
- [ ] 11.4 `evidence.md` complete; the implementation commit is the orchestrator's, never amending the planning or the merge commit; nothing pushed.
