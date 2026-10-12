# Evidence: `join-movie`

A cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` and `release-0.9.md` at the repository
root). Worktree `machinome/WTs/v0.9-joins-join-movie`, branch
`v0.9-joins-join-movie`, cut from the line `v0.9-joins` at 40087800 (after
`join-viewer` and `join-skills`). Planning commit 0f30f974, ratified by the
orchestrator on 12 October 2026 with every recommendation of its Open
Questions accepted and three tasks added (4.4, 6.4 and the sentence of
10.2); the join merge 646f664d on top of it. Applied on 12 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), Node 24.11.1 and npm
11.6.2, the OpenSpec CLI 1.6.0. Every command ran with `env -C <dir>` and
absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-join-movie`, `<scratch>`
is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C6-apply/`
and `<propose>` the proposer's `.../scratchpad/C6-propose/`. `D` is
`packages/machinome-movie`, `P` its package directory `D/machinome/movie`,
`J` its JavaScript directory `P/js`. The core's tests ran from
`<bench>/packages/machinome` on the bench venv (`<bench>/.venv/bin/python -m
pytest -q -p no:cacheprovider ...`), the package's from `<bench>/D`, one
pytest process at a time. Logs are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -3
646f664d Join the videomaker: its whole history at its final paths
0f30f974 Propose join-movie: the videomaker as the distribution machinome-movie, imported as machinome.movie, its command machinome movie
40087800 Integrate join-skills: the machinome skills as machinome.skills, installed by machinome skills
$ git -C <bench> status --short | wc -l
0
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
$ git -C <bench> ls-files | wc -l
5322
```

`git status --short --ignored` showed `.env`, `.venv/`, the root's
`node_modules/`, the widget's `dist/` and the members' `__pycache__/` and
`*.egg-info/` leavings, all ignored.

### 1.2 The bench venv and the base counts (task 1.2)

The bench venv the orchestrator synced from the lock before the join:
fifteen `__editable__` `.pth` files (`machinome-0.8.1`, the two engines, the
nine node packages, `machinome_viewer-0.8.1`, `machinome_skills-0.8.1` and
`machinome_mechanics-0.1.0`), and

```
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome_movie"
ModuleNotFoundError: No module named 'machinome_movie'
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome.movie"
ModuleNotFoundError: No module named 'machinome.movie'
```

The base counts: the orchestrator's brief names none for 40087800. The
line's recorded counts are those of the two cycles it integrates
(`joins-0.9.md`, Progress): `join-viewer` 4865 passed, 9 skipped;
`join-skills` 4857 passed, 24 skipped, 7562 subtests (on its own base
5af14f71, without the viewer). Not rerun here.

### 1.3 The MODIFIED requirement against the baseline (task 1.3)

The requirement "Extras select independent Machinome products" extracted
from `openspec/specs/framework-identity/spec.md` at the bench's head
(`<scratch>/base-req.md`) and from this change's delta
(`<scratch>/change-req.md`), `diff`: the delta is the baseline with the
movie's names in the first sentence, the movie's sentence after the skills'
(the skills' sentence rewrapped, its words unchanged), the `movie` names in
the scenario "The extras keep the Machinome name under a version floor" (its
title kept), and the scenario "A user installs the movie extra" added after
the skills'. No other difference; no scenario title changes.

### 1.4 The probes relied on (task 1.4)

By reference to design.md: probe 1 (677 files; 83322ce, a36e32f, ca99a77;
no path outside `packages/`), 3 (the reds of the join), 4 (298 at the
original layout; 22, 11, then 9 at the new place), 5 (the re-pin), 7 and 8
(the shallow layout; 493 passed, 12 failed of 505), 10 (the member lock), 11
(the installed case), 12 (the seam's reds), 13 (197 packages on the viewer's
line), 14 (the timings), 15 (vet), 16 (the projects), 17 (the deltas
archived).

## 2. The join

### 2.1 The import (task 2.1, the orchestrator's)

A fresh clone of `file:///home/asa/devel/machinome/videomaker` (`main`
1617f81, `live-audio-mixer` 866c25a, `record-review` a0a1219, 251 commits)
rewritten by `<propose>/filter-repo-command.sh`, the command of design.md
Decision 2 (log `scratchpad/C6-join/filter-repo.log`): 251 commits, none
pruned; `main` 83322ce, `live-audio-mixer` a36e32f, `record-review` ca99a77,
the rehearsal's hashes. `git ls-tree -r --name-only main` lists the 677
paths of `<propose>/rehearsal-ls-files.txt` exactly (the diff empty; the
listing at `scratchpad/C6-join/ls-files.txt`); no commit of the three
branches touches a path outside `packages/` (0); each branch is two commits
on 83322ce.

### 2.2 The merge (task 2.2, the orchestrator's)

`git fetch <clone> main live-audio-mixer:movie-live-audio-mixer
record-review:movie-record-review` into the bench; the merge commit
646f664d (parents 0f30f974 and 83322ce4), `git merge
--allow-unrelated-histories --no-ff` of 83322ce onto 0f30f974, no conflict;
`git status --short` empty afterwards; tracked files 5322 (4645 before the
join plus 677; `git diff --stat 0f30f974 646f664d`: 677 files changed,
198266 insertions).

```
$ git -C <bench> log --format='%h %ad %s' --date=short -- packages/machinome-movie/machinome/movie/js/src/render.mjs | tail -1
a716989b 2026-09-19 Build YAML-to-video workflow with cached ElevenLabs narration
$ git -C <bench> log --oneline -3 movie-live-audio-mixer
a36e32f5 feat: audition live film audio as synchronized channels
6961fd44 plan: live film audio audition with separate stems
83322ce4 fix(player): jump forward two seconds with right arrow
$ git -C <bench> log --oneline -3 movie-record-review
ca99a77e Add native live movie review recording
c5521139 Plan native live movie review recording
83322ce4 fix(player): jump forward two seconds with right arrow
```

### 2.3 The gates on the joined tree (task 2.3)

`tests/test_repository_layout.py tests/test_release_records.py
tests/test_core_names_no_split_words.py tests/test_docs_structure.py`
(`<scratch>/2.3-join-reds.out`): 10 failed, 89 passed, 2054 subtests
passed. Each red, with its reason:

- `TheWorkspaceTest::test_every_member_is_a_workspace_source`: the root's
  `[tool.uv.sources]` lacks `'machinome-movie': {'workspace': True}`.
- `test_the_readme_links_every_package_and_states_the_licence` (subtest
  `machinome-movie`): `'packages/machinome-movie/' not found` among the
  root README's links.
- `test_every_sibling_is_in_the_table` (subtest `machinome-movie`):
  "packages/machinome-movie is in neither EXTENSIONS nor PRODUCTS".
- `test_the_guide_installs_every_member_without_uv` (subtest
  `machinome-movie`): "CONTRIBUTING.rst does not name -e
  packages/machinome-movie".
- `TheNodeWorkspaceTest::test_one_lockfile_at_the_root_names_the_widget`:
  the tracked locks are `['package-lock.json',
  'packages/machinome-movie/machinome/movie/js/package-lock.json']`, not
  the root's alone (the node workspace's test on the movie's tracked lock).
- `test_every_member_is_numbered_with_the_core` (subtest `machinome-movie`):
  `'0.0.0' != '0.8.1'`.
- `test_every_pin_between_members_is_compatible` (subtest
  `machinome-movie`, `machinome`): `'' != '~=0.8.1'`, the bare
  `machinome`.
- `test_the_version_is_bumped_from_the_root` (subtest `machinome-movie`):
  `packages/machinome-movie/pyproject.toml` not among `.bumpversion.cfg`'s
  files.
- `test_no_module_names_the_split_but_by_its_two_words`: three modules,
  seven occurrences of the identifier `exact_seconds`
  (`machinome/movie/document.py` lines 17, 242, 257; `take.py` 21, 381, 407;
  `names.py` 107).
- `LicenceFactTest::test_no_page_spells_a_licence` (subtest
  `howto/film-a-movie.rst`): the page spells a licence identifier literally
  (the README's sentence on the Leonardo sources' licence, line 523).

Nothing else is red. Design.md probe 3 counted two subtests of
`test_docs_structure.py` on `howto/film-a-movie.rst`; on this head one
fails, the licence-identifier test; the rest of probe 3's list is as
found. The node workspace's red is the one task 2.3 names.

## 3. Red first, on the joined tree

Nothing of the package changed in this group.

### 3.1 The layout gate (task 3.1)

`tests/test_repository_layout.py` gains: the `PRODUCTS` row; `NODE_MEMBERS`
a mapping of each member's directory to its package name, the root's
`workspaces` its keys in order, each member's `package.json` named and
private; `OWN_LOCKS` and `MOVIE_JS`; the lock test renamed
`test_the_root_s_lock_names_each_member_and_the_movie_keeps_its_own` (the
tracked locks are the root's and the movie's; the root lock names each
member by its name; the movie's lock is named `@machinome/movie`);
`test_the_movie_s_own_lock_agrees_with_its_manifest_and_the_root_s`;
`test_the_root_installs_each_member_s_dependencies_beside_it`; `.npmrc`
among the root's files; the widget's CI step named by `--workspace` and no
step of the test job running `--workspaces`;
`test_the_test_job_runs_the_movie_s_node_projects_without_a_browser`; the
default group with `machinome[movie]`; the docstring.

Run (`<scratch>/3.1-red.out`): 20 failed, 39 passed, 243 subtests passed.
The reds, each with its reason:

- `test_every_member_is_a_workspace_source`: no `machinome-movie` source.
- `test_the_default_group_is_the_framework_dev_and_the_products_extras`:
  `'machinome[movie]'` missing.
- `test_the_test_job_builds_and_tests_the_widget_before_the_suite`: four
  subtests, "the job has no step that runs npm run typecheck|npm test|npm
  run build --workspace <widget> at the root", and the step "Build and test
  the widget" runs `--workspaces`.
- `test_the_test_job_runs_each_product_s_tests` (`machinome-movie`): "the
  test job runs no pytest from packages/machinome-movie".
- `test_the_test_job_runs_the_movie_s_node_projects_without_a_browser`:
  "the job has no step that runs the movie's pure and stage projects".
- `test_the_readme_links_every_package_and_states_the_licence`
  (`machinome-movie`): the README links no `packages/machinome-movie/`.
- `test_the_repository_s_files_are_there` (`.npmrc`): `.npmrc is missing`.
- `test_the_guide_installs_every_member_without_uv` (`machinome-movie`):
  no `-e packages/machinome-movie`.
- `test_each_product_directory_holds_its_package_and_its_record`: no
  `LICENSE`, `LICENSES`, `MANIFEST.in` among the entries.
- `test_each_product_manifest_states_the_set_s_licence`: `KeyError:
  'license'` (no licence, `packages` not `find`).
- `test_each_product_readme_names_its_install_and_the_licence`: no `pip
  install "machinome[movie]"` in the Python half's README.
- `test_each_product_resolves_from_its_directory`: `ModuleNotFoundError:
  No module named 'machinome.movie'`.
- `test_the_root_package_is_a_private_workspace`: the root's `workspaces`
  lists the widget alone.
- `test_the_root_s_lock_names_each_member_and_the_movie_keeps_its_own`:
  `KeyError` for the movie in the root lock; the movie's lock named
  `machinome-videomaker`.
- `test_the_movie_s_own_lock_agrees_with_its_manifest_and_the_root_s`:
  `KeyError: 'packages/machinome-movie/machinome/movie/js'` in the root
  lock.
- `test_the_root_installs_each_member_s_dependencies_beside_it`: `.npmrc is
  missing`.
- and the four of 2.3 (the workspace source, the README, the guide; the
  lock count is now the renamed test's).

`test_every_sibling_is_in_the_table` passes from here on: the row is in
`PRODUCTS`.

### 3.2 to 3.5 The release records, the extras, vet and the manual

`tests/test_release_records.py` gains
`test_the_movie_s_node_version_files_agree`; `tests/test_kernel_extras.py`
`EXTRAS['movie']`; `tests/test_machinome_identity.py` `('movie',
'machinome-movie')`; `tests/test_vet_universe.py` the contract's tuple and
`test_the_movie_is_internal_and_its_former_name_outside`;
`tests/test_docs_structure.py`
`test_the_films_are_three_how_tos_and_a_reference_section`,
`test_no_page_shows_the_videomaker_s_former_command_lines`, the install
page's distribution and its two lines, and in `CommandReferenceTest`
`test_the_movie_command_has_its_section` and
`test_the_videomaker_is_no_longer_to_add_its_command`. The skills' test
`test_the_skills_package_is_no_longer_to_add_its_command` now reads "the
skills package ``machinome skills``", the words of Decision 12's sentence
("The movie package adds ``machinome movie`` and the skills package
``machinome skills``, below; ...").

Run (`<scratch>/3.2-3.5-red.out`): 29 failed, 75 passed, 2075 subtests
passed. The reds:

- 3.2: `test_the_movie_s_node_version_files_agree`: `J/package.json` and
  the member lock's two entries at `0.0.0`, the root lock without an entry
  for `J`, `.bumpversion.cfg` not naming `J/package.json`; with 2.3's three
  (`0.0.0`, the bare `machinome`, the bump).
- 3.3: `KeyError: 'movie'` in `test_each_extra_lists_what_its_module_needs`
  and in `test_distribution_import_command_and_extras_share_the_name`.
- 3.4: `test_the_contract`, the tuple without `'machinome.movie'`;
  `test_the_movie_is_internal_and_its_former_name_outside`, the model
  importing `machinome.movie` vetted pure ("Items in the second set but not
  the first: ('sim/model.py', 'framework-internal', 'machinome.movie')"),
  as probe 15 found: vet judges a name by its place in the universe.
- 3.5: the four toctree entries absent and
  `reference/movie/index.rst` missing; the former command lines on
  `howto/declare-a-movie.rst` (`machinome_movie`), `howto/film-a-movie.rst`
  (`bin/videomaker.mjs`, `machinome_movie`, `--viewer`) and
  `reference/movie/episode.rst` (`--viewer`), and the changelog's line not
  yet written; the install page without `machinome-movie`, `pip install
  "machinome[movie]"` and `machinome movie setup`; `cli.rst` without the
  section `.. _movie-command:`, without "The movie package adds
  ``machinome movie``" and still naming the videomaker as to add its
  command, so the skills' sentence of Decision 12 is not there either; and
  2.3's licence identifier on `howto/film-a-movie.rst`.

### 3.6 The package's new tests

`D/tests/test_command.py` (17 tests) and `D/tests/test_package.py` (6
tests). The command's tests run each case in a process of its own through
a bootstrap that gives the command module a scratch JavaScript directory
(a copy of `J/bin/videomaker.mjs`, `J/package.json` and
`J/package-lock.json`, its `node_modules/esbuild/package.json` present or
not, inside a scratch npm workspace or not) and, where a case needs it, a
viewer report, then runs `machinome.movie.__main__.main`; Node and npm are
fakes written per test (`MACHINOME_NODE` names the fake, which answers
`--version` with `FAKE_NODE_VERSION`, records its arguments and working
directory, and exits with `FAKE_NODE_STATUS`; the fake `npm` records its own
and writes `node_modules/esbuild/package.json`). The help and `python -m`
tests run the venv's `machinome` and `python -m machinome.movie`.

Run from `D` (`<scratch>/3.6-red.out`): 22 failed, 1 passed. The command's
cases fail with `ModuleNotFoundError: No module named 'machinome.movie'` in
their process, and `machinome movie -h` with argparse's invalid choice (no
entry point); the in-process tests of `test_package.py` with `No module named
'jsonschema'` (`python -m pytest` puts `D` on the path, the namespace finds
the portion, and its eager root imports `jsonschema`, which the venv lacks
before the sync) and the manifest test on its name's version `0.0.0`. The
expected red was the collection's `ModuleNotFoundError`; the modules import
nothing of the package at their top, so each test fails on its own instead.
`test_no_module_of_the_former_name_is_provided` passes already: the bench
venv never installed `machinome_movie` (the product ran it from `python/`
on `PYTHONPATH`); it holds the line from here on.

## 4. The package

### 4.1 The links (task 4.1)

`ln -s ../../LICENSE LICENSE` and `ln -s ../../LICENSES LICENSES` from `D`,
`git add`ed; both resolve to the root's (`LICENSES/` lists
`CERN-OHL-S-2.0.txt` and `GPL-2.0-or-later.txt`).

### 4.2 The manifest, README, MANIFEST.in and .gitignore (task 4.2)

`README.md`, `MANIFEST.in` and `.gitignore` are design.md Decision 3's,
verbatim. `pyproject.toml` is Decision 3's but for the data tables, which
task 4.4 changed (below): `include-package-data = false`, the wheel's data
named in `[tool.setuptools.package-data]` (`machinome-movie-0.2.json`,
`js/package.json`, `js/package-lock.json`, `js/bin/*`, `js/src/*`,
`js/stage/*`, `js/player/*`, `js/transport/*`, `js/schema/*`), and
`[tool.setuptools.exclude-package-data]` `"machinome.movie" =
["js/*.test.*"]`; `[tool.setuptools.packages.find]` is the design's,
`include = ["machinome.movie"]`.

### 4.3 The member's manifest and lock (task 4.3)

`J/package.json` edited as Decision 3 says: the name `@machinome/movie`, the
version `0.8.1`, the set's licence expression, `bin` and the `video` script
gone, Playwright `1.63.0`, TypeScript, `@types/react` and `@types/react-dom`
moved to `dependencies`, every version exact. Its lock regenerated in
`<scratch>/member-lock` (the two files alone, outside any workspace):

```
$ env -C <scratch>/member-lock npm install --package-lock-only --no-audit --no-fund
npm warn EBADENGINE Unsupported engine { package: '@asamuzakjp/css-color@7.1.2', required: { node: '^22.22.2 || ^24.15.0 || >=26.0.0' }, current: { node: 'v24.11.1', npm: '11.6.2' } }
(three more for @asamuzakjp/dom-selector, jsdom 30.1.1 and w3c-xmlserializer, development dependencies)
up to date in 892ms
```

Copied back; `git diff --stat` of the lock: 16 insertions, 60 deletions
(`<scratch>/4.3-lock.diff`, 76 changed lines). Read with a script comparing
the two `packages` tables: the name and version (top and root entry), the
root entry's licence, its `dependencies` and `devDependencies` as the
manifest's, `bin` gone; Playwright and `playwright-core` 1.62.0 to 1.63.0,
Playwright's optional `fsevents` and the entry `node_modules/fsevents` gone;
the `dev` flag dropped from 24 entries: the three moved packages and what
only they install (`typescript`, its 20 platform packages
`@typescript/typescript-*`, `@types/react`, `@types/react-dom`, and
`csstype`). One more line than probe 10 named: `node_modules/picomatch`
loses its `"peer": true` flag (npm recomputes the flag with TypeScript no
longer a development dependency). Nothing else.

### 4.4 The wheel declares what it ships (task 4.4)

In a scratch copy of the tracked and new files of `D` with `LICENSE` and
`LICENSES` (`<scratch>/wheel44/`, then `<scratch>/wheel44b/`), `python -m
build --wheel` on the bench venv (setuptools 84.0.0):

- design.md Decision 3's manifest (`include-package-data = true`, the
  exclusions keyed by `machinome.movie`): 20 warnings "Package
  'machinome.movie.js...' is absent from the `packages` configuration"
  (`<scratch>/4.4-design.out`), probe 11's count.
- `include = ["machinome.movie", "machinome.movie.js*"]` with `exclude` for
  `js.test*`, `js.fixtures*`, `js.scripts*` and `js.node_modules*`
  (`<scratch>/4.4-v1.out`): 13 warnings remain, one for each excluded
  directory (`machinome.movie.js.fixtures`, `...js.test.support`, ...), and
  the wheel grows by 106 entries, the files of the excluded directories
  carried as data of `machinome.movie.js`. setuptools warns for every file
  of the sdist's manifest under a package's directory whose own directory is
  not a package (`build_py.analyze_manifest`, `_IncludePackageDataAbuse`),
  whatever `exclude-package-data` later drops, and that analysis runs only
  when `include-package-data` is true.
- The remedy kept: `include-package-data = false` and the wheel's data named
  in `package-data`, the sdist still given the whole of `js/` by
  `MANIFEST.in` (`<scratch>/4.4-f.out`, then on the final tree
  `<scratch>/4.4-build.out`): 0 warnings of that kind; the build output's
  other four lines are `MANIFEST.in`'s `recursive-exclude` finding no
  `__pycache__` or `*.py[co]`, twice (sdist and wheel steps).

On the final tree (`<scratch>/wheel44b/`, after group 5): the wheel holds 77
entries (`<scratch>/4.4-wheel.list`): the twelve modules and `cli.py`, the
schema `machinome/movie/machinome-movie-0.2.json` as a regular file,
`js/package.json`, `js/package-lock.json`, `js/bin/videomaker.mjs`, `js/src/`
(30), `js/stage/` (10), `js/player/` (7), `js/transport/` (4), `js/schema/`,
the three licence files and the entry point `movie =
machinome.movie.cli:Movie`; 0 entries under `js/test/`, `js/fixtures/`,
`js/scripts/`, no `*.test.*` and no `node_modules`. The file list equals the
design manifest's wheel but for `cli.py`, absent there (76 entries,
`<scratch>/4.4-design.list` against `<scratch>/4.4-f.list`: identical before
`cli.py` existed). The sdist of the same tree: 684 files
(`<scratch>/4.4-f2.out`; 0 package warnings when the wheel is built from it).

## 5. The source at its address

### 5.1 The import (task 5.1)

`git diff` of each file shows those lines alone:

- `stage.py`: `_shipped` tests `cls.__module__ == 'machinome.movie' or
  ...startswith('machinome.movie.')`.
- `watch.py`: its docstring's first line and the evaluation command
  `[sys.executable, '-m', 'machinome.movie', 'evaluate', project, movie]`.
- `__main__.py`: rewritten by 5.3.
- `J/src/text.mjs` and `J/src/timeline.mjs`: the comments naming
  `python/machinome_movie/text.py` and `names.py` name
  `machinome/movie/text.py` and `names.py`.

### 5.2 The lazy root (task 5.2)

`__init__.py`: its docstring and `__all__` unchanged; the imports replaced by
`_MODULES`, each of the 45 names of `__all__` mapped to its module (the
table and `__all__` hold the same 45 names), and a module `__getattr__` that
imports the name's module and binds every name of that module at once.

### 5.3 The command and `python -m` (task 5.3)

`P/cli.py`, new: the class `Movie` of Decision 5 (its docstring, `needs_node
= False`, `add_arguments` with the eleven verbs as subparsers, `handle`),
the module importing `json`, `math`, `os`, `shutil`, `subprocess`, `sys`
and `pathlib` alone at its import. `list`, `evaluate` and `watch` carry the
former `__main__.main`'s behaviour, a refusal of the movie's own still
written `machinome-movie: <refusal>`; the command's own refusals are one
line `Error: <refusal>`, exit 1. `P/__main__.py` builds an
`argparse.ArgumentParser(prog='machinome movie')`, gives it to
`Movie().add_arguments` and runs `handle`: one parser for `python -m
machinome.movie` and `machinome movie`, so `watch`'s evaluation in a process
of its own runs `python -m machinome.movie evaluate`. The JavaScript
directory is the module's `JS`, read at each call.

### 5.4 The schema link (task 5.4)

```
$ readlink <bench>/packages/machinome-movie/machinome/movie/machinome-movie-0.2.json
js/schema/machinome-movie-0.2.json
```

It resolves to `J/schema/machinome-movie-0.2.json`; the wheel carries it as
a regular file (4.4).

### 5.5 The Node side's words (task 5.5)

- `J/src/episode.mjs`, the two refusals: "... Install a machinome-viewer that
  declares it: pip install -U "machinome[viewer]"." in place of "Select a
  [newer] machinome-viewer bundle with --viewer."; `J/test/annotations.test.mjs`'s
  two expectations follow.
- `J/src/render.mjs`'s retry hint: `retry: machinome movie review
  ${manifestOutput}`.
- `J/src/speech.mjs`'s refusal: "No ElevenLabs key: set ELEVENLABS_API_KEY in
  the environment, or in the .env of the directory machinome movie runs from;
  looked in ..."; `keyFiles()` unchanged. No test matches that sentence (the
  pipeline test asserts only that no refusal names the key).

## 6. The npm workspace

### 6.1 The second member and `.npmrc` (task 6.1)

The root `package.json`'s `workspaces` gains
`packages/machinome-movie/machinome/movie/js` after the widget's, nothing
else changed; the root `.npmrc` is Decision 6's, one setting
(`install-strategy=shallow`) and its comment.

### 6.2 The install (task 6.2)

No `node_modules` on the bench is a link (`find <bench>/node_modules
-maxdepth 1 -type l`: none). From the root, the root lock as `join-viewer`
left it copied first to `<scratch>/root-lock.before.json` (2698 lines):

```
$ env -C <bench> npm install --no-audit --no-fund
(four EBADENGINE warnings, jsdom 30.1.1 and three of its dependencies ask for Node ^22.22.2 or ^24.15.0; this is 24.11.1)
added 43 packages in 8s
```

(43: the root's `node_modules` already held the viewer's packages; 6.3's
`npm ci` from nothing adds 144, probe 7's count.) The lock grows from 2698
to 4126 lines, `git diff --stat`: 1431 insertions, 3 deletions; 177 entries
before, 264 after, 86 of them the movie's. The comparison of
`<scratch>/compare_viewer.py` (probe 7's: every entry of the earlier lock at
its path with its version and its resolved URL): "viewer resolutions: 176,
kept 176, moved 0". The entries are the 264 of probe 7's lock
(`<propose>/npm-ws-nested/package-lock.json`), path for path; 25 differ in
their flags alone, the `dev` flag that TypeScript and the React types no
longer carry. `J/node_modules` holds 34 entries, the movie's direct
dependencies among them, and `.bin/tsc` and `.bin/esbuild`;
`J/node_modules/playwright-core/browsers.json` names `chromium` and
`chromium-headless-shell` revision 1243, which `~/.cache/ms-playwright`
holds.

### 6.3 `npm ci` (task 6.3)

```
$ env -C <bench> npm ci --no-audit --no-fund
added 144 packages in 4s
```

The lock unchanged (`cmp` against the copy taken after 6.2), `J/node_modules`
34 entries again; `git -C <bench> status --short | grep -c node_modules`: 0.

### 6.4 The widget under the shallow layout (task 6.4)

From the root, `TMPDIR` under `<scratch>`, the widget named by
`--workspace packages/machinome-viewer/machinome/viewer/web/widget`:

- `npm run typecheck`: `tsc --noEmit`, exit 0 (`<scratch>/6.4-typecheck.out`).
- `npm test`: "Test Files 65 passed | 1 skipped (66)", "Tests 1715 passed
  | 2 skipped (1717)", 71.45 s, exit 0 (`<scratch>/6.4-test.out`):
  `join-viewer`'s counts.
- `npm run build`: `dist/machinome-viewer.js 895.9kb` (917391 bytes),
  exit 0 (`<scratch>/6.4-build.out`).

`scripts/check-dist`'s viewer row is recorded at 11.4.

## 7. The core and the workspace

### 7.1 The extra (task 7.1)

`git diff packages/machinome/pyproject.toml` shows one hunk: after the
`mechanics` extra, the `movie` extra `["machinome-movie~=0.8.1"]` and its
three-line comment of Decision 7.

### 7.2 The uv workspace, the lock and the sync (task 7.2)

The root's sources gain `machinome-movie = { workspace = true }` after
`machinome-mechanics`; the dev group gains `"machinome[movie]"`, its comment
naming the skills and movie packages' tests and commands.

```
$ env -C <bench> uv lock
Resolved 198 packages in 562ms
Added jsonschema v4.26.0
Added jsonschema-specifications v2025.9.1
Added machinome-movie v0.8.1
Added referencing v0.37.0
Added rpds-py v2026.9.1
```

The line's lock held 193 packages (`grep -c '^\[\[package\]\]'`), now 198:
the member and the four of probe 13; `git diff --stat uv.lock`: 200
insertions, 1 deletion.

```
$ env -C <bench> uv sync --python 3.12
 + jsonschema==4.26.0
 + jsonschema-specifications==2025.9.1
 ~ machinome==0.8.1 (from file://<bench>/packages/machinome)
 + machinome-movie==0.8.1 (from file://<bench>/packages/machinome-movie)
 + referencing==0.37.0
 + rpds-py==2026.9.1
```

Sixteen `__editable__` `.pth` files, the new one
`__editable__.machinome_movie-0.8.1.pth` naming
`<bench>/packages/machinome-movie`. From `/tmp`:

```
$ env -C /tmp <bench>/.venv/bin/machinome movie -h
usage: machinome movie [-h] VERB ...

positional arguments:
  VERB
    list      print a project's movies table
    evaluate  write a movie document
    watch     evaluate a movie, then again whenever a file of its project
              changes, until interrupted
    check     check a film: its sources, narration, takes and stage
    speech    generate the narration a film still lacks
    preview   draw a film's storyboard and its highlight checks
    render    render a film to video
    build     generate the narration a film lacks, then render it with its
              audio
    live      serve a film at a local address and reload it when its inputs
              change, until interrupted
    review    make the review pack of a rendered film's manifest
    setup     install the Node side's dependencies into this package
...
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome.movie as m; print(m.__file__)"
<bench>/packages/machinome-movie/machinome/movie/__init__.py
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome_movie"
ModuleNotFoundError: No module named 'machinome_movie'
```

`machinome -h` lists `movie`, "Film a machine: evaluate a project's movies,
then check, voice, preview, render, build, serve and review them.", after
`vet` and before `skills`.

### 5.2, continued: the name `evaluate` (found once the package was installed)

With the venv synced, a test added to `D/tests/test_package.py`,
`test_the_function_evaluate_keeps_its_name_beside_its_module`, ran red
against the lazy root as 5.2 first wrote it (`<scratch>/5.2-naive.out`: 1
failed, 6 passed): after `import machinome.movie.evaluate`, `from
machinome.movie import evaluate` gave the module, not the function, because
the import system binds a submodule to the package's attribute of its name
and the module `__getattr__` is then never asked. The eager root rebound the
name to the function by its own `from .evaluate import ... evaluate`. The
root now sets its module's class to a `types.ModuleType` subclass whose
`__setattr__` keeps an exported name whose module has the same name bound to
the name's object (`evaluate` alone has one). Green: 7 passed
(`<scratch>/5.2-fixed.out`).

### 7.3 The vet universe and the split-word gate (task 7.3)

`machinome/vet/universe.toml`: `"machinome.movie"` in `[contract] deny`
after `"machinome.viewer.web"`, with its comment naming the change.
`tests/test_core_names_no_split_words.py`: `ORDINARY` gains
`machinome/movie/names.py`, `document.py` and `take.py`, each
`{'ex' 'act_seconds'}`, with the comment of Decision 8.

### 7.4 Group 3's core tests again (task 7.4)

The seven modules of 2.3 and group 3 (`<scratch>/7.4.out`): 28 failed, 132
passed, 2447 subtests passed. Green now: the extras (3.3), vet (3.4), the
split-word gate, the product's entries, manifest, README, resolution, the
members, both locks, `.npmrc`, the numbering and the pins. Red, each named
in a later group: the CI steps (four subtests and two tests, 11.5); the
README and the guide (12.2); the bump (`.bumpversion.cfg` naming neither the
manifest nor `J/package.json`, 11.1); the manual's tests and the licence
identifier on `howto/film-a-movie.rst` (group 10).

## 8. The seam's tests

### 8.1 The fakes renamed (task 8.1)

Before the edit, on the synced venv, `tests/test_cli_contributed.py
tests/test_cli_lazy_imports.py tests/test_cli.py` (`<scratch>/8.1-red.out`):
6 failed, 51 passed, 33 subtests passed. The reds, probe 12's on the
`movie` fakes:

- `test_a_contributed_command_runs_with_its_own_verbs`, its three subtests:
  exit 1, "Error: machinome movie is contributed by more than one package:
  fake-movie (machinome_fake_movie:Movie), machinome-movie
  (machinome.movie.cli:Movie)".
- `test_help_lists_contributed_commands_after_the_framework`: the fake's
  `movie` and its docstring not listed (the name is unavailable).
- `test_a_name_two_packages_contribute_runs_neither`: three packages named,
  not two.
- `test_the_contract_walk_reads_a_fake_distribution`: `'fake-movie': ['movie
  is also contributed by machinome-movie']`.

Probe 12's fifth, `test_a_module_that_cannot_be_imported` (the choices
ending `gone,movie`), passes on this line: `join-skills` computes the
expected choices from the installed contributors.

`tests/contributed_commands.py`: `fake-movie` is `fake-film`, its entry
`film = machinome_fake_film:Film`, its class `Film` with the docstring "Make
films of machines (a fake contributed command).", its verbs unchanged and
its output `film <verb> <source>`; `fake-movie-two` is `fake-film-two`,
`film = machinome_fake_film_two:Film`; `FAKE_MODULES` follows; the
portion fake's comment says the movie package's `machinome.movie` ships as
one. `tests/test_cli_contributed.py` follows (the invocations `film build
film.yaml`, `film list build`, `film render film.yaml`, the collision on
`film`, `FILM_DOC`); `tests/test_cli_lazy_imports.py`'s fake walk names
`fake-film`, and the real walk's docstring names the `movie` entry.

After (`<scratch>/8.1-green.out`): 54 passed, 36 subtests passed.

### 8.2 The conformance walk's red, once (task 8.2)

`needs_node = False` deleted from `Movie` (the file copied first to
`<scratch>/cli.py.keep`), then
`tests/test_cli_lazy_imports.py::RegistryConformanceTest::test_every_contributed_entry_resolves_and_honours_the_contract`
(`<scratch>/8.2-red.out`): 1 failed, 1 passed, 1 subtest passed;
`SUBFAILED(command='movie', dist='machinome-movie')`, "['needs_node is not
declared as True or False'] != []". The copy restored; `cmp` against it:
identical (`cli.py` is a new file, so `git diff` shows none).

## 9. The tests at their new place

### 9.1 Python (task 9.1)

`machinome_movie` to `machinome.movie` in `test_fixtures.py`,
`test_cli.py`, `test_evaluation.py`, `test_take.py` (2), `test_declarations.py`
(2), `test_watch.py` (4) and `test_repository.py` (the import and
`resources.files`), and in the fixture project's four movie modules
(`videos/takes.py`, `videos/minimal/movie.py`, `videos/count/movie.py`,
`videos/tour/movie.py`; design.md says five, the project holds four that
import it); `conftest.py`'s `REPOSITORY` is `PYTHON / 'machinome' / 'movie' /
'js'` (`FIXTURES` and `SCHEMA` follow); `test_take.py`'s path to
`fixtures/documents` reads `D/machinome/movie/js/fixtures/documents`;
`test_repository.py`'s package directory `PYTHON / 'machinome' / 'movie'`.

`env -C <bench>/packages/machinome-movie <bench>/.venv/bin/python -m pytest -q
-p no:cacheprovider` (`<scratch>/9.1.out`): 20 failed, 302 passed (322: the
298 and the 24 of 3.6 and 5.2). The task expected 9 failed; the count
includes the fixture documents' roots, which 9.2 moves (probe 4's middle
step): 11 of `test_fixtures.py` (the three documents differing from their
evaluation in `root`, `../../python/tests/...` against
`../../../../../tests/...`, and eight invalid fixtures, each refused for
another reason or not at all while its root names no project; all eleven pass
once 9.2 moves the roots), the fixture revision's (the manifests record
e14e6852, the project's commit is now 55ad41bf) and the eight pinning tests
of `test_repository.py` reading `docs/`, `README.md` and `CHANGELOG.md` at
the product's former root.

### 9.2 The fixture documents, the Node paths and the re-pin (task 9.2)

The roots of the fixture documents: 76 JSON files under `J/fixtures/`
(`documents/` 3, `invalid/` 70, `resolved/` 3) name
`"../../python/tests/fixtures/project/`, one each, now
`"../../../../../tests/fixtures/project/`; design.md's 77 counted
`fixtures/README.md` too, whose three mentions of `python/tests/...` and of
`PYTHONPATH` set to `python/` now name the package's `tests/fixtures/project/`
and the package's directory. The fourteen path lines of
`<propose>/probe_js_patch.py` (twelve edits, two of them on two lines each;
its `stage-build.mjs` part dropped, `<scratch>/js_paths.py`) applied:
`scripts/pin-fixture-project.mjs`, `scripts/draw-fixture-still.mjs`,
`test/export.test.mjs`, `test/fixture-still.test.mjs`, `test/memo.test.mjs`,
`test/repository.test.mjs` (six lines), `test/stage-types.test.mjs`,
`test/support/fixture-movie.mjs` and `test/support/reach.mjs`. Beside them,
probe 5's two other lines of `pin-fixture-project.mjs` (`PYTHONPATH` the
package's directory, `-m machinome.movie`) and three comments
(`pin-fixture-project.mjs`'s usage, `draw-fixture-still.mjs`'s and
`fixture-movie.mjs`'s first lines).

```
$ env -C <J> TMPDIR=<scratch>/tmp node scripts/pin-fixture-project.mjs --python <bench>/.venv/bin/python --machinome <bench>/.venv/bin/machinome
Export counter: made from 55ad41bf95652c3491ba14501372f2f3a5a08365, manifest changed, written to ../../../tests/fixtures/project/export/counter.
Export seesaw: made from 55ad41bf95652c3491ba14501372f2f3a5a08365, manifest changed, written to ../../../tests/fixtures/project/export/seesaw.
Revision: 55ad41bf95652c3491ba14501372f2f3a5a08365, recorded by every export's source.
Document minimal: changed, written to fixtures/documents/minimal.json.
Document tour: changed, written to fixtures/documents/tour.json.
Document count: changed, written to fixtures/documents/count.json.
Now run node scripts/pin-resolved.mjs minimal tour count and review the pins before committing.
$ env -C <J> TMPDIR=<scratch>/tmp node scripts/pin-resolved.mjs minimal tour count
Wrote <J>/fixtures/resolved/minimal.json; review it before committing.
Wrote <J>/fixtures/resolved/tour.json; review it before committing.
Wrote <J>/fixtures/resolved/count.json; review it before committing.
```

(`<scratch>/9.2-repin.out`, `<scratch>/9.2-pin-resolved.out`; the framework's
build log lines between them omitted.) Probe 5's revision, 55ad41b. `git diff
--stat` of `J/fixtures/` and `D/tests/fixtures/`: 83 files, 105 insertions,
105 deletions: the 76 roots; in the six documents and resolved pins, their
root and `sourceRevision` (e14e6852 to 55ad41bf), nothing else (the diff's
changed lines, counted by content: 6 revisions and 6 roots, each in and out);
the two export manifests, 16 lines each, their parts' `mtime` and the
recorded `revision` alone; the four fixture modules' import lines. No model
file of either export changed (`git status` lists only the two
`manifest.json` under `export/`).

### 9.3 The pinning tests read the manual (task 9.3)

`D/tests/test_repository.py`: `PAGE` is `packages/machinome/docs/howto/declare-a-movie.rst`,
`FILM` `howto/film-a-movie.rst`, `PAGES` the films' seven pages; the nine
pinning tests keep their facts in reStructuredText's spelling (double
backquotes, section titles read from the underlines, code blocks from
`.. code-block:: python`): the page is linked from the how-to and the toctree;
the narrator's sentences; no project or checkout named (the declarations page
by its four words, every film page by `Leonardo`, `worktree`, `WTs/`,
`../projects` and the former module name); the examples are the fixture's
code; the package's `CHANGELOG.md`; the clocked take's sections and
sentences; the status line in the how-to; and `watch` on the page, in the CLI
reference's synopsis and in `__main__.py`'s docstring (the package's README,
Decision 3's, shows no usage lines). 17 passed (`<scratch>/9.3-py.out`).

`J/test/repository.test.mjs`: the twelve tests that read the product's
records read the manual's pages (`howto/film-a-movie.rst` with
`reference/movie/command.rst` where the README held the facts; the stage,
document, declarations and episode pages), the package's `CHANGELOG.md`,
`workflow/architecture-overview.md` and its decision log at
`workflow/adrs/`, each fact in its new spelling; the assertions on
`AGENTS.md` go, those on the test layers held by `vitest.config.mjs`'s
projects (the stage project's `transport/**/*.test.ts` and
`player/**/*.test.ts`); the `.gitignore` assertion on `/WTs/` goes with the
product's `.gitignore`; the options test reads the command reference and the
CLI reference for every option the Node side declares but `--viewer`, and no
film page names `--viewer`; the status-claims test reads the how-to's
installed-viewer sentence (`|viewer_version|`, `|viewer_api|`). Run alone
before the suite: `env -C <J> TMPDIR=<scratch>/tmp
./node_modules/.bin/vitest run test/repository.test.mjs --project pure`
(`<scratch>/9.3-node.out`): 17 passed, after one red found by it: the stage
page's grid table had split the view row's sentence across cell borders, so
the Markdown tables of the stage and document pages were rewritten as
`list-table`s (10.2).

The four comments citing `AGENTS.md` (`vitest.config.mjs`,
`test/support/memo.mjs`, `test/support/reach.mjs`, `test/memo.test.mjs`) cite
the package's ADR-003.

### 9.4 The Python tests (task 9.4)

From `D` (`<scratch>/9.4.out`): 322 passed in 48.03 s, no failure: the 298
and the 24 new (`test_command.py` 17, `test_package.py` 7).

### 9.6 The core's suite collects none of them (task 9.6)

`pytest --collect-only -q` from the framework's directory
(`<scratch>/9.6.out`): 4898 tests collected; `grep -c machinome-movie`: 0.

## 10. The manual

### 10.1 Red first (task 10.1)

A fresh venv `<scratch>/docs-venv` (uv, CPython 3.12) installing
`packages/machinome/docs/requirements.txt` alone (Sphinx 9.1.0, the theme,
the published `machinome-viewer`), then from the framework's directory
`python -m sphinx -b html -n -W --keep-going docs <scratch>/html-red`
(`<scratch>/10.1-red.out`): exit 1, "build finished with problems, 319
warnings (with warnings treated as errors)": 73 "Inline literal start-string
without end-string", 73 "Inline interpreted text or phrase reference
start-string without end-string", 72 "Unexpected indentation", 60 "Block
quote ends without a blank line", 22 "Definition list ends without a blank
line", 8 "Undefined substitution referenced", 5 "document isn't included in
any toctree" (the five pages the join landed), 4 "Line block ends without a
blank line", 2 "Inline emphasis start-string without end-string": the
Markdown read as reStructuredText.

### 10.2 The pages (task 10.2)

Each of the five pages the join landed is edited in place (its file
rewritten with the converted text, never moved). The conversion was made in
the scratch directory with pandoc 3.9 (from the `pypandoc_binary` wheel in a
scratch venv, `-f gfm -t rst --columns=78`), a post-processing script
(`<scratch>/post.py`: the manual's heading style, `code-block`, the
links to the manual's pages as `:doc:`), and by hand:

- `howto/film-a-movie.rst`, "Film a movie of your machine", written from the
  README's sections a reader follows: what the films are, "Install"
  (`pip install "machinome[movie]"`, `machinome movie setup`, the Chromium
  line it prints, FFmpeg the system's, and `machinome movie setup --remove`
  before `pip uninstall machinome-movie`, since pip leaves what `setup`
  installed), "The viewer" (the installed viewer, `|viewer_version|` and
  `|viewer_api|`, and the API each film needs), "The narration key"
  (`ELEVENLABS_API_KEY` in the environment or the `.env` of the directory
  the command runs from, kept out of the repository), "Make a film" (a
  project and a movie name, and an episode's `episode.yaml`, through
  `check`, `speech`, `preview`, `render`, `review`), "Edit a film live"
  (`watch` beside `live`), "Timing and revisions" (the sawmill's numbers as
  an example by kind). What left the page, as Decision 12 says: the tool's
  and the Leonardo sources' licences, "no remote is configured", the
  repository's tests and OpenSpec records, the link to `first-rehearsal.md`,
  every project path, the voices of named episodes.
- `reference/movie/command.rst`, "The movie command", new: the synopsis,
  the three forms of a source, Node and the viewer, the exit statuses,
  `list`/`evaluate`/`watch`, then the README's verb sections whole (`check`,
  `speech`, `preview`, `render`, `build`, `review`, `live` with its routes,
  its watching and the player), what a film records of its trees and its
  export, "What a film writes" (the README's Output, the cache key, release
  readiness) and `setup` (its install, its second step, `--remove` before
  `pip uninstall`, its two refusals). `--viewer` is gone from the text: the
  films are drawn by the installed viewer's bundle, never one an export
  carries.
- `reference/movie/index.rst`, "Movies", new: the package, its version
  (`|release|`) and the toctree `command`, `document`, `episode`.
- `howto/declare-a-movie.rst` ("Declare a movie"),
  `howto/draw-a-movie-stage.rst` ("Draw a movie's stage"),
  `reference/movie/document.rst` ("The movie document"),
  `reference/movie/episode.rst` ("The episode format"): converted, their
  substance kept; `python -m machinome_movie` is `machinome movie`, the
  package is `machinome.movie` installed by the extra, `videomaker live` is
  `machinome movie live`, the viewer refusal's sentence is the Node side's
  new one; the document page loses its status paragraph's campaign record,
  its provenance parentheticals (fourteen "finding n of the react-stage
  change", the changes and ADR numbers of the product's log, the pilot's
  rulings: a teaching page carries none, `write-the-manual` rule) and its
  "Schema and fixtures" section's fixture paths; its example JSON names a
  sawmill, a calculator and the set `playbill` instead of the project, and
  its five illustrative blocks with `…` are `code-block:: text` (as
  `json` they failed the build's highlighting, four warnings); the episode
  page's status line names no project. The stage and document pages' four
  Markdown tables became `list-table`s (pandoc's grid tables split their
  sentences across cell borders, which `J/test/repository.test.mjs` found).
- `index.rst`: the three how-tos after `howto/embed-the-viewer`,
  `reference/movie/index` after `reference/viewer/index`.

### 10.3 The CLI reference and the install page (task 10.3)

`reference/cli.rst`: "Commands from other packages" closes with "The movie
package adds ``machinome movie`` and the skills package ``machinome
skills``, below; the studio (``machinome studio``) is to add its own.", then
the section `.. _movie-command:` `machinome movie`: the synopsis of the
eleven verbs, the sources, Node and the viewer, the options, the exit
statuses and the link to `/reference/movie/command`. `start/install.rst`:
"Packages and licences" names `machinome-movie` among the set's packages
under the set's licence; the extras paragraph ("Four more extras exist")
gains `movie` with its two lines, `pip install "machinome[movie]"` and
`machinome movie setup`, Node 22, and Chromium and FFmpeg as the how-to's
steps.

Beside them, one page this change makes wrong otherwise:
`reference/viewer/troubleshooting.rst` told a checkout to run `npm run build
--workspaces`, which with a second member that has no `build` script would
fail; it names the widget (`--workspace
packages/machinome-viewer/machinome/viewer/web/widget`), as CI and the
guide now do.

### 10.4 The build (task 10.4, first run)

The build of 10.1 into `<scratch>/html` (`<scratch>/10.4-try2.out`): exit
0, no warning, after the four highlighting warnings of the first try
(`<scratch>/10.4-try1.out`). `test_docs_structure.py`, `test_docs_exports.py`
and `test_node_root_exports_nothing.py` (`<scratch>/10.4-tests.out`): 67
passed, 1 failed, the changelog's line, written in 12.1. The final build is
13.4's.

## 11. The version records, `scripts/check-dist` and CI

### 11.1 `.bumpversion.cfg` and the bump on a copy (task 11.1)

After the viewer's tables: `[bumpversion:file(version):packages/machinome-movie/pyproject.toml]`,
`[bumpversion:file(pins):packages/machinome-movie/pyproject.toml]` (`~=`)
and `[bumpversion:file:packages/machinome-movie/machinome/movie/js/package.json]`
(`"version": "{current_version}"`). On a copy (`<scratch>/bump/`: the
configuration and the 21 files it names, a git repository, one commit):
`bump2version --no-commit --no-tag --new-version 0.9.0 patch` exit 0
(`<scratch>/11.1-bump.out`), 22 files changed; the movie's `version =
"0.9.0"`, its pins `machinome~=0.9.0` and `machinome-viewer~=0.9.0`,
`J/package.json`'s `"version": "0.9.0"` and the core's `movie` extra
`machinome-movie~=0.9.0`. Nothing written in the bench.

### 11.2 Red first (task 11.2)

`scripts/check-dist` did not parse on this line: `SyntaxError: '{' was
never closed` at `SMOKES = {` (line 240). The viewer's row lacked its
closing `},` before the skills' row; the line's head 40087800, the
integration of `join-skills`, introduced it (`git show
<commit>:scripts/check-dist | python3 -c 'compile(...)'`: 8315e65c and
78a584df parse, 40087800 and 646f664d do not). The row's closing `},` is
inserted, one line: the orchestrator's correction of the line, commit
675edac4 ("scripts/check-dist: close the viewer's smoke row"), made the same
way here so the merge takes it once. Then:

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
check-dist failed: machinome-movie has no smoke in scripts/check-dist
Nothing uploaded.
```

exit 1 (`<scratch>/11.2-red.out`).

### 11.3 The row (task 11.3)

The row of Decision 11 after the viewer's, verbatim; the start refuses when
the movie is a member and `node` or `npm` is not on the `PATH`; the
docstring names the movie's smoke. `flake8 --max-line-length=89
scripts/check-dist`: 0.

### 11.5 CI (task 11.5)

`.github/workflows/python-app.yml`, the test job: the widget's step names
it (`npm run typecheck|test|build --workspace
packages/machinome-viewer/machinome/viewer/web/widget`) after `npm ci`;
after the viewer package's step, "Run the movie package's tests" (`python
-m pytest` from `packages/machinome-movie`) and "Run the movie package's
Node tests" (`npm test --workspace packages/machinome-movie/machinome/movie/js
-- --project pure --project stage` from the root). The browser-snapshot
job's `npm run build --workspaces --if-present` is unchanged: the movie has
no `build` script, which `--if-present` skips.

## 12. The records

### 12.1 The changelogs (task 12.1)

`HISTORY.rst` (the end of `Unreleased`), `docs/project/changelog.rst` (the
end of `Unreleased`) and `D/CHANGELOG.md` (its first sentence and the first
bullet of `Unreleased`): the entries of design.md Decision 14, verbatim.

### 12.2 The repository's records (task 12.2)

- `CREDITS.md`: the section "Installed by `machinome movie setup`, and drawn
  into every film" before the historical section, each package with its
  licence, repository and version as the installed `package.json` states
  them (esbuild 0.28.2 MIT, highlight.js 11.12.0 BSD-3-Clause, Playwright
  1.63.0 Apache-2.0, React and React DOM 19.3.0 MIT, TypeScript 7.0.2
  Apache-2.0, yaml 2.8.1 ISC, the React types MIT), ElevenLabs and FFmpeg
  named, seven summary rows, the ISC licence's link; the last-updated line
  was already 2026-10-12.
- `docs/architecture.md`: the extras sentence gains `[movie]`; "CLI": "The
  first is `machinome movie`, from the repository's distribution
  `machinome-movie` (ADR-191); `machinome skills` ... is the second
  (ADR-190); the studio's follows at its join" in place of "the movie's and
  the studio's follow at their joins"; the section "Movies (the distribution
  `machinome-movie` · spec `movie-distribution`)"; the Map's row.
- The root `README.md`: the row after the viewer's, verbatim.
- `CONTRIBUTING.rst`: `-e packages/machinome-movie \` in the pip block; the
  Node paragraph names both members, the root's `.npmrc` and that `machinome
  movie setup` is for an installed copy; the widget's build and test lines
  name the widget (`--workspaces` would run the movie's suite or fail on its
  missing `build`); "Running tests" gains Decision 14's sentence.
- `context7.json`: six folders excluded (`D/openspec`, `D/tests`,
  `D/workflow`, `D/experiments`, `J/test`, `J/fixtures`) and the rule after
  the skills' one, verbatim.
- `AI-USE.md`: the clause on the films.

### 12.3 ADR-191 (task 12.3)

`docs/adrs/BUILD/ADR-191-the-videomaker-is-a-product-of-the-set-its-node-side-installed-by-its-command.md`,
Status Proposed, Change `join-movie`, amending ADR-182 and ADR-188, related
to ADR-187, ADR-189 and ADR-190, as Decision 14 outlines it; its index line
under BUILD after ADR-190's. ADR-182 and ADR-188 gain the dated status
amendment and the consequence "Neutral (2026-10-12, `join-movie`): ...";
their index lines gain "amended by 191".

### 12.4 The product's record (task 12.4)

`D/openspec/config.yaml`'s context says what Decision 15 says;
`D/openspec/specs/declarative-movie/spec.md`'s four command lines
(`list`, `evaluate`, `watch` twice) are `machinome movie`, titles kept; the
specs hold no `Code:` line and no other user's command line (the
`live-preview` spec states the Node side's own options, `--viewer` among
them, which `bin/videomaker.mjs` still takes). `D/workflow/README.md`'s
closing section is the maintainer notes in force; `D/workflow/adrs/README.md`
gains the dated note of Decision 15; `D/workflow/architecture-overview.md`
the dated note at its top.

```
$ env -C <bench>/packages/machinome-movie openspec validate --specs --strict
...
Totals: 18 passed, 0 failed (18 items)
```

(`<scratch>/12.4-validate.out`, exit 0.)

### 12.5 The former spellings (task 12.5)

The tracked files the join or this change added or changed, and the new ones
(722, `<scratch>/12.5-files.txt`), grepped for `machinome_movie`,
`bin/videomaker.mjs`, `--viewer` and the Leonardo sources' licence
identifier (`<scratch>/12.5-counts.txt`, 130 files): the product's archived
changes (86 files, 154 lines), its workflow archive (11, 30), `ongoing/` (2,
2), `adrs/` (3, 3), `experiments/` (3, 7), `first-rehearsal.md` (1),
`warts.md` (2), `architecture-overview.md` (4); the former-name lines of
`HISTORY.rst`, `docs/project/changelog.rst` (1) and `D/CHANGELOG.md` (8);
the Node side's own option and command file, which stay
(`bin/videomaker.mjs` 2, `cli.py` 2 passing `--viewer`, the pipeline and
viewer tests that spawn `bin/videomaker.mjs` with `--viewer`:
`movie-pipeline` 24, `provenance` 10, `live` 9, `review-pack` 2,
`real-viewer` 3, `take` 3, `test/support/reach.mjs` 6, the `live-preview`
spec 3); the tests that assert their absence (`test_command.py` 4,
`test_repository.py` 1, `test_docs_structure.py` 1, `test_vet_universe.py`
2, `repository.test.mjs` 3); `scripts/check-dist`'s shipped-file assertion
(1); ADR-191 (5) and its index line (1), which name what is no longer
provided; this evidence file. No reader-facing page of the manual holds
one but the changelog's line.

### 9.5 The Node suite (task 9.5)

From the root, after the widget's bundle was built (6.4), `TMPDIR` under
`<scratch>`:

```
$ env -C <bench> TMPDIR=<scratch>/tmp-node VIDEOMAKER_VIEWER_BUNDLE=<bench>/packages/machinome-viewer/machinome/viewer/web/widget/dist/machinome-viewer.js npm test --workspace packages/machinome-movie/machinome/movie/js -- --cold
 Test Files  52 passed (52)
      Tests  505 passed (505)
   Duration  1046.77s
```

(`<scratch>/9.5-node-suite.out`, exit 0, 17:27.71 wall clock): the four
projects ran, `pure` 25 files, `stage` 6, `slow` 17 and `viewer` 4 on the
bench's viewer 0.8.1 (API 29); none skipped, none failed; probe 8's twelve
pinning failures are green. The run started after 9.3 and before 12's
edits to the package's changelog, decision log index and workflow notes;
13.2 runs it again on the final tree.

### 11.4 and 6.4 `scripts/check-dist` on the tree (task 11.4)

`env -C <bench> TMPDIR=<scratch>/tmp PATH=<bench>/.venv/bin:$PATH
<bench>/.venv/bin/python scripts/check-dist` (`<scratch>/11.4-check-dist.out`),
exit 0, "Every distribution built, checked, installed and smoked; nothing
uploaded.": sixteen members built, 32 archives `twine check --strict`
PASSED. The movie's: `machinome_movie-0.8.1.tar.gz` 929 entries,
`machinome_movie-0.8.1-py3-none-any.whl` 77 entries (probe 11: 926 and
77); its wheel installed by path, `review` refused before `setup` naming it,
`setup` installed, `review missing.json` reached Node, `setup --remove`
removed `js/node_modules`, the licence files, "machinome-movie 0.8.1 module
<venv>/.../machinome/movie/__init__.py Node side installed and removed",
`machinome movie -h` exit 0. The viewer's row green (its sdist hook built
the bundle from this layout; `machinome-viewer describe` and `machinome
viewer` exit 0), its archives 1089 and 21 entries; the framework's 1139 and
114.

A finding of this run: afterwards `J/node_modules` was empty (the root's
`node_modules` 79 entries, the lock unchanged). Reproduced: after the root's
`npm ci` (`J/node_modules` 34 entries), `npm ci` in the widget's directory,
which the viewer's build hook (`machinome/viewer/web/packaging.py`,
`build_frontend`) runs when its sdist is built, installs that member alone
and leaves the movie's `node_modules` empty (0 entries); the root's `npm ci`
restores it (144 packages, 34 entries). `check-dist` therefore needs a root
`npm ci` after it on a checkout before the movie's Node suite runs; its own
throwaway environment is not affected, and CI's dist job runs nothing after
it. Not changed here: the hook is the viewer's (a `--workspace` or root
`npm ci` there would keep both members).

`git -C <bench> status --short` after the run: the files of this change
alone, no `node_modules`, `dist/` or build leavings listed.

## 13. Validation

### 13.1 The suite (task 13.1)

`env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH
<bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider`
(`<scratch>/13.1-suite.out`): 4894 passed, 9 skipped, 8422 subtests passed,
in 972.91 s, exit 0. The skips: four FreeCAD (`MACHINOME_FREECAD_ROOT` not
set), the browser photograph (`MACHINOME_WEB_SNAPSHOT_E2E`), networkx, the
jscad CLI, the two vendor STEP files: the viewer line's nine. The tests
collected against the base, `pytest --collect-only` on an archive of
646f664d's `packages/machinome/tests` (4889) and on the bench (4899),
diffed by node id (`<scratch>/base-ids.txt`, `<scratch>/now-ids.txt`):
eleven added (`test_docs_structure.py` four:
`test_the_films_are_three_how_tos_and_a_reference_section`,
`test_no_page_shows_the_videomaker_s_former_command_lines`,
`test_the_movie_command_has_its_section`,
`test_the_videomaker_is_no_longer_to_add_its_command`;
`test_release_records.py`'s `test_the_movie_s_node_version_files_agree`;
`test_repository_layout.py` five:
`test_the_test_job_runs_the_movie_s_node_projects_without_a_browser`,
`test_the_guide_runs_the_movie_s_two_suites`,
`test_the_movie_s_own_lock_agrees_with_its_manifest_and_the_root_s`,
`test_the_root_installs_each_member_s_dependencies_beside_it`,
`test_the_root_s_lock_names_each_member_and_the_movie_keeps_its_own`;
`test_vet_universe.py`'s `test_the_movie_is_internal_and_its_former_name_outside`)
and one renamed away (`test_one_lockfile_at_the_root_names_the_widget`): +10.
The base's run, not given by the brief, is therefore 4884 passed and 9
skipped on this line (inferred from the collection, not run).
`test_the_guide_runs_the_movie_s_two_suites` was written after the guide's
edit; its assertions, run on the base's `CONTRIBUTING.rst` (`git show
0f30f974:CONTRIBUTING.rst`), miss all five spellings, and on the bench none.

### 13.2 The package's two suites on the final tree (task 13.2)

Python, from `D` (`<scratch>/13.2-py.out`): 322 passed in 37.69 s.

Node, from the root, as 9.5 after the root's `npm ci` restored
`J/node_modules` (`<scratch>/13.2-node-suite.out`): 52 files, 505 tests
passed, none skipped, `pure` 25 files, `stage` 6, `slow` 17, `viewer` 4,
980.70 s (16:21.50 wall clock), exit 0.

The orchestrator's sweep (13.6), the projects' move and the originating
check (group 14) and the records' closing (group 15) remain; this change
stops at 13.9.

### 13.3 The lint (task 13.3)

`flake8 --max-line-length=89 machinome tests ../machinome-*/machinome` from
the framework's directory (`<scratch>/13.3-flake8.out`): 1805 lines, 290 of
them the movie package's modules (`document.py` 90, `evaluate.py` 61,
`movie.py` 52, `stage.py` 38, `take.py` 33, `project.py` 5, `names.py` 4,
`anchors.py`, `watch.py` and `__init__.py` 2 each, its two lines of
`__all__` unchanged, `__main__.py` 1, the usage line of its docstring;
`cli.py` 0). The ten core test files this change edited carry the base's
lines alone (`test_cli_lazy_imports.py` 4 at the base and now; the others
0). CI's lint step is `continue-on-error`.

### 13.4 The manual (task 13.4)

The build of 10.1 into `<scratch>/html` on the final tree
(`<scratch>/13.4-docs.out`): exit 0, no warning. Read as text from the built
HTML: the three how-tos, the section's four pages and the CLI reference's
section render their substitutions (`|release|` 0.8.1, `|viewer_version|`,
`|viewer_api|`), their links and code blocks.

### 13.5 `scripts/check-dist` on a clean copy (task 13.5)

The tree on the bench is 11.4's run. A clean copy: `git ls-files -z
--cached --others --exclude-standard | tar --null -T - -cf -` unpacked under
`<scratch>/clean` (the tracked files and this change's nine new ones, links
kept: 5297 files, 36 links), then `scripts/check-dist` there
(`<scratch>/13.5-clean-check-dist.out`): exit 0, sixteen members, 32
archives PASSED; the framework's sdist 1083 entries and wheel 114, the
movie's 929 and 77, the viewer's 1089 and 21; the movie's smoke as in 11.4.

### 13.6 The universe sweep (task 13.6)

The orchestrator's; not run here.

### 13.7 Git (task 13.7)

`git -C <bench> status --short`: 175 entries, 164 modified, 2 added (the
two links), 9 untracked (`.npmrc`, `D/MANIFEST.in`, `P/cli.py`,
`D/tests/test_command.py`, `D/tests/test_package.py`, ADR-191,
`reference/movie/command.rst` and `index.rst`, this file); 83 of the
modified are fixtures (76 roots, the three documents and three resolved
pins among them, the two export manifests, the four fixture modules); no
`node_modules`. `git ls-files -ci --exclude-standard | wc -l`: 34, the base's.

### 13.8 OpenSpec (task 13.8)

```
$ env -C <bench>/packages/machinome openspec validate join-movie --strict
Change 'join-movie' is valid
```

## 13.9, the orchestrator's review

At the checkpoint the orchestrator asked for the fix of 11.4's finding in
this cycle, since the second member brought it; design.md Decision 6 is not
amended, and this section records the departure.

`packages/machinome-viewer/machinome/viewer/web/packaging.py`,
`build_frontend`: `npm ci` now runs at the npm workspace's root when an
ancestor `package.json` names the widget's directory among its
`workspaces` (a new `workspace_root`, as `machinome.movie.cli` finds it), in
the widget's directory otherwise; `npm run build` stays in the widget's
directory. The symbolic-`node_modules` refusals are unchanged and still
come first.

Red first, `packages/machinome-viewer/tests/test_packaging.py` gaining
`test_packaging_installs_at_the_workspace_root_that_names_the_widget` (a
scratch tree whose root `package.json` names the widget and a second
member; `subprocess.check_call` patched as the module's tests patch it; the
calls asserted `npm ci` at the root, `npm run build` in the widget) and
`test_packaging_installs_in_the_widget_under_a_root_that_names_another` (a
root naming another directory: both calls in the widget). From
`packages/machinome-viewer` (`<scratch>/13.9-packaging-red.out`): 1 failed,
10 passed, the first test, `npm ci` called with `cwd` the widget's
directory instead of the workspace's root; the second passes already, a
guard. After the fix (`<scratch>/13.9-packaging-green.out`): the module
11 passed. `flake8 --max-line-length=89` of `packaging.py`: 0; of the test
module, one line, the base's (line 145, not this change's).

`packages/machinome-viewer/CHANGELOG.md`, under `Unreleased`: "`npm ci` of
the widget's build runs at the workspace root, so a second member's
dependencies survive it."

The original case, once, on the bench, through the hook's own function:
`env -C <bench> <bench>/.venv/bin/python -c "from machinome.viewer.web import
packaging; packaging.build_frontend(packaging.WIDGET)"`
(`<scratch>/13.9-build-frontend.out`): exit 0, "added 144 packages", the
bundle built (`dist/machinome-viewer.js 895.9kb`, 917391 bytes);
`J/node_modules` 34 entries before and after (11.4's run left 0), the root's
79, the root lock unchanged.

## 14, the orchestrator's

Done by the orchestrator on 12 October 2026, recorded here as it reported
them.

### 14.1 The projects' move

33 files in five repositories: the 21 Python modules importing
`machinome.movie`, and 12 film READMEs running the verbs through `machinome
movie` (every `node .../bin/videomaker.mjs <verb> <source> --viewer
<bundle>` and `python -m machinome_movie evaluate` line; the lines passing
the videomaker checkout to a project's own script unchanged, as the stage
modules are). One commit per repository, "Import the films from
machinome.movie and run them with machinome movie": Leonardo 05776cc (20
files), kossel 6cb8ea2 (6), Curta-Type-I-3x 6ad3a38 (3), Metamaquina2
2589956 (3), lumiere-cinematographe f7ec9e1 (1). In Leonardo four of the
files also held the pilot's uncommitted edits, which stay in its tree
unstaged (the move's rules were staged over each file's committed content).
`grep -rn machinome_movie` over the catalogue's `*.py` and `README.md`
(worktrees and `node_modules` excluded): 0 afterwards.

### 14.2 The originating check

From the bench's venv in the Curta's repository, `TMPDIR` under the
scratch directory: `machinome movie check <Curta> addition` exit 0, the
viewer 0.8.1 found through the entry point, the shots reported, the three
provenance lines saying the project, the tool and the export are dirty, as
they are on a bench; `machinome movie preview <Curta> addition` exit 0, 11
highlights measured, the storyboard written at
`videos/addition/_build/storyboard.jpg` (548641 bytes, 15:57) and looked at
by the orchestrator: the Curta posed through the viewer across the film's
shots.

### 14.3 The sweep

The universe sweep after the move, on the bench: 63 repositories, 130 rows, 122 ok, 0 expected, 2 unexpected, 0 timeout, 6 no-model, identical to `join-mechanics`'s row for row (the two unexpected rows wall clock 41 and fender-bender's, as before); the catalogue's self-referencing link `machinome-projects` excluded with `--only '^(?!machinome-projects/)'`, 24 directories skipped

## 15. Records closing

### 15.1 ADR-191 (task 15.1)

ADR-191 promoted to Accepted, its change link the archive's
(`../../../openspec/changes/archive/2026-10-12-join-movie/`); its index
line in `docs/adrs/README.md` says Accepted. `docs/architecture.md` checked
against it: its section "Movies" now also says that in the checkout the
Node side is the root npm workspace's second member, installed by the
root's `npm ci` with each member's direct dependencies beside it (the
root's `.npmrc`); the CLI paragraph, the Map row and the extras sentence
already said what the ADR decides.

### 15.2 The archive (task 15.2)

1.3's comparison again at the bench's head: the requirement "Extras select
independent Machinome products" of `openspec/specs/framework-identity/spec.md`
is byte for byte the one 1.3 read (`diff` empty), so the MODIFIED copy
stands.

```
$ env -C <bench>/packages/machinome openspec archive join-movie -y
Proposal warnings in proposal.md (non-blocking):
  ⚠ Why section should not exceed 1000 characters
  ⚠ Consider splitting changes with more than 10 deltas
Task status: 60/69 tasks
Warning: 9 incomplete task(s) found. Continuing due to --yes flag.
...
Totals: + 11, ~ 1, - 0, → 0
Specs updated successfully.
Change 'join-movie' archived as '2026-10-12-join-movie'.
```

(`<scratch>/15.2-archive.out`; the nine open tasks were 13.6, 13.9, 14.1 to
14.3 and 15.1 to 15.4.) `cli`, `cli-startup-cost`,
`framework-contributor-guidance`, `user-documentation` and `vet` + 1 each,
`framework-identity` + 1 and ~ 1, `movie-distribution` created with five
requirements, probe 17's totals. Scenarios before and after: `framework-identity`
35 to 40, `cli` 116 to 119, `cli-startup-cost` 41 to 43,
`user-documentation` 91 to 93, `framework-contributor-guidance` 12 to 13,
`vet` 67 to 69, `movie-distribution` 11; none lost. The created spec's
Purpose is written in place of the CLI's placeholder.

```
$ env -C <bench>/packages/machinome openspec validate --specs --strict
...
Totals: 48 passed, 0 failed (48 items)
```

(`<scratch>/15.2-validate.out`, exit 0.) No active change remains.

### 15.3 The plan's progress (task 15.3)

`workflow/ongoing/joins-0.9.md`, "Progress": entry 5, `join-movie`, after
the viewer's and the skills' entries, with the branch, the planning and
merge commits, the two fetched branches, the ADR, the suite, the package's
two counts, the manual, `check-dist`, the lock, the projects' move, the
originating check and the sweep's placeholder.

The tests that read these records, on the closed tree (no other pytest
running but the orchestrator's sweep, which builds nothing of the suite's):
`tests/test_node_root_exports_nothing.py tests/test_repository_layout.py
tests/test_docs_structure.py tests/test_release_records.py` from the
framework's directory, 112 passed, 2518 subtests passed
(`<scratch>/15-records.out`); `D/tests/test_repository.py`, 17 passed.

### 15.4 This file (task 15.4)

Complete but for the sweep's numbers, which the orchestrator writes. The
implementation commit is the orchestrator's, never amending the planning
or the merge commit; nothing pushed.
