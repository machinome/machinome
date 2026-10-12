# Evidence: `join-viewer`

The third cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` at the repository root, cycle 3). Worktree
`machinome/WTs/v0.9-joins-join-viewer`, branch `v0.9-joins-join-viewer`, cut
from the line `v0.9-joins` at 484a528f. Planning commit 912fb7b4, ratified by
the orchestrator on 12 October 2026, the import address `machinome.viewer.web`
decided by the pilot on the same day; join merge commit 7ed45449, made by the
orchestrator. Applied on 12 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), Node 24.11.1 and npm
11.6.2, the OpenSpec CLI 1.6.0, OpenSCAD 2021.01 at `/usr/bin/openscad`. Every
command ran with `env -C <dir>` and absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-join-viewer` and
`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C3-apply/`.
The core's tests ran from `<bench>/packages/machinome` on the bench venv
(`<bench>/.venv/bin/python -m pytest -q -p no:cacheprovider ...`); the
viewer's from `<bench>/packages/machinome-viewer`; one pytest process at a
time. Logs are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -3
7ed45449 Join machinome-viewer: its whole history at its final paths
912fb7b4 Propose join-viewer: machinome-viewer joins as the distribution machinome-viewer, imported as machinome.viewer.web
484a528f Implement join-mechanics: the mechanics helpers as the distribution machinome-mechanics, imported as machinome.mechanics
$ git -C <bench> status --short | wc -l
0
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
```

`git status --short --ignored` showed `!! .env`, `!! .venv/` and the thirteen
packages' build leavings (`__pycache__/`, `*.egg-info/`).

### 1.2 The bench venv and the base's counts (task 1.2)

The orchestrator synced the venv from the lock before the join. Thirteen
`__editable__` files: `__editable__.machinome-0.8.1.pth`,
`__editable__.machinome_mechanics-0.1.0.pth` and those of
`machinome_engine_brep`, `machinome_engine_mesh`, `machinome_node_build123d`,
`machinome_node_cadquery`, `machinome_node_freecad`, `machinome_node_jscad`,
`machinome_node_molejo`, `machinome_node_openscad`, `machinome_node_solid2`,
`machinome_node_step` and `machinome_node_stl`, all 0.8.1. No
`machinome-viewer` and no `playwright` in its `site-packages`.

The base's counts, named by the orchestrator for 484a528f and not rerun: the
suite 4838 passed, 24 skipped (sixteen of the skips the viewer's); the lint;
the sweep of `join-mechanics` (63 repositories, 130 rows, 122 ok, 0 expected,
2 unexpected, 0 timeout, 6 no-model); the clean copy's framework sdist and
wheel as `join-mechanics` recorded them.

### 1.3 The probes this cycle relies on (task 1.3, by reference)

design.md, Probes: probe 1 (893 files, 285 commits, `main` 1b41968, the four
`viewer-` tags); probe 3 (the reds of the join); probe 4 (vitest 1715 passed
at the original, 121 failed at the new place before the paths move); probes 5
and 6 (the npm workspace and the currency red); probe 7 (192 packages);
probe 8 (Chromium 1243 absent at the time); probes 10 to 13 (the import's
cost, the archives, the two wheels installed together, the folded manual);
probe 15 (no bump table for the lock); probes 19 to 21 (the address, the
seam's future file, the vet's reading).

## 2. The join

### 2.1 and 2.2 The import and the merge (the orchestrator's, as measured)

- A fresh clone of `file:///home/asa/devel/machinome/machinome-viewer`
  rewritten with `scratchpad/C3-revise/filter-repo-command.web.sh` (its log
  `scratchpad/C3-join/filter-repo.log`: "Parsed 291 commits", "HEAD is now
  at 1b41968"); `main` at 1b41968, 285 commits; `git ls-tree -r --name-only
  main` listed the 893 paths of
  `scratchpad/C3-revise/rehearsal-ls-files.web.txt` exactly (diff empty; the
  list is `scratchpad/C3-join/ls-files.txt`); no path outside `packages/`
  (0); the tags `viewer-v0.7.0`, `viewer-v0.7.1`, `viewer-v0.8.0`,
  `viewer-v0.8.1`.
- `main` and the four tags fetched into the bench; the merge commit 7ed45449
  (parents 912fb7b4 and 1b419680), `git merge --allow-unrelated-histories
  --no-ff` of that branch onto 912fb7b4, no conflict, 893 files, 283596
  insertions; `git status --porcelain` empty afterwards.

The applier re-read the facts on the bench:

```
$ git -C <bench> ls-tree -r --name-only 912fb7b4 | wc -l
3692
$ git -C <bench> ls-tree -r --name-only 7ed45449 | wc -l
4585
$ git -C <bench> diff --shortstat 912fb7b4 7ed45449
 893 files changed, 283596 insertions(+)
$ git -C <bench> rev-list --count HEAD
1272
$ git -C <bench> tag -l 'viewer-*'
viewer-v0.7.0
viewer-v0.7.1
viewer-v0.8.0
viewer-v0.8.1
$ git -C <bench> log --format='%h %ad %s' --date=short -- \
    packages/machinome-viewer/machinome/viewer/web/server.py | wc -l
42
$ git -C <bench> log --format='%h %ad %s' --date=short -- \
    packages/machinome-viewer/machinome/viewer/web/server.py | tail -1
88f844be 2023-07-18 Web viewer - base web server, untested
$ git -C <bench> log --format='%h %ad %s' --date=short -- \
    packages/machinome-viewer/machinome/viewer/web/widget/src/evaluator.ts | wc -l
10
$ git -C <bench> log --format='%h %ad %s' --date=short -- \
    packages/machinome-viewer/machinome/viewer/web/widget/src/evaluator.ts | tail -1
95bdcf05 2026-07-16 Add embeddable viewer widget to 'solid export' (viewers/widget)
```

The tree grew by 893 files, 3692 to 4585. `server.py` reads back to the
framework commit of 18 July 2023 without `--follow`, and `evaluator.ts` to
the commit of 16 July 2026 that added the widget.

### 2.3 The gates red on the joined tree (task 2.3)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_repository_layout.py \
    tests/test_release_records.py tests/test_core_names_no_scad.py \
    tests/test_core_names_no_split_words.py tests/test_core_kernel_free.py \
    tests/test_node_root_exports_nothing.py
7 failed, 98 passed, 554 subtests passed in 15.34s
```

(`<scratch>/gates-at-join.txt`.) The reds, each the join's, as probe 3
expected:

- `TheWorkspaceTest::test_every_member_is_a_workspace_source`: the root's
  sources lack `'machinome-viewer': {'workspace': True}`.
- `TheRootIsTheRepositorysTest::test_the_readme_links_every_package_and_states_the_licence`
  (`package='machinome-viewer'`): "'packages/machinome-viewer/' not found"
  among the root README's links.
- `TheExtensionPackagesTest::test_every_sibling_is_in_the_table`
  (`package='machinome-viewer'`): "packages/machinome-viewer is in neither
  EXTENSIONS nor PRODUCTS".
- `TheExtensionPackagesTest::test_the_guide_installs_every_member_without_uv`
  (`package='machinome-viewer'`): "CONTRIBUTING.rst does not name -e
  packages/machinome-viewer".
- `VersionFilesTest::test_every_pin_between_members_is_compatible`, two
  subtests: `'>=0.8.1' != '~=0.8.1'` for `machinome-viewer>=0.8.1` and
  `machinome-viewer[snapshot]>=0.8.1`, the core's two floors.
- `VersionFilesTest::test_the_version_is_bumped_from_the_root`
  (`member='machinome-viewer'`): "'packages/machinome-viewer/pyproject.toml'
  not found" among `.bumpversion.cfg`'s tables.

The four name gates (`test_core_names_no_scad.py`,
`test_core_names_no_split_words.py`, `test_core_kernel_free.py`,
`test_node_root_exports_nothing.py`) green with the viewer's modules at
`machinome/viewer/web/`. Nothing else red.

## 3. Red first, on the joined tree

Nothing of the package changed in this group; the tests changed, and each
was run against the joined tree.

### 3.1 The layout gate (`tests/test_repository_layout.py`)

The `PRODUCTS` row at `machinome.viewer.web` with its twelve entries; the
package-directory test refusing an `__init__.py` at every level above the
package (`machinome/`, then `machinome/viewer/`); the tests-and-specs test
reading a `tests/` holding a `test_*.py` module; the new class
`TheNodeWorkspaceTest` (four tests: the private root `package.json` with no
`version` and the widget's directory as its one workspace, one tracked
`package-lock.json`, at the root, whose member entry is `@machinome/viewer`,
`/node_modules/` in the root `.gitignore`, no tracked `node_modules/` or
`widget/dist/`); `package.json` and `package-lock.json` among the root's
files; `test_the_test_job_builds_and_tests_the_widget_before_the_suite` and
`test_the_dist_job_sets_up_node_before_checking`; the module docstring.

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_repository_layout.py
15 failed, 36 passed, 201 subtests passed in 4.19s
```

(`<scratch>/red-3.1.txt`.) Each red and its reason:

- `test_every_member_is_a_workspace_source`: the root's sources lack the
  viewer (as in 2.3).
- `test_the_readme_links_every_package_and_states_the_licence`
  (`machinome-viewer`): the root README does not link
  `packages/machinome-viewer/` (as in 2.3).
- `test_the_guide_installs_every_member_without_uv` (`machinome-viewer`):
  "CONTRIBUTING.rst does not name -e packages/machinome-viewer" (as in 2.3).
- `test_the_repository_s_files_are_there`, two subtests: the root's
  `package.json` and `package-lock.json` are missing.
- `test_the_test_job_builds_and_tests_the_widget_before_the_suite` and
  `test_the_dist_job_sets_up_node_before_checking`: "the job has no step that
  sets up Node".
- `test_the_test_job_runs_each_product_s_tests` (`machinome-viewer`): "the
  test job runs no pytest from packages/machinome-viewer".
- `test_each_product_directory_holds_its_package_and_its_record`
  (`machinome-viewer`): the entries lack `LICENSE` and `LICENSES`.
- `test_each_product_manifest_states_the_set_s_licence`
  (`machinome-viewer`): the manifest's `license` is the expression the
  product carried, not `GPL-2.0-or-later OR CERN-OHL-S-2.0+` (the first
  assertion; `license-files`, `include` and `namespaces` differ too).
- `test_each_product_readme_names_its_install_and_the_licence`
  (`machinome-viewer`): the README carries the install line
  `pip install "machinome[viewer]"` but not the words
  "GPL-2.0-or-later or CERN-OHL-S-2.0-or-later".
- `test_each_product_resolves_from_its_directory` (`machinome-viewer`):
  `ModuleNotFoundError: No module named 'machinome.viewer'`; no installed
  package provides it on the bench venv.
- `TheNodeWorkspaceTest`: three of its four tests red, the root
  `package.json` missing (`FileNotFoundError`), the one tracked lock at
  `packages/machinome-viewer/machinome/viewer/web/widget/package-lock.json`
  rather than the root, and `/node_modules/` absent from the root
  `.gitignore`; `test_no_install_or_bundle_is_tracked` green.

The product-directory test does not reach its `__init__.py` levels while the
entries differ; it passed them once the links existed (group 4).

### 3.2 The release records (`tests/test_release_records.py`)

`test_the_viewer_extras_floor_at_the_matching_viewer` replaced by
`test_the_viewer_extras_pin_the_set_s_viewer` (each extra's name, its bracket
and `~=` the manual's `viewer_version`); the new
`test_the_viewer_s_version_files_agree` (`__init__.py`, the widget's
`package.json`, the root lock's member entry; `.bumpversion.cfg` naming the
first two); the docstring.

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_release_records.py
8 failed, 15 passed, 142 subtests passed in 0.39s
```

(`<scratch>/red-3.2.txt`.) The reds: the two subtests of
`test_every_pin_between_members_is_compatible` and of
`test_the_viewer_extras_pin_the_set_s_viewer`, `'>=0.8.1' != '~=0.8.1'`, the
core's two floors; `test_the_version_is_bumped_from_the_root` (as in 2.3);
`test_the_viewer_s_version_files_agree`, three subtests: the root
`package-lock.json` is missing, and neither
`packages/machinome-viewer/machinome/viewer/web/__init__.py` nor
`.../widget/package.json` is a table of `.bumpversion.cfg`. Its
`__init__.py` and `package.json` subtests green: both already state 0.8.1.

### 3.3 The manual's structure (`tests/test_docs_structure.py`)

The new `test_the_browser_viewer_is_three_how_tos_and_a_reference_section`
(the How-to toctree naming `howto/browser-viewer`, `howto/share-an-export`,
`howto/embed-the-viewer`, the Reference toctree `reference/viewer/index`, the
section's toctree the eight pages in order); `KernelExtrasTest.STALE` gains
`machinome-viewer.readthedocs` and `github.com/machinome/machinome-viewer`;
`LicenceFactTest` admits no identifier on any page and only
`framework_licence`'s in the README; the constant naming the product's
licence, the stale-grant constant and `LicenceWordingTest` removed; the
distributions test gains `machinome-viewer`; the new
`test_the_viewer_facts_are_the_widget_s` (`viewer_api` and
`document_versions` equal the widget's `package.json`).

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_docs_structure.py
22 failed, 19 passed, 1450 subtests passed in 0.86s
```

(`<scratch>/red-3.3.txt`.) The reds:

- the new navigation test: four subtests, none of the four entries in its
  toctree, and the section's toctree (the six pages of the product's
  reference index);
- `test_no_reader_page_carries_the_kernels_or_the_old_addresses`, eight
  subtests: `machinome-viewer.readthedocs` on `concepts/publishing.rst`,
  `reference/manuals.rst` and `tutorial/10-share.rst`;
  `github.com/machinome/machinome-viewer` on `howto/share-an-export.rst`,
  `project/contributing.rst`, `reference/cli.rst`, `start/install.rst` and
  `README.rst`;
- `test_no_page_spells_a_licence`, eight subtests: the product's licence
  identifier on `concepts/publishing.rst`, `howto/share-an-export.rst`,
  `project/changelog.rst`, `project/status.rst`, `project/upgrading.rst`,
  `reference/manuals.rst`, `start/install.rst` and `why.rst`;
- `test_the_readme_states_the_framework_licence_of_conf`: the README spells
  the product's identifier beside the framework's words.

Green against the expectation of task 3.3: the installation page already
names `machinome-viewer` (its link to the product's repository), so the
distributions test passed at the join; and `conf.py` already states viewer
API 29 and "1 to 13", the widget's declaration.

### 3.4 The links into the manual (`tests/test_viewer_documentation_links.py`)

Rewritten: six cases, `reference/manuals.rst` linking
`/reference/viewer/index`, `concepts/publishing.rst` linking
`/howto/browser-viewer`, `/reference/viewer/index` and
`/howto/embed-the-viewer`, `tutorial/10-share.rst` linking
`/howto/embed-the-viewer` and `start/install.rst` linking
`/howto/browser-viewer`, each as a `:doc:` target; and no page of the manual
nor `README.rst` linking `machinome-viewer.readthedocs.io`.

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_viewer_documentation_links.py
7 failed in 0.18s
```

Every case red: no page links a target inside the manual, and three pages
(`concepts/publishing.rst`, `reference/manuals.rst`,
`tutorial/10-share.rst`) link the separate manual. The installation page's
target is the operating guide: Decision 10 names none for it, and the
operating guide is the page a reader goes to once installed.

### 3.5 The parity fixture's default (`tests/test_generate_parity_fixture.py`)

`DefaultFixturePathTest` rewritten on a temporary repository holding
`packages/machinome/` and the viewer's
`packages/machinome-viewer/machinome/viewer/web/widget/src/`: the default
resolves there from `packages/machinome/`; no Git command runs; the refusal
names the directory and the argument; the refusal comes before a build; an
explicit path is written. The worktree and Git-common-directory cases went
with the behaviour they tested.

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_generate_parity_fixture.py -k DefaultFixturePath
3 failed, 2 passed, 5 deselected in 3.64s
```

The reds: the default and the refusal both exit "<root>/packages/machinome is
not a Git checkout, so no machinome-viewer checkout can be found beside it"
(the tool asks Git for the sibling of the primary checkout), and
`test_no_git_command_is_run` fails on the `git rev-parse` it runs. The
refusal-before-build and explicit-path cases pass at the join.

### 3.6 The core's tests that spell the viewer's module

`tests/test_viewer_bundle.py` (the expected command), `test_browser_renderer.py`
and `test_manager_develop.py` (`VIEWER`), `test_cli_lazy_imports.py`
(`machinome.viewer.web.server`, `machinome.viewer.web.capture`).

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q -rs \
    -p no:cacheprovider tests/test_viewer_bundle.py tests/test_browser_renderer.py \
    tests/test_manager_develop.py tests/test_cli_lazy_imports.py
5 failed, 59 passed, 15 skipped, 23 subtests passed in 8.83s
```

(`<scratch>/red-3.6.txt`.) The reds, each `'machinome_viewer' !=
'machinome.viewer.web'` in the command the framework builds:
`LookupTest.test_the_viewer_runs_through_this_interpreter`
(`test_viewer_bundle.py`), one mocked capture command in
`test_browser_renderer.py` (line 240), and three `Popen` expectations of
`test_manager_develop.py` (`DefaultViewerTest.test_the_web_viewer_is_the_default_when_installed`,
`ExplicitViewerTest.test_explicit_web_uses_the_same_browser_viewer`,
`ExplicitViewerTest.test_web_dev_asks_the_viewer_to_start_its_frontend`).
The task expected `test_viewer_bundle.py`'s alone: the four others mock the
lookup and run without an installed viewer. The 15 skips: fourteen of
`test_browser_renderer.py` and one of `test_cli_lazy_imports.py`,
"machinome-viewer not installed".

### 3.7 The vet universe (`tests/test_vet_universe.py`)

`test_the_contract`'s denylist gains `machinome.viewer.web`; the new
`test_the_browser_viewer_is_internal_and_its_former_name_outside` vets two
scratch projects.

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_vet_universe.py
2 failed, 14 passed, 7 subtests passed in 0.22s
```

The reds: the denylist tuple lacks `'machinome.viewer.web'`; the project
importing `machinome.viewer.web.server` gives no finding (design.md probe
21), where `('sim/model.py', 'framework-internal', 'machinome.viewer.web')`
is expected. The second project's `outside-universe`,
`machinome_viewer.server` already holds.

### 3.8 The viewer's pinning tests

Rewritten as Decision 11 says: `tests/test_licence.py` (the grant read from
the core's manifest; both manifests and the widget's `package.json`; the
links `LICENSE` and `LICENSES`; every SPDX line of the package's tracked
files outside `openspec/changes/archive/`, `workflow/archive/`,
`workflow/adrs/` and `workflow/evidence/`; the banner template and a built
bundle with the expression and `Source: https://github.com/machinome/machinome`;
the README with the manual's words); `test_machinome_identity.py` (the
console script, the entry point, the package search, `machinome/viewer/web/`
with no `__init__.py` above it and no former directory, `machinome~=` its
own version, the Homepage alone); `test_documentation.py` (the twelve pages
under `packages/machinome/docs/`, no `docs/` or `.readthedocs.yaml` in the
package, the changelog's release section, `conf.py`'s facts equal to the
widget's, no documentation URL but the Homepage, no page linking the separate
manual, the CLI reference and the `describe` example at
`reference/viewer/cli.rst`, the full-screen, profile-contact, film-annotation
and on-demand facts at the pages' new paths); `test_version.py` (the
package imported as `machinome.viewer.web`); and the new
`test_packaging_refuses_a_shared_workspace_root` (`test_packaging.py`) and
`test_a_stale_bundle_with_hoisted_dependencies_is_rebuilt`
(`test_currency.py`), whose modules import the package at its address.

With `PYTHONPATH=<bench>/packages/machinome-viewer` alone the run stops at
collection: `machinome.viewer.web` resolves to
`<bench>/packages/machinome-viewer/machinome/viewer/web/__init__.py`
(`machinome` the core's `__init__.py`, `machinome.viewer` a namespace whose
one path entry is `packages/machinome-viewer/machinome/viewer`), but its
`bundle.py` imports `machinome_viewer.currency`, which nothing provides
(`ModuleNotFoundError: No module named 'machinome_viewer'`, collecting
`tests/test_version.py`; `<scratch>/red-3.8-plain.txt`). The package's own
imports move in 4.4, so for the behavioural reds the run added a scratch
link `<scratch>/shim/machinome_viewer -> <bench>/packages/machinome-viewer/machinome/viewer/web`
to the path:

```
$ env -C <bench>/packages/machinome-viewer \
    PYTHONPATH=<bench>/packages/machinome-viewer:<scratch>/shim \
    <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider \
    tests/test_licence.py tests/test_machinome_identity.py \
    tests/test_documentation.py tests/test_version.py tests/test_packaging.py \
    tests/test_currency.py
175 failed, 39 passed, 1 skipped, 8 subtests passed in 10.90s
```

(`<scratch>/red-3.8.txt`.) The reds and their reasons:

- `test_licence.py`: `test_every_header_states_the_grant`, 156 subtests,
  one per SPDX line of the 155 files (`build.mjs` twice), each stating the
  product's former expression; `test_the_manifests_agree` (the manifest's
  `license`); `test_the_licence_texts_are_the_repository_s`, two subtests
  ("LICENSE is not a link", `LICENSES` absent);
  `test_the_banner_template_states_the_grant_and_the_source` (the banner's
  SPDX line); `test_the_readme_states_the_licence` (the words absent). The
  built-bundle test skipped: no bundle.
- `test_machinome_identity.py`: the console script and entry point at
  `machinome_viewer`; `machinome~=` absent from the dependencies ("not enough
  values to unpack"); the URLs name the product's repository and
  documentation.
- `test_documentation.py`: the manifest's URLs; three framework pages link
  the separate manual; `MANIFEST.in` names `.readthedocs.yaml`; the
  `describe` example's paths are `/installation/machinome_viewer/widget/...`;
  `compatibility.rst` does not read "This release declares:" (the film and
  on-demand tests). Green: the pages exist at their paths, and
  `test_the_release_facts_are_the_widget_s` (`conf.py` already states the
  widget's API and versions).
- `test_packaging.py`: `test_packaging_refuses_a_shared_workspace_root`,
  "RuntimeError not raised": the guard reads the widget's `node_modules`
  only. Four more failures of that module
  (`test_source_distribution_builds_the_one_frontend`,
  `test_the_wheel_hook_builds_what_is_missing_or_stale`,
  `test_wheel_builds_the_widget_when_its_output_is_missing` and `..._stale`)
  are the mixed names of this run, not reds of the cycle: they patch
  `machinome_viewer.packaging.*` (moved in 7.1) while the module under test
  is `machinome.viewer.web.packaging`.
- `test_currency.py`: `test_a_stale_bundle_with_hoisted_dependencies_is_rebuilt`,
  `BundleStale: ... was not rebuilt: the widget's dependencies are not
  installed, and a rebuild never installs them`.
- `test_version.py`: green (both declarations and the changelog state
  0.8.1).

## 4. The package

### 4.1 The links

```
$ env -C <bench>/packages/machinome-viewer ln -s ../../LICENSE LICENSE
$ env -C <bench>/packages/machinome-viewer ln -s ../../LICENSES LICENSES
$ git -C <bench> ls-files -s packages/machinome-viewer | grep ^120000
120000 30cff740... 0	packages/machinome-viewer/LICENSE
120000 06ad40db... 0	packages/machinome-viewer/LICENSES
```

Both added with `git add`; their targets `../../LICENSE` and `../../LICENSES`.

### 4.2 The package's files

`pyproject.toml`, `README.md`, `MANIFEST.in` and `.gitignore` written as
design.md Decision 3 gives them, verbatim, in place of the product's.

### 4.3 The headers, the widget's licence and the banner

The 155 files carrying `SPDX-License-Identifier:` outside
`openspec/changes/archive/` (`git grep -l` listed 155) each had their line
rewritten to the set's expression by one `sed` substitution; `git diff
--numstat` of those files shows `1 1` for 149 of them and `2 2` for
`build.mjs` (its file header and its banner template); the six test modules
of group 3 show their rewrites. Then the widget's `package.json` `license`,
the banner's `Source:` line (`https://github.com/machinome/machinome`) and
the comment above the banner (it names the bundle's licence, the licence of
every package of the repository, its source, and the retained notices).

```
$ git -C <bench> grep -n 'SPDX-License-Identifier' -- packages/machinome-viewer \
    ':!packages/machinome-viewer/openspec/changes/archive' \
    | grep -v 'GPL-2.0-or-later OR CERN-OHL-S-2.0+'
packages/machinome-viewer/tests/test_licence.py:43:SPDX = re.compile(...)
packages/machinome-viewer/tests/test_licence.py:102:        self.assertIn(f'SPDX-License-Identifier: {GRANT}', build)
packages/machinome-viewer/tests/test_licence.py:115:        self.assertIn(f'SPDX-License-Identifier: {GRANT}', head)
```

Every other line states the set's expression; the three left are the test's
pattern.

### 4.4 The source at its address

`machinome_viewer` became `machinome.viewer.web` in the imports of
`__main__.py`, `bundle.py` (two), `capture.py` (two), `cli.py` (three),
`server.py` (two); `packaging.py`'s `_currency_name`, its `ImportError`
message and its comment citing `MANIFEST.in`
(`machinome/viewer/web/widget`); `__main__.py`'s docstring (`python -m
machinome.viewer.web`); `cli.py`'s comment path
(`packages/machinome/machinome/manager/develop.py`). The docstrings naming
the `machinome.viewer` entry point keep the group's name. `git diff` of the
eight modules shows those lines, the headers and 4.5's two functions, and no
other line (49 insertions, 29 deletions). `grep -rn machinome_viewer` over
the eight modules: nothing.

### 4.5 The dependency lookup and the guard

`currency.py`: `_require_dependencies` asks the new `_build_program_installed`,
which walks from the widget directory up to the filesystem root for
`node_modules/esbuild`, a directory, never reading `node_modules`' contents;
the refusal and its remedy are unchanged. `packaging.py`: `build_frontend`
refuses before `npm ci` when a `node_modules` from the widget up to the
filesystem root is a symbolic link, naming it. Run with the patch targets of
the two modules renamed (`machinome_viewer.packaging.*` and the `froms` set
of `test_deciding_currency_imports_only_the_standard_library`, the 7.1 lines
of those two modules, done here so the modules run whole):

```
$ env -C <bench>/packages/machinome-viewer PYTHONPATH=<bench>/packages/machinome-viewer \
    <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider \
    tests/test_currency.py tests/test_packaging.py
29 passed, 4 subtests passed in 1.13s
```

`test_packaging_refuses_a_shared_workspace_root` and
`test_a_stale_bundle_with_hoisted_dependencies_is_rebuilt` green with them.

A side effect of 3.8's run, found here: the four mixed-name failures of
`test_packaging.py` patched `machinome_viewer.packaging.build_frontend` while
calling `machinome.viewer.web.packaging`, so the real `build_frontend` ran on
the bench's widget: an `npm ci` and `npm run build` inside
`packages/machinome-viewer/machinome/viewer/web/widget/` at 11:39 (before
the root's `package.json` existed), which wrote `widget/node_modules/` from
the widget's own lock and `widget/dist/`. Both are ignored, nothing tracked
changed. The 4.5 run's `ThisInstallationTest` then rebuilt the stale bundle
through the currency check (`dist/.build.lock`). The `widget/node_modules/`
left behind was removed after 5.2 (below); the bundle was rebuilt in 5.3.

### 4.6 The widget's fixture paths

`'../../../tests/fixtures` became `'../../../../../tests/fixtures` in the
nine files under `src/`, and `'../../../../tests/fixtures` became
`'../../../../../../tests/fixtures` in the six under `src/run/`, by `sed` on
the quoted prefix: 26 lines in 14 files (`document`, `expressions` (3),
`navtree`, `partControls`, `selectedControls`, `tree` (4); `run/acceptance`,
`run/cost` (4), `run/program` (5), `run/run`, `run/source-timing-curta`,
`run/source-timing-version`, `run/source-timing`, `run/time-drives`).
`documentation.test.ts`: its root `new URL('../../../../../../../',
import.meta.url)`, seven levels above `src/`, and its pages
`packages/machinome/docs/reference/viewer`. `git diff --numstat` of `src/`:
those lines and the headers, nothing else; the three labels
`'tests/fixtures/...'` of `run/program.test.ts` (data passed to
`loadProgram`, not paths) unchanged.

## 5. The npm workspace

### 5.1 The lockfile and the root's files

```
$ git -C <bench> mv packages/machinome-viewer/machinome/viewer/web/widget/package-lock.json package-lock.json
```

Its top-level `"version": "0.8.1"` (line 3) removed; the root `package.json`
of Decision 5 written and added; `/node_modules/` added to the root
`.gitignore` after `/.venv/`. After 5.2, `git status --short` shows
`RM packages/machinome-viewer/machinome/viewer/web/widget/package-lock.json
-> package-lock.json`: rename detected.

### 5.2 The install

```
$ env -C <bench> npm install --no-audit --no-fund
added 101 packages, and removed 100 packages in 3s
$ env -C <bench> npm install --package-lock-only
up to date, audited 103 packages in 801ms
$ env -C <bench> npm ci --no-audit --no-fund
added 101 packages in 3s
```

"added 101 packages" as probe 5 found. The "removed 100 packages" are the
widget's own `node_modules/` that 3.8's side effect (4.5) had installed:
npm emptied it into the root's, leaving empty scope directories and its
`.package-lock.json`, which were removed (`rm -rf` of
`widget/node_modules`, created by this cycle), before the `npm ci` that
proved the root lock installs alone. The comparison of the lock's
`node_modules/*` entries against the widget's former lock (a copy taken
before the edit, `<scratch>/widget-lock-before.json`): 174 entries each
side, besides the new link `node_modules/@machinome/viewer`, 0 differences.
The lock's keys: `""` (`machinome-repository`, its `workspaces`), the
member's `packages/machinome-viewer/machinome/viewer/web/widget` (`version`
0.8.1, `license` `GPL-2.0-or-later OR CERN-OHL-S-2.0+`) and `node_modules/*`;
`node_modules/@machinome/viewer` is `{"resolved":
"packages/machinome-viewer/machinome/viewer/web/widget", "link": true}`.
Its top level holds `name`, `lockfileVersion` and `requires`, no `version`.
The root's `node_modules/` holds 79 entries, the member linked as
`node_modules/@machinome/viewer -> ../../packages/machinome-viewer/machinome/viewer/web/widget`;
the widget holds no `node_modules/`.

### 5.3 Typecheck, tests and build from the root

```
$ env -C <bench> npm run typecheck --workspaces --if-present
> tsc --noEmit                                         (exit 0)
$ env -C <bench> npm test --workspaces --if-present
 Test Files  65 passed | 1 skipped (66)
      Tests  1715 passed | 2 skipped (1717)            (exit 0)
$ env -C <bench> npm run build --workspaces --if-present
  dist/machinome-viewer.js  895.9kb                    (exit 0)
```

(`<scratch>/npm-typecheck.txt`, `npm-test.txt`, `npm-build.txt`.) The
skipped file is `src/run/profile-installed-benchmark.test.ts`, the skipped
tests its one and one of `src/run/profile-contact.test.ts`, as at the
original. The bundle's first lines: `machinome-viewer 0.8.1 - viewer API 29`,
`SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+`, `Source:
https://github.com/machinome/machinome`, the three `Bundles` notices.
`git status --short` lists no `node_modules/` or `dist/`.

## 6. The core, the uv workspace and the sync

### 6.1 The command, the extras and the vet denial

`machinome/viewers/bundle.py`: `viewer_command()` returns `[sys.executable,
'-m', 'machinome.viewer.web']`; the docstring names the repository's package
`machinome.viewer.web` and drops "separately licensed"; `INSTALL_REMEDY`
reads "It is the package machinome-viewer; install it with: pip install
"machinome[viewer]"". `pyproject.toml`: the `viewer` and `web-snapshot`
extras `machinome-viewer~=0.8.1` and `machinome-viewer[snapshot]~=0.8.1`
under Decision 6's comment; the `dev` extra gains `"machinome[web-snapshot]"`
after `"machinome[all]"`. `machinome/vet/universe.toml`: `"machinome.viewer.web"`
after the engine's file operations, with its comment. `git diff` of the three
files shows those hunks alone.

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_vet_universe.py
16 passed, 7 subtests passed in 0.15s
```

### 6.2 The root manifest, the lock and the sync

The root's sources gain `machinome-viewer = { workspace = true }` after
`machinome-node-stl`; `exclude-dependencies = ["machinome-studio"]`, its
comment naming the studio alone.

```
$ env -C <bench> /home/asa/.local/bin/uv lock
Resolved 192 packages in 831ms
Added greenlet v3.5.6
Added machinome-viewer v0.8.1
Added playwright v1.63.0
Added pyee v13.0.1
$ git -C <bench> diff --stat -- uv.lock
 uv.lock | 150 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++---
 1 file changed, 145 insertions(+), 5 deletions(-)
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
 + greenlet==3.5.6
 ~ machinome==0.8.1 (from file://<bench>/packages/machinome)
 + machinome-viewer==0.8.1 (from file://<bench>/packages/machinome-viewer)
 + playwright==1.63.0
 + pyee==13.0.1
```

(`<scratch>/uv-lock.txt`, `uv-lock.diff`, `uv-sync.txt`.) Fourteen
`__editable__` `.pth` files, the new one
`__editable__.machinome_viewer-0.8.1.pth` holding
`<bench>/packages/machinome-viewer`. From `/tmp` on the bench venv
(`<scratch>/probe-resolve.txt`): `machinome.viewer.web.__file__` is
`<bench>/packages/machinome-viewer/machinome/viewer/web/__init__.py`,
`__version__` 0.8.1; `machinome.viewer.__path__` is the one entry
`<bench>/packages/machinome-viewer/machinome/viewer`;
`entry_points(group='machinome.viewer')` gives `[('bundle',
'machinome.viewer.web.bundle:describe')]`; `find_spec('machinome_viewer')` is
`None` and `import machinome_viewer` raises `ModuleNotFoundError`; `httpx`
0.27.2 is installed (the viewer's server tests need it, through the lock).
`python -m machinome.viewer.web describe` exits 0 with the bench's bundle,
`apiVersion` 29, `documentVersions` 1 to 13, `version` 0.8.1
(`<scratch>/describe.txt`).

Chromium: the orchestrator fetched revision 1243 for the locked Playwright
1.63.0 into the shared cache before this step
(`scratchpad/C3-join/playwright-install.log`: "Chrome Headless Shell
153.0.8010.12 (playwright chromium-headless-shell v1243) downloaded";
`~/.cache/ms-playwright` holds `chromium-1243` and
`chromium_headless_shell-1243`). The applier ran no `playwright install`.

### 6.3 The parity fixture's default

`tools/generate_parity_fixture.py`: `VIEWER_FIXTURE` is the path from the
framework's directory, `../machinome-viewer/machinome/viewer/web/widget/src/parity-fixture.json`;
`default_fixture` resolves it without Git and refuses, naming the directory
and the argument, when it is absent; `import subprocess` and the Git lookup
are gone; the docstring follows.

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_generate_parity_fixture.py
10 passed, 2 warnings in 5.37s
```

The default from the bench names
`<bench>/packages/machinome-viewer/machinome/viewer/web/widget/src/parity-fixture.json`.
Out of scope, found while applying: the tool run into the scratch directory
writes a fixture that differs from the committed one (`cmp` at line 49; 1070
differing lines in `diff`, the bindings table among them). The committed
fixture is the product's as at bd2bf75 and the widget's parity test passes
against it; whether it should be regenerated is not this change's.

### 6.4 The gates after the sync

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH \
    <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider \
    tests/test_repository_layout.py tests/test_release_records.py \
    tests/test_vet_universe.py tests/test_viewer_bundle.py \
    tests/test_browser_renderer.py tests/test_manager_develop.py \
    tests/test_cli_lazy_imports.py
8 failed, 149 passed, 1 skipped, 400 subtests passed in 11.80s
```

(`<scratch>/run-6.4.txt`.) The eight, as the task expects, are groups 9 and
10's: the two CI tests ("the job has no step that sets up Node"), the
viewer's pytest step, the root README's link, the guide's `-e
packages/machinome-viewer`, and the three bump tables
(`packages/machinome-viewer/pyproject.toml`, `.../web/__init__.py`,
`.../widget/package.json`). The skip is the end-to-end capture ("set
MACHINOME_WEB_SNAPSHOT_E2E=1"); the fifteen "machinome-viewer not installed"
skips of 3.6 run and pass.

## 7. The tests at their new place

### 7.1 The imports and paths

`machinome_viewer` became `machinome.viewer.web` in the viewer's test modules
and `support.py` (`from machinome.viewer.web... import`, the `patch()`
targets, `[sys.executable, '-m', 'machinome.viewer.web', 'describe']`,
`test_bundle.py`'s set of imports), and `test_profile_document.py`'s path
`Path(__file__).parents[1] / 'machinome' / 'viewer' / 'web' / 'widget' / ...`:
38 lines in 18 files by the script's count (`support.py` 1, `test_cli.py`
11, `test_capture.py` 5, `test_bundle.py` 4, `test_server.py` 3,
`test_profile_document.py` 2, twelve modules 1 each), besides the rewrites
of 3.8 and the patch targets moved in 4.5. `grep -n machinome_viewer` over
`tests/*.py` leaves `test_machinome_identity.py`'s refusal of the former
directory and `test_version.py`'s local alias.

### 7.2 The viewer's tests from its directory

```
$ env -C <bench>/packages/machinome-viewer <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
3 failed, 247 passed, 2 skipped, 57 warnings, 185 subtests passed in 280.32s
```

(`<scratch>/viewer-pytest-7.2.txt`.) The three failures are the
documentation tests that read pages group 8 writes
(`test_no_page_links_the_separate_manual`,
`test_describe_example_matches_package_versions`,
`test_film_annotations_are_documented_as_part_of_the_0_8_0_release`); the two
skips the Curta's ("the Curta's own builds are not at
<bench>/../projects/Calculators/Curta-Type-I-3x/_build"). Every browser test
passed with Chromium 1243.

```
$ env -C <bench>/packages/machinome-viewer \
    MACHINOME_CURTA_BUILDS=/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x/_build \
    <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
1 failed, 251 passed, 57 warnings, 185 subtests passed in 373.40s
```

(`<scratch>/viewer-pytest-7.2-curta.txt`.) The two Curta tests ran and
passed. This run overlapped the applier's group 8 edits of the pages, so
its one failure, `test_no_page_links_the_separate_manual` on
`concepts/publishing.rst`, read a page not yet edited; 11.2 reruns on the
final tree.

### 7.3 The core's suite collects none of them

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest \
    --collect-only -q -p no:cacheprovider | grep -c machinome-viewer
0
```

(4870 tests collected; `<scratch>/collect-7.3.txt`.)

## 8. The manual

### 8.1 Red first

A fresh venv `<scratch>/docs-venv-jv` (uv, Python 3.12) installing
`packages/machinome/docs/requirements.txt` alone: Sphinx 9.1.0,
sphinx-rtd-theme 3.1.0, machinome-viewer 0.8.0 (the published one).

```
$ env -C <bench>/packages/machinome <scratch>/docs-venv-jv/bin/python -m sphinx \
    -b html -n -W --keep-going docs <scratch>/jv-html-red
exit 1, 32 warnings
```

(`<scratch>/jv-sphinx-red.txt`.) The 32 of probe 13: six pages in no toctree
(`howto/browser-viewer`, `howto/embed-the-viewer`, `howto/share-an-export`,
`reference/viewer/compatibility`, `reference/viewer/index`,
`reference/viewer/troubleshooting`); 19 unknown documents (`troubleshooting`,
`sharing`, `reference/layouts` twice, `reference/running` twice,
`reference/clocked`, `reference/mount` twice, `embedding` twice,
`installation`, `reference/cli` twice, `../installation`, `../embedding`,
`../using-the-viewer`, `../compatibility`, `reference/layouts` of the
troubleshooting page); the two includes `howto/examples/embed.html` and
`embed.js` not found; five undefined substitutions (`package-version` twice,
`viewer-api` twice, `document-versions`).

### 8.2 to 8.5 The edits

- `docs/conf.py`: the autodoc path leaves `packages/machinome-viewer` out,
  with its comment; `viewer_version`'s comment; `html_js_files`,
  `html_css_files` and `setup(app)` connecting `copy_the_embedding_example`
  on `build-finished` (the example, the spinner export as `spinner/`, the
  installed bundle through `machinome.viewers.bundle.bundle_path()`).
- `docs/index.rst`: the three how-tos after `howto/mechanism-formulas`,
  `reference/viewer/index` after `reference/mechanics/index`.
- `docs/_exports/spinner/` copied from
  `packages/machinome-viewer/tests/fixtures/spinner/` (`diff -r` empty; three
  files added).
- `_static/viewer-demo.css` without the rule for every table cell.
- `reference/viewer/index.rst` rewritten in place ("Browser viewer"); the
  reference pages' substitutions and links; `cli.rst`'s title "The
  machinome-viewer command", its `python -m machinome.viewer.web` sentence
  and its `describe` paths; `compatibility.rst`'s "This release declares:"
  and "It loads no project Python code"; `troubleshooting.rst`'s `npm ci`
  and `npm run build --workspaces` from the root.
- The three how-tos: titles of Decision 10's table; the operating guide's
  opening (install, `machinome viewer`, `machinome develop`), "Try the
  viewer" with its button on `embed-the-viewer/embed.html`, its own sections
  after a heading "What the viewer shows"; the sharing guide's links and
  licence paragraph; the embedding guide's includes, demo and links.
- The framework's pages: `start/install.rst`, `concepts/publishing.rst`,
  `tutorial/10-share.rst`, `reference/cli.rst`, `reference/manuals.rst`,
  `project/status.rst`, `why.rst`, `project/upgrading.rst`,
  `project/contributing.rst`, the two released lines of
  `project/changelog.rst`.

### 8.6 The build, the browser and the pages' tests

```
$ env -C <bench>/packages/machinome <scratch>/docs-venv-jv/bin/python -m sphinx \
    -b html -n -W --keep-going docs <scratch>/jv-html
exit 0, no warning
```

`<scratch>/jv-html/howto/embed-the-viewer/` holds `embed.html`, `embed.js`,
`machinome-viewer.js` (the published 0.8.0's, its banner "machinome-viewer
0.8.0 - viewer API 29") and `spinner/`. Served and opened in Chromium
(`<scratch>/jv-look.py`, Playwright 1.63.0 of the bench venv): the embedding
guide's "Run this example" and the operating guide's "Load interactive
spinner" each load the frame, status "Drag to orbit · scroll to zoom · open
Assembly to inspect", no page error and no HTTP error; the photographs
`<scratch>/jv-shots/howto-embed-the-viewer.html.png` and
`howto-browser-viewer.html.png` show the red hub and the three blue blades
with the timeline and the Assembly tab, looked at; the section's index
(`reference-viewer-index.png`) reads "Browser viewer", its two paragraphs
with "viewer API 29 and reads document versions 1 to 13", and the eight
pages listed, under the Reference part of the navigation.

```
$ env -C <bench>/packages/machinome-viewer <bench>/.venv/bin/python \
    scripts/check-docs-browser.py <scratch>/jv-html
{"pages": 12, "viewports": [1440, 390], "local_links": 265,
 "mobile_menu": "passed", "search": "passed", "interactive_example": "passed",
 "reference_examples": {"pascaline": {"elapsed": 1, "outcomes": [{"handle": 0,
 "input": "units_entry", "status": "completed", "admitted": 1}]},
 "calculator": {"admitted": 360, "restored": true}}, "browser_errors": []}
```

(`<scratch>/check-docs-browser.txt`; screenshots under
`packages/machinome-viewer/_build/docs-review/`, ignored; the 390-pixel
operating guide looked at.) The script adapted as Decision 11 says: the
twelve pages (three how-tos and the section), the built HTML of the manual
or its first argument, the reference's scripts from
`packages/machinome/docs/reference/viewer/`, the fixtures from the package's
`tests/fixtures`, the example at `howto/embed-the-viewer/embed.html`, the
spinner button on the operating guide, the mobile menu's link to it.

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_docs_structure.py tests/test_docs_exports.py \
    tests/test_viewer_documentation_links.py tests/test_node_root_exports_nothing.py
2 failed, 67 passed, 1591 subtests passed
$ env -C <bench>/packages/machinome-viewer ... tests/test_documentation.py
13 passed
$ env -C <bench> npm test --workspaces --if-present -- src/documentation.test.ts
 Test Files  1 passed (1)
      Tests  111 passed (111)
```

The two failures were `README.rst`'s (the stale link and the identifier),
group 10.4's edit; after it, 10.4's run below is green.

## 9. The version records, `scripts/check-dist` and CI

### 9.1 The bump tables, proved on a copy

`.bumpversion.cfg` gains the five tables of Decision 7 after the FreeCAD
package's: the viewer manifest's `version` and `pin`, its `__init__.py`, its
widget's `package.json` and `docs/conf.py`'s `(viewer)` table. On a copy
(`<scratch>/jv-bump`: the configuration, the eighteen files its tables name,
the root `package.json` and `package-lock.json`, made a git repository):

```
$ env -C <scratch>/jv-bump <bench>/.venv/bin/bump2version --no-commit --no-tag \
    --new-version 0.9.0 patch
$ env -C <scratch>/jv-bump npm install --package-lock-only
$ git -C <scratch>/jv-bump diff --stat
 20 files changed, 53 insertions(+), 53 deletions(-)
```

(`<scratch>/jv-bump.diff`.) Of the viewer, `git diff -U0` moves the
manifest's `version` and its pin `machinome~=0.9.0`, `__init__.py`'s
`__version__`, the widget's `"version"`, `viewer_version` in `docs/conf.py`
and, by npm, the lock's member entry (one line, `"version": "0.9.0"`, at its
line 2682), and nothing else of it; the core's two extras move to
`machinome-viewer~=0.9.0` and `machinome-viewer[snapshot]~=0.9.0` through
the core's existing `(pins)` table. Nothing was written in the bench.

### 9.2 Red first

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
check-dist failed: machinome-viewer has no smoke in scripts/check-dist
Nothing uploaded.
```

### 9.3 The row

`VIEWER_WIDGET`, `VIEWER_API` and `VIEWER_DOCUMENTS` read once at the top
beside `MECHANICS_VERSION` (the script imports `json` and `shutil`); the
`machinome-viewer` row of Decision 9 after the mechanics package's, verbatim;
`main` refuses before building when the viewer is a member and `npm` is not
on the PATH ("machinome-viewer's bundle is built by npm; put Node 22 and npm
on the PATH"); the docstring's requirements name Node 22 and npm, and what the
script writes inside the repository gains the root's `node_modules/` and the
widget's `dist/`. `git diff` removes three docstring lines and changes no
line of another row.

```
$ env -C <bench> <bench>/.venv/bin/flake8 --max-line-length=89 scripts/check-dist
(no output, exit 0)
```

### 9.4 The run

```
$ env -C <bench> PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python scripts/check-dist
Members: machinome, machinome-engine-brep, machinome-engine-mesh,
  machinome-mechanics, machinome-node-build123d, machinome-node-cadquery,
  machinome-node-freecad, machinome-node-jscad, machinome-node-molejo,
  machinome-node-openscad, machinome-node-solid2, machinome-node-step,
  machinome-node-stl, machinome-viewer
...
machinome-viewer 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/viewer/web/__init__.py API 29 documents 1 to 13
   machinome-viewer describe: exit 0
   machinome viewer: exit 0
Every distribution built, checked, installed and smoked; nothing uploaded.
```

(`<scratch>/check-dist-9.4.txt`, exit 0.) Fourteen members built; 14
`twine check --strict` runs, 28 archives `PASSED`; the viewer's wheel
installed by its path, its smoke printing 0.8.1, its module inside the
throwaway venv, API 29, documents 1 to 13, `License-Expression:
GPL-2.0-or-later OR CERN-OHL-S-2.0+` and `licenses/LICENSE`,
`licenses/LICENSES/CERN-OHL-S-2.0.txt`, `licenses/LICENSES/GPL-2.0-or-later.txt`
listed. The archives' entries: `machinome-0.8.1.tar.gz` 1073 and its wheel
114; `machinome_viewer-0.8.1.tar.gz` 1090 and its wheel 22 (the bench's
`dist/` held a `.build.lock` from a currency rebuild, the 22nd entry the
task allows); `machinome_mechanics-0.1.0` 213 and 17; the engines and node
packages as before (18 and 8 each; freecad 22 and 11; openscad 23 and 12).

`git -C <bench> status --short` afterwards: the edited and added files of
the change and nothing else; `node_modules/` and `widget/dist/` ignored. The
viewer's sdist hook ran `npm ci` inside the widget, which installed at the
bench's root (79 entries, as before) and left an empty
`widget/node_modules/` directory (no file in it; ignored by the package's
`.gitignore`): the step probe 6 could not identify that leaves one behind.
With Decision 4's lookup an empty directory no longer passes for installed
dependencies.

### 9.5 CI

`.github/workflows/python-app.yml`: in `test`, after the sync,
`actions/setup-node@v4` (Node 22, npm cache on `package-lock.json`) and
"Build and test the widget" at the root (`npm ci`, typecheck, test and build
of the workspaces), then "Run tests" unchanged, the mechanics step, and "Run
the viewer package's tests" from `packages/machinome-viewer`
(`playwright install --with-deps chromium`, `python -m pytest`); in
`browser-snapshot`, the step that installed the viewer from Git replaced by
Node and "Build the viewer and install Chromium" at the root (`npm ci`, the
build, `playwright install --with-deps chromium`); in `dist`,
`actions/setup-node@v4` with Node 22 before "Check the distributions"; `lint`
and `docs` unchanged. The workflow parses with `yaml.safe_load`; the layout
gate's CI tests are green in 10.4's run.

## 10. The records

### 10.1 The history and the changelogs

`HISTORY.rst`, after the mechanics bullet of `Unreleased`, and
`docs/project/changelog.rst`, at the end of its `Unreleased`: the entries of
Decision 12, verbatim. The viewer's `CHANGELOG.md`: a `## Unreleased`
section above `0.8.1` with Decision 12's two bullets, verbatim; the 0.7.0
section's identity bullet loses the licence words in place ("Package
`machinome-viewer`, import `machinome_viewer`, entry point
`machinome.viewer`. The framework reaches it only through that entry point
and separate processes; ..."), rewrapped. The framework changelog's two
released lines (0.8.0's licence bullet, 0.7's "Independent viewer") lose the
identifier in place (8.5).

### 10.2 `CREDITS.md`

A section "Bundled in the browser viewer" before the historical one: three.js
0.156.1 (MIT License, Copyright 2010-2023 three.js authors), jokenizer 1.0.1
(MIT License, Copyright (c) 2018 Umut Özel), molejo 0.2.0 (Apache License
2.0, as its `LICENSE` file and the banner name it, its `NOTICE` retained,
Copyright (C) 2026 Luis Henrique Cassis Fagundes), the versions read from
the root lock (`node_modules/three` 0.156.1 MIT, `node_modules/jokenizer`
1.0.1 MIT, `node_modules/molejo` 0.2.0 Apache-2.0) and the notices from the
bundle's banner; the historical section's last sentence as Decision 12
gives it; three rows in the summary table; the date 2026-10-12.

### 10.3 `docs/architecture.md`

The viewers section's opening, `sys.executable -m machinome.viewer.web`, the
decision log kept at `packages/machinome-viewer/workflow/adrs/`, the
diagram's label "machinome-viewer (own process)", the Map row's last cell
"015, 018, 041, 068, 103, 188 (the viewer itself:
`packages/machinome-viewer/`)"; and, beyond Decision 12's list, two
sentences that the join made false: the known gap "The CI browser-snapshot
job installs the viewer from Git" now reads "builds the viewer from the
repository", and the parity fixture "committed in the viewer repository"
now reads "committed in the viewer's package, `packages/machinome-viewer/`
(ADR-068, ADR-188), so widening the vocabulary regenerates it there".

### 10.4 The root's records and the README

The root `README.md`'s row after the mechanics package's;
`packages/machinome/README.rst`'s "Install" sentence (rewrapped) and its
"Licence" sentence removed; `CONTRIBUTING.rst`: the opening's sentence on
browser-viewer changes gone, "Development environment" with Node.js 22 and
npm, `npm ci` at the root and Chromium, `-e packages/machinome-viewer` in the
pip block before the mechanics line, the `npm ci` and `npm run build
--workspaces` commands after it, "Running tests" with the viewer's and the
widget's tests, the parity-fixture note; beyond Decision 12, the
browser-snapshot note's "Install a matching viewer with its snapshot extra"
now says the workspace installs it. `context7.json`: the three folders and
the viewer's rule of Decision 12. `AI-USE.md`: the viewer leaves the list of
sibling repositories and joins the paragraph on what is agent-written.

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH \
    <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider \
    tests/test_repository_layout.py tests/test_release_records.py \
    tests/test_docs_structure.py tests/test_profile_documentation.py \
    tests/test_viewer_documentation_links.py tests/test_docs_exports.py \
    tests/test_kernel_extras.py
123 passed, 1945 subtests passed in 6.04s
$ env -C <bench>/packages/machinome-viewer <bench>/.venv/bin/python -m pytest -q \
    -p no:cacheprovider tests/test_documentation.py tests/test_version.py \
    tests/test_licence.py tests/test_machinome_identity.py
28 passed, 163 subtests passed in 0.22s
```

### 10.5 The decision records

`docs/adrs/BUILD/ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md`,
Status Proposed, as Decision 12 outlines it: its options name the address
chosen and the two refused; its links resolve. ADR-068's status ("repository
and licence superseded 2026-10-12 by ADR-188") and a dated consequence;
ADR-182's, ADR-183's and ADR-187's status lines ("amended 2026-10-12 by
ADR-188") and the dated consequence "Neutral (2026-10-12, `join-viewer`)".
The index: ADR-188's line under BUILD after ADR-187, "amended by 188" on the
lines of ADR-182, ADR-183 and ADR-187, ADR-068's line noting "repository and
licence superseded by 188", and the nine *Relocated* entries of VIEWER-WEB
and EXPORT reading "*Kept* in the viewer's log,
`packages/machinome-viewer/workflow/adrs/` (ADR-068, ADR-188)".

### 10.6 The product's record

`openspec/config.yaml`'s context (the package at its address and directory,
the widget the npm workspace's member, the licence sentence gone);
`openspec/specs/viewer-distribution/spec.md` (its `Code:` line, the
licence and source the distribution and banner state, `python -m
machinome.viewer.web`, the identity's package and repository, "SHALL NOT
import the framework's modules" with the `machinome` package's own
`__init__` excepted and the pin of its own release, the scenarios' words;
titles kept); `user-documentation/spec.md` ("Makers have a viewer manual",
"The manual is reproducible and reviewable", "The manual states the 0.8.0
release", its Purpose, and, beyond Decision 13's list, "The manual states
the 0.8.1 release", whose home note, installation page, README and
context7 statements no longer exist; titles kept); the `Code:` lines of
`development-server`, `snapshot-capture`, `viewer-assembly-navigation` and
`viewer-package`; `workflow/README.md`'s two paragraphs and
`workflow/documentation.md` rewritten in place for the folded manual, its
Read the Docs section gone; the decision log's dated note under
"Provenance".

```
$ env -C <bench>/packages/machinome-viewer openspec validate --specs --strict
Totals: 16 passed, 0 failed (16 items)
```

### 10.7 The licences named in what the change and the join touched

Over the 947 paths the change touched or the join added (`git diff
--name-only 912fb7b4`, staged and untracked, and the 893 joined paths),
text files only, a case-insensitive count of the identifier and the long
name of the licence the product carried and a count of the framework's
former licence's name (the counts per file in
`<scratch>/licence-grep.txt`): the licence the product carried appears
only in the viewer's archived changes (21 files of 9 archived changes, 38
lines), its two active changes
`execute-running-time-drives` (evidence) and `slide-and-turn-parts`
(design, proposal), its decision log (ADR-050, ADR-051),
`workflow/archive/changelog-before-0.7.md`, `workflow/release-0.7.md` (3)
and `release-0.8.md` (1), `HISTORY.rst`'s released entries (lines 939 and
1484) and ADR-068's original text (5, the status line and consequence this
change added name none). The second name appears besides as third-party
provenance: `CREDITS.md` (11: watchdog, cadquery, manifold3d, molejo and
the rest), `package-lock.json` (4, the dependencies' own licences) and the
banner template of `build.mjs` (molejo, 2). No current file, and no record
this change writes, names either licence the product or the framework
carried.

## 11. Validation and the originating check

### 11.1 The whole suite

`pgrep -af "WTs/v0.9-joins-.*[p]ytest"` printed nothing before the run.

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH \
    <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
4865 passed, 9 skipped, 55 warnings, 7856 subtests passed in 705.44s (0:11:45)
```

(`<scratch>/suite-11.1.txt`, exit 0.) No failure. The nine skips: four
"MACHINOME_FREECAD_ROOT is not set", the end-to-end capture "set
MACHINOME_WEB_SNAPSHOT_E2E=1 to photograph through the installed viewer",
networkx absent (`test_connectivity.py:314`), the jscad CLI absent
(`test_jscad_integration.py:25`), and the Internal-Cycloidal-Actuator vendor
STEP absent (`test_step_assembly.py:426` and `:546`). Against the base's
4838 passed and 24 skipped: fifteen of the sixteen skips the viewer's absence
caused now run (the sixteenth, the end-to-end capture, skips on its opt-in),
and the change's tests add twelve: in `test_repository_layout.py` the four
of `TheNodeWorkspaceTest` and the two CI tests; in `test_release_records.py`
`test_the_viewer_s_version_files_agree` (the extras test replaced one for
one); in `test_docs_structure.py`
`test_the_browser_viewer_is_three_how_tos_and_a_reference_section` and
`test_the_viewer_facts_are_the_widget_s` less the removed
`LicenceWordingTest`; in `test_viewer_documentation_links.py` seven cases for
three; in `test_generate_parity_fixture.py` five `DefaultFixturePathTest`
cases for six; in `test_vet_universe.py`
`test_the_browser_viewer_is_internal_and_its_former_name_outside`.
4838 + 15 + 12 = 4865; 24 - 15 = 9.

### 11.2 The viewer's tests and the widget's

```
$ env -C <bench>/packages/machinome-viewer <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
250 passed, 2 skipped, 57 warnings, 185 subtests passed in 256.28s
$ env -C <bench>/packages/machinome-viewer \
    MACHINOME_CURTA_BUILDS=/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x/_build \
    <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
252 passed, 57 warnings, 185 subtests passed in 363.56s
$ env -C <bench> npm run typecheck --workspaces --if-present     (exit 0)
$ env -C <bench> npm test --workspaces --if-present
 Test Files  65 passed | 1 skipped (66)
      Tests  1715 passed | 2 skipped (1717)
$ env -C <bench> npm run build --workspaces --if-present
  dist/machinome-viewer.js  895.9kb
```

(`<scratch>/viewer-pytest-11.2.txt`, `viewer-pytest-11.2-curta.txt`,
`npm-*-11.2.txt`.) The two skips of the first run are the Curta's, which the
second runs. 244 passed and 2 skipped at the original (probe 8); the
viewer's tests gain six here (the two new behaviour tests, and four net in the
rewritten pinning modules).

### 11.3 The lint

```
$ env -C <bench>/packages/machinome bash -c \
    '<bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-*/machinome'
```

1515 lines (`<scratch>/lint-11.3.txt`), 3 of them the viewer's modules
(`bundle.py`: two unused imports, `pathlib.Path` and `PACKAGE_DIR`;
`cli.py:95`: a 91-character line), the same three the joined modules carry
at 7ed45449 under their former import (checked on copies,
`<scratch>/lintbase/`). The core files this change edited lint to 18 lines
before and after the change. (A first run that let the shell expand
`../machinome-*` from the wrong directory counted 1376 lines without the
packages; discarded.)

### 11.4 The manual on the final tree

```
$ env -C <bench>/packages/machinome <scratch>/docs-venv-jv/bin/python -m sphinx \
    -b html -n -W --keep-going docs <scratch>/jv-html-final
exit 0, no warning
$ env -C <bench>/packages/machinome-viewer <bench>/.venv/bin/python \
    scripts/check-docs-browser.py <scratch>/jv-html-final
pages 12, local_links 265, interactive_example passed, browser_errors []
```

### 11.5 `scripts/check-dist` on the tree and on a clean copy

On the tree, 9.4. On a clean copy (`git ls-files -z --cached --others
--exclude-standard` packed with `tar --null -T -`, unpacked under
`<scratch>/jv-clean/`, links kept, no `node_modules`):

```
$ env -C <scratch>/jv-clean PATH=<bench>/.venv/bin:$PATH \
    <bench>/.venv/bin/python scripts/check-dist
machinome-viewer 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/viewer/web/__init__.py API 29 documents 1 to 13
Every distribution built, checked, installed and smoked; nothing uploaded.
```

(`<scratch>/check-dist-clean.txt`, exit 0; 28 archives PASSED; the viewer's
sdist built its bundle by an `npm ci` that installed at the copy's root.)

| archive | tree | clean copy | base clean copy |
|---|---|---|---|
| `machinome` sdist | 1073 | 1072 | 1059 |
| `machinome` wheel | 114 | 114 | |
| `machinome-viewer` sdist | 1090 | 1089 | |
| `machinome-viewer` wheel | 22 | 21 | |
| `machinome-mechanics` sdist and wheel | 213, 17 | 213, 17 | |
| every other member | as 9.4 | as 9.4 | |

The framework's sdist grows by 13 entries, none removed: the twelve joined
pages and the directory `docs/reference/viewer/` (the base's built in
scratch from `git archive 484a528f`, the final's from the clean copy;
`<scratch>/jv-sd/base.txt`, `final.txt`, `diff` of the two). The committed
spinner export is not in it: the framework's `MANIFEST.in` carries `docs` as
`*.rst conf.py Makefile make.bat *.jpg *.png *.gif`, as for the tutorial's
exports. The viewer's wheel on the clean copy is 21: no `dist/.build.lock`,
its bundle built by the sdist hook rather than by a currency rebuild.

### 11.6 The universe sweep

The orchestrator's; not run here.

### 11.7 The originating check

On scratch copies only, with the bench venv:

```
$ env -C <scratch>/jv-new PATH=<bench>/.venv/bin:$PATH machinome new starter
$ env -C <scratch>/jv-new/starter PATH=<bench>/.venv/bin:$PATH \
    machinome snapshot --renderer web -o <scratch>/jv-starter-web.png
Snapshot saved to <scratch>/jv-starter-web.png
```

The PNG, 1920 x 1080, shows the starter's cube with its bore through the top,
looked at. Under `strace -f -e trace=execve` (`<scratch>/jv-snapshot-execve.txt`)
the framework executed `<bench>/.venv/bin/python3 -m machinome.viewer.web
capture <staging> -o <png> --imgsize 1920x1080 --time 0.0`.

The posed project `Vibecoded-demos/gear-shift` (model
`root.gearbox:GearboxDemo`), its ten tracked files copied to
`<scratch>/jv-gearshift/` (no `_build`):

```
$ env -C <scratch>/jv-gearshift PATH=<bench>/.venv/bin:$PATH MACHINOME_PORT=8731 \
    setsid machinome develop
```

The framework started `<bench>/.venv/bin/python3 -m machinome.viewer.web
serve --build-dir <scratch>/jv-gearshift/_build ...` (seen in `ps`), Uvicorn
on port 8731. Opened in Chromium once `/build/viewer.json` answered 200
(`<scratch>/jv-develop-shot.py`): title "Gearbox Demo", the bundle
`/_viewer/bundle.js`, `MachinomeViewer.apiVersion` 29, no page error. The
photograph `<scratch>/jv-develop-gearshift.png`, looked at, shows the
gearbox on its open frame, the brass gears on the input, lay and output
shafts, the red selector fork and the crank, the Assembly navigator listing
`open_frame`, `input_axis`, `layshaft_axis`, `output_axis` and `selector`,
and the timeline bar. A first attempt opened the page before the first build
had published and showed "Failed to load /build/viewer.json: 404"; the
script now waits for the document. Both develop runs were stopped by their
process group; port 8731 is free. The Curta was skipped, as the brief says.

### 11.8 Git

`git -C <bench> status --short`: 238 entries, 229 modified, 6 added (the
root `package.json`, the viewer's two links, the spinner export's three
files), 1 renamed (`RM` the widget's lock to the root), 2 untracked (ADR-188
and this `evidence.md`), each a file of groups 3 to 10 and nothing else.
`git -C <bench> ls-files -ci --exclude-standard | wc -l`: 34, as at the base.
Ignored leavings: the root's `node_modules/`, the widget's `dist/` and an
empty `widget/node_modules/` (9.4), the package's `_build/docs-review/`.

### 11.9 The change

```
$ env -C <bench>/packages/machinome openspec validate join-viewer --strict
Change 'join-viewer' is valid
```

## 12. Records closing (after the orchestrator's review)

The orchestrator reviewed the checkpoint on 12 October 2026 and asked for
two corrections first.

- The viewer's `user-documentation` spec, scenario "A maker reads which
  version they have" (title kept): its THEN no longer names a version; the
  compatibility page states the viewer's version, the set's, and the
  framework release it matches. The other version numbers in the specs and
  deltas this change wrote are the subjects of release records ("The 0.8.0
  release is recorded", "The 0.8.1 release is recorded", the viewer's "The
  manual states the 0.8.1 release") and the mechanics package's floor
  `machinome>=0.8.0`; they stay.
- The applier's leavings on the bench removed: `widget/dist/.build.lock`
  (0 bytes, 11:42, the 3.8 run's currency rebuild, the tree wheel's 22nd
  entry) and `widget/node_modules/` with the vitest cache `.vite` it held.
  The package's `machinome_viewer.egg-info/` and `_build/` stay, the
  build's own ignored scratch.

### 12.1 ADR-188

Status Accepted; its index line under BUILD reads **Accepted**.
`docs/architecture.md` agrees with it: the viewers section names the
distribution, the package `machinome.viewer.web`, the extra, the process
command and ADR-188; the decision log kept in the viewer's directory; the
Map row cites 188.

### 12.2 The archive

```
$ env -C <bench>/packages/machinome openspec archive join-viewer -y
Totals: + 0, ~ 13, - 0, → 1
Specs updated successfully.
Change 'join-viewer' archived as '2026-10-12-join-viewer'.
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 46 passed, 0 failed (46 items)
$ env -C <bench>/packages/machinome-viewer openspec validate --specs --strict
Totals: 16 passed, 0 failed (16 items)
```

(`<scratch>/jv-archive.txt`, `jv-validate-specs.txt`.) The CLI's
non-blocking warnings: the proposal's Why exceeds 1000 characters, more than
ten deltas, and the tasks unchecked at archive time (ticked afterwards in
the archived `tasks.md`, all but 11.6, the orchestrator's, and 12.3, whose
sweep line waits on it). Scenario counts after the archive, as design.md
Decision 14 rehearsed: `framework-identity` 29 to 32, `viewer-distribution`
13 to 14, `user-documentation` 86 to 89, `framework-contributor-guidance` 9
to 11, `vet` 66 to 67, `kinematics` 98.

### 12.3 The plan's progress

`workflow/ongoing/joins-0.9.md`, "Progress": the entry `3. join-viewer`
with the branch, the planning and merge commits, the ADR, the suite, the
viewer's and the widget's counts, the manual, `check-dist` with the clean
copy's counts, the lock and the originating check; the sweep's line left as
"(sweep: the orchestrator's numbers)" for the orchestrator's run.

### 12.4 This record

Complete to this point. The implementation commit is the orchestrator's,
never amending the planning commit 912fb7b4 or the merge commit 7ed45449;
nothing pushed.

## Departures from the design, and findings

- 3.4: the installation page's link target, which Decision 10 does not name,
  is `/howto/browser-viewer`.
- 3.6: five reds where the task expected one; the four others are mocked
  lookups that run without an installed viewer.
- 3.8: the behavioural reds needed a scratch link standing for the former
  module name, since the package's own imports move only in 4.4; the run's
  four mixed-name failures of `test_packaging.py` ran the real
  `build_frontend` once on the bench's widget (4.5).
- 4.5: the patch targets of `test_packaging.py` and the import set of
  `test_currency.py` (7.1's lines) moved here, so the two modules run whole.
- 8.3: `compatibility.rst`'s "released with Machinome 0.8.1" reads
  "released with Machinome |release|", a literal version a bump would leave
  behind under the new "This release declares:".
- 8.4: the operating guide's own opening paragraph sits under a new heading,
  "What the viewer shows", after "Try the viewer"; the embedding guide's
  "the example on the manual's home page" names the operating guide.
- 10.3, 10.4, 10.6: sentences the join made false outside Decision 12 and
  13's lists were corrected in place (architecture's CI gap and parity
  fixture, the contributor guide's browser-snapshot note, the viewer's "The
  manual states the 0.8.1 release" requirement).
- 9.4: an empty `widget/node_modules/` is what `npm ci` run inside the
  widget leaves (the step probe 6 could not name).
- 6.3: the committed parity fixture differs from the tool's present output;
  not regenerated (out of scope).
