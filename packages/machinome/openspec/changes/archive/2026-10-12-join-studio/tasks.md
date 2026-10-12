## 1. Evidence baseline

- [x] 1.1 Record the base: `git -C <bench> log --oneline -1` is the planning commit on top of the line's head with `join-movie` and `release-tooling` integrated (the orchestrator names it), the worktree clean but this change; start `evidence.md` in this change with it.
- [x] 1.2 Record the bench venv the orchestrator synced from the lock (the `__editable__` `.pth` files, no `machinome.studio` importable: `<bench>/.venv/bin/python -c "import machinome.studio"` raises `ModuleNotFoundError`) and the base counts the orchestrator names for that head without rerunning them: the suite, `uv lock`'s package count, the clean copy's framework sdist and wheel, `make check`'s members and archives.
- [x] 1.3 Record the probes of design.md the cycle relies on, by reference: probe 1 (738 files, 318 commits, fd139a5), probe 3 (the reds of the join), probe 4 (the seeded lock), probe 5 (the fastapi conflict, 195 packages on 675edac4), probes 6 to 9 (the resources, the archives, the wheels, the cost), probe 10 (the tests: 499 at the original, 443 at the new place before the pins, the OpenSpec CLI needed), probes 11 to 17.

## 2. The join (the orchestrator's, after the planning commit)

- [x] 2.1 The orchestrator clones `file:///home/asa/devel/machinome/machinome-studio` fresh under the scratch directory and runs the `git filter-repo` command of design.md Decision 2 (`<scratch>/filter-repo-command.sh`) in it; `git ls-tree -r --name-only main` lists the 738 paths of `<scratch>/rehearsal-ls-files.txt`, `main` is fd139a5, and no commit of `main` touches a path outside `packages/`, or each difference is explained.
- [x] 2.2 The orchestrator fetches `main` from that clone into the bench and merges it into `v0.9-joins-join-studio` with `git merge --allow-unrelated-histories`, one merge commit, no conflict. Record in `evidence.md`: the merge commit; `git log --format='%h %ad %s' --date=short -- packages/machinome-studio/machinome/studio/app.py` reaching the commit of 20 July 2026 without `--follow`, and the same on `packages/machinome-studio/machinome/studio/frontend/src/main.tsx`; `git ls-files -s packages/machinome-studio | grep ^120000` listing the four profile skill links; `git status --short` clean.
- [x] 2.3 On the joined tree, run `tests/test_repository_layout.py`, `test_release_records.py`, `test_core_names_no_split_words.py` and `test_node_root_exports_nothing.py` on the bench venv from the framework's directory. Expected red, design.md probe 3: the workspace source, the README, the table and the guide, each naming `machinome-studio`; the frontend's own lock; the member's version 0.1.0, the core's unpinned extra and the bump table; the split-word gate (13 occurrences in `mcp_server.py` and `preparation.py`); the node-root gate (26 offences in the two skills); and `TheMakefileTest` naming the directory (as `release-tooling` lands it). Record each reason; anything else red is investigated before group 3.

## 3. Red first, on the joined tree (nothing of the package's code or manifest changes in this group)

- [x] 3.1 `tests/test_repository_layout.py` (design.md Decision 10): the `PRODUCTS` row, `NODE_MEMBERS`'s third member, the tracked locks, the default group's `machinome[studio]`, the CI's OpenSpec step, the docstring. Run it. Expected red: the product's entries (no `LICENSE`, `LICENSES`, `MANIFEST.in`), its manifest (the former licence, `include`, `namespaces`), its README, its resolution (no installed package provides `machinome.studio`), the root `package.json`'s members, the frontend's lock, the default group, the CI step, and 2.3's four. Record each reason.
- [x] 3.2 `tests/test_release_records.py` (Decision 10): `test_the_studio_s_frontend_version_files_agree`. `tests/test_kernel_extras.py`: `EXTRAS['studio']`. Run them. Expected red: the frontend's version 0.0.0, no root lock entry, no bump table; the extra's unpinned requirement.
- [x] 3.3 `tests/test_vet_universe.py` (Decision 10): the denylist tuple and `test_the_studio_is_internal_and_its_former_name_outside`. Run it. Expected red: the tuple, and the first project vetted pure (design.md probe 12).
- [x] 3.4 `tests/test_core_names_no_split_words.py` (Decision 10): the `ORDINARY` and `ORDINARY_TEXT` entries of the studio's ordinary adjective. Run it. Expected red: the gate still fails, now only on the test tool's `kernel`, `exact` and `faceted` (seven occurrences, design.md probes 3 and 16).
- [x] 3.5 `tests/test_docs_structure.py` (Decision 13): the toctree entries, the section's toctree, the install page's distribution and lines, the CLI section, the stale spellings and their record. Run it. Expected red: the pages outside the navigation, the section, the install page, the CLI section, `python -m floor` and `machinome-studio --projects-dir` on the joined pages. Record each.
- [x] 3.6 The studio's tests rewritten as Decision 14 says: the address (`floor` to `machinome.studio`, the resource root, the import root), the copied profiles, `test_packaging.py`, `test_license_headers.py`, `test_machinome_identity.py`, `test_product_identity.py`, `test_documentation.py`, the new `test_the_studio_imports_no_framework_module` and `test_a_profile_skill_may_reach_another_package_through_shop_skills`, the browser tests' opt-in and their viewer at `machinome.viewer.web`, `test_scoped_tools.py`'s `engine`. Run them from `packages/machinome-studio` with `PYTHONPATH=<bench>/packages/machinome-studio` on the bench venv, the OpenSpec CLI on the PATH. Expected red: `ModuleNotFoundError` for `machinome.studio.cli` (the command module does not exist yet), the resource root naming `machinome/`, the link refused "must link directly to shop-skills/<skill>", the console script, the licence lines, the documentation's pages and facts, the tool's `engine`. Record each reason and which module the imports resolved to.
- [x] 3.7 Record in `evidence.md` every red of group 3 with its reason.

## 4. The package and its source

- [x] 4.1 The links, from `packages/machinome-studio/`: `ln -s ../../LICENSE LICENSE`, `ln -s ../../LICENSES LICENSES`; `git add` them; `git ls-files -s packages/machinome-studio | grep ^120000` lists them with the profile links.
- [x] 4.2 `pyproject.toml`, `README.md`, `MANIFEST.in` and `.gitignore` of design.md Decision 3, verbatim, in place of the product's.
- [x] 4.3 The 89 SPDX lines of the 88 current files of design.md "What the join touches" and the frontend's `package.json` `license`; `git diff` of each header shows that line and nothing else of it. `git grep -n 'SPDX-License-Identifier' -- packages/machinome-studio ':!packages/machinome-studio/openspec/changes/archive' ':!packages/machinome-studio/workflow'` shows the set's expression on every line but `tests/test_license_headers.py`'s pattern.
- [x] 4.4 The source of Decision 4: the lazy root; `preparation.shop_resource_root()`; `app.py`'s profile lookup; `mcp_server.mcp_command`'s module; the two backends' `PYTHONPATH` entry; `codex_auth`'s login line and import; `orchestrator.run`; the docstrings. `P/cli.py` (Decision 6) and `P/packaging.py` (Decision 3), each with the set's SPDX and copyright header; `flake8 --max-line-length=89` on them: 0.
- [x] 4.5 The tests of 3.6 that read the address, the resource root, the command and the packaging green; `test_floor_entrypoint.py`, `test_orchestrator.py`, `test_opencode_backend.py` and the Codex modules green.

## 5. The skills

- [x] 5.1 `P/shop-skills/machinome-simulate` and one link per profile, as design.md Decision 5 spells them; `git add`; each resolves to the skills package's `SKILL.md`.
- [x] 5.2 `profiles._skill_path` of Decision 5; the prompts of the builder, the designer and the machinist naming `machinome-simulate`; `test_a_profile_skill_may_reach_another_package_through_shop_skills`, `test_runtime_profiles.py`, `test_project_runtime_selection.py` and `test_openspec_tools.py` green.

## 6. The corrections the gates require (design.md Decision 7; as the pilot settles Open Questions 12)

- [x] 6.1 `mcp_server.machinome_test`'s `engine`, its refusal, docstring and schema; `test_scoped_tools.py` green; `tests/test_core_names_no_split_words.py` green.
- [x] 6.2 The two skills: the seven node-root imports from each name's module; every flag, variable, tool parameter and quoted output of `machinome test` in their 0.8 spelling, the output read from `machinome test --mesh` on the bench; `git diff` of each skill shows those lines alone. `tests/test_node_root_exports_nothing.py` green. Record in `evidence.md` the descriptive lines left with the 0.7 engine words, by skill and line.

## 7. The npm workspace

- [x] 7.1 The root `package.json`'s third member and the frontend's `package.json` of design.md Decision 8; `git rm` the frontend's `package-lock.json`; seed the root lock from it as Decision 8 says (the script kept under the scratch directory), then `env -C <bench> npm install --no-audit --no-fund` and `npm install --package-lock-only`. Expected: the frontend's 133 resolutions kept, none of the root's moved, "up to date"; record the comparison. If a resolution moved, stop and report.
- [x] 7.2 `env -C <bench> npm test --workspace packages/machinome-studio/machinome/studio/frontend` and `npm run build --workspace ...`: exit 0, `P/static/index.html` written; `npm run build --workspaces --if-present` builds the widget and the studio; `git -C <bench> status --short` shows no `node_modules/` or `static/`.

## 8. The core, the uv workspace and the sync

- [x] 8.1 The core's `pyproject.toml`'s `studio` extra and its comment (Decision 9); `machinome/vet/universe.toml`'s denylist line and its comment (Decision 10); `git diff` shows those hunks alone; `tests/test_vet_universe.py` and `tests/test_kernel_extras.py` green.
- [x] 8.2 The root `pyproject.toml`'s source, `exclude-dependencies` gone, the default group (Decision 9); `env -C <bench> /home/asa/.local/bin/uv lock` (expected: the base's count plus two, the member and tomlkit; record the diff's package lines); `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12` (one `__editable__` `.pth` file more). Then from `/tmp`: `<bench>/.venv/bin/python -c "import machinome.studio as s; print(s.__file__)"` names `P/__init__.py`; `import floor` raises `ModuleNotFoundError`; `machinome studio -h` lists `--projects-dir` and `--port`; `importlib.metadata.entry_points(group='machinome.commands')` holds `studio = machinome.studio.cli:Studio`. If the lock or the sync fails, stop and report.
- [x] 8.3 The seam's tests, `tests/test_cli_contributed.py` and `tests/test_cli_lazy_imports.py`, with the package installed: green, the walk reading `studio` (design.md probe 11). The cost of Decision 6: `python -X importtime -c "import machinome.studio.cli"` names no module of the startup requirement's list; `machinome -h` and `machinome studio -h` timed against the base, nine runs each, alternating; record the medians.
- [x] 8.4 `tests/test_repository_layout.py`, `test_release_records.py`, `test_core_names_no_split_words.py` and `test_node_root_exports_nothing.py` again. Expected green but the README, guide, Makefile, CI and bump tests (groups 11 and 12). Record.

## 9. The tests at their new place

- [x] 9.1 The studio's tests: `env -C <bench>/packages/machinome-studio <bench>/.venv/bin/python -m pytest -q -rfs -p no:cacheprovider` (no `PYTHONPATH`) with the built surface and the OpenSpec CLI on the PATH: expected green but the documentation tests group 10 settles; the browser tests skipping naming `MACHINOME_STUDIO_E2E`. Then once with `MACHINOME_STUDIO_E2E=1` and the widget's bundle built: the browser tests pass, the real-bundle test included. Record the counts against probe 10's (499 passed at the original).
- [x] 9.2 `env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest --collect-only -q -p no:cacheprovider | grep -c machinome-studio`: expected 0.

## 10. The manual

- [x] 10.1 Red first: a fresh venv under the scratch directory installing `packages/machinome/docs/requirements.txt` alone, then `env -C <bench>/packages/machinome <venv>/bin/python -m sphinx -b html -n -W --keep-going docs <scratch>/html-red`. Expected: exit 1 with the warnings of design.md probe 13 (43); record them.
- [x] 10.2 `docs/conf.py`'s release facts and substitutions, `docs/index.rst`'s four toctree lines (Decision 13).
- [x] 10.3 The section's index rewritten in place, the four reference pages and the three how-tos edited as Decision 13 says, the opening how-to's install part.
- [x] 10.4 The framework's pages of Decision 13: `start/install.rst`, `reference/cli.rst`, `project/status.rst`, `project/upgrading.rst`'s 0.8 sentence, each rewrapped at its width, the rest of each page unchanged.
- [x] 10.5 The build of 10.1 into `<scratch>/html`: exit 0, no warning. Open the section's index, the opening how-to and the command page in Chromium and look at them; record. `test_docs_structure.py` and the studio's `tests/test_documentation.py` green.

## 11. The version records, the Makefile, `scripts/check-dist` and CI

- [x] 11.1 `.bumpversion.cfg`'s three tables of design.md Decision 10. The bump on a copy, as `release-tooling` proves `make bump`: the configuration and the files it names copied under the scratch directory with the root `package-lock.json`, made a Git repository, `make bump VERSION=0.9.0` or its recipe's commands there; record that `git diff -U0` moves the studio's manifest version, its two pins, the frontend's `package.json` and the root lock's entry for it, and nothing else of the studio. Nothing is written in the bench.
- [x] 11.2 The Makefile's lines of Decision 11 (`PACKAGES`, `TESTED`, `STUDIO_FRONTEND`, `test-machinome-studio`, `CLEAN`); `TheMakefileTest` green; `make test PKG=machinome-studio` on the bench: the frontend's typecheck and build, then the studio's tests green.
- [x] 11.3 Red first: `env -C <bench> <bench>/.venv/bin/python scripts/check-dist` fails "machinome-studio has no smoke in scripts/check-dist"; record it.
- [x] 11.4 The npm refusal and the row of Decision 12, the docstring; `git diff` shows no line of another row changed. `flake8 --max-line-length=89 scripts/check-dist`: 0.
- [x] 11.5 `make check` (or `scripts/check-dist` on the tree and on a clean copy): seventeen members built, 34 archives `twine check --strict` passed, the studio's wheel installed by its path, its line printing 0.8.1 and "hub answered", `machinome studio -h` exit 0, nothing uploaded. Record the studio's archives' member counts (expected about 1172 and 113, design.md probe 7) and the framework's sdist growth by the eight pages; `git -C <bench> status --short` afterwards.
- [x] 11.6 `.github/workflows/python-app.yml`: the OpenSpec CLI step of Decision 11 in the `test` job; the layout gate's CI tests green.

## 12. The records

- [x] 12.1 `HISTORY.rst`, `docs/project/changelog.rst` and the studio's `CHANGELOG.md`: the entries of design.md Decision 15, verbatim. `test_release_records.py` green.
- [x] 12.2 `CREDITS.md`: the studio's section of Decision 15, its package versions read from the root lock and its fonts' copyright lines from their notices, the identity's statement as the pilot settles Open Questions 13, the skills section's source named; `P/frontend/public/assets/brand/README.md`'s pointer to `CREDITS.md`.
- [x] 12.3 `docs/architecture.md`: the section, the Commands paragraph and the Map row of Decision 15.
- [x] 12.4 The root `README.md`'s row, `CONTRIBUTING.rst`'s edits, `context7.json`'s folders and rule, and `AI-USE.md`'s edits of Decision 15. The layout gate's README, guide and index tests, and `test_release_records.py`'s context7 test green.
- [x] 12.5 `docs/adrs/BUILD/ADR-193-the-studio-is-a-product-of-the-set-reached-by-machinome-studio.md` as Decision 15 outlines it (Open Questions 10), Status Proposed; its index line under BUILD after ADR-192; ADR-182's, ADR-188's and ADR-189's notes and dated consequences.
- [x] 12.6 Grep the tracked files this change and the join added or changed (`git diff --name-only <planning commit>` and the 738 joined paths) for the licence the product carried and the framework's former one: found only in the studio's archived changes, `workflow/design/`, `workflow/spikes/`, `workflow/architecture-overview.md`'s line on the viewer, `workflow/archive/`, its decision log, and third-party provenance in `CREDITS.md`; record the count per file.

## 13. The product's record, brought current in place

- [x] 13.1 The studio's specs, `openspec/config.yaml`, `workflow/README.md`, `workflow/documentation.md`, `P/frontend/README.md`, `scripts/test-e2e`, `scripts/build-favicon` and the decision log's note of design.md Decisions 14 to 16, in place.
- [x] 13.2 `env -C <bench>/packages/machinome-studio openspec validate --specs --strict`: passes (record the CLI's report; if the CLI cannot run there, record why).

## 14. Validation and the originating check

- [x] 14.1 The whole suite, one process, from the framework's directory on the bench venv with the bundles built (`make test PKG=machinome`, or `env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider`), output to a file under the scratch directory. Record passed, skipped (each reason) and failed. Expected: no failure; the base's skips; the passed count the base's plus the tests this change adds, named.
- [x] 14.2 The studio's tests as 9.1, and `make test` for every package with tests: no failure; record the counts.
- [x] 14.3 The lint: `make lint`; record the count and the part the studio contributes (CI's lint step is `continue-on-error`).
- [x] 14.4 The manual as in 10.5 on the final tree: exit 0.
- [x] 14.5 `scripts/check-dist` as in 11.5 on the final tree and on a clean copy of the tracked tree; record both runs' counts.
- [x] 14.6 No universe sweep: record that no project repository imports `floor` or `machinome.studio` or names `machinome-studio --projects-dir` (the grep of design.md's Context, rerun), and that the core's one change a model could reach is the vet's denylist.
- [x] 14.7 The originating check of design.md Decision 18 on the bench venv: `machinome studio --projects-dir <scratch catalogue> --port <a free port other than 9010>` with a fresh clone of `Vibecoded-demos/gear-shift`; the hub photographed in Chromium; then `python -m machinome.studio` on the same catalogue, the project opened by `POST /api/sessions` (no agent run), its floor page photographed with the gearbox in the viewer; both stopped, the port free, the clone's `git status` clean; look at both photographs and record the commands, the PNGs and what they show.
- [x] 14.8 Git: `git -C <bench> status --short` shows the edited, added and removed files of groups 3 to 13 and nothing else; `git ls-files -ci --exclude-standard | wc -l` equals its count at the base.
- [x] 14.9 `env -C <bench>/packages/machinome openspec validate join-studio --strict`.
- [x] 14.10 Stop before any commit and report to the orchestrator: the reds of 2.3, group 3, 10.1 and 11.3, the counts of 7.1, 8.2, 8.3, 9.1, 11.1, 11.5 and 14.1 to 14.7, and anything that departed from the design. Resume only on the orchestrator's message.

## 15. Records closing (after the orchestrator's review)

- [x] 15.1 ADR-193 promoted to Accepted if written; `docs/adrs/README.md` updated; `docs/architecture.md` checked against it.
- [x] 15.2 `env -C <bench>/packages/machinome openspec archive join-studio -y`, then `openspec validate --specs --strict`.
- [x] 15.3 The root's `workflow/ongoing/release-0.9.md`, "Progress": the cycle's entry with its branch, the planning commit, the merge commit, the ADR, the suite's count, the studio's tests, the manual, `check-dist` with the clean copy's counts, the lock and the originating check.
- [x] 15.4 `evidence.md` complete; the implementation commit and the integration are the orchestrator's, never amending the planning or the merge commit; nothing pushed.
