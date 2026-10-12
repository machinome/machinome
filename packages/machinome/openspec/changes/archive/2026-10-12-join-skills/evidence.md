# Evidence: `join-skills`

A cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` and `release-0.9.md` at the repository
root). Worktree `machinome/WTs/v0.9-joins-join-skills`, branch
`v0.9-joins-join-skills`, cut from the line `v0.9-joins` at 5af14f71.
Planning commit 624aab77, ratified by the orchestrator on 12 October 2026;
the join merge 36974f3e on top of it. Applied on 12 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), the OpenSpec CLI 1.6.0.
Every command ran with `env -C <dir>` and absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-join-skills` and
`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C5-apply/`.
The core's tests ran from `<bench>/packages/machinome` on the bench venv
(`<bench>/.venv/bin/python -m pytest -q -p no:cacheprovider ...`), the
package's from `<bench>/packages/machinome-skills`, one pytest process at a
time. Logs are in `<scratch>`, never in the bench.

The orchestrator's resolution of the design's open questions (12 October
2026): Open Questions 1 to 6, 8 and 10 as the design recommends; 7 declined,
the joined commit's message kept as written, as every join keeps its
history's messages, so Decision 1's `--replace-message` was not run and no
record of this change quotes that subject; 9 declined, `machinome skills`
without the package stays argparse's invalid choice and no hint is written.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -3
36974f3e Join machinome-skills: its history at its final paths
624aab77 Propose join-skills: machinome-skills joins as the distribution machinome-skills, its installer the second contributor of machinome.commands
5af14f71 workflow: the command seam's entry under Progress
$ git -C <bench> status --short | wc -l
0
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
```

`git status --short --ignored` showed `.env`, `.venv/` and the members'
`__pycache__/` and `*.egg-info/` leavings, all ignored.

### 1.2 The bench venv and the base counts (task 1.2)

The bench venv the orchestrator synced from the lock before the join:
thirteen `__editable__` `.pth` files (`machinome-0.8.1`, the two engines,
the nine node packages at 0.8.1 and `machinome_mechanics-0.1.0`), and

```
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome.skills"
ModuleNotFoundError: No module named 'machinome.skills'
```

The base counts at 5af14f71, as the orchestrator recorded them, not rerun:
the suite 4854 passed, 24 skipped, 7508 subtests passed.

### 1.3 The probes relied on (task 1.3)

By reference to design.md: probe 1 (OpenSpec 1.6.0's 31 tool ids with a
skills directory, its `generatedBy` marker and its rewrite on any
difference), probe 2 (OpenSpec overwrote a user's unmarked skill), probe 3
(the clients' directories), probe 4 (8 files, the rewrite), probe 5 (the
merge clean, the five reds of the join), probe 6 (the seam's four reds with
a real contributor), probe 7 (`agent-skills/` builds without warnings; 16
wheel entries; PyPI 404), probe 8 (the command from the wheel), probe 9 (the
prompt), probe 10 (cost), probe 11 (189 packages), probe 12 (no project names
the package), probe 13 (the deltas archive).

## 2. The join

### 2.1 The import (task 2.1, the orchestrator's)

A fresh clone of `file:///home/asa/devel/machinome/machinome-skills`
rewritten with `scratchpad/C5-join/filter-repo-command.sh` (log
`scratchpad/C5-join/filter-repo.log`): the command of design.md Decision 1
without `--replace-message` (Open Questions 7 declined). One commit parsed
and rewritten; `main` at 1b86a97, author Luis Fagundes, 2026-09-20 20:15:07
+0000, its message kept as written. `git ls-tree -r --name-only main`: the
eight paths of `scratchpad/C5-join/ls-files.txt`, all under
`packages/machinome-skills/`:

```
packages/machinome-skills/.gitignore
packages/machinome-skills/README.md
packages/machinome-skills/machinome/skills/agent-skills/machinome-simulate/SKILL.md
packages/machinome-skills/machinome/skills/agent-skills/machinome-simulate/references/source-adaptation.md
packages/machinome-skills/machinome/skills/agent-skills/machinome/SKILL.md
packages/machinome-skills/machinome/skills/agent-skills/machinome/references/mechanical-contracts.md
packages/machinome-skills/tests/test_skill_format.py
packages/machinome-skills/workflow/evaluation.md
```

No tag (`git tag | wc -l`: 0). The head differs from the rehearsal's
9a23c9a because the message is not rewritten.

### 2.2 The merge (task 2.2, the orchestrator's)

The merge commit 36974f3e, parents 624aab77 and 1b86a970, `git merge
--allow-unrelated-histories --no-ff` of that branch: no conflict, 8 files
changed, 736 insertions; `git status --porcelain` empty afterwards.

```
$ git -C <bench> log --follow --format='%h %ad %an' --date=short -- packages/machinome-skills/machinome/skills/agent-skills/machinome/SKILL.md
1b86a970 2026-09-20 Luis Fagundes
$ git -C <bench> log --follow --format='%h %ad %an' --date=short -- packages/machinome-skills/tests/test_skill_format.py
1b86a970 2026-09-20 Luis Fagundes
```

Both reach the rewritten founding commit of 20 September 2026.

### 2.3 The gates on the joined tree (task 2.3)

`tests/test_repository_layout.py tests/test_release_records.py`
(`<scratch>/2.3-join-reds.out`): 5 failed, 49 passed, 327 subtests passed,
the five of design.md probe 5, each naming `machinome-skills`:

- `test_every_member_is_a_workspace_source`: the sources lack
  `'machinome-skills': {'workspace': True}`.
- `test_the_members_are_the_package_directories` (member
  `machinome-skills`): `packages/machinome-skills holds no pyproject.toml`.
- `test_the_readme_links_every_package_and_states_the_licence`:
  `'packages/machinome-skills/' not found` among the root README's links.
- `test_every_sibling_is_in_the_table`: `packages/machinome-skills is in
  neither EXTENSIONS nor PRODUCTS`.
- `test_the_guide_installs_every_member_without_uv`: `CONTRIBUTING.rst does
  not name -e packages/machinome-skills`.

Nothing else red; `test_release_records.py` passed whole.

## 3. Red first, on the joined tree

### 3.1 The layout gate (task 3.1)

`PRODUCTS` gains the skills row; `test_each_product_keeps_its_tests_and_specs`
asks every product's `tests/` for a `test_*.py` and `openspec/specs/` only of
a product whose entries name `openspec`; the default group's test, renamed
`test_the_default_group_is_the_framework_dev_and_the_products_extras`,
expects three entries; the docstring names the skills package.
`<scratch>/3.1-layout-red.out`: 10 failed, 34 passed, 200 subtests passed:

- `test_every_member_is_a_workspace_source`, as in 2.3.
- `test_the_members_are_the_package_directories`, as in 2.3.
- `test_the_default_group_is_the_framework_dev_and_the_products_extras`:
  `['machinome[dev]', 'machinome[mechanics]'] != [..., 'machinome[skills]']`.
- `test_the_test_job_runs_each_product_s_tests` (product
  `machinome-skills`): `the test job runs no pytest from
  packages/machinome-skills`.
- `test_the_readme_links_every_package_and_states_the_licence`, as in 2.3.
- `test_the_guide_installs_every_member_without_uv`, as in 2.3.
- `test_each_product_directory_holds_its_package_and_its_record`: the
  entries `['.gitignore', 'README.md', 'machinome', 'tests', 'workflow']`,
  not the nine of the row (no `LICENSE`, `LICENSES`, `MANIFEST.in`,
  `pyproject.toml`).
- `test_each_product_manifest_states_the_set_s_licence`: `FileNotFoundError`
  for `packages/machinome-skills/pyproject.toml`.
- `test_each_product_readme_names_its_install_and_the_licence`:
  `'pip install "machinome[skills]"' not found` in the product's README.
- `test_each_product_resolves_from_its_directory`: `ModuleNotFoundError: No
  module named 'machinome.skills'`.

`test_every_sibling_is_in_the_table` turned green with the row.

### 3.2 The identity and the extras (task 3.2)

`tests/test_machinome_identity.py tests/test_kernel_extras.py`
(`<scratch>/3.2-red.out`): 2 failed, 22 passed, 78 subtests passed;
`test_distribution_import_command_and_extras_share_the_name` (extra `skills`)
and `test_each_extra_lists_what_its_module_needs` (extra `skills`), each
`KeyError: 'skills'`.

### 3.3 The manual's structure (task 3.3)

`tests/test_docs_structure.py` gains `test_the_skills_guide_is_a_how_to`,
`machinome-skills` in the installation page's distributions, and a class
`CommandReferenceTest` with `test_the_skills_command_has_its_section` and
`test_the_skills_package_is_no_longer_to_add_its_command`
(`<scratch>/3.3-red.out`): 4 failed, 20 passed, 1165 subtests passed:

- `test_the_skills_guide_is_a_how_to`: `'howto/assistant-skills' not found`
  in the How-to toctree.
- `test_the_installation_page_names_the_extension_distributions`
  (distribution `machinome-skills`): `'machinome-skills' not found` in
  `start/install.rst`.
- `test_the_skills_command_has_its_section`: `'.. _skills-command:\n\nmachinome
  skills\n' not found` in `reference/cli.rst`.
- `test_the_skills_package_is_no_longer_to_add_its_command`: `'The skills
  package adds ``machinome skills``' not found` in "Commands from other
  packages".

### 3.4 The package's tests (task 3.4)

As joined, the check script collects nothing
(`<scratch>/3.4-join-collects-nothing.out`, run from
`packages/machinome-skills` with `PYTHONPATH=<bench>/packages/machinome-skills`):
`no tests ran`, exit 5.

`tests/test_skill_format.py` rewritten in place from the check script, each
check a test over the shipped skills (Decision 11); `tests/test_command.py`
new. Run together, the collection stops at `test_command.py`
(`<scratch>/3.4-red.out`, exit 2): `ImportError: cannot import name
'installer' from 'machinome.skills' (unknown location)`, the form `from
machinome.skills import installer` takes for the module the design names
(`ModuleNotFoundError` for `machinome.skills.installer`); the directory
`machinome/skills/` is then a namespace directory with no `__init__.py`.
The format tests alone (`<scratch>/3.4-format-red.out`): 3 failed, 10 passed,
16 subtests passed:

- `test_the_licence_is_the_set_s` (skill `machinome` and skill
  `machinome-simulate`): the field names the licence the product carried,
  not `GPL-2.0-or-later OR CERN-OHL-S-2.0+`.
- `test_every_shipped_file_is_named_by_the_package_data`: `FileNotFoundError`
  for `packages/machinome-skills/pyproject.toml`.

### 3.5 Every red of group 3 (task 3.5)

Recorded in 3.1 to 3.4 above.

## 4. The package

### 4.1 The links (task 4.1)

```
$ env -C <bench>/packages/machinome-skills ln -s ../../LICENSE LICENSE
$ env -C <bench>/packages/machinome-skills ln -s ../../LICENSES LICENSES
$ git -C <bench> add packages/machinome-skills/LICENSE packages/machinome-skills/LICENSES
$ git -C <bench> ls-files -s packages/machinome-skills | grep ^120000
120000 30cff7403da04711c46979a06f6bf8eb10ee088a 0	packages/machinome-skills/LICENSE
120000 06ad40db40b426ca6c609aa4663782c2b8d02e92 0	packages/machinome-skills/LICENSES
```

Targets `../../LICENSE` and `../../LICENSES`.

### 4.2 The manifest, `MANIFEST.in`, README and `.gitignore` (task 4.2)

`pyproject.toml`, `MANIFEST.in` and `README.md` as design.md Decision 2
writes them, the README replacing the product's in place; `.gitignore`
edited in place to `.pytest_cache/` and `dist/` with its comment.

### 4.3 The licence field (task 4.3)

`git diff 36974f3e -- packages/machinome-skills/machinome/skills/agent-skills`:
2 files changed, 2 insertions, 2 deletions, the `license:` line of each
`SKILL.md`, now `license: GPL-2.0-or-later OR CERN-OHL-S-2.0+`; nothing else
of the four files.

### 4.4 The modules and the registry (task 4.4)

`machinome/skills/__init__.py` (the docstring alone), `cli.py` (the class
`Skills`, importing nothing at module scope; `handle` imports the
installer), `installer.py` (standard library only) and `tools.toml`, 32
rows: `agents` then OpenSpec 1.6.0's 31 ids in its order, each with `name`,
`detect`, `project`, `personal` (absent for `trae`) and `source`, the
directories of design.md Decision 5's table. Fifteen rows' `source` says
"personal inferred". `flake8 --max-line-length=89 machinome tests` from
`packages/machinome-skills`: 0.

## 5. The core, the workspace and the sync

### 5.1 The extra (task 5.1)

`git diff -- packages/machinome/pyproject.toml`: one hunk, the extra
`skills = ["machinome-skills~=0.8.1"]` and its comment, before `all`.

### 5.2 The lock and the sync (task 5.2)

The root manifest gains `machinome-skills = { workspace = true }` and the
dev group `["machinome[dev]", "machinome[mechanics]", "machinome[skills]"]`
with its comment.

```
$ env -C <bench> /home/asa/.local/bin/uv lock
Resolved 189 packages in 1.67s
Added machinome-skills v0.8.1
```

`git diff -- uv.lock` (`<scratch>/5.2-uv-lock.diff`, 65 lines): the member
`machinome-skills` in the manifest's members, the dev group's
`machinome[skills]`, the extra `skills` and its requirement, and the
package `machinome-skills` 0.8.1 from `packages/machinome-skills`, editable,
requiring `machinome`; its added and removed lines are probe 11's
(`scratchpad/C5-propose/uv-lock.diff`), the hunks cut at other lines.

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Resolved 189 packages in 10ms
Prepared 2 packages in 1.67s
Uninstalled 1 package in 51ms
Installed 2 packages in 18ms
 ~ machinome==0.8.1 (from file://<bench>/packages/machinome)
 + machinome-skills==0.8.1 (from file://<bench>/packages/machinome-skills)
```

Fourteen `__editable__` `.pth` files, the new one
`__editable__.machinome_skills-0.8.1.pth: <bench>/packages/machinome-skills`.
From `/tmp`:

```
$ <bench>/.venv/bin/python -c "import machinome.skills as s; print(s.__file__)"
<bench>/packages/machinome-skills/machinome/skills/__init__.py
$ <bench>/.venv/bin/machinome skills -h
usage: machinome skills [-h] {install,update,list} ...
positional arguments:
  {install,update,list}
    install             copy the skills into the directories of the tools you
                        name, or choose them at a prompt
    update              rewrite the copies older than the installed package
    list                print the tools and where each reads its skills, then
                        the copies under a path
```

`git -C <bench> status --short --ignored packages/machinome-skills` shows
the build leaving `machinome_skills.egg-info/` and `__pycache__/` as ignored
only.

### 5.3 The package's tests (task 5.3)

From `packages/machinome-skills`, no `PYTHONPATH`
(`<scratch>/5.3-package.out`): 46 passed, 170 subtests passed. The core's
collection (`<scratch>/5.3-collect.out`): 4877 tests collected, `grep -c
machinome-skills` 0.

### 5.4 The gates again (task 5.4)

`test_repository_layout.py`, `test_machinome_identity.py`,
`test_kernel_extras.py`, `test_release_records.py` (`<scratch>/5.4.out`): 4
failed, 72 passed, 431 subtests passed, the four of groups 8 and 9:
`test_the_test_job_runs_each_product_s_tests`,
`test_the_readme_links_every_package_and_states_the_licence`,
`test_the_guide_installs_every_member_without_uv` and
`test_the_version_is_bumped_from_the_root` (`'packages/machinome-skills/pyproject.toml'
not found` among the configuration's files).

## 6. The seam's tests with a real contributor

### 6.1 The reds (task 6.1)

`tests/test_cli_contributed.py tests/test_cli_lazy_imports.py` on the
synced venv (`<scratch>/6.1-seam-red.out`): 4 failed, 31 passed, 1 skipped,
25 subtests passed, probe 6's four:

- `test_a_second_contributor_runs`: exit 1, `Error: machinome skills is
  contributed by more than one package: fake-skills
  (machinome_fake_skills:Skills), machinome-skills
  (machinome.skills.cli:Skills)`.
- `test_help_lists_contributed_commands_after_the_framework`: the fake's
  `skills` help not found; the help lists the real `skills` as unavailable
  for the same collision.
- `test_a_module_that_cannot_be_imported`: expects
  `{build,...,vet,gone}`, reads `{build,...,vet,gone,skills}`.
- `test_the_contract_walk_reads_a_fake_distribution`: the failures read
  `'machinome-skills': []` beside the fakes'.

`test_every_contributed_entry_resolves_and_honours_the_contract` passed,
walking `machinome-skills`'s entry `skills`.

### 6.2 The edits (task 6.2)

`tests/contributed_commands.py`: the fake `fake-skills` is `fake-lessons`,
entry `lessons = machinome_fake_lessons:Lessons`, docstring "Teach a lesson
(a fake contributed command).". `tests/test_cli_contributed.py`: `INSTALLED`,
the names `importlib.metadata.entry_points(group='machinome.commands')`
reports for distributions whose name does not begin `fake-`, read once at
import, and `choices(*fakes)`, the framework's `COMMAND_ORDER` then the
installed and fake names sorted, used by the help's test and the gone
module's test; `test_a_second_contributor_runs` runs `lessons install`.
`tests/test_cli_lazy_imports.py`: the walk on fakes compares the fakes'
distributions alone, and the docstring of the walk over the environment
says it walks `skills`. The computation names no product, so a later
contributor's join needs no edit of it.

`tests/test_cli_contributed.py tests/test_cli_lazy_imports.py
tests/test_cli.py` (`<scratch>/6.2-seam-green.out`): 53 passed, 1 skipped,
35 subtests passed.

### 6.3 The walk's need (task 6.3)

The line `needs_node = False` deleted from `Skills` in
`packages/machinome-skills/machinome/skills/cli.py`, one run of
`test_every_contributed_entry_resolves_and_honours_the_contract`
(`<scratch>/6.3-walk-red.out`): 1 failed, `SUBFAILED(command='skills',
dist='machinome-skills')`, `['needs_node is not declared as True or False']
!= []`. The file restored from its copy, `cmp` equal.

## 7. The manual

### 7.1 The pages (task 7.1)

`docs/howto/assistant-skills.rst`, "Give your assistant the machinome
skills", listed after `howto/mechanism-formulas` in the How-to toctree;
`start/install.rst`: "Three more extras exist", `skills` among them, and
`machinome-skills` in "Packages and licences"; `reference/cli.rst`: the
sentence of Decision 15 and the section `machinome skills` with
`.. _skills-command:`.

### 7.2 The build (task 7.2)

A fresh venv `<scratch>/docs-venv` (`uv venv --python 3.12`, then `uv pip
install -r packages/machinome/docs/requirements.txt` alone: Sphinx, the
theme and `machinome-viewer` 0.8.0 from the index):

```
$ env -C <bench>/packages/machinome <scratch>/docs-venv/bin/python -m sphinx -b html -n -W --keep-going docs <scratch>/html
build succeeded.
```

Exit 0, no warning (`<scratch>/7.2-sphinx.out`). The rendered how-to and the
command reference's section were read as text from the built HTML; the
marker's version renders as 0.8.1 through `|release|`. One sentence of the
how-to was corrected after reading it ("two lines added" became "a marker
added": the marker is three lines). `tests/test_docs_structure.py`: 23
passed, 1197 subtests passed.

## 8. The version records, `scripts/check-dist` and CI

### 8.1 The bump (task 8.1)

`.bumpversion.cfg` gains the two tables of Decision 13.
`tests/test_release_records.py`: 14 passed, 134 subtests passed. On a copy
(`<scratch>/bump-copy`: the configuration and the 17 files it names, a git
repository of one commit), `bump2version --no-commit --no-tag --new-version
0.9.0 patch`: exit 0, 17 files changed; `git diff -U0` moves the skills
manifest's `version = "0.8.1"` and `"machinome~=0.8.1"` and the core's
`"machinome-skills~=0.8.1"` to 0.9.0. Nothing was written in the bench.

### 8.2 Red first (task 8.2)

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
check-dist failed: machinome-skills has no smoke in scripts/check-dist
Nothing uploaded.
```

### 8.3 The row (task 8.3)

The row of Decision 14 after the mechanics package's, with two departures
found by its first run (8.4): the wheel's files are read without
`__pycache__/` entries, and the copies' `SKILL.md` are counted (4) before
they are read. `git diff scripts/check-dist`: 60 insertions after the fix,
no deletion, no line of another row changed. `flake8 --max-line-length=89
scripts/check-dist`: 0.

### 8.4 The run (task 8.4)

The first run (`<scratch>/8.4-check-dist-first.out`) built, checked and
installed every member and failed at the skills smoke: pip's record of the
installed wheel lists the bytecode it compiled
(`machinome/skills/__pycache__/__init__.cpython-312.pyc`, `cli`,
`installer`), which the design's list of shipped files did not exclude. With
`'__pycache__' not in path` added to the filter, the second run
(`<scratch>/8.4-check-dist.out`): exit 0, fourteen members, 28 archives
`twine check --strict` PASSED, the skills wheel installed by its path,

```
machinome-skills 0.8.1 installed 8 files for agents and claude
$ <tmp>/venv/bin/machinome skills list
   machinome skills list: exit 0
Every distribution built, checked, installed and smoked; nothing uploaded.
```

and the three licence files listed under `licenses/`. The archives: the
skills wheel 16 entries, its sdist 37 entries (with `tests/test_command.py`,
`tests/test_skill_format.py` and `workflow/evaluation.md`); the framework's
sdist 1062 and wheel 114; the others as listed in the log. `git -C <bench>
status --short` afterwards: the change's files only.

### 8.5 CI (task 8.5)

`.github/workflows/python-app.yml`'s `test` job gains the step "Run the
skills package's tests" after the mechanics package's, `working-directory:
packages/machinome-skills`, `run: python -m pytest`.
`test_the_test_job_runs_each_product_s_tests` green (9.4's run).

## 9. The records

### 9.1 to 9.6 (tasks 9.1 to 9.6)

- `HISTORY.rst` and `docs/project/changelog.rst`: the entries of Decision
  16, verbatim, at the end of `Unreleased`.
- `CREDITS.md`: the section "Adapted from Machinome Studio, in the skills
  package" after the FreeCAD package's, and the last-updated line
  2026-10-12. Its source is the product's `NOTICE` at 69e67ff, whose
  provenance sentence reads: "The mechanical workflow guidance is adapted
  from the machinome and simulate-project skills in Machinome Studio, with
  revisions for independent, cross-harness use and documentation-based API
  lookup." and whose copyright line reads "Copyright 2026 Luis Henrique
  Cassis Fagundes"; its licence line is not repeated here.
- `docs/architecture.md`: the CLI sentence, the extras sentence, the section
  "Skills package" before "Load-bearing invariants", and the Map row.
- The root `README.md`'s row, `CONTRIBUTING.rst`'s pip line and test
  sentence, `context7.json`'s two folders and its rule (after the mechanics
  helpers' rule), and `AI-USE.md`'s phrase.
- The product's `workflow/evaluation.md`: "Mechanical checks" rewritten and
  the section "Distribution since the join (12 October 2026)" appended at
  the end; `git diff` shows those two places only, the live cases and the
  validation boundary of 20 September 2026 unchanged.
- ADR-190, Status Proposed, in `docs/adrs/BUILD/`, and its index line after
  ADR-189's in `docs/adrs/README.md`.

The gates (`<scratch>/9.4-gates.out`): `test_repository_layout.py`,
`test_release_records.py`, `test_machinome_identity.py`,
`test_kernel_extras.py`, `test_docs_structure.py`: 95 passed, 1636 subtests
passed.

### 9.7 The licence names (task 9.7)

Over the 45 files `git diff --name-only 624aab77` and the untracked files
name (`<scratch>/9.7-files.txt`): the added lines of `git diff 624aab77`
name the licence the product carried, or the framework's former one, 0
times, and the new files 0 times. In those files the name stands only in
lines this change did not write: `HISTORY.rst`'s released sections (lines
955 and 1498) and `CREDITS.md`'s rows for third-party dependencies. `git diff
36974f3e` removes 6 lines that named it (the README, the check script and
the two frontmatters). The joined commit's subject names it: Open
Questions 7 was declined and the message kept as written.

## 10. Validation and the originating check

### 10.1 The suite (task 10.1)

No other pytest of the campaign was running (`pgrep -af
"WTs/v0.9-joins-.*[p]ytest"` printed nothing; an earlier check found the
viewer's applier's suite and this run waited for it to end).

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
```

The first run (`<scratch>/10.1-suite-first.out`): 1 failed, 4856 passed, 24
skipped, 7562 subtests passed, in 818 s. The failure is a test design.md
did not name: `tests/test_vet_command.py::HelpTest::test_the_top_level_help_lists_vet_after_import_step`,
`'import-step,vet}' not found` in a help whose choices read
`{build,...,import-step,vet,skills}`; it assumed, as the seam's tests did,
that no contributor is installed. It now asserts
`import-step,vet[},]`, the framework's commands ending with `vet` and the
installed contributors' following (`tests/test_vet_command.py`: 15 passed;
its lint 0, as at the base).

The second run (`<scratch>/10.1-suite.out`): **4857 passed, 24 skipped,
7562 subtests passed, 0 failed**, in 934 s. Against the base's 4854 passed,
24 skipped, 7508 subtests: three tests added, all in
`tests/test_docs_structure.py` (`NavigationTest::test_the_skills_guide_is_a_how_to`,
`CommandReferenceTest::test_the_skills_command_has_its_section`,
`CommandReferenceTest::test_the_skills_package_is_no_longer_to_add_its_command`);
the renamed `test_the_default_group_is_the_framework_dev_and_the_products_extras`
replaces its former name; 54 subtests added (the skills row of the
products' and the extras' loops, the new docs tests' spellings, the
contract walk's entry `skills`). The 24 skips, by reason: 14 in
`test_browser_renderer.py`, 1 in `test_scad_presentation.py` and 1 in
`test_cli_lazy_imports.py`, `machinome-viewer` not installed; 4 from
`freecad_support.py`, `MACHINOME_FREECAD_ROOT` not set; 2 in
`test_step_assembly.py`, the vendor STEP not present; 1 in
`test_connectivity.py`, networkx not installed; 1 in
`test_jscad_integration.py`, no jscad CLI.

### 10.2 The package's tests (task 10.2)

From `packages/machinome-skills` (`<scratch>/10.2-package.out`): 47 passed,
170 subtests passed, 0 failed: `test_skill_format.py` 11 tests,
`test_command.py` 36, among them `TheCommandTest::test_list_runs_alone`, added
after 5.3 for the `cli` delta's scenario "The skills command runs alone"
(the dispatch of `machinome skills list` imports `machinome.skills.cli` and
`machinome.skills.installer` and no `machinome.manager.*` module).

### 10.3 The lint (task 10.3)

`flake8 --max-line-length=89 machinome tests ../machinome-*/machinome` from
`packages/machinome` (`<scratch>/10.3-lint.txt`): 1512 lines, 0 of them under
`../machinome-skills/`. No module of the core changed; each core test module
this change edits (`test_repository_layout.py`, `test_machinome_identity.py`,
`test_kernel_extras.py`, `test_docs_structure.py`, `test_cli_contributed.py`,
`test_cli_lazy_imports.py`, `contributed_commands.py`,
`test_vet_command.py`) has the same count as at 624aab77 (4 for
`test_cli_lazy_imports.py`, 0 for the others). The package's own `machinome`
and `tests`: 0. `scripts/check-dist`: 0.

### 10.4 The manual (task 10.4)

As in 7.2 on the final tree (`<scratch>/10.4-sphinx.out`): `build
succeeded.`, exit 0, no warning; the how-to, its links from
`start/install.html` and `project/changelog.html`, and the anchor
`skills-command` in `reference/cli.html` present.

### 10.5 `scripts/check-dist` on the tree and on a clean copy (task 10.5)

On the tree: 8.4's second run (`<scratch>/8.4-check-dist.out`), made after
every edit of groups 3 to 9; the one later edit,
`tests/test_vet_command.py` (10.1), changes no archive's member list. On a
clean copy: every file `git ls-files -z --cached --others --exclude-standard`
names (the tracked tree and this change's new files, not yet tracked),
packed with `tar --null -T -` and unpacked under `<scratch>/clean-copy`,
links kept, every regular file byte-equal to the bench's (0 differ), then
`env -C <scratch>/clean-copy <bench>/.venv/bin/python scripts/check-dist`
(`<scratch>/10.5-check-dist-clean.out`): exit 0, the fourteen members, 28
archives `twine check --strict` PASSED, `machinome-skills 0.8.1 installed 8
files for agents and claude`, `machinome skills list: exit 0`, `Every
distribution built, checked, installed and smoked; nothing uploaded.` Every
archive's member count equals the tree's: the framework's sdist 1062 and
wheel 114, the skills sdist 37 and wheel 16, mechanics 213 and 17, FreeCAD
22 and 11, OpenSCAD 23 and 12, every other extension package 18 and 8. The
framework's sdist grows by one entry, `docs/howto/assistant-skills.rst`
(a build of the framework's sdist alone, `<scratch>/core-sdist`, lists it as
the only one of this change's new framework files; ADR-190 and `evidence.md`
are not in the sdist), so 1061 at the base.

### 10.6 The originating check (task 10.6)

A scratch git project `<scratch>/origin-project` (one commit, a README), the
bench venv's `machinome` (`<scratch>/10.6-origin.out`,
`<scratch>/10.6-update.out`):

```
$ machinome skills install --tools agents,claude
.agents/skills/ (agents)
  wrote .agents/skills/machinome/SKILL.md
  wrote .agents/skills/machinome/references/mechanical-contracts.md
  wrote .agents/skills/machinome-simulate/SKILL.md
  wrote .agents/skills/machinome-simulate/references/source-adaptation.md
.claude/skills/ (claude)
  wrote .claude/skills/machinome/SKILL.md
  wrote .claude/skills/machinome/references/mechanical-contracts.md
  wrote .claude/skills/machinome-simulate/SKILL.md
  wrote .claude/skills/machinome-simulate/references/source-adaptation.md
exit 0
```

The eight files at `.agents/skills/<skill>/` and `.claude/skills/<skill>/`,
the directories Codex's and Claude Code's documentation name (design.md
probe 3); each `SKILL.md`'s `name` equal to its directory, each with
`installed-by: machinome-skills` and `version: "0.8.1"`. The `claude`
(Claude Code 2.1.280) and `codex` (codex-cli 0.162.1) programs are on the
PATH, and neither was asked to list the project's skills: either would write
its session record under the user's real `~/.claude` or `~/.codex`, which
this cycle's rules forbid, and under a scratch `HOME` neither has its
credentials. Not run, for the orchestrator to run if wanted.

One copy's marker edited to 0.8.0
(`.claude/skills/machinome/SKILL.md`), then:

```
$ machinome skills update
.agents/skills/machinome: 0.8.1, current
.agents/skills/machinome-simulate: 0.8.1, current
  wrote .claude/skills/machinome/SKILL.md
  wrote .claude/skills/machinome/references/mechanical-contracts.md
.claude/skills/machinome: 0.8.0 -> 0.8.1
.claude/skills/machinome-simulate: 0.8.1, current
exit 0
$ git status --short
?? .agents/
?? .claude/
```

### 10.7 The projects (task 10.7)

The grep of design.md probe 12 over `/home/asa/devel/machinome/projects`, on
12 October 2026 (`<scratch>/10.7-projects-grep.txt`): 0 files. No universe
sweep is owed.

### 10.8 Git (task 10.8)

`git -C <bench> status --short`: 45 entries, the files of groups 3 to 9 and
`evidence.md` (two links staged as added, seven new files of the package,
the how-to, ADR-190 and `evidence.md` untracked, the rest modified), nothing
else. `git ls-files -ci --exclude-standard | wc -l`: 34, as at the base.

### 10.9 The change (task 10.9)

```
$ env -C <bench>/packages/machinome openspec validate join-skills --strict
Change 'join-skills' is valid
```

### The mechanics package's `tests/pyproject.toml` (design.md Decision 12)

The layout gate no longer asks a product's `tests/` for a `pyproject.toml`.
Proved once that the mechanics helpers' integration tests need theirs: a
scratch copy of `packages/machinome-mechanics/` (`tests/` and the manifest)
run with the bench venv, 9 failed with the file (the documentation tests,
whose `docs/` and changelog the copy lacks), 12 failed with it moved aside
(`<scratch>/12-mech-with.out`, `<scratch>/12-mech-without.out`); the three
more are `test_declarative.py::DeclaredFaceTest::test_the_escape_hatch_computes_a_static_phase`,
`test_motion.py::test_a_helper_drives_a_joint_at_numeric_states` and
`test_motion.py::test_the_realized_law_preserves_symbolic_math`, each
`ProjectManifestError: No pyproject.toml with [tool.machinome] found`.

### 10.10 The checkpoint (task 10.10)

The applier stopped before any commit and reported to the orchestrator. The
orchestrator reviewed the work and messaged back two corrections, both made
before group 11:

- `docs/architecture.md`: the CLI sentence no longer numbers the
  contributors. The pilot's numbering (`release-0.9.md`, decision 4) has the
  movie first, the skills second and the studio third, but the skills land
  on the line before the movie. It now reads "`machinome skills`, from the
  repository's distribution `machinome-skills`, is one (ADR-190); the
  movie's and the studio's follow at their joins." The HISTORY bullet's "the
  second a package adds" stays, since it is the pilot's numbering.
- `HISTORY.rst`: the seam's Unreleased bullet ended "No package declares one
  yet.", which this join made false. It now ends "The packages that declare
  one are recorded below."

The orchestrator kept the departures recorded above: the `__pycache__`
filter and the four-marker check in the smoke, the `test_vet_command.py`
assertion, the registry's `source` field, `test_list_runs_alone`, and the
installer's behaviours the design left open. The two assistants of 10.6 were
not run, for the reason recorded there.

## 11. Records closing

### 11.1 ADR-190 (task 11.1)

ADR-190 is promoted to **Accepted**, with its change link pointing at the
archive, and its index line in `docs/adrs/README.md` reads Accepted.
`docs/architecture.md` was checked against it and agrees: the CLI sentence,
the section "Skills package (the distribution `machinome-skills` · spec
`skills-distribution`)", the extras sentence and the Map row
(`skills-distribution`, ADRs 187, 189 and 190).

### 11.2 The archive and the specs (task 11.2)

```
$ env -C <bench>/packages/machinome openspec archive join-skills -y
Applying changes to openspec/specs/cli/spec.md:
  + 1 added
Applying changes to openspec/specs/framework-contributor-guidance/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/framework-identity/spec.md:
  ~ 2 modified
Applying changes to openspec/specs/skills-distribution/spec.md:
  + 6 added
Applying changes to openspec/specs/user-documentation/spec.md:
  + 1 added
Totals: + 8, ~ 3, - 0, → 0
Change 'join-skills' archived as '2026-10-12-join-skills'.
```

These are probe 13's totals (`<scratch>/11.2-archive.out`). The archive
printed two warnings that block nothing: the proposal's Why section is over
1000 characters, and the change has more than 10 deltas. It also counted 5
open tasks, which were 10.10 and group 11; they are ticked now. The
framework-identity spec gains the three new scenarios and drops no scenario
title.

The placeholder Purpose of the new `openspec/specs/skills-distribution/spec.md`
is replaced with the sentence the task gives. Then
(`<scratch>/11.2-validate.out`):

```
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 47 passed, 0 failed (47 items)
```

### 11.3 The plan (task 11.3)

`workflow/ongoing/joins-0.9.md`, under Progress, gains entry "4.
`join-skills`." at the end of the section. Entry 3 is the viewer's, which
lands on the line first, from its own bench.

### 11.4 Closing (task 11.4)

This file is complete. The implementation commit is the orchestrator's. It
does not amend the planning commit 624aab77 or the merge commit 36974f3e,
and nothing is pushed.
