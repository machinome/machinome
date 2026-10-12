# Evidence: `join-studio`

A cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` and `release-0.9.md` at the repository
root). Worktree `machinome/WTs/v0.9-joins-join-studio`, branch
`v0.9-joins-join-studio`, on the line `v0.9-joins` at feb1b46e (after
`join-movie` and `release-tooling`). Planning commit e08b5539, ratified by
the orchestrator on 12 October 2026 with every recommendation of its Open
Questions accepted; the join merge d291bc8b on top of it. Applied on
12 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), Node 24.11.1 and npm
11.6.2, the OpenSpec CLI 1.6.0. Every command ran with `env -C <dir>` and
absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-join-studio`, `<scratch>`
is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C8-apply/`,
`<propose>` the proposer's `.../scratchpad/C8-propose/` and `<join>` the
orchestrator's `.../scratchpad/C8-join/`. `D` is `packages/machinome-studio`,
`P` its package directory `D/machinome/studio`. The core's tests ran from
`<bench>/packages/machinome` on the bench venv (`<bench>/.venv/bin/python -m
pytest -q -p no:cacheprovider ...`), the package's from `<bench>/D`, one
pytest process at a time. Logs are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -4
d291bc8b Join the studio: its whole history at its final paths
e08b5539 Propose join-studio: the studio as the distribution machinome-studio, imported as machinome.studio, its command machinome studio
feb1b46e Implement release-tooling: one Makefile declares the set's steps, check-dist keeps a release's archives
afef5c96 Propose release-tooling: one Makefile declares the set's steps, check-dist keeps a release's archives
$ git -C <bench> status --short | wc -l
0
$ git -C <bench> ls-files | wc -l
6095
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
```

### 1.2 The bench venv and the base counts (task 1.2)

The orchestrator's resync of the bench venv after the join
(`<join>/uv-sync-2.log`) ended `exit 1`:

```
  × Failed to build `machinome @ file:///.../packages/machinome`
  ├─▶ Failed to parse entry: `machinome-studio`
  ╰─▶ `machinome-studio` is included as a workspace member, but is missing
      an entry in `tool.uv.sources`
```

The joined directory `packages/machinome-studio/` is a member of the root's
`members = ["packages/*"]`, and the core's unpinned extra `studio =
["machinome-studio"]` names it, so uv refuses to lower the core's
requirements until the root names its source (task 8.2). The venv was the
one synced from the lock at 675edac4 (`<join>/uv-sync.log`, 14:46), fifteen
`__editable__` `.pth` files, without the movie. Brought to the lock of the
joined head without resolving (`<scratch>/1.2-sync-frozen.out`):

```
$ env -C <bench> uv sync --frozen --python 3.12
Installed 6 packages in 48ms
 + jsonschema==4.26.0
 + jsonschema-specifications==2025.9.1
 ~ machinome==0.8.1 (from file:///.../packages/machinome)
 + machinome-movie==0.8.1 (from file:///.../packages/machinome-movie)
 + referencing==0.37.0
 + rpds-py==2026.9.1
exit 0
```

The orchestrator accepted this sync at the checkpoint's review on
12 October 2026: its own resync could not add a member with no source
entry. Sixteen `__editable__` `.pth` files afterwards (`machinome-0.8.1`, the two
engines, the nine node packages, `machinome_viewer`, `machinome_skills`,
`machinome_movie` at 0.8.1, `machinome_mechanics-0.1.0`); `git status
--short` still empty, and

```
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome.studio"
ModuleNotFoundError: No module named 'machinome.studio'
```

The base counts, as `release-tooling` recorded them for feb1b46e
(`joins-0.9.md`, Progress, and that change's evidence), not rerun here: the
core's suite 4909 passed, 9 skipped; `uv lock` 198 packages; the clean
copy's framework sdist 1083 entries and wheel 114; `make check` sixteen
members, 32 archives, 32 PASSED.

### 1.3 The probes relied on (task 1.3)

By reference to design.md: probe 1 (738 files, 318 commits, fd139a5),
probe 3 (the reds of the join), probe 4 (the seeded lock: 133 resolutions,
0 moved), probe 5 (the fastapi conflict; 195 packages on 675edac4), probes 6
to 9 (the resources, the archives of 1172 and 113 entries, the wheels, the
command's cost), probe 10 (the studio's tests: 499 passed at the original,
443 at the new place before the pins, the OpenSpec CLI needed), probes 11
to 17.

## 2. The join

### 2.1 The import (task 2.1, the orchestrator's)

A fresh clone of `file:///home/asa/devel/machinome/machinome-studio`
(`main` 0a09e05, 347 commits) rewritten by
`<propose>/filter-repo-command.sh` (`<join>/filter-repo.log`): `main`
fd139a5, 318 commits (29 pruned as empty, having touched only dropped
files), the rehearsal's hash; `git ls-tree -r --name-only main` lists the
738 paths of `<propose>/rehearsal-ls-files.txt` exactly (diff empty; the
listing at `<join>/ls-files.txt`); commits of `main` touching a path outside
`packages/`: 0.

### 2.2 The merge (task 2.2, the orchestrator's)

`git fetch <clone> main` into the bench; the merge commit d291bc8b, `git
merge --allow-unrelated-histories --no-ff` of fd139a5 onto e08b5539, no
conflict; `git status --short` empty afterwards; tracked files 6095 (5357
before the join plus 738). Read again on the bench:

```
$ git -C <bench> log --format='%h %ad %s' --date=short -- D/machinome/studio/app.py | tail -1
a3ca3e5d 2026-07-20 feat: apply and archive FastAPI shop-floor rebuild cycle
$ ... | wc -l
30
$ git -C <bench> log --format='%h %ad %s' --date=short -- D/machinome/studio/frontend/src/main.tsx | tail -1
9831f04d 2026-07-20 feat: apply and archive shop-agent lifecycle cycle
$ ... | wc -l
55
$ git -C <bench> ls-files -s D | grep ^120000
120000 6cedcf25... 0	D/machinome/studio/profiles/fordesmac/skills/machinome
120000 b458ea64... 0	D/machinome/studio/profiles/fordesmac/skills/machinome-api
120000 6cedcf25... 0	D/machinome/studio/profiles/openspec-builder/skills/machinome
120000 b458ea64... 0	D/machinome/studio/profiles/openspec-builder/skills/machinome-api
$ git -C <bench> ls-files D | wc -l
730
$ git -C <bench> diff --stat e08b5539 d291bc8b | tail -1
 738 files changed, 89073 insertions(+)
```

All without `--follow`.

### 2.3 The gates on the joined tree (task 2.3)

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider \
    tests/test_repository_layout.py tests/test_release_records.py \
    tests/test_core_names_no_split_words.py tests/test_node_root_exports_nothing.py
12 failed, 98 passed, 763 subtests passed in 7.76s
```

(`<scratch>/2.3-gates.out`.) Each red, with its reason:

- `TheWorkspaceTest::test_every_member_is_a_workspace_source`: the root's
  `tool.uv.sources` lacks `machinome-studio`.
- `TheMakefileTest::test_the_package_list_is_the_package_directories`
  (subtest `machinome-studio` and the whole list): "the Makefile's PACKAGES
  omits machinome-studio".
- `TheRootIsTheRepositorysTest::test_the_readme_links_every_package_and_states_the_licence`
  (`machinome-studio`): `packages/machinome-studio/` not linked from the
  root `README.md`.
- `TheExtensionPackagesTest::test_every_sibling_is_in_the_table`
  (`machinome-studio`): "packages/machinome-studio is in neither EXTENSIONS
  nor PRODUCTS".
- `TheExtensionPackagesTest::test_the_guide_installs_every_member_without_uv`
  (`machinome-studio`): "CONTRIBUTING.rst does not name -e
  packages/machinome-studio".
- `TheNodeWorkspaceTest::test_the_root_s_lock_names_each_member_and_the_movie_keeps_its_own`:
  the tracked locks include
  `D/machinome/studio/frontend/package-lock.json`.
- `VersionFilesTest::test_every_member_is_numbered_with_the_core`
  (`machinome-studio`): `'0.1.0' != '0.8.1'`.
- `VersionFilesTest::test_every_pin_between_members_is_compatible`
  (`machinome` requiring `machinome-studio`): `'' != '~=0.8.1'`, the core's
  unpinned extra.
- `VersionFilesTest::test_the_version_is_bumped_from_the_root`
  (`machinome-studio`): `D/pyproject.toml` not among `.bumpversion.cfg`'s
  files.
- The split-word gate: 13 occurrences in two modules, `mcp_server.py` 9
  (759 "Stage the exact paths given", 971, 978 `"exact"`, ...) and
  `preparation.py` 4 (648, 650, 803 `_require_exact_repository`).
- The node-root gate: two files, 26 offences,
  `shop-skills/machinome-api/SKILL.md` 24 (from line 32) and
  `shop-skills/machinome/SKILL.md` 2 (line 59).

Twelve failures, each design.md probe 3's or `TheMakefileTest` as
`release-tooling` lands it; nothing else red.

## 3. Red first, on the joined tree

Nothing of the package's code or manifest changed in this group; the tests
alone.

### 3.1 The layout gate (task 3.1)

`tests/test_repository_layout.py`: the `PRODUCTS` row of design.md
Decision 10, `NODE_MEMBERS`'s third member `@machinome/studio`, the default
group's `machinome[studio]`, the docstring's sentences; in
`TheContinuousIntegrationTest` the one npm step the test job may spell (the
OpenSpec CLI, `npm install -g @fission-ai/openspec@1.6.0`) exempted from the
rule that a job spells no `npm`, and two new tests,
`test_the_test_job_installs_the_openspec_cli_before_the_tests` (after Node,
before `make test`) and `test_the_studio_s_rule_builds_its_frontend_before_its_tests`
(`STUDIO_FRONTEND`, the rule's typecheck, build and pytest in that order,
the static directory in `CLEAN`). Two corrections of the gate the studio's
directory needs, not foreseen by the design:

- `test_each_product_manifest_states_the_set_s_licence` held `find` to
  `{'include': [address], 'namespaces': True}`; the studio's manifest of
  Decision 3 includes `machinome.studio.backends` beside its address. The
  test now holds the first `include` to the address and every other to a
  subpackage beneath it.
- `test_each_product_directory_holds_its_package_and_its_record` split `git
  ls-files` on whitespace, and the studio's design reference holds
  `workflow/design/build/Project Floor.dc.html`: the listing now reads one
  path a line (the first red run listed an entry `Floor.dc.html`).

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_repository_layout.py
16 failed, 48 passed, 416 subtests passed in 3.44s
```

(`<scratch>/3.1-layout.out`.) Each red:

- the workspace source (`machinome-studio` absent from `tool.uv.sources`);
- the default group (`machinome[studio]` absent);
- `STUDIO_FRONTEND`: "the Makefile assigns STUDIO_FRONTEND 0 times with :=";
- the CI step: "the job has no step that installs the OpenSpec CLI";
- `TESTED` (twice) and `PACKAGES` (twice): "the Makefile's TESTED omits
  machinome-studio", "... PACKAGES omits machinome-studio";
- the root README: `packages/machinome-studio/` not linked;
- the guide: "CONTRIBUTING.rst does not name -e packages/machinome-studio";
- the product's entries: the tracked top-level entries lack `LICENSE`,
  `LICENSES` and `MANIFEST.in`;
- the product's manifest: its `license` the licence the product carried,
  not `GPL-2.0-or-later OR CERN-OHL-S-2.0+` (and its `find`, `include =
  ["floor", "floor.*"]`, `namespaces = false`);
- the product's README: `pip install "machinome[studio]"` absent;
- the resolution: `ModuleNotFoundError: No module named 'machinome.studio'`;
- the root `package.json`'s members: the third absent;
- the tracked locks: `D/machinome/studio/frontend/package-lock.json`.

### 3.2 to 3.5 The release records, the extra, vet, the split-word gate and the manual (tasks 3.2 to 3.5)

- `tests/test_release_records.py`: `test_the_studio_s_frontend_version_files_agree`
  (the frontend's `package.json` version, the root lock's entry for the
  member, `.bumpversion.cfg`'s table), and the docstring's sentence.
- `tests/test_kernel_extras.py`: `EXTRAS['studio'] = {f'machinome-studio~={VERSION}'}`.
- `tests/test_vet_universe.py`: the contract's tuple gains
  `'machinome.studio'`; `test_the_studio_is_internal_and_its_former_name_outside`.
- `tests/test_core_names_no_split_words.py`: `ORDINARY`'s
  `machinome/studio/preparation.py` entry and `ORDINARY_TEXT`'s two, as
  Decision 10 spells them.
- `tests/test_docs_structure.py`: `test_the_studio_is_three_how_tos_and_a_reference_section`,
  `KernelExtrasTest.STALE` gaining `github.com/machinome/machinome-studio`,
  `machinome-studio --projects-dir` and `python -m floor` (`RECORDS`
  admitting the last in `project/changelog.rst`), the install page's
  `machinome-studio`, `pip install "machinome[studio]"` and `playwright
  install chromium`, `test_the_studio_command_has_its_section` and
  `test_the_studio_is_no_longer_to_add_its_command`.

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider \
    tests/test_repository_layout.py tests/test_release_records.py tests/test_kernel_extras.py \
    tests/test_vet_universe.py tests/test_core_names_no_split_words.py tests/test_docs_structure.py
41 failed, 137 passed, 3100 subtests passed in 8.03s
```

(`<scratch>/3.2-3.5.out`; the layout gate's sixteen as in 3.1.) The reds
beyond the layout gate:

- release records: the member's version `'0.1.0' != '0.8.1'`; the core's
  pin `'' != '~=0.8.1'`; the bump (`D/pyproject.toml` not in
  `.bumpversion.cfg`); the new test's three subtests: the frontend's
  version `0.0.0`, no root lock entry for the member, no table for its
  `package.json`.
- the extra: `{'machinome-studio'} != {'machinome-studio~=0.8.1'}`.
- vet: the contract's tuple lacks `machinome.studio`; the new test's first
  project is vetted pure (`set()` where `('sim/model.py',
  'framework-internal', 'machinome.studio')` is expected), design.md probe
  12.
- the split-word gate: one module, 7 occurrences, all the test tool's
  (`mcp_server.py` 971 the docstring, 978 `"exact"` and `"faceted"`, and
  the schema's), the six ordinary ones admitted (probe 16).
- the manual: the three how-tos and `reference/studio/index` in no
  toctree of `index.rst`; the install page without `machinome-studio` and
  `pip install "machinome[studio]"`; no section `machinome studio` in the
  CLI reference (`'.. _studio-command:...' not found`) and its "Commands
  from other packages" still saying the studio "is to add its own"; the
  stale spellings on the joined pages: `machinome-studio --projects-dir` in
  `howto/open-a-studio-project.rst`, `python -m floor` in
  `reference/studio/command.rst` and `reference/studio/troubleshooting.rst`,
  `github.com/machinome/machinome-studio` in `reference/studio/index.rst`,
  and, which the design did not name, the viewer's former separate manual
  `machinome-viewer.readthedocs` in `howto/studio-workspace.rst` and
  `reference/studio/index.rst`.

### 3.6 The studio's tests at the address (task 3.6)

The mechanical rewrite of `floor` to `machinome.studio` and of the resource
paths, taken from the proposer's prototype (`git -C <propose>/merge diff --
D/tests`, 42 files, 258 lines each way, `git apply` on the bench), then the
rewrites of Decision 14:

- `test_packaging.py` rewritten: the entry point in `machinome.commands`, no
  `scripts`, the version and the pins the core's, the `find`, the package
  data; and the new `FrameworkBoundaryTest.test_the_studio_imports_no_framework_module`.
- `test_license_headers.py` rewritten: the set's expression read from the
  core's manifest, on every tracked source file outside the records, and no
  SPDX line of a current file naming another.
- `test_machinome_identity.py`: the manifest's name and description, the
  README's `# machinome-studio` and command, the scripts' paths.
- `test_product_identity.py`: the plugin and setup-script tests go with the
  files they read.
- `test_documentation.py` rewritten for the folded manual: the eight pages
  under `packages/machinome/docs/`, the navigation, no manual of the
  package's own, the framework `conf.py`'s `studio_*` literals equal to the
  source constants and their substitutions, every launcher option of
  `__main__.py`, `orchestrator.py` and `cli.py` and every configuration key
  in `reference/studio/command.rst`, no catalogue project, checkout, former
  launcher, former module or readthedocs URL on a page.
- `test_runtime_profiles.py`: the builder's skills
  `machinome-api`, `machinome`, `machinome-simulate`; the profile's link read
  one level; the new `test_the_builder_s_skills_include_the_skills_package_s_simulate`
  and `test_a_profile_skill_may_reach_another_package_through_shop_skills`.
- The copied profiles (`test_runtime_profiles.py` 5, `test_openspec_tools.py`
  1, `test_project_runtime_selection.py` 1) copy `shop-skills/` with its
  links followed.
- `test_floor_entrypoint.py`: the registry's `shop_root` is the package
  directory; the new `StudioCommandTest` (the contract, `handle` calling
  `orchestrator.run`, the refusal without a folder, the listing loading none
  of the application in a fresh interpreter, the lazy root).
- `test_shop_lifecycle_e2e.py`: the class skips unless
  `MACHINOME_STUDIO_E2E=1`, naming it; the real bundle from
  `machinome.viewer.web`.
- `test_scoped_tools.py`: `engine="mesh"`/`"brep"` as `--mesh`/`--brep`,
  `fast`, `faceted` and `exact` refused naming `'brep' or 'mesh'`, `kernel`
  refused, the schema's `engine` enum.
- Three resource roots the mechanical rewrite left at `D`: the source test's
  `load_profile`, the model watcher's registry, the frame-precision test's
  `shop-skills/` (this last fixed after the red run below).

```
$ env -C <bench>/D PYTHONPATH=<bench>/D PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rfs -p no:cacheprovider
136 failed, 392 passed, 24 skipped, 2 warnings, 332 subtests passed in 233.47s (0:03:53)
```

(`<scratch>/3.6-studio-red.out`, classified in `<scratch>/3.6-classified.txt`.)
The imports resolved to the package directory at its address through
`PYTHONPATH` (`machinome.studio` from `<bench>/D/machinome/studio/`), the
core's `machinome/__init__.py` admitting the portion. The reds, by reason:

- 19 `FileNotFoundError`: 17 for `D/machinome/profiles` (the resource root
  naming `machinome/`, the model watcher's and the API's profile lookups),
  `D/machinome/studio/cli.py` (the launcher-options test reading the command
  module), and `D/shop-skills/machinome-api/SKILL.md` (the frame-precision
  test, corrected afterwards).
- 19 + 3 Codex `CodexProtocolError`: "Codex role context differs from its
  immutable project contract" (the role context built from the former
  resource root) and "Floor worker response failed".
- 18 `FloorAPITest` "Connection refused": the hub started as `python -m
  machinome.studio` exits at once, `RuntimeError: Directory
  '.../machinome/studio/static/assets' does not exist` (no built surface;
  read by starting it by hand).
- 3 `ModuleNotFoundError: No module named 'machinome.studio.cli'` and the
  fresh-interpreter listing test's `CalledProcessError` (the same).
- 3 `ModuleNotFoundError: No module named 'tomlkit'`: the bench venv does
  not yet hold the studio's dependencies (the sync of 8.2 installs them).
- 2 stdio MCP tests, `JSONDecodeError`: the server subprocess exits (the
  same `tomlkit`).
- 1 `OrchestratorShutdownAcceptanceTest`, "orchestrator did not open" (no
  built surface).
- the link refused: "profile openspec-builder.skills.machinome must link
  directly to shop-skills/<skill>"; the builder's skills
  `['machinome-api', 'machinome']`; the allowlist sets lacking
  `machinome-simulate`.
- the entry point's `shop_root` naming `D/machinome`, not the package
  directory.
- the console script and the manifest (`scripts` present, no
  `entry-points`, `find` `['floor', 'floor.*']`, version `0.1.0`).
- the licence lines (every tracked source file's SPDX line names the
  product's former licence); the boundary test:
  `machinome/studio/codex_auth.py floor.backends.codex_policy`.
- the identity: the former description, the scripts' `floor/` paths.
- the documentation's pages and facts (40 subtests): no `studio_*` literal
  or substitution in the framework's `conf.py`, the pages outside the
  navigation, the section's toctree, `$ machinome-studio`, `scripts/setup`,
  `github.com/machinome/machinome-studio`, `readthedocs.io`, `python -m
  floor.codex_auth login`, the package's `docs` extra, its root's docstring,
  its README and changelog.
- the tool's `engine`: `TypeError: ProjectTools.machinome_test() got an
  unexpected keyword argument 'engine'`.

Skipped: the 23 browser tests, "the browser tests run when
MACHINOME_STUDIO_E2E=1 is set", and the development workspace's
installation (as at the original).

### 3.7 (task 3.7)

Recorded above.

### 11.3, run here: `scripts/check-dist` red (task 11.3)

Run before any edit of the script (`<scratch>/11.3-check-dist-red.out`):

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
check-dist failed: machinome-studio has no smoke in scripts/check-dist
Nothing uploaded.
exit 1
```

### 10.1, run here: the manual red (task 10.1)

A fresh venv `<scratch>/docs-venv` from `packages/machinome/docs/requirements.txt`
alone (Sphinx 9.1.0, sphinx-rtd-theme 3.1.0, machinome-viewer 0.8.0), on the
joined pages before any of group 10's edits (`<scratch>/10.1-docs-red.out`):

```
$ env -C <bench>/packages/machinome <scratch>/docs-venv/bin/python -m sphinx -b html -n -W --keep-going docs <scratch>/html-red
build finished with problems, 43 warnings (with warnings treated as errors).
exit 1
```

The 43, design.md probe 13's: 20 unknown documents (`reference/cli`,
`installation`, `the-floor`, `working-with-agents`, `troubleshooting`,
`reference/profiles`, `reference/project-configuration`, `project/status`,
`opening-a-project`, `../installation`), 8 undefined substitutions
(`machinome-version`, `required-viewer-api` twice, `claude-models`,
`claude-efforts`, `codex-models`, `codex-efforts`, `build-volume`), 7 pages
in no toctree, 8 toctree entries naming documents of the former layout.

## 4. The package and its source

### 4.1 The links (task 4.1)

```
$ ln -s ../../LICENSE D/LICENSE; ln -s ../../LICENSES D/LICENSES; git add ...
$ git -C <bench> ls-files -s D | grep ^120000
120000 30cff740... 0	D/LICENSE
120000 06ad40db... 0	D/LICENSES
(and the four profile skill links of 2.2)
```

### 4.2 The manifest, README, MANIFEST.in and .gitignore (task 4.2)

`D/pyproject.toml`, `D/README.md` and `D/MANIFEST.in` as design.md Decision
3 spells them, verbatim; `D/.gitignore` replaced by the package's own
leavings of Decision 3. `MANIFEST.in` added with `git add`.

### 4.3 The licence lines (task 4.3)

```
$ git -C <bench> grep -l 'SPDX-License-Identifier: <the former expression>' -- D ':!D/openspec/changes/archive' ':!D/workflow' | wc -l
88
```

The 88 lines (79 `#`, 7 `//`, one `/* */`, one `<!-- -->`) in 88 files
(`machinome/studio/` 37, `scripts/` 2, `tests/` 49, `test_license_headers.py`
already rewritten in 3.6, so 88 lines rather than design.md's 89) rewritten
by a script asserting one occurrence per file; the frontend's `package.json`
`license` the set's. `git diff -U0` of those files shows the SPDX line alone
(and, for the files group 3 or 4 also edits, their other hunks).

```
$ git -C <bench> grep -n 'SPDX-License-Identifier' -- D ':!D/openspec/changes/archive' ':!D/workflow' | grep -v 'GPL-2.0-or-later OR CERN-OHL-S-2.0+'
(nothing)
```

`test_license_headers.py` names the marker in two pieces and reads the
expression from the core's manifest, so no line holds a pattern.

### 4.4 The source at its address (task 4.4)

As Decision 4: the lazy root (`__all__ = ["create_app"]`, a module
`__getattr__`); `preparation.shop_resource_root()` returns
`Path(__file__).resolve().parent`, its docstring saying so; `app.py`'s
default profile lookup calls it; `mcp_server.mcp_command` runs
`machinome.studio.mcp_server`; the Claude and OpenCode backends put
`shop_root.parents[1]` on `PYTHONPATH`; `codex_auth.LOGIN_COMMAND` is
`python -m machinome.studio.codex_auth login` and its one absolute import
`machinome.studio.backends.codex_policy`; `orchestrator.main()` parses and
calls the new `run(arguments)`; the docstrings of `__init__.py`,
`launcher.py` and `__main__.py` name `machinome studio` and the module forms.
`P/cli.py` (`Studio`) and `P/packaging.py` (the two hooks) are new, each with
the copyright and SPDX lines; both `git add`ed.

```
$ <bench>/.venv/bin/python -m flake8 --max-line-length=89 P/cli.py P/packaging.py
(exit 0)
```

Two departures from the design, found by the tests:

- **The Codex floor worker's working directory.** `backends/codex_tools.py`
  starts the MCP server for a Codex role with `cwd=context.shop_root` and a
  stripped environment with no `PYTHONPATH`: at the former root that
  directory held `floor/`, and `python -m floor.mcp_server` resolved from
  it. At the address the resource root is the package directory, from which
  `machinome.studio` does not resolve without an install, and which would put
  the package's modules (`packaging`, `openspec`, `profiles`) on `sys.path`
  as top-level names. The worker now runs from `Path(shop_root).parents[1]`,
  the directory holding the package's `machinome/`, the rule Decision 4 gave
  the two other backends' `PYTHONPATH`. Red before it: four Codex tests
  "Floor worker response failed" (`<scratch>/4.5b.out`); green after
  (`<scratch>/4.5c.out`, 75 passed).
- **The build hook's `npm ci`** runs at the npm workspace's root when the
  frontend is a member (found as the viewer's hook finds it), else in the
  frontend: the movie's join found that `npm ci` from a member's directory
  empties the other members' `node_modules`. Decision 3 says the hook runs
  `npm ci` "in the frontend, which inside the workspace install[s] at the
  root"; this is that, spelled as the viewer's hook spells it.

### 4.5 The tests of the address, the command and the packaging (task 4.5)

The tests' remaining resource roots, found in this group: the Codex
fixtures' `RoleContext(str(ROOT), ...)` (six, in five modules) and the
OpenCode and orchestrator tests' `shop_root=str(ROOT)` name the package
directory. With `PYTHONPATH=<bench>/D`, the venv not yet holding `tomlkit`:

```
$ ... pytest -q tests/test_floor_entrypoint.py tests/test_orchestrator.py tests/test_opencode_backend.py \
    tests/test_packaging.py tests/test_license_headers.py tests/test_backend_probe.py tests/test_codex_*.py
6 failed, 198 passed, 2 warnings, 30 subtests passed in 43.08s     (<scratch>/4.5b.out)
$ ... pytest -q tests/test_codex_*.py
75 passed, 1 warning, 18 subtests passed in 5.19s                  (<scratch>/4.5c.out, after the worker's cwd)
```

The six of the first run: the four Codex worker tests above; the shutdown
acceptance test, "orchestrator did not open" (no built surface until group
7); the packaging test's core extra (`['machinome-studio'] !=
['machinome-studio~=0.8.1']`, group 8).

## 5. The skills

### 5.1 The links (task 5.1)

```
$ readlink P/shop-skills/machinome-simulate
../../../../machinome-skills/machinome/skills/agent-skills/machinome-simulate
$ readlink P/profiles/{openspec-builder,fordesmac}/skills/machinome-simulate
../../../shop-skills/machinome-simulate      (each)
$ readlink -f .../machinome-simulate/SKILL.md
<bench>/packages/machinome-skills/machinome/skills/agent-skills/machinome-simulate/SKILL.md   (all three)
$ git -C <bench> ls-files -s D | grep -c ^120000
9
```

### 5.2 The loader and the allowlists (task 5.2)

`profiles._skill_path` reads the profile's link one level (`os.readlink`,
normalised against the link's directory), requires it to name
`shop-skills/<skill>` of the same shop, then resolves that entry and
requires a directory holding `SKILL.md`. The frontmatter `skills:` of
`openspec-builder/builder.md`, `fordesmac/designer.md` and
`fordesmac/machinist.md` gain `machinome-simulate`; the foreman and the
librarian do not.

```
$ ... pytest -q tests/test_runtime_profiles.py tests/test_project_runtime_selection.py tests/test_openspec_tools.py \
    tests/test_role_contracts.py tests/test_orchestrator.py tests/test_frame_precision_contract.py
4 failed, 129 passed, 1 warning, 57 subtests passed in 55.20s      (<scratch>/5.2.out)
```

The four: three `ModuleNotFoundError: No module named 'tomlkit'` (the venv,
group 8) and the shutdown test (the built surface, group 7). The new
`test_a_profile_skill_may_reach_another_package_through_shop_skills` and
`test_the_builder_s_skills_include_the_skills_package_s_simulate` pass.

## 6. The corrections the gates require

### 6.1 The test tool (task 6.1)

`ProjectTools.machinome_test(path, failfast, engine)`: `engine` in
`("brep", "mesh")`, passed as `--brep`/`--mesh`, refused otherwise "engine
must be 'brep' or 'mesh', not ..."; the schema's `engine` enum and
description as Decision 7 spells it.

```
$ ... pytest -q tests/test_scoped_tools.py                         (the studio's)
23 passed, 57 subtests passed in 1.53s                             (<scratch>/6.1-scoped.out)
$ ... pytest -q tests/test_core_names_no_split_words.py tests/test_node_root_exports_nothing.py   (the core's)
33 passed, 172 subtests passed in 6.27s                            (<scratch>/6-gates.out)
```

### 6.2 The skills (task 6.2)

What `machinome test --mesh` prints on the bench, read from a scratch
project made by `machinome new probe` (`<scratch>/6.2-mesh.out`):

```
Comparing on the mesh engine (volume epsilon 0 mm³): verdicts are at tessellation precision, not the B-rep engine's.
...
Ran 2 tests in 0.22 seconds: 2 passed, 0 failed (mesh engine, volume epsilon 0 mm³)
```

`git diff -U0` of the two skills shows these lines alone:

- `shop-skills/machinome/SKILL.md`: line 22 `machinome test --mesh`, 24
  `machinome test --brep`; the import at 59 as two imports
  (`machinome.node.assembly`, `machinome.node.cadquery`); 812 to 813
  `machinome test --mesh` and `engine="mesh"`; 893 `machinome test --brep`
  (`engine="brep"`); 896 the quoted summary `(mesh engine, ...)`.
- `shop-skills/machinome-api/SKILL.md`: the import list at 32 as fourteen
  imports, each name from its module (`assembly`, `fusion`, `cadquery`,
  `build123d`, `solid2`, `openscad`, `jscad`, `stl`, `step`, `molejo`,
  `declarative`, `decorators`, `markings`, `frames`), the two comments kept
  on their lines; the imports at 188, 799, 905, 1521 and 1840 from their
  modules; 1711 to 1712 `machinome test --mesh`, `--brep` and
  `SOLID_TEST_ENGINE`; 1714 to 1715 the quoted lines `Comparing on the mesh
  engine ...` and `(mesh engine, volume epsilon E mm³)`; 2485 the synopsis
  `[--brep | --mesh]`.

The node-root gate is green (6.1's run). The descriptive lines left with
the 0.7 engine words, by skill and line (after the edit):

- `machinome/SKILL.md` (11 lines): 538, 798, 810, 816, 818, 819, 892,
  893, 896, 897, 899 ("the faceted path", "Work on the faceted kernel",
  "runs exact", "the exact run", "the exact kernel", "the two kernels",
  "the exact verdict", "A faceted failure", "a faceted pass").
- `machinome-api/SKILL.md` (20 lines): the table row at 104, and 134, 179,
  1442, 1443, 1540, 1662, 1704, 1708, 1709, 1710, 1713, 1716, 1717, 1719,
  1720, 1722, 1726, 1732, 1736 ("faceted and slow", "faceted-kernel
  verdicts", "the exact kernel is unaffected", "on the faceted path", "one
  **kernel**", "`exact` (the default ...)", "or `faceted` (every question
  ...)", "A faceted run prints", "an exact run's output", "makes a faceted
  run", "the exact kernel refuses it", "A faceted verdict", "the faceted
  kernel for the loop", "both kernels", "the installed kernels").

The list is `grep -n -E 'faceted|kernel|exact run|runs exact|exact
verdict|exact kernel|`exact`'` over each skill.

Lines where "exact" is the ordinary adjective or names exact geometry
(`node.exact`, "exact nodes") are not counted.

## 7. The npm workspace

### 7.1 The third member and the seeded lock (task 7.1)

The root `package.json`'s `workspaces` gains
`packages/machinome-studio/machinome/studio/frontend`; the frontend's
`package.json` is `@machinome/studio`, version `0.8.1`, the set's licence
(4.3), `private`, its scripts and dependencies unchanged;
`D/machinome/studio/frontend/package-lock.json` removed with `git rm`. The
root lock seeded by `<scratch>/seed-root-lock.py` from the frontend's own
lock (`<scratch>/frontend-own-lock.json`, the root's before at
`<scratch>/root-lock-before.json`):

```
$ <bench>/.venv/bin/python <scratch>/seed-root-lock.py <bench> <scratch>/frontend-own-lock.json
root entries before 264, member resolutions seeded 133, entries after 399
$ env -C <bench> npm install --no-audit --no-fund
added 128 packages in 9s                                           (<scratch>/7.1-npm-install.out)
$ env -C <bench> npm install --package-lock-only --no-audit --no-fund
up to date in 349ms
```

The comparison (`<scratch>/7.1-compare.txt`): 399 entries before and after
the install; the root's 264 entries unchanged but the root entry's
`workspaces`; the member's 133 resolutions kept (version, resolved and
integrity each), 0 moved, 0 missing; the one new key outside the member
`node_modules/@machinome/studio`; every entry equal to the seeded one, npm
having only sorted the keys. A second `npm install --package-lock-only`:
"up to date", the lock byte for byte. `git diff --stat package-lock.json`:
1964 insertions, 1 deletion. The member's own `node_modules` holds 50
directories (TypeScript 5.9.3, vite 7.3.6).

### 7.2 The frontend from the root (task 7.2)

```
$ env -C <bench> npm test --workspace D/machinome/studio/frontend          exit 0, 2.6 s
$ env -C <bench> npm run build --workspace D/machinome/studio/frontend     exit 0, 10.3 s, P/static/index.html written
  (vite's chunk-size warning, as the original build gives)
$ env -C <bench> npm run build --workspaces --if-present                   exit 0: @machinome/viewer (dist/machinome-viewer.js 895.9kb), @machinome/studio
$ git -C <bench> status --short | grep -E 'node_modules|static/|dist/'
(nothing)
```

## 8. The core, the uv workspace and the sync

### 8.1 The extra and the vet (task 8.1)

`packages/machinome/pyproject.toml`: `studio = ["machinome-studio~=0.8.1"]`
with the comment of Decision 9; `machinome/vet/universe.toml`: `deny` gains
`"machinome.studio"` after `"machinome.movie"` with its comment. `git diff`
shows those two hunks alone.

```
$ ... pytest -q tests/test_vet_universe.py tests/test_kernel_extras.py
36 passed, 85 subtests passed in 2.20s                             (<scratch>/8.1.out)
```

### 8.2 The workspace, the lock and the sync (task 8.2)

The root `pyproject.toml`: `machinome-studio = { workspace = true }` after
`machinome-skills`; `exclude-dependencies` and its comment gone; the `dev`
group gains `"machinome[studio]"`, its comment naming the studio.

```
$ env -C <bench> uv lock
Resolved 200 packages in 799ms
Added machinome-studio v0.8.1
Added tomlkit v0.15.1
```

198 at the base plus two. The lock's diff (`<scratch>/8.2-uv-lock.diff`): 38
insertions, 2 deletions; its package lines `+name = "machinome-studio"`,
`+version = "0.8.1"`, `+name = "tomlkit"`, `+version = "0.15.1"`.

```
$ env -C <bench> uv sync --python 3.12
Installed 3 packages in 37ms
 ~ machinome==0.8.1 (from file:///.../packages/machinome)
 + machinome-studio==0.8.1 (from file:///.../packages/machinome-studio)
 + tomlkit==0.15.1
```

Seventeen `__editable__` `.pth` files, the new one naming `<bench>/D`. From
`/tmp` (`<scratch>/8.2-probes.out`):

```
$ python -c "import machinome.studio as s; print(s.__file__)"
<bench>/D/machinome/studio/__init__.py
$ python -c "import floor"
ModuleNotFoundError: No module named 'floor'
$ machinome studio -h
usage: machinome studio [-h] [--projects-dir PATH] [--port PORT]
...  (exit 0)
$ python -c "...entry_points(group='machinome.commands')..."
[('skills', 'machinome.skills.cli:Skills', 'machinome-skills'), ('movie', 'machinome.movie.cli:Movie', 'machinome-movie'), ('studio', 'machinome.studio.cli:Studio', 'machinome-studio')]
$ machinome -h
    studio              Open the studio: the project hub and its agents, in
                        the browser
```

### 8.3 The seam and the cost (task 8.3)

```
$ ... pytest -q tests/test_cli_contributed.py tests/test_cli_lazy_imports.py tests/test_machinome_identity.py
40 passed, 32 subtests passed in 16.53s                            (<scratch>/8.3-seam.out)
$ ... pytest -v tests/test_cli_lazy_imports.py -k test_every_contributed_entry_resolves_and_honours_the_contract
1 passed, 22 deselected, 3 subtests passed                          (skills, movie, studio)
```

`test_cli_lazy_imports.py`'s docstring of that walk now names the studio's
entry (it said the walk would hold the studio once the workspace installed
it).

The cost: `python -X importtime -c "import machinome.studio.cli"` from `/tmp`
(`<scratch>/8.3-importtime.txt`): 78 modules, none of `fastapi`,
`starlette`, `uvicorn`, `watchdog`, `tomlkit`, `pydantic`,
`machinome.studio.app` or `machinome.studio.orchestrator`;
`machinome.studio.cli` cumulative 32 ms. The timing against the base: the
bench venv holds the studio after the sync, so two light venvs were made
under the scratch directory from the bench's members, editable in compat
mode, `timing-base` (the core, the viewer, the skills and the movie) and
`timing-studio` (the same and the studio); nine runs each, alternating
(`<scratch>/timing.py`, `<scratch>/8.3-timing.txt`):

```
base machinome -h: median 639 ms, min 585, max 1564
studio machinome -h: median 637 ms, min 603, max 1578
studio machinome studio -h: median 78 ms, min 71, max 90
```

`machinome -h` with and without the studio within the run-to-run spread;
`machinome studio -h` 78 ms (design.md probe 9: 76 ms with a lazy root, 351
ms with the eager one).

### 8.4 The four gates again (task 8.4)

```
$ ... pytest -q tests/test_repository_layout.py tests/test_release_records.py \
    tests/test_core_names_no_split_words.py tests/test_node_root_exports_nothing.py
106 passed, 816 subtests passed in 17.85s                          (<scratch>/8.4-gates.out)
```

All green: the README row, the guide, the Makefile, CI and the bump tables
of groups 11 and 12 had been written before this run (the order of the
work, not of the tasks; their reds are 2.3's and 3.1's).


## 9. The tests at their new place

### 9.1 The studio's tests (task 9.1)

From `<bench>/D`, no `PYTHONPATH`, the package installed by the sync, the
surface built, the OpenSpec CLI on the `PATH`
(`<scratch>/9.1-studio.out`, before the manual's group): 51 failed, 479
passed, 24 skipped. The failures: the documentation tests group 10 settles
(45 subtests over 4 tests), the identity's scripts test (13.1), and one
test of the address the mechanical rewrite had left: `OpenCodeBackend(ROOT,
...)` built at `D` rather than the package directory, so its `PYTHONPATH`
held the bench's root (`'<bench>/D' not found in ['<bench>']`). That test
and the orchestrator's five Claude backends built at `ROOT` now name
`ROOT / "machinome" / "studio"` (`<scratch>/9.1-fix.out`: 101 passed).

On the final tree, `make test PKG=machinome-studio` (11.2): 485 passed, 24
skipped. Once with the browser tests opted in, `TMPDIR` under the scratch
directory, the widget's bundle built by `npm run build --workspaces`
(`<scratch>/9.1-studio-e2e.out`):

```
$ env -C <bench>/D MACHINOME_STUDIO_E2E=1 TMPDIR=<scratch>/tmp-e2e PATH=<bench>/.venv/bin:$PATH \
    <bench>/.venv/bin/python -m pytest -q -rfs -p no:cacheprovider
508 passed, 1 skipped, 3 warnings, 420 subtests passed in 173.54s (0:02:53)
exit 0
```

The one skip: the development workspace's installation, as at the
original. The 23 browser tests passed, the real-bundle test among them
(the viewer found at `machinome.viewer.web`). Against probe 10's 499 passed
and 1 skipped at the original layout (500 tests), 509 tests: three gone with
what they read (the plugin, the setup script, the console script) and
twelve added (`test_packaging.py` four and the boundary test,
`test_license_headers.py` one, `test_runtime_profiles.py` two,
`StudioCommandTest` five), `test_documentation.py` one fewer (23 for 24).

### 9.2 The core's suite collects none of them (task 9.2)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest --collect-only -q -p no:cacheprovider | grep -c machinome-studio
0
4921 tests collected
```

(`<scratch>/9.2-collect.out`.)

## 10. The manual

### 10.1 Red first (task 10.1)

Recorded above, before group 3's end: 43 warnings, exit 1.

### 10.2 to 10.4 The pages (tasks 10.2 to 10.4)

- `docs/conf.py`: the release facts `studio_viewer_api`,
  `studio_claude_models`, `studio_claude_efforts`, `studio_codex_version`,
  `studio_codex_models`, `studio_codex_efforts` and `studio_build_volume`
  as literals with their comment, and their seven substitutions, the
  model and effort lists rendered as literals by a helper `literals()`.
- `docs/index.rst`: the three how-tos after `howto/draw-a-movie-stage`,
  `reference/studio/index` after `reference/movie/index`.
- `reference/studio/index.rst` rewritten in place: the title "Studio", the
  landing's two paragraphs, the package sentence, a sentence sending the
  reader to the three how-tos, "What it runs against" and "Limits" for the
  joined package (`|release|`, `|studio_viewer_api|`,
  `|studio_codex_version|`, Linux x86_64; no clone, no setup script, no
  licence sentence, no link to the former repository), the toctree of the
  four reference pages.
- `howto/open-a-studio-project.rst`: the title "Open a project in the
  studio", an opening paragraph, "What you need" (Linux, Python 3.11, Git,
  OpenSCAD, the OpenSpec CLI `npm install -g @fission-ai/openspec`, a
  logged-in backend) and "Install" (`pip install "machinome[studio]"`,
  `playwright install chromium`) before its own sections; `machinome studio
  --projects-dir ~/machines` and the configuration file's two lines; every
  link to its new page.
- `howto/studio-workspace.rst`: the title "Work in a project's workspace";
  the viewer's guide as the `:doc:` link to `/howto/browser-viewer` in place of the
  viewer's former separate manual's URL (a stale spelling the framework's
  gate names, which the design did not list); `|studio_build_volume|`.
- `howto/studio-agents.rst`: the title "Choose and steer the studio's
  agents"; `machinome-simulate` among the skills, with the three roles that
  may load it; the section "Using Codex", from the dropped installation
  page, with `python -m machinome.studio.codex_auth login`.
- `reference/studio/command.rst`: the title "The studio command", the
  synopsis `machinome studio [--projects-dir PATH] [--port PORT]`, the
  module forms at `machinome.studio`, "It opens no browser", the Codex
  login at its module; the options, the configuration file and the
  precedence unchanged.
- `reference/studio/project-configuration.rst`: the four substitutions
  renamed. `reference/studio/profiles.rst`: `machinome-simulate` in the
  builder's, the designer's and the machinist's rows, and one sentence
  saying it is the skills package's. `reference/studio/troubleshooting.rst`:
  the setup script gone from three entries, the blank page's remedy a
  reinstall of the package (the source build is the contributor guide's),
  the viewer's remedy `pip install --upgrade "machinome[studio]"`, the
  Codex login at its module, every link to its new page.
- The framework's pages: `start/install.rst` ("Five more extras": the
  `studio` extra with its distribution, its prerequisites and its second
  step, and `machinome-studio` among the packages of the set under the
  set's licence); `reference/cli.rst` ("Commands from other packages" names
  the studio's command; the section `machinome studio`, anchor
  `studio-command`); `project/status.rst` (the studio's paragraph);
  `project/upgrading.rst` (the 0.8 sentence in that release's past,
  "In 0.8 the ``studio`` extra named Machinome Studio, which no index
  served.").

### 10.5 The build (task 10.5)

```
$ env -C <bench>/packages/machinome <scratch>/docs-venv/bin/python -m sphinx -b html -n -W --keep-going docs <scratch>/html
build succeeded.
exit 0
```

(`<scratch>/10.5-docs.out`, 0 lines with "warning".) Photographed in
Chromium from `<scratch>/html` (`<scratch>/photograph-docs.py`) and looked
at: `<scratch>/docs-studio-index.png` (the section "Studio" under Reference
in the navigation, the package sentence, "What it runs against" with API 20
and codex-cli 0.157.1, the limits, the four reference pages listed);
`<scratch>/docs-open-a-studio-project.png` (the install part, the two
install lines, `machinome studio --projects-dir ~/machines`, the
configuration file's block, every link resolved to a page title);
`<scratch>/docs-studio-command.png`; `<scratch>/docs-cli-studio.png` (the
CLI reference's section `machinome studio` with its synopsis, options,
module forms and exit statuses).

```
$ ... pytest -q tests/test_docs_structure.py tests/test_docs_exports.py tests/test_release_records.py tests/test_repository_layout.py
123 passed, 3038 subtests passed in 5.97s                          (<scratch>/10.5-tests.out)
$ env -C <bench>/D ... pytest -q tests/test_documentation.py
2 failed, 22 passed, 230 subtests passed                           (<scratch>/10.5-studio-doc.out)
```

The two: the records test globbed `*product*.md` under the manual and found
five framework ADRs named for products (my test's error, narrowed to the
records' own names and directories), and the studio's changelog, not yet
written (12.1). Both green in 11.2's run.

## 11. The version records, the Makefile, `scripts/check-dist` and CI

### 11.1 The bump on a copy (task 11.1)

`.bumpversion.cfg` gains, after the skills' tables (themselves after the
movie's), the studio's three: `file(version)` and `file(pins)` of
`D/pyproject.toml`, and `file` of the frontend's `package.json`. On a copy
(`<scratch>/bump-copy`, a Git repository of the 28 files the configuration
names, with the root `package.json`, `.npmrc`, `package-lock.json` and the
three members' `package.json` and the movie's lock):

```
$ env -C <scratch>/bump-copy <bench>/.venv/bin/python -m bumpversion --no-commit --no-tag --new-version 0.9.0 patch   exit 0
$ env -C <scratch>/bump-copy npm install --package-lock-only --no-audit --no-fund                                     exit 0
$ git -C <scratch>/bump-copy diff --stat
 25 files changed, 68 insertions(+), 68 deletions(-)
```

(`<scratch>/11.1-stat.txt`, `<scratch>/11.1-diff.txt`.) Of the studio: its
manifest's `version = "0.9.0"`, its two pins `machinome~=0.9.0` and
`machinome-viewer[snapshot]~=0.9.0`, the frontend's `"version": "0.9.0"`,
the root lock's entry for `packages/machinome-studio/machinome/studio/frontend`
at 0.9.0 (with the widget's and the movie's), and the core's extra
`machinome-studio~=0.9.0`; nothing else of the studio. The recipe's loop
over `MEMBER_LOCKS` (the movie's own lock) and `uv lock` were not run on
the copy, which holds no uv workspace; neither names the studio. Nothing was
written in the bench.

### 11.2 The Makefile (task 11.2)

`PACKAGES` gains `machinome-studio` after `machinome-skills`; `TESTED` gains
it after `machinome-movie`; `STUDIO_FRONTEND` beside `WIDGET` and
`MOVIE_JS`; the rule `test-machinome-studio` (the frontend's typecheck and
build, then pytest from the package's directory) with its comment; `CLEAN`
gains the studio's `static/`. `TheMakefileTest` green in 8.4.

```
$ env -C <bench> PYTEST_ADDOPTS="-rfs -p no:cacheprovider" make test PKG=machinome-studio
npm test --workspace packages/machinome-studio/machinome/studio/frontend
npm run build --workspace packages/machinome-studio/machinome/studio/frontend
✓ built in 8.03s
cd packages/machinome-studio && <bench>/.venv/bin/python -m pytest
485 passed, 24 skipped, 3 warnings in 109.28s
exit 0
```

(`<scratch>/11.2-make-test-studio.out`.) The 24 skips: the 23 browser tests,
"the browser tests run when MACHINOME_STUDIO_E2E=1 is set", and the
development workspace's installation.

### 11.3 Red first (task 11.3)

Recorded above: "machinome-studio has no smoke in scripts/check-dist".

### 11.4 The row (task 11.4)

The refusal before building when the studio is a member and npm is absent;
the docstring's account of what it writes (the members' `node_modules/` and
the studio's `machinome/studio/static/`); the row of Decision 12 after the
movie's, two of its lines wrapped at 89 columns (the shipped skill's path
and the viewer pin). `git diff scripts/check-dist`: 3 lines removed, all of
the docstring; no line of another row changed.

```
$ <bench>/.venv/bin/python -m flake8 --max-line-length=89 scripts/check-dist
(exit 0)
```

### 11.6 CI (task 11.6)

`.github/workflows/python-app.yml`'s `test` job gains, after "Install
Chromium" and before "Run the tests", the step "Install the OpenSpec CLI",
`npm install -g @fission-ai/openspec@1.6.0`, with its comment; "Run the
tests"' comment names the studio. The layout gate's rule that no job spells
`npm` exempts that one step by its exact command; its new
`test_the_test_job_installs_the_openspec_cli_before_the_tests` holds it
after Node and before `make test`. Green in 8.4.

## 12. The records

### 12.1 The changelogs (task 12.1)

`HISTORY.rst`: the bullet of Decision 15 at the end of `Unreleased` (after
`release-tooling`'s, itself after the movie's). `docs/project/changelog.rst`:
the bullet at the end of `Unreleased`. The studio's `CHANGELOG.md`: the
`Unreleased` opening paragraph, the subsection "Joined to the Machinome
repository" with its three bullets above "What a maker gets", and the
manual's bullet saying the manual is part of Machinome's.

### 12.2 `CREDITS.md` and the brand README (task 12.2)

`CREDITS.md`'s section "Carried by the studio", after the viewer's: the
three fonts with their notices' copyright lines (Anta 2019 and the
Machinome adaptation 2026, Space Grotesk 2020, IBM Plex Mono 2017 with its
reserved font name), the identity's artwork with the trademark statement
(Open Questions 13: no public licence; trademarks of Poiesis Tecnologia da
Informação LTDA, to which the repository's licence grants no right), and the
ten packages minified into the built surface with the versions the root lock
resolves for the frontend (react, react-dom 19.2.7, scheduler 0.27.0, three
0.185.1, monaco-editor 0.56.0, @monaco-editor/react 4.7.0,
@monaco-editor/loader 1.7.0, state-local 1.0.7, marked 14.0.0, dompurify
3.4.8 under "MPL-2.0 OR Apache-2.0" as its `package.json` names it). The
summary table is unchanged (a compatibility column the design did not ask
for). "Adapted from Machinome Studio, in the skills package" names
`packages/machinome-studio/` in place of the former repository's URL.
`P/frontend/public/assets/brand/README.md` points at `CREDITS.md` in place
of the dropped `NOTICE`; the `NOTICE`'s term on a modified version's name
and marks is left to the pilot.

### 12.3 `docs/architecture.md` (task 12.3)

The section "Studio (STUDIO · specs `studio-distribution`, `cli`)" after
"Movies"; the CLI paragraph's last sentence names `machinome studio` the
third contributor (ADR-193); the Map's row "Studio, the distribution
`machinome-studio`".

### 12.4 The root's records (task 12.4)

The root `README.md`'s row after the movie's; `CONTRIBUTING.rst` (the three
npm members, the OpenSpec CLI's global install, `-e
packages/machinome-studio` in the pip block, the studio's tests with `make
test PKG=machinome-studio` and `MACHINOME_STUDIO_E2E=1`, the surface's build
from the root and its being untracked, `make clean`'s list);
`context7.json` (three `excludeFolders` and the rule, inserted as text so no
other line moves); `AI-USE.md` (the studio under
`packages/machinome-studio/`, joined with its history on 12 October 2026, in
the paragraph on what is agent-written; machinome-studio out of the sibling
repositories). The layout gate's README, guide and index tests and the
release records' context7 test are green (8.4, 10.5).

### 12.5 ADR-193 and the amendments (task 12.5)

`docs/adrs/BUILD/ADR-193-the-studio-is-a-product-of-the-set-reached-by-machinome-studio.md`,
Status Proposed, Change `join-studio`, as Decision 15 outlines it, with two
consequences the design's outline did not list (the identity's artwork
travelling without the set's licence, Open Questions 13; the branches held
in the former repository, Decision 1). Its index line under BUILD after
ADR-192 ("**Proposed**, amends 182/188/189, cites 187/190/191"). ADR-182,
ADR-188 and ADR-189: their status lines name the amendment, each gains a
dated consequence "Neutral (2026-10-12, `join-studio`): ...", and their
index lines "amended by 193".

### 12.6 The former licences (task 12.6)

Over the 782 paths of `git diff --name-only e08b5539` and the untracked
files (the join's 738 among them), `grep -c` for the licence the product
carried (its identifier's prefix and its long name) and for the framework's former one
(`<scratch>/12.6-grep.txt`):

- the product's former licence: `HISTORY.rst` 1 (a line of its 0.6-era
  entries, unchanged by this change); the studio's archived changes, 8
  files (three spikes, five records), 1 each but `adopt-the-viewer-navigator`'s
  evidence 2; `workflow/architecture-overview.md` 1 (its line on the
  viewer); `workflow/design/` 10 files, 1 each; `workflow/spikes/` 3 files,
  1 each. No line this change wrote (one of this file's red reasons quoted
  it and was rewritten).
- the framework's former licence: `HISTORY.rst` 1 (unchanged by this
  change); `CREDITS.md` and `package-lock.json`, third-party provenance and
  third-party packages' own `license` fields only.

## 13. The product's record

### 13.1 In place (task 13.1)

- `openspec/config.yaml` names neither the package nor the repository
  (`schema: spec-driven`): unchanged.
- `openspec/specs/shop-floor-lifecycle/spec.md`, "The shop starts from an
  installed command": `machinome studio`, a command of `machinome` through
  `machinome.commands`, no console script and no module `floor`; the module
  forms at `machinome.studio` in the requirement and its scenarios (two
  `python -m floor.orchestrator`, one `python -m floor`, eight command
  spellings in this and the configuration file's scenarios); titles kept.
- `openspec/specs/shop-runtime-profile/spec.md`, "Profile prompts and
  skills are contained and allowlisted": the profile's link read one level,
  `shop-skills/<skill>` a directory or a relative link to one; the scenario
  "A skill link escapes its runtime namespace" reworded, its title kept; the
  scenario "A shop skill links the skills package" added.
- `openspec/specs/scoped-agent-tools/spec.md`, "machinome build and test
  tools": the test tool's `engine`; the scenario "Tests run on the engine
  the agent names" added.
- `openspec/specs/user-documentation/spec.md`: every requirement's body for
  the folded manual, every requirement and scenario title kept.
- `openspec/specs/product-identity/spec.md`: the package
  `machinome.studio` and the command `machinome studio` beside the
  identifier `machinome-studio`; "plugin" and "repository" leave the
  identifier's list.
- `workflow/README.md` (its note on `documentation.md` and "Where this
  fits"), `workflow/documentation.md` (rewritten: the pages in the
  framework's manual, the release facts and the tests that hold them),
  `P/frontend/README.md` (the commands from the root, `static/` beside the
  package's modules, `make test PKG=machinome-studio` and the browser
  tests' opt-in), `scripts/test-e2e` (the build from the root, then the
  three modules with `MACHINOME_STUDIO_E2E=1`), `scripts/build-favicon`
  (reads and writes under `P/frontend/public/assets/`), the decision log's
  note of Decision 15 under its opening, its index's line for ADR 0033 and
  that ADR's status line, the index's pointer to `../architecture-overview.md`.

### 13.2 (task 13.2)

```
$ env -C <bench>/D openspec validate --specs --strict
Totals: 26 passed, 0 failed (26 items)
exit 0
```

(`<scratch>/13.2-validate.out`.)

## 14. Validation and the originating check

### 14.3 The lint (task 14.3)

```
$ env -C <bench> make lint
591 files would be reformatted, 200 files would be left unchanged, 1 file would fail to reformat.
(make's exit 2)
```

(`<scratch>/14.3-lint.out`.) flake8: 2549 lines, 744 of them the studio's,
so 1805 elsewhere, `release-tooling`'s count; black: 28 more files to
reformat and 2 more left unchanged than `release-tooling`'s 563 and 198, the
studio's modules (its new `cli.py` and `packaging.py` among the unchanged;
flake8 at 89 columns finds nothing in either). The failing file is the
vet's planted `broken.py`, as before. CI's lint step is
`continue-on-error`.

### 14.6 No universe sweep (task 14.6)

```
$ grep -rIlE --include=*.py '^(from|import) (floor|machinome\.studio)\b' /home/asa/devel/machinome/projects
(no file)
$ grep -rIlE --include=*.md --include=*.sh --include=*.toml 'machinome-studio --projects-dir|python -m floor' /home/asa/devel/machinome/projects
(no file)
```

(`<scratch>/14.6-grep.txt`.) The core's one change a model could reach is
`machinome/vet/universe.toml`'s denylist, which names `machinome.studio`, a
package no project imports.

### 14.1 The suite (task 14.1)

```
$ env -C <bench> PYTEST_ADDOPTS="-q -rs -p no:cacheprovider" make test PKG=machinome
1 failed, 4915 passed, 9 skipped, 55 warnings, 9046 subtests passed in 790.68s (0:13:10)
```

(`<scratch>/14.1-suite.out`.) The one failure is my invocation's, not the
tree's: `test_supported_node_types.py::TheFreeCADTestsSkipWithoutARuntimeTest::test_the_public_module_skips_naming_the_variable`
runs a pytest subprocess that inherits `PYTEST_ADDOPTS`, where my extra
`-q` made it `-qq`, which prints no summary line, so "1 skipped" was not
found. Rerun alone without that variable (`<scratch>/14.1-rerun-one.out`):
1 passed. The run of 14.2 below, without `-q`, holds the core's count.

The nine skips are the base's (four FreeCAD without
`MACHINOME_FREECAD_ROOT`, the real browser capture without
`MACHINOME_WEB_SNAPSHOT_E2E`, networkx, the jscad CLI, two vendor STEP
files). 4916 tests run: the base's 4909 passed and the seven this change
adds, `test_the_test_job_installs_the_openspec_cli_before_the_tests` and
`test_the_studio_s_rule_builds_its_frontend_before_its_tests` (layout),
`test_the_studio_s_frontend_version_files_agree` (release records),
`test_the_studio_is_internal_and_its_former_name_outside` (vet), and
`test_the_studio_is_three_how_tos_and_a_reference_section`,
`test_the_studio_command_has_its_section` and
`test_the_studio_is_no_longer_to_add_its_command` (the manual).

### 14.9 OpenSpec (task 14.9)

```
$ env -C <bench>/packages/machinome openspec validate join-studio --strict
Change 'join-studio' is valid
```

### 14.2 Every package's tests (task 14.2)

```
$ env -C <bench> PYTEST_ADDOPTS="-rs -p no:cacheprovider" make test
the core:            4916 passed, 9 skipped, 55 warnings in 790.80s
the mechanics:       204 passed
the skills:          47 passed
the viewer's widget: Test Files 65 passed | 1 skipped; Tests 1715 passed | 2 skipped
the viewer:          252 passed, 2 skipped
the movie:           322 passed; its Node pure and stage projects, 31 files, 329 passed
the studio:          its frontend's typecheck and build, then 485 passed, 24 skipped
exit 0
```

(`<scratch>/14.2-make-test.out`.) The core's 4916 are the base's 4909 and
the seven of 14.1, its nine skips the base's. The studio's browser tests, run
once opted in, are 9.1's.

### 11.5 and 14.5 `scripts/check-dist` on the tree and on a clean copy (tasks 11.5 and 14.5)

ADR-193 and this file added to the index (`git add`) so the clean copy of
the tracked files holds them. Then:

```
$ env -C <bench> TMPDIR=<scratch>/tmp-check make check
```

(`<scratch>/14.5-make-check.out`, exit 0.) Each run, the tree's and the
clean copy's: seventeen members built (`Members: machinome, ...,
machinome-skills, machinome-studio, machinome-viewer`), 34 archives, each
`twine check --strict` PASSED (68 PASSED lines over the two runs), every
linked file of each sdist a regular file equal to the root's (the studio's
`LICENSE` and the two `LICENSES` texts among them), every wheel installed in
a throwaway venv and smoked, "Every distribution built, checked, installed
and smoked; nothing uploaded." The studio's row on each run:

```
License-Expression: GPL-2.0-or-later OR CERN-OHL-S-2.0+
   licenses/LICENSE
   licenses/LICENSES/CERN-OHL-S-2.0.txt
   licenses/LICENSES/GPL-2.0-or-later.txt
machinome-studio 0.8.1 module <venv>/lib/python3.12/site-packages/machinome/studio/__init__.py hub answered
$ <venv>/bin/machinome studio -h
   machinome studio -h: exit 0
```

That is, in the installed environment: the wheel's files owned by the
distribution holding `cli.py`, `static/index.html` and
`shop-skills/machinome-simulate/SKILL.md` and no frontend source,
`node_modules` or `machinome/__init__.py`; the resource root the installed
package directory; the version and both pins the set's; the core's extra;
the entry point; both profiles loaded, the builder's skills
`machinome-api`, `machinome`, `machinome-simulate`; `machinome studio` on a
scratch catalogue printing its address and its hub answering with the
studio's page.

The archives' entries: the studio's sdist 1172 and wheel 113 on both runs
(design.md probe 7's); the framework's sdist 1149 from the tree and 1093
from the clean copy, the base's 1083 and ten: the eight joined pages,
ADR-193 and this file; its wheel 114, unchanged. `git -C <bench> status
--short` afterwards: no new path; no `dist/`.

### 14.7 The originating check (task 14.7)

A scratch catalogue `<scratch>/catalogue` holding a fresh clone of
`file:///home/asa/devel/machinome/projects/Vibecoded-demos/gear-shift`
(f3c79c2, profile `fordesmac`), and `<scratch>/originating.py` run from the
bench venv on port 9287 (not the pilot's 9010), `XDG_CONFIG_HOME` an empty
scratch directory and neither `MACHINOME_STUDIO_CONFIG` nor `FLOOR_PORT` set
(`<scratch>/14.7-originating.out`):

```
$ machinome studio --projects-dir <scratch>/catalogue --port 9287
shop-floor open at http://127.0.0.1:9287                           (<scratch>/14.7-hub.out)
GET /health          {"status": "open"}
GET /api/entries     the project gear-shift, openable, profile fordesmac, branch main, state closed
GET /api/backends    claude found (2.1.280), opencode found (1.18.31), codex found (codex-cli 0.162.1)
```

The hub photographed in Chromium, `<scratch>/14.7-hub.png`, and looked at:
the wordmark with its `Studio` qualifier, the working folder (1 project),
three backends detected, the card of gear-shift with its model preview
("closed · fordesmac · 7d ago") and the New project card; no page error.
Stopped (SIGTERM).

```
$ python -m machinome.studio --projects-dir <scratch>/catalogue --port 9287
POST /api/sessions {"path": "gear-shift"}    202 {"state": "opening"}
GET /api/entries     gear-shift state open, model_building false, failure null
```

No agent started (the module form runs the hub without agents). The floor
page `/projects/gear-shift` photographed after 15 s,
`<scratch>/14.7-floor.png`, and looked at: the title bar "Studio /
gear-shift", "fordesmac · open"; the Model area with the gearbox in the
viewer (the frame, the three shafts with their gears, the selector); the
assembly navigator with `GearboxDemo` (ROOT) and its five children
`open_frame`, `input_axis`, `layshaft_axis`, `output_axis`, `selector`;
"No agents are currently manifested"; the Foreman's empty conversation; no
page error. Stopped. Afterwards `ss -ltn` shows nothing on 9287 and no
studio process remains; `git -C <scratch>/catalogue/gear-shift status
--short` is empty.

### 14.8 Git (task 14.8)

`git -C <bench> status --short` (`<scratch>/14.8-status.txt`): 163 lines,
152 modified, 9 added (`D/LICENSE`, `D/LICENSES`, `D/MANIFEST.in`,
`P/cli.py`, `P/packaging.py`, the three `machinome-simulate` links,
ADR-193), this file added and modified since, the frontend's lock deleted;
no untracked path. `git ls-files -ci --exclude-standard | wc -l`: 34, the
base's. The ignored leavings are the build's and the suites' (the members'
`__pycache__`, `*.egg-info`, `node_modules`, the studio's `static/`, the
widget's `dist/`, the viewer's `tests/_shots/`, the core's test fixtures'
STEP and STL files).

## 14.10 The checkpoint (task 14.10)

Reported to the orchestrator; reviewed on 12 October 2026, the six
departures recorded above standing, the frozen sync of 1.2 accepted, and one
correction asked for: the studio's `CHANGELOG.md` "What a maker gets" opened
with the pre-join bullet on the `machinome-studio` command. Its first lines
now name the command `machinome studio`, installed by `pip install
"machinome[studio]"`, starting the same hub as `python -m
machinome.studio.orchestrator`; the rest of the bullet and of the section is
unchanged. The orchestrator's own validation of the bench (`make test
PKG=machinome`, `make test PKG=machinome-studio`, `make docs`, `make
check`) started at 18:30; no pytest and no `check-dist` of mine ran during
it, and the archive below ran once its `make check` was building the clean
copy, outside the bench.

## 15. Records closing

### 15.1 ADR-193 (task 15.1)

`docs/adrs/BUILD/ADR-193-the-studio-is-a-product-of-the-set-reached-by-machinome-studio.md`:
Status Accepted, its change link the archive's; its index line in
`docs/adrs/README.md` "**Accepted**, amends 182/188/189, cites 187/190/191".
`docs/architecture.md` checked against it: the section "Studio", the CLI
paragraph's third contributor and the Map's row agree with the decision
outcome.

### 15.2 The archive (task 15.2)

```
$ env -C <bench>/packages/machinome openspec archive join-studio -y
Specs to update:
  cli: update
  cli-startup-cost: update
  framework-contributor-guidance: update
  framework-identity: update
  studio-distribution: create
  user-documentation: update
  vet: update
Totals: + 10, ~ 1, - 0, → 0
Change 'join-studio' archived as '2026-10-12-join-studio'.
```

(`<scratch>/15.2-archive.out`; its task count, 58 of 63 at that moment,
counted 14.10 and group 15 before this section ticked them.) The created
spec `studio-distribution`'s Purpose written in place of the CLI's
placeholder.

```
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 50 passed, 0 failed (50 items)
```

(`<scratch>/15.2-validate.out`.)

### 15.3 The plan's progress (task 15.3)

`workflow/ongoing/joins-0.9.md`, Progress, entry "6. `join-studio`." after
the movie's, written as entries 3 to 5 are: the branch, the planning and
merge commits, ADR-193, the package and its command, the skills and the
corrections, the npm workspace, the specs, the lock's 200 packages, the
suite's count, the studio's tests, the manual, `check-dist` with the clean
copy's counts, the originating check, and that no universe sweep runs: no
project repository reaches the studio (14.6) and the core's one change a
model could reach is the vet's denial.

### The record-reading tests at the close

After the orchestrator's run ended (its log: the core 4916 passed, 9
skipped; the studio 485 passed, 24 skipped; `make docs` and `make check`
exit 0):

```
$ ... pytest -q tests/test_repository_layout.py tests/test_release_records.py tests/test_docs_structure.py \
    tests/test_expression_type_cost.py tests/test_node_root_exports_nothing.py        (the core's)
128 passed, 3149 subtests passed in 17.05s                         (<scratch>/15-close-core.out)
$ ... pytest -q tests/test_documentation.py tests/test_machinome_identity.py tests/test_packaging.py   (the studio's)
31 passed, 232 subtests passed in 2.51s                            (<scratch>/15-close-studio.out)
```

### 15.4 This file (task 15.4)

Complete. The implementation commit and the integration are the
orchestrator's, never amending the planning commit e08b5539 or the merge
commit d291bc8b; nothing pushed.
