## 1. Evidence baseline

- [x] 1.1 Record the base: `git -C <bench> log --oneline -1` is the planning commit on top of 5af14f71 (or the line's head the orchestrator names), the worktree clean but this change; start `evidence.md` in this change with it.
- [x] 1.2 Record the bench venv the orchestrator synced from the lock (thirteen `__editable__` `.pth` files, no `machinome.skills` importable: `<bench>/.venv/bin/python -c "import machinome.skills"` raises `ModuleNotFoundError`) and the base counts the orchestrator names for 5af14f71 without rerunning them: the suite (4854 passed, 24 skipped, 7508 subtests), the CLI modules (`test_cli_lazy_imports.py` and `test_cli.py`), the clean copy's framework sdist and wheel.
- [x] 1.3 Record the probes of design.md the cycle relies on, by reference: probe 1 (OpenSpec's 31 ids, its marker and its update rule), probe 2 (OpenSpec overwrote an unmarked skill), probe 3 (the clients' directories), probe 4 (8 files, the rewritten subject), probe 5 (the merge clean; the five reds of the join), probe 6 (the seam's four reds with a real contributor), probe 7 (`agent-skills/` builds without warnings; 16 wheel entries; PyPI 404), probe 8 (the command from the wheel), probe 9 (the prompt), probe 10 (cost), probe 11 (189 packages), probe 12 (no project names the package), probe 13 (the deltas archive).

## 2. The join (the orchestrator's, after the planning commit)

- [x] 2.1 The orchestrator clones `file:///home/asa/devel/machinome/machinome-skills` fresh under the scratch directory, writes the message expression file of design.md Decision 1 from `git log -1 --format=%s`, and runs the `git filter-repo` command of Decision 1 in the clone; `git ls-tree -r --name-only main` lists the 8 paths of `<scratch>/rehearsal-ls-files.txt`, the head is 9a23c9a, no path lies outside `packages/machinome-skills/`, and the subject is "Create portable machinome skills package", or each difference is explained.
- [x] 2.2 The orchestrator fetches `main` from that clone into the bench and merges it into `v0.9-joins-join-skills` with `git merge --allow-unrelated-histories`, one merge commit, no conflict. Record in `evidence.md`: the merge commit; `git log --follow --format='%h %ad %an %s' --date=short` on `packages/machinome-skills/machinome/skills/agent-skills/machinome/SKILL.md` and on `packages/machinome-skills/tests/test_skill_format.py`, each reaching the rewritten commit of 20 September 2026; `git status --short` clean.
- [x] 2.3 On the joined tree, run `tests/test_repository_layout.py` and `tests/test_release_records.py` on the bench venv from the framework's directory. Expected red, design.md probe 5: `test_every_member_is_a_workspace_source`, `test_the_members_are_the_package_directories`, `test_the_readme_links_every_package_and_states_the_licence`, `test_every_sibling_is_in_the_table` and `test_the_guide_installs_every_member_without_uv`, each naming `machinome-skills`. Record each reason. Anything else red is investigated before group 3.

## 3. Red first, on the joined tree (nothing of the package's code or manifest exists in this group)

- [x] 3.1 `tests/test_repository_layout.py` (design.md Decision 12): the `PRODUCTS` row, the products' tests-and-specs test, the default group's test renamed with the three entries, the docstring. Run it. Expected red: the product's entries (no `pyproject.toml`, `MANIFEST.in`, `LICENSE`, `LICENSES`), its manifest and README, its resolution (`ModuleNotFoundError: No module named 'machinome.skills'`), the CI step, the default group, and 2.3's five. Record each reason.
- [x] 3.2 `tests/test_machinome_identity.py` and `tests/test_kernel_extras.py` (Decision 12). Run them. Expected red: `KeyError: 'skills'` in each.
- [x] 3.3 `tests/test_docs_structure.py` (Decisions 12 and 15): the how-to in the navigation and its spellings, `machinome-skills` on the installation page, the command reference's section and the retired "to add" wording. Run it. Expected red: the page absent, the distribution, the section. Record each.
- [x] 3.4 The package's `tests/test_skill_format.py`, rewritten in place from `check.py` as Decision 11 says, and `tests/test_command.py`, new. Run them from `packages/machinome-skills` with `PYTHONPATH=<bench>/packages/machinome-skills` on the bench venv. Expected red: the licence test on both skills (the field names the licence the product carried); the manifest-pattern test (no manifest yet); `test_command.py` failing at collection with `ModuleNotFoundError` for `machinome.skills.installer`. Record each reason.
- [x] 3.5 Record in `evidence.md` every red of group 3 with its reason.

## 4. The package

- [x] 4.1 The links, from `packages/machinome-skills/`: `ln -s ../../LICENSE LICENSE`, `ln -s ../../LICENSES LICENSES`; `git add` them; `git ls-files -s packages/machinome-skills | grep ^120000` lists two with those targets.
- [x] 4.2 `pyproject.toml`, `MANIFEST.in` and `README.md` of design.md Decision 2, verbatim, the README replacing the product's in place; `.gitignore` edited in place.
- [x] 4.3 The licence line of each `SKILL.md` (Decision 4); `git diff <merge commit> -- packages/machinome-skills/machinome/skills/agent-skills` shows those two lines and nothing else.
- [x] 4.4 `machinome/skills/__init__.py`, `cli.py`, `installer.py` and `tools.toml` of Decisions 3 and 5 to 9, the registry's 32 rows as Decision 5's table; every module with the set's SPDX and copyright header; `flake8 --max-line-length=89` on them: 0.

## 5. The core, the workspace and the sync

- [x] 5.1 The core's `pyproject.toml`: the `skills` extra and its comment of Decision 10; `git diff` shows that hunk alone.
- [x] 5.2 The root `pyproject.toml`'s source and dev group of Decision 10; `env -C <bench> /home/asa/.local/bin/uv lock` (expected "Resolved 189 packages"; record the lock's diff, expected that of probe 11); `env -C <bench> /home/asa/.local/bin/uv sync --python 3.12` (expected fourteen `__editable__` `.pth` files; record them). Then from `/tmp`: `<bench>/.venv/bin/python -c "import machinome.skills as s; print(s.__file__)"` names the bench's package directory and `<bench>/.venv/bin/machinome skills -h` lists the three verbs. If the lock or the sync fails, stop and report. `git -C <bench> status --short` shows no build leaving under `packages/machinome-skills`.
- [x] 5.3 The package's tests again, from its directory without `PYTHONPATH`: expected green; record the counts. `env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest --collect-only -q -p no:cacheprovider | grep -c machinome-skills`: expected 0.
- [x] 5.4 `tests/test_repository_layout.py`, `test_machinome_identity.py`, `test_kernel_extras.py` and `test_release_records.py` again. Expected green but the README, guide and CI tests (groups 8 and 9) and `test_the_version_is_bumped_from_the_root` (group 8). Record.

## 6. The seam's tests with a real contributor

- [x] 6.1 Run `tests/test_cli_contributed.py` and `tests/test_cli_lazy_imports.py` on the synced venv. Expected red, design.md probe 6: `test_a_second_contributor_runs`, `test_help_lists_contributed_commands_after_the_framework`, `test_a_module_that_cannot_be_imported`, `test_the_contract_walk_reads_a_fake_distribution`; `test_every_contributed_entry_resolves_and_honours_the_contract` green, walking `machinome-skills`. Record each reason.
- [x] 6.2 The edits of Decision 12 to `tests/contributed_commands.py` (`fake-lessons`), `tests/test_cli_contributed.py` (the computed choices; `lessons install`) and `tests/test_cli_lazy_imports.py` (the fakes' failures alone). Run the two modules and `tests/test_cli.py`: green; record the counts.
- [x] 6.3 The walk's need, shown once: a temporary edit deleting `needs_node` from `Skills` in `packages/machinome-skills/machinome/skills/cli.py`, one run of `test_every_contributed_entry_resolves_and_honours_the_contract`: red naming the term; the edit reverted, `git diff` of `cli.py` back to the change's. Record.

## 7. The manual

- [x] 7.1 `docs/howto/assistant-skills.rst` (Decision 15) and its line in `docs/index.rst`'s How-to toctree after `howto/mechanism-formulas`; `start/install.rst`'s extras paragraph and "Packages and licences"; `reference/cli.rst`'s sentence and the section `machinome skills` with `.. _skills-command:`.
- [x] 7.2 A fresh venv under the scratch directory installing `packages/machinome/docs/requirements.txt` alone, then `env -C <bench>/packages/machinome <venv>/bin/python -m sphinx -b html -n -W --keep-going docs <scratch>/html`: exit 0, no warning. Look at the rendered how-to and the command reference's section; record. `test_docs_structure.py` green.

## 8. The version records, `scripts/check-dist` and CI

- [x] 8.1 `.bumpversion.cfg`'s two tables of design.md Decision 13. `test_release_records.py` green. The bump on a copy: the root's `.bumpversion.cfg` and the files it names copied under the scratch directory, made a git repository, `bump2version --no-commit --no-tag --new-version 0.9.0 patch`; record that `git diff -U0` moves the skills manifest's version and its `machinome~=` pin, and the core's `machinome-skills~=` pin, to 0.9.0. Nothing is written in the bench.
- [x] 8.2 Red first: `env -C <bench> <bench>/.venv/bin/python scripts/check-dist` fails "machinome-skills has no smoke in scripts/check-dist"; record it.
- [x] 8.3 The row of Decision 14; `git diff` shows no line of another row changed. `flake8 --max-line-length=89 scripts/check-dist`: 0.
- [x] 8.4 Run it: fourteen members built, 28 archives `twine check --strict` passed, the skills wheel installed by its path, its line printing the set's version 0.8.1 and "installed 8 files for agents and claude", `machinome skills list: exit 0`, the licence files listed, nothing uploaded. Record the archives' member counts (the skills wheel 16, its sdist with `workflow/evaluation.md`) and `git -C <bench> status --short` afterwards.
- [x] 8.5 `.github/workflows/python-app.yml`: the step of Decision 14. The layout gate's CI tests green.

## 9. The records

- [x] 9.1 `HISTORY.rst` and `docs/project/changelog.rst`: the entries of design.md Decision 16, verbatim. `test_release_records.py` green.
- [x] 9.2 `CREDITS.md`: the section and the date of Decision 16; the product's `NOTICE` text (from the original repository) recorded in `evidence.md` as its source.
- [x] 9.3 `docs/architecture.md`: the CLI sentence, the section, the extras sentence and the Map row of Decision 16.
- [x] 9.4 The root `README.md`'s row, `CONTRIBUTING.rst`'s pip line and test sentence, `context7.json`'s folders and rule, and `AI-USE.md`'s phrase of Decision 16. The layout gate's README, guide, link and index tests and `test_release_records.py`'s context7 test green.
- [x] 9.5 The product's `workflow/evaluation.md` brought current in place, as Decision 16 says; its live cases and its validation boundary of 20 September 2026 unchanged (`git diff` shows the "Mechanical checks" section and the new section only).
- [x] 9.6 Unless the orchestrator declined it (design.md Open Questions 5): `docs/adrs/BUILD/ADR-190-the-machinome-skills-are-a-package-of-the-set-installed-by-a-command.md` as Decision 16 outlines it, Status Proposed; its index line under BUILD after ADR-189's. If declined: the HISTORY bullet ends "(ADR-189)".
- [x] 9.7 Grep the tracked files this change and the join added or changed (`git diff --name-only <planning commit>`) for the licence the product carried and the framework's former licence: found in no file of the final tree; the joined commit's subject names neither (`git log -1 --format=%s <the joined commit>`); record the counts.

## 10. Validation and the originating check

- [x] 10.1 The whole suite, one process, from the framework's directory on the bench venv: `env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider`, output to a file under the scratch directory. Record passed, skipped (each reason) and failed. Expected: no failure; the base's skips; the passed count the base's with each test this change adds named.
- [x] 10.2 The package's tests from its directory as 5.3: no failure; record the counts.
- [x] 10.3 The lint: `flake8 --max-line-length=89 machinome tests` and the `../machinome-*/machinome` paths from the framework's directory; record the count and the part the package contributes (expected 0).
- [x] 10.4 The manual as in 7.2 on the final tree: exit 0.
- [x] 10.5 `scripts/check-dist` as in 8.4 on the final tree, and once on a clean copy of the tracked tree (`git ls-files -z | tar --null -T - -cf -` unpacked under the scratch directory, links kept), recording the archives' counts from both (the framework's sdist grows by the how-to; record by how much).
- [x] 10.6 The originating check of design.md Decision 17, in a scratch git project with the bench venv's `machinome`: `machinome skills install --tools agents,claude`; the eight files at the paths Codex's and Claude Code's documentation name, each `SKILL.md`'s `name` equal to its directory and carrying the marker; where `claude` or `codex` is on the PATH, each asked to list the project's skills, the answer recorded (or "not run: <program> absent"); one copy's marker edited to 0.8.0 and `machinome skills update` rewriting it alone; `git -C <project> status --short` showing `.agents/` and `.claude/` only.
- [x] 10.7 The projects' grep of design.md probe 12 repeated on the day: 0 files, so no universe sweep; record.
- [x] 10.8 Git: `git -C <bench> status --short` shows the edited and added files of groups 3 to 9 and nothing else; `git ls-files -ci --exclude-standard | wc -l` equals its count at the base.
- [x] 10.9 `env -C <bench>/packages/machinome openspec validate join-skills --strict`.
- [x] 10.10 Stop before any commit and report to the orchestrator: the reds of 2.3, group 3, 6.1, 6.3 and 8.2, the counts of 5.2, 5.3, 6.2, 7.2, 8.1, 8.4 and 10.1 to 10.7, and anything that departed from the design. Resume only on the orchestrator's message.

## 11. Records closing (after the orchestrator's review)

- [x] 11.1 ADR-190 promoted to Accepted if written; `docs/adrs/README.md` updated; `docs/architecture.md` checked against it.
- [x] 11.2 `env -C <bench>/packages/machinome openspec archive join-skills -y` (expected `skills-distribution` created and totals + 8, ~ 3, as design.md probe 13); replace the created spec's placeholder Purpose with "Ship the machinome skills for assistants that read Agent Skills, at the set's version and under its licence, and install them where each assistant reads its skills through `machinome skills`, never overwriting what the command did not write and never deleting."; then `openspec validate --specs --strict` (expected 47 passed).
- [x] 11.3 The plan's progress (`workflow/ongoing/release-0.9.md` or `joins-0.9.md`, as the orchestrator keeps them): the cycle's entry with its branch, the planning commit, the merge commit, the ADR, the suite count of 10.1, the package's count of 10.2, the manual, `check-dist` with the clean copy's counts, the lock and the originating check.
- [x] 11.4 `evidence.md` complete; the implementation commit is the orchestrator's, never amending the planning or the merge commit; nothing pushed.
