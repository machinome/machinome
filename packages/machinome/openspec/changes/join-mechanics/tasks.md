## 1. Evidence baseline

- [ ] 1.1 Record the base: `git -C <bench> log --oneline -1` is the planning commit on top of d5d194ad (or the line's head the orchestrator names), the worktree clean but this change; start `evidence.md` in this change with it.
- [ ] 1.2 Record the bench venv the orchestrator synced from the lock (twelve `__editable__` `.pth` files; `machinome-mechanics` 0.1.0 from PyPI, `site-packages/machinome_mechanics/`) and the base counts the orchestrator names for d5d194ad without rerunning them: the suite (4827 passed, 24 skipped at the digest integration), the lint, the sweep of `join-freecad` (63 repositories, 130 rows, 122 ok, 0 expected, 2 unexpected, 0 timeout, 6 no-model), the clean copy's framework sdist and wheel.
- [ ] 1.3 Record the probes of design.md the cycle relies on, by reference: probe 1 (main 34 failed, 2 errors; the branch 38 failed, 2 errors), probe 2 (the branch 201 passed with fourteen lines), probe 3 (195 passed on published 0.8.0), probe 4 (157 files, 45 commits, 4d3e075, `mechanics-v0.1.0`), probe 6 (the reds of the join), probe 7 (198 passed, 3 failed at the new place; the core collects none), probe 9 (the folded manual: exit 1 at the join, 141 examples green after), probe 10 (188 packages; uv does not check the floors), probe 11 (pip chooses the published wheel), probe 14 (the deltas archive).

## 2. The join (the orchestrator's, after the planning commit)

- [ ] 2.1 The orchestrator clones `file:///home/asa/devel/machinome/machinome-mechanics` fresh under the scratch directory and runs the `git filter-repo` command of design.md Decision 2 in it; `git ls-tree -r --name-only v0.8-symbolic-assertions` lists the 157 paths of `<scratch>/rehearsal-ls-files.txt`, no commit of any branch touches a path outside `packages/`, the branch's head is 4d3e075 and the tag `mechanics-v0.1.0` exists, or each difference is explained.
- [ ] 2.2 The orchestrator fetches `v0.8-symbolic-assertions` and `refs/tags/mechanics-v0.1.0` from that clone into the bench and merges the branch into `v0.9-joins-join-mechanics` with `git merge --allow-unrelated-histories`, one merge commit, no conflict. Record in `evidence.md`: the merge commit; `git log --follow --format='%h %ad %s' --date=short -- packages/machinome-mechanics/machinome/mechanics/belts.py` reaching the commit of 20 September 2026 that wrote it; `git log` on `packages/machinome-mechanics/machinome/mechanics/gears.py` reaching the founding commit of 11 September 2026; `git tag -l 'mechanics-*'`; `git status --short` clean.
- [ ] 2.3 On the joined tree, run `tests/test_repository_layout.py`, `test_release_records.py`, `test_core_names_no_scad.py` and `test_node_root_exports_nothing.py` on the bench venv from the framework's directory. Expected red, design.md probe 6: `test_every_member_is_a_workspace_source`, `test_the_readme_links_every_package_and_states_the_licence`, `test_every_sibling_is_in_the_table`, `test_the_guide_installs_every_member_without_uv`; `test_every_member_is_numbered_with_the_core`, `test_every_pin_between_members_is_compatible`, `test_the_version_is_bumped_from_the_root`; the core-names gate on `__init__.py` (two) and `linkages.py` (one); the root-import scan on the two test modules and the two example modules. Record each reason. Anything else red is investigated before group 3.

## 3. Red first, on the joined tree (nothing of the package changes in this group)

- [ ] 3.1 `tests/test_mechanics_boundary.py` (design.md Decision 6): the extra expected as `["machinome-mechanics>=0.1.0"]`; the guard refusing `machinome.mechanics` and below; the new `test_the_guard_refuses_the_helpers_address`. Run it. Expected red: the extra (bare), and the control (under the old guard `import machinome.mechanics` is not refused; it fails otherwise, since no installed package provides the address yet: record which). The guard edit itself keeps `test_math_and_motion_work_with_helpers_refused` green.
- [ ] 3.2 `tests/test_repository_layout.py` (Decision 6): `PRODUCTS`, `TheProductsTest`, the sibling test reading both tables, the index test admitting a product's folders, `test_the_test_job_runs_each_product_s_tests`, the docstring. Run it. Expected red: the product's manifest (licence, `include`, dependency), its README (no install line, no licence), its entries (no `LICENSE` or `LICENSES` link), its resolution (the PyPI 0.1.0 provides no `machinome.mechanics`), the CI step, and 2.3's workspace, README and guide tests. Record each reason.
- [ ] 3.3 `tests/test_release_records.py` (Decisions 6 and 7): `OWN_VERSION`, the two skips, the floors in the pin test, `test_a_member_of_its_own_version_is_outside_the_bump`, the docstring. Run it. Expected red: the pin test (the core's bare requirement is no floor; the product's `machinome>=0.7.0` passes as a floor), and the new test if `mechanics_version` or the changelog disagree with the manifest (expected green on those; record). `test_every_member_is_numbered_with_the_core` and `test_the_version_is_bumped_from_the_root` turn green with the skip.
- [ ] 3.4 `tests/test_vet_universe.py` (Decision 6): the contract `('machinome', 'molejo')` and `test_the_mechanics_helpers_are_inside_and_their_former_name_outside`. Run it. Expected red: the contract, and the former name vetted pure.
- [ ] 3.5 `tests/test_docs_structure.py` (Decision 10): the How-to toctree names `howto/mechanism-formulas` and the Reference toctree `reference/mechanics/index`; the section's toctree lists `conventions` and the nine families in order; `KernelExtrasTest.STALE` gains `'machinome' '_mechanics'` and `'machinome-mechanics.readthedocs'`, with `RECORDS` admitting the former name on `project/changelog.rst` and `project/upgrading.rst`; the distributions' test gains `machinome-mechanics`; a test that `mechanics_version` equals `packages/machinome-mechanics/pyproject.toml`'s version. Run it. Expected red: the two toctrees, the stale spellings on the pages that link the separate manual, the installation page's distribution. Record each.
- [ ] 3.6 The package's `tests/test_documentation.py` and `tests/test_machinome_identity.py`, rewritten as design.md Decision 11 says. Run them from `packages/machinome-mechanics` with `PYTHONPATH=<bench>/packages/machinome-mechanics` on the bench venv. Expected red: the identity test's manifest, licence, `include`, Homepage and the modules' imports of `machinome_mechanics`; the documentation test's links to Read the Docs on the pages and the how-to's examples (the root import of `AssemblyNode`). Record each reason and which module `machinome_mechanics` resolved to.
- [ ] 3.7 Record in `evidence.md` every red of group 3 with its reason.

## 4. The package

- [ ] 4.1 The links, from `packages/machinome-mechanics/`: `ln -s ../../LICENSE LICENSE`, `ln -s ../../LICENSES LICENSES`; `git add` them; `git ls-files -s packages/machinome-mechanics | grep ^120000` lists two with those targets.
- [ ] 4.2 `pyproject.toml`, `README.md`, `MANIFEST.in` and `.gitignore` of design.md Decision 3, verbatim, in place of the product's.
- [ ] 4.3 The nineteen SPDX lines of Decision 3; `git diff` of each file shows that line and nothing else of its header.
- [ ] 4.4 The source of Decision 4: the ten internal import lines, `__init__.py`'s docstring paragraphs and sentence, `linkages.py`'s sentence; `git diff` of the package directory shows those and the headers, nothing else. `test_core_names_no_scad.py` green.

## 5. The core and the workspace

- [ ] 5.1 The core's `pyproject.toml`: the `mechanics` extra and its comment of Decisions 5 and 6; `git diff` shows that hunk alone.
- [ ] 5.2 The root `pyproject.toml`'s source of Decision 5; `env -C <bench> /home/asa/.local/bin/uv lock` (expected "Resolved 188 packages"; record the lock's diff, expected that of probe 10); `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12` (expected thirteen `__editable__` `.pth` files; record them and the line uninstalling the PyPI 0.1.0). Then from `/tmp`: `<bench>/.venv/bin/python -c "import machinome.mechanics as m; print(m.__file__)"` names the bench's package directory, and `<bench>/.venv/bin/python -c "import machinome_mechanics"` fails with `ModuleNotFoundError`. If the lock or the sync fails, stop and report. `git -C <bench> status --short` shows no build leaving under `packages/machinome-mechanics`.
- [ ] 5.3 `machinome/vet/universe.toml`: the contract of Decision 6. `tests/test_vet_universe.py` green.
- [ ] 5.4 `tests/test_mechanics_boundary.py`, `test_repository_layout.py` and `test_release_records.py` again. Expected green but the README, guide and CI tests (groups 9 and 10) and anything named there. Record.

## 6. The tests at their new place

- [ ] 6.1 The package's tests: `machinome_mechanics` to `machinome.mechanics` and the fourteen lines of design.md Decision 11; `test_mechanisms.py`'s docstring; `git diff` of each module shows those lines and nothing else.
- [ ] 6.2 `env -C <bench>/packages/machinome-mechanics <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider` (no `PYTHONPATH`): expected green but `test_documentation.py`'s example and link tests (group 7). Record the counts.
- [ ] 6.3 `env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest --collect-only -q -p no:cacheprovider | grep -c machinome-mechanics`: expected 0.

## 7. The manual

- [ ] 7.1 Red first: a fresh venv under the scratch directory installing `packages/machinome/docs/requirements.txt` alone, then `env -C <bench>/packages/machinome <venv>/bin/python -m sphinx -b html -n -W --keep-going docs <scratch>/html-red`. Expected: exit 1, the warnings and errors of design.md probe 9 (three pages in no toctree, the former layout's links and includes, the drawings, `Unknown directive type "doctest"`); record them.
- [ ] 7.2 `docs/conf.py`: `sphinx.ext.doctest` and `mechanics_version`'s comment (Decision 10). `docs/index.rst`: the two toctree lines.
- [ ] 7.3 `reference/mechanics/index.rst` rewritten in place and the family and conventions pages edited, as Decision 10 says; `howto/mechanism-formulas.rst` converted in place with its first examples, and its two example modules' imports.
- [ ] 7.4 The framework's pages of Decision 10: `start/install.rst`, `reference/api.rst`, `concepts/relations.rst`, `howto/timeline.rst`, `reference/manuals.rst`, `project/upgrading.rst`'s link, each rewrapped at its width, the rest of each page unchanged.
- [ ] 7.5 The build of 7.1 into `<scratch>/html`: exit 0, no warning. Look at the rendered section index, the cranks page's drawing, the linkages page's drawing and the how-to with its downloads; record. `test_docs_structure.py`, `test_docs_exports.py` and `test_node_root_exports_nothing.py` green; the package's `tests/test_documentation.py` green (expected 141 or more examples, none failed; record the count per page).

## 8. The version records, `scripts/check-dist` and CI

- [ ] 8.1 The bump on a copy, as `join-freecad` did: the root's `.bumpversion.cfg` and the files it names copied under the scratch directory with `packages/machinome-mechanics/pyproject.toml`, made a git repository, `bump2version --no-commit --no-tag --new-version 0.9.0 patch`; record that `git diff -U0` changes none of the mechanics manifest's lines. Nothing is written in the bench.
- [ ] 8.2 Red first: `env -C <bench> <bench>/.venv/bin/python scripts/check-dist` fails "machinome-mechanics has no smoke in scripts/check-dist"; record it.
- [ ] 8.3 `MECHANICS_VERSION` and the row of design.md Decision 9; `git diff` shows no line of another row changed. `flake8 --max-line-length=89 scripts/check-dist`: 0.
- [ ] 8.4 Run it: thirteen members built, 26 archives `twine check --strict` passed, the mechanics wheel installed by its path, its line printing 0.1.0, its module inside the venv and "numeric and symbolic", the licence files listed, nothing uploaded. Record the archives' member counts and `git -C <bench> status --short` afterwards.
- [ ] 8.5 `.github/workflows/python-app.yml`: the step of Decision 8. The layout gate's CI tests green.

## 9. The records

- [ ] 9.1 `HISTORY.rst`, `docs/project/changelog.rst` and the package's `CHANGELOG.md`: the entries of design.md Decision 12, verbatim; the 0.1.0 bullet as the orchestrator decides (Open Questions 5). `test_release_records.py` and `test_profile_documentation.py` green.
- [ ] 9.2 `CREDITS.md`: unchanged; record the product's `NOTICE` text as the reason.
- [ ] 9.3 `docs/architecture.md`: the section, the extras sentence and the Map row of Decision 12.
- [ ] 9.4 The root `README.md`'s row, `packages/machinome/README.rst`'s sentence, `CONTRIBUTING.rst`'s pip block and test sentence, `context7.json`'s folders and rule, and `AI-USE.md`'s two edits of Decision 12. The layout gate's README, guide, link and index tests, `test_docs_structure.py`'s `ReadmeTest` and `test_release_records.py`'s context7 test green.
- [ ] 9.5 Unless the orchestrator declined it (design.md Open Questions 2): `docs/adrs/BUILD/ADR-187-the-mechanics-helpers-are-a-portion-of-the-repository-at-their-own-version.md` as Decision 12 outlines it, Status Proposed; its index line under BUILD after ADR-183; ADR-132's and ADR-183's and ADR-182's notes and dated consequences. If declined: the dated consequences alone, ADR-132's superseding note, and the HISTORY bullet's "(ADR-187)" as Open Questions 2 says.
- [ ] 9.6 The product's record of design.md Decision 13, in place: its three specs, `openspec/config.yaml`, `workflow/README.md` and `workflow/documentation.md`; `env -C <bench>/packages/machinome-mechanics openspec validate --specs --strict` passes (record the CLI's report; if the CLI cannot run there, record why).
- [ ] 9.7 Grep the tracked files this change and the join added or changed (`git diff --name-only <planning commit>` and the 157 joined paths) for the licence the product carried and the framework's former licence: found only in the product's sixteen archived changes, its workflow notes but `README.md` and `documentation.md`, and the changelog's 0.1.0 section unless Open Questions 5 removes it; record the count per file.

## 10. Validation

- [ ] 10.1 The whole suite, one process, from the framework's directory on the bench venv: `env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider`, output to a file under the scratch directory. Record passed, skipped (each reason) and failed. Expected: no failure; the base's skips; the passed count the base's with each test this change adds named.
- [ ] 10.2 The package's tests from its directory as 6.2: no failure; record the counts (expected 201 formula and integration tests and the rewritten pinning tests).
- [ ] 10.3 The lint: `flake8 --max-line-length=89 machinome tests` and the `../machinome-*/machinome` paths from the framework's directory; record the count and the part the package contributes (probe 13: 5).
- [ ] 10.4 The manual as in 7.5 on the final tree: exit 0.
- [ ] 10.5 `scripts/check-dist` as in 8.4 on the final tree, and once on a clean copy of the tracked tree (`git ls-files -z | tar --null -T - -cf -` unpacked under the scratch directory, links kept), recording the archives' counts from both (the framework's sdist grows by the joined manual pages, drawings and examples; record by how much).
- [ ] 10.6 Git: `git -C <bench> status --short` shows the edited and added files of groups 3 to 9 and nothing else; `git ls-files -ci --exclude-standard | wc -l` equals its count at the base.
- [ ] 10.7 `env -C <bench>/packages/machinome openspec validate join-mechanics --strict`.
- [ ] 10.8 Stop before any commit and report to the orchestrator: the reds of 2.3, group 3, 7.1 and 8.2, the counts of 5.2, 6.2, 6.3, 7.5, 8.1, 8.4 and 10.1 to 10.5, and anything that departed from the design. Resume only on the orchestrator's message.

## 11. The projects' move and the sweep (the orchestrator's, after the implementation commit)

- [ ] 11.1 The workspace's `scripts/load-projects.d/join-mechanics.toml` of design.md Decision 15, in the workspace under its own process. The sweep of Decision 17 on the bench: record the rows of the 27 repositories as expected on `machinome_mechanics` and every other row as at the base.
- [ ] 11.2 The move of Decision 16 in each of the 27 repositories, under its own process, with its commit message; record each repository's commit and its files touched.
- [ ] 11.3 Thor (`simulation/test_thor.py`), 3DPrintedClocks (`simulation/test_*.py`) and dragon-r1 (`simulation/test_*.py`) on the bench venv: their counts.
- [ ] 11.4 The sweep of Decision 17 again: expected the base's counts row for row (63 repositories, 130 rows, 122 ok, 0 expected, 2 unexpected, 0 timeout, 6 no-model); any difference reported with its explanation, not worked around. Record in `evidence.md`.

## 12. Records closing (after the orchestrator's review)

- [ ] 12.1 ADR-187 promoted to Accepted if written; `docs/adrs/README.md` updated; `docs/architecture.md` checked against it.
- [ ] 12.2 `env -C <bench>/packages/machinome openspec archive join-mechanics -y` (expected "~ 6 modified, → 1 renamed", probe 14), then `openspec validate --specs --strict`.
- [ ] 12.3 The root's `workflow/ongoing/joins-0.9.md`, "Progress": the cycle's entry with its branch, the planning commit, the merge commit, the ADR, the suite count of 10.1, the package's count of 10.2, the manual, `check-dist` with the clean copy's counts, the lock, the projects' move and the sweep's counts.
- [ ] 12.4 `evidence.md` complete; the implementation commit is the orchestrator's, never amending the planning or the merge commit; nothing pushed.
