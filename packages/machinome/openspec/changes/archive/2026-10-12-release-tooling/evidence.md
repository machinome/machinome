# Evidence: `release-tooling`

The third cycle of the road to Machinome 0.9.0
(`workflow/ongoing/release-0.9.md` at the repository root), a cycle of the
joins campaign (`workflow/ongoing/joins-0.9.md`). Worktree
`machinome/WTs/v0.9-joins-release-tooling`, branch
`v0.9-joins-release-tooling`. Planning commit afef5c96, ratified by the
orchestrator on 12 October 2026 with every recommendation of its Open
Questions accepted, on the line's head 462f7119, which holds the movie's
join (`join-movie`) and the correction 675edac4 of `scripts/check-dist`'s
brace. Applied on 12 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), GNU Make 4.3, Node
24.11.1 and npm 11.6.2, the OpenSpec CLI 1.6.0. Every command ran with
`env -C <dir>` or absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-release-tooling`,
`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C7-apply/`
and `<propose>` the proposer's `.../scratchpad/C7-propose/`. The core's
tests ran from `<bench>/packages/machinome` on the bench venv
(`<bench>/.venv/bin/python -m pytest -q -p no:cacheprovider ...`), one
pytest process at a time. Logs are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -3
afef5c96 Propose release-tooling: one Makefile declares the set's steps, check-dist keeps a release's archives
462f7119 Integrate join-movie: the videomaker as machinome.movie, the command machinome movie
d8882c74 Implement join-movie: the videomaker as the distribution machinome-movie, imported as machinome.movie, run as machinome movie
$ git -C <bench> status --short | wc -l
0
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
$ git -C <bench> ls-files | wc -l
5342
```

`git status --short --ignored` showed `.env`, `.venv/`, the root's
`node_modules/`, the widget's `dist/` and `node_modules/`, the members'
`*.egg-info/` and `__pycache__/` leavings and the viewer's `tests/_shots/`,
all ignored.

### 1.2 The movie has landed (task 1.2)

```
$ ls <bench>/packages/machinome-movie/machinome/movie/js/package.json \
     <bench>/packages/machinome-movie/machinome/movie/js/package-lock.json
.../js/package-lock.json
.../js/package.json
```

The root `package.json`'s `workspaces`: the widget,
`packages/machinome-movie/machinome/movie/js`. `ls <bench>/packages`:
sixteen directories (the core, two engines, nine node packages, mechanics,
movie, skills, viewer). The Makefile therefore takes every line of design.md
Decision 1 that names the movie (`machinome-movie` in `PACKAGES` and
`TESTED`, `MOVIE_JS`, `MEMBER_LOCKS`, `test-machinome-movie`), and the counts
below are sixteen members and 32 archives.

### 1.3 The bench venv and the line's last suite count (task 1.3)

The orchestrator resynced the bench venv from the lock before this
application (`<...>/scratchpad/C7-join/uv-sync-2.log`, ending `exit 0`):
sixteen `__editable__` `.pth` files, `machinome_movie-0.8.1` among them,
`machinome_mechanics-0.1.0` the one of its own version.

The line's last suite count, from the latest archived evidence on the line
(`openspec/changes/archive/2026-10-12-join-movie/evidence.md`, 13.1, not
rerun here): 4894 passed, 9 skipped, 8422 subtests passed, in 972.91 s.

### 1.4 The lint base (task 1.4)

```
$ env -C <bench>/packages/machinome sh -c \
    '<bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-*/machinome | wc -l'
1805
$ (same paths) <bench>/.venv/bin/black --check ...    # exit 123
562 files would be reformatted, 198 files would be left unchanged, 1 file would fail to reformat.
```

flake8's exit 1; 1805 lines, the movie's modules included (the movie's own
evidence, 13.3, counted 1805 with 290 of them its modules). The file black
fails to parse is the deliberate fixture
`tests/vet_projects/unparseable/sim/broken.py` (design.md probe 6). Both are
the counts CI tolerates (`continue-on-error`).

### 1.5 The root's npm install is the bench's (task 1.5)

```
$ test -d <bench>/node_modules -a ! -L <bench>/node_modules && echo NM-DIR-OK
NM-DIR-OK
```

## 2. Red first

### 2.1 `tests/test_check_dist.py` (task 2.1)

New: the script loaded from the checkout with
`importlib.machinery.SourceFileLoader`, six tests, building nothing.

On the bench (`<scratch>/2.1-red.out`): 5 failed, 1 passed in 0.21 s.
`test_the_script_parses` is green at once: the brace of design.md probe 1 is
on the line already (675edac4, Open Questions 12, the orchestrator's
correction before this change's planning commit). The reds:

| Test | Red reason |
|---|---|
| `test_out_refuses_a_folder_that_is_not_empty` | `TypeError: main() takes 0 positional arguments but 1 was given` |
| `test_out_refuses_a_file` | the same |
| `test_nothing_is_kept_when_a_check_fails` | the same |
| `test_keep_copies_every_archive_flat` | `AttributeError: module 'check_dist' has no attribute 'keep'` |
| `test_keep_refuses_two_archives_of_one_name` | the same |

The red the design expected at 40087800 (probe 1), shown on a scratch tree
`<scratch>/base-40087800/` holding `git show 40087800:scripts/check-dist`,
the two files the script reads at import (the mechanics manifest, the
widget's `package.json`) and this test module (`<scratch>/2.1-red-at-40087800.out`):
6 failed in 0.07 s, each `SyntaxError: '{' was never closed`.

### 2.2 `tests/test_repository_layout.py` (task 2.2)

Edited: the module docstring names the root `Makefile` (change
`release-tooling`, ADR-192); `Makefile` out of `FRAMEWORK_ENTRIES`; the
Makefile-reading helpers of probe 8 (`makefile()`, `make_variable()`,
`make_expanded()`, `make_rules()`, `make_targets()`, the `RULE` pattern,
`MAKEFILE`, `TARGETS`); `TheMakefileTest`, seven tests; `/.docs-venv/` in
`test_the_root_ignores_the_benches_and_the_venv`; the CI tests in their new
form: `test_every_job_calls_the_makefile` in place of
`test_every_job_runs_from_the_package_directory`,
`test_the_test_job_runs_each_product_s_tests` reading `TESTED`,
`test_the_dist_job_checks_the_distributions` reading `make check`,
`test_the_test_job_builds_the_bundles_and_chromium_before_the_tests` in
place of `test_the_test_job_builds_and_tests_the_widget_before_the_suite`,
`test_the_dist_job_sets_up_node_before_checking` reading `make check`. The
movie's `test_the_test_job_runs_the_movie_s_node_projects_without_a_browser`
(landed by `join-movie` after the design was written) keeps its name and
reads the Makefile's `test-machinome-movie` rule (its Python tests, then
`npm test --workspace $(MOVIE_JS) -- --project pure --project stage`) and
the test job's `make widget` before `make test`.

Run (`<scratch>/2.2-red.out`): 19 failed, 41 passed, 298 subtests passed in
4.31 s. The reds:

- `TheMakefileTest`, all seven: `test_the_makefile_is_the_repository_s`
  "`<bench>/Makefile` is missing"; the six others
  `FileNotFoundError: ... '<bench>/Makefile'`.
- `test_the_root_ignores_the_benches_and_the_venv`, subtest
  `/.docs-venv/`: "'/.docs-venv/' not found".
- `test_every_job_calls_the_makefile`, six subtests, each naming the command
  its job spells: "the lint job spells black in its step 'Black'"; "the test
  job spells npm in its step 'Build and test the widget'"; "the
  browser-snapshot job spells npm in its step 'Build the viewer and install
  Chromium'"; "the docs job spells pip install in its step 'Install docs
  requirements'"; "the dist job spells twine in its step 'Install build and
  twine'"; "the build job spells pip install in its step 'Install
  packaging'".
- `test_the_test_job_runs_each_product_s_tests`: "'make test' not found in
  []".
- `test_the_dist_job_checks_the_distributions`: "'make check' not found in
  []".
- `test_the_dist_job_sets_up_node_before_checking`: "the job has no step
  that runs make check".
- `test_the_test_job_builds_the_bundles_and_chromium_before_the_tests`: "the
  job has no step that runs make widget".
- `test_the_test_job_runs_the_movie_s_node_projects_without_a_browser`:
  "ValueError: 'make widget' is not in list".

Green, as expected: every other test, `test_the_framework_s_entries_are_not`
among them (`Makefile` left its list while the framework's file is still
there; `test_the_makefile_is_the_repository_s` is the one that names it).

### 2.3 `tests/test_docs_exports.py` (task 2.3)

`ActionsDocsJobBuildsNothingTest` reads the docs job and the root Makefile's
`docs` recipe (`docs_recipe()`): no forbidden step in either and no Node,
apt or submodule in the recipe (`test_no_forbidden_step`), the job's one
command `make docs` (`test_the_job_runs_the_makefile_s_docs_target`, new),
the recipe's one install `-r packages/machinome/docs/requirements.txt`
(`test_installs_the_requirements_alone`), its Sphinx with `-W`
(`test_builds_with_warnings_as_errors`). The module docstring names the
target.

Run (`<scratch>/2.3-red.out`): 4 failed, 15 passed, 10 subtests passed in
0.78 s; each of the class's four tests `FileNotFoundError: ...
'<bench>/Makefile'` (the job's own red, after the file exists, is in 4.3).

### 2.4 `tests/test_release_records.py` (task 2.4)

`released_version()` reads `current_version` of the root's
`.bumpversion.cfg` (`configparser`, section `bumpversion`, through a new
`bumpversion()`); `test_every_version_file_agrees_with_pyproject` holds the
core's `pyproject.toml` (`version = "<v>"`) in place of the cfg; a new
`test_the_bump_neither_commits_nor_tags`; the docstring says the cfg states
the version once.

Run on the bench (`<scratch>/2.4-red.out`): 1 failed, 16 passed, 171 subtests
passed; the red `test_the_bump_neither_commits_nor_tags`: "Lists differ:
['current_version', 'commit', 'tag'] != ['current_version']".

On a scratch copy of the tracked tree (`<scratch>/records-copy/`, `git
ls-files -z | tar --null -T - -cf - | tar -x`) whose cfg reads
`current_version = 0.9.0` and whose manifests read 0.8.1, `-k
test_every_version_file_agrees_with_pyproject`:

- this change's module (`<scratch>/2.4-copy-now.out`): 4 subtests failed,
  naming `pyproject.toml` ('version = "0.9.0"' not found), with
  `machinome/__init__.py`, `docs/conf.py` and `machinome/vet/universe.toml`,
  each a copy left behind;
- the base's module, `git show HEAD:packages/machinome/tests/test_release_records.py`
  beside it (`<scratch>/2.4-copy-base.out`): 1 subtest failed, naming
  `.bumpversion.cfg` ("'current_version = 0.8.1' not found"), the three
  others passing: at the base the cfg was the copy and the manifest the
  source.

### 2.5 The kernel extras' CI test (task 2.5)

`-k test_ci_syncs_the_locked_workspace` of `tests/test_kernel_extras.py`
before the CI's edit (`<scratch>/2.5-before.out`): 1 passed, 3 subtests
passed.

## 3. `scripts/check-dist`

### 3.1 The brace (task 3.1)

Nothing to do on the bench: the line `    },` that closes the viewer's row is
on the line since 675edac4 (`python3 -c "import ast; ast.parse(...)"` of
the bench's script parses), and `test_the_script_parses` was green at 2.1;
the `--out` tests were red there with the reasons this task expected
(`TypeError: main() takes 0 positional arguments`, `AttributeError: ...
'keep'`).

### 3.2 `--out` (task 3.2)

`import argparse`; `keep_out(out)`; `keep(out, scratch, wheels)`;
`main(argv=None)` parsing `--out DIR` (the docstring's first line its
description), `keep_out` before the temporary directory, `keep` after the
last smoke's commands inside it; the refusal "`<DIR>` exists and is not an
empty folder; the archives of a release are kept in a new one"; the
docstring's last paragraph. `keep` names each archive built twice in its
refusal ("two members build an archive of one name: <names>"), where the
proposer's prototype listed every name.

```
$ git -C <bench> diff --stat scripts/check-dist
 scripts/check-dist | 46 +++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 45 insertions(+), 1 deletion(-)
```

The one line removed is `def main():`; no row of `SMOKES` changed.
`env -C <bench> <bench>/.venv/bin/flake8 --max-line-length=89
scripts/check-dist | wc -l`: 0. `tests/test_check_dist.py`: 6 passed, 4
subtests passed in 0.13 s, each test under 0.005 s.

### 3.3 By hand (task 3.3)

```
$ <bench>/.venv/bin/python <bench>/scripts/check-dist --help
usage: check-dist [-h] [--out DIR]

Build, check and smoke every distribution of the repository; upload nothing.

options:
  -h, --help  show this help message and exit
  --out DIR   keep the archives, once every one is built, checked and smoked,
              flat in DIR, a new or empty folder
$ <bench>/.venv/bin/python <bench>/scripts/check-dist --out <scratch>/3.3-out   # holds one file
check-dist failed: <scratch>/3.3-out exists and is not an empty folder; the archives of a release are kept in a new one
Nothing uploaded.
```

Exit 1 in 0.08 s; the folder still holds its one file.

## 4. The Makefile

### 4.1 The file (task 4.1)

`<bench>/Makefile` is design.md Decision 1's block verbatim, the movie's
lines included (1.2): the block extracted from design.md with `awk` into
`<scratch>/Makefile.decision1` (165 lines, 76 holding a tab) equals the
proposer's `<propose>/Makefile.design` (`diff`: none), and was copied to the
bench. No line was corrected. `git -C <bench> rm packages/machinome/Makefile`
(the cookiecutter file whose `release` target ran `twine upload dist/*`).

### 4.2 The configuration and the ignore (task 4.2)

`.bumpversion.cfg`: the lines `commit = True` and `tag = True` removed,
nothing else (`git diff`: two deletions). The root `.gitignore`:
`/.docs-venv/` after `/dist/`.

### 4.3 The gates with the file (task 4.3)

`tests/test_repository_layout.py tests/test_release_records.py
tests/test_docs_exports.py` (`<scratch>/4.3.out`): 12 failed, 83 passed, 610
subtests passed in 6.18 s. Green now: `TheMakefileTest` (seven),
`test_the_root_ignores_the_benches_and_the_venv`, every release-records
test (`test_the_bump_neither_commits_nor_tags` included), and the docs
class's `test_no_forbidden_step`, `test_installs_the_requirements_alone`,
`test_builds_with_warnings_as_errors` (they read the recipe). Still red,
the CI's (group 5): the six subtests of `test_every_job_calls_the_makefile`
and the five other CI tests with the reasons of 2.2, and
`test_the_job_runs_the_makefile_s_docs_target`: "Lists differ: ['pip
install -r docs/requirements.txt', 'python -m sphinx -b html -W docs
docs/_build'] != ['make docs']", the docs job's red once the file exists
(task 2.3).

### 4.4 The gate's reds on planted mutations (task 4.4)

Each planted in the bench's Makefile, `-k TheMakefileTest` of the layout
module run (the CI tests being red until group 5), the plant removed by
copying `<scratch>/Makefile.decision1` back, and `diff` of the two: none.
Logs `<scratch>/4.4-<name>.out`.

| Plant | Fails | Naming |
|---|---|---|
| `machinome-node-stl` dropped from `PACKAGES` | `test_the_package_list_is_the_package_directories` | subtest `package='machinome-node-stl'`: "'machinome-node-stl' not found in [...]: the Makefile's PACKAGES omits machinome-node-stl" |
| `machinome-skills` dropped from `TESTED` | `test_the_tested_list_is_the_core_and_the_products` | "the Makefile's TESTED omits machinome-skills" |
| `upload: dist ## ...` | `test_upload_is_reached_by_no_other_target` | "Lists differ: ['dist'] != [] : the rule upload has a prerequisite" |
| `.venv` added to `CLEAN` | `test_clean_removes_only_what_git_ignores` | subtest `path='.venv'`: "make clean removes .venv" |
| a target `sweep: ## Run the universe sweep` (recipe `scripts/load-projects`) | `test_the_targets_are_the_decided_ones` | subtest `target='sweep'`: "the Makefile has a target sweep with a help line" |

### 4.5 The targets that refuse or print (task 4.5)

From the bench root, uv and npm on the PATH (`<scratch>/4.5.out`):

```
$ make 
  make help     List the targets
  make version  Print the set's version, current_version of .bumpversion.cfg
  make bump     Move the set to VERSION=X.Y.Z: every copy and every lock; no commit, no tag
  make sync     Install the workspace from its locks: every package editable, the npm members, Chromium
  make test     Run the tests of PKG=<package>, or of every package with tests, stopping at the first failure
  make lint     Check the style of every package's sources with black and flake8, as CI does
  make docs     Build the manual with warnings as errors, from docs/requirements.txt alone, into packages/machinome/docs/_build/html
  make widget   Install the npm workspace from its lock and build its bundles
  make dist     Build, check and smoke every archive of the commit into dist/vX.Y.Z; upload nothing
  make upload   Upload dist/vX.Y.Z to PyPI with twine; run by no other target
  make check    Build, check and smoke every archive from the tree and from a clean copy of its tracked files; keep nothing
  make clean    Remove what the targets wrote: the docs venv, the manual's build, build scratch, the bundle
exit 0
$ make version
0.8.1
exit 0
$ make test PKG=machinome-engine-brep
make test: machinome-engine-brep keeps no tests of its own; the core's suite tests it: make test PKG=machinome
make: *** [Makefile:123: test-machinome-engine-brep] Error 2
exit 2
$ make test PKG=nope
make test: nope is not a package; the packages are machinome machinome-engine-brep machinome-engine-mesh machinome-mechanics machinome-movie machinome-node-build123d machinome-node-cadquery machinome-node-freecad machinome-node-jscad machinome-node-molejo machinome-node-openscad machinome-node-solid2 machinome-node-step machinome-node-stl machinome-skills machinome-viewer
make: *** [Makefile:126: test-nope] Error 2
exit 2
$ make bump
make bump: name the version: make bump VERSION=X.Y.Z
make: *** [Makefile:79: bump] Error 2
exit 2
$ make bump VERSION=0.8.1
make bump: the set is at 0.8.1 already
make: *** [Makefile:80: bump] Error 2
exit 2
$ make -n upload
test -n "$(ls -A dist/v0.8.1 2>/dev/null)" || { echo 'make upload: no archives in dist/v0.8.1; make dist builds them' >&2; exit 1; }
<bench>/.venv/bin/python -m twine upload dist/v0.8.1/*
exit 0
```

`make` prints twelve lines and runs nothing else; `make upload` was never
run.

## 5. CI on the targets

### 5.1 The workflow (task 5.1)

`.github/workflows/python-app.yml` as design.md Decision 11: no job keeps
`defaults.run.working-directory`; every setup step kept (checkout, the apt
action for OpenSCAD, `astral-sh/setup-uv` 0.11.8, "Sync the workspace" with
`uv sync --locked --python 3.12` and its `GITHUB_PATH` line at
`working-directory: .`, `actions/setup-node` 22, `playwright install
--with-deps chromium`); the commands are the targets: `lint` "Lint" `make
lint` (`continue-on-error`, the two steps one); `test` "Build the bundles"
`make widget`, "Install Chromium", "Run the tests" `make test` (the movie's
two steps, added by `join-movie`, go with the others: its rule runs them);
`browser-snapshot` `make widget`, Chromium, the end-to-end step unchanged
with `working-directory: packages/machinome` on the step; `docs` checkout,
setup-uv (its cache keyed on the docs requirements), "Build the manual (fail
on warnings)" `make docs`, no Node, no workspace; `dist` (needs `test`,
`docs`) setup-uv, the sync, Node, `make check`; `build` (on a tag, needs
`test`) setup-uv, the sync, Node, "The tag names the set's version" `test
"$GITHUB_REF_NAME" = "v$(make -s version)"`, `make dist`, `gh release
create "$GITHUB_REF_NAME" "dist/$GITHUB_REF_NAME"/* --title
"${GITHUB_REF_NAME#v}"` with the token; the `packaging` step and
`MACHINOME_VERSION` gone. The workflow's header comment says every job calls
the Makefile.

`env -C <bench> <bench>/.venv/bin/python -c "import yaml;
yaml.safe_load(open('.github/workflows/python-app.yml'))"`: parses. Nothing
of the workflow can run on this machine.

### 5.2 The gates (task 5.2)

`tests/test_repository_layout.py tests/test_docs_exports.py
tests/test_kernel_extras.py` (`<scratch>/5.2.out`): 90 passed, 524 subtests
passed in 6.54 s. `-k test_ci_syncs_the_locked_workspace` after the edit: 1
passed, 3 subtests passed (task 2.5's "after").

## 6. The records

### 6.1 `CONTRIBUTING.rst` (task 6.1)

"Development environment": the requirements paragraph says `npm ci` at the
root is what `make sync` and `make widget` run, Chromium's install what
`make sync` runs, and that the steps are the root Makefile's targets, `make`
alone listing them, uv and npm found on the PATH and the workspace's
commands in `.venv`; the install with uv is `make sync` (what it runs, in one
sentence); the install without uv is kept (the layout test's pip spelling);
the bundles are `make widget`. "Running tests": `make test`, `make test
PKG=machinome`, `make lint`, `make docs`; pytest of one file from
`packages/machinome`, where the `openspec` command runs; the extension
packages tested by the core's suite; each product's paragraph names `make
test PKG=machinome-mechanics`, `-viewer`, `-skills` and `-movie` and what
each runs, the movie's whole Node suite kept as `npm test --workspace
packages/machinome-movie/machinome/movie/js` from the root (design.md
Decision 5); `make check` before a pull request touching packaging; `make
clean`. The browser-capture note says `make widget` and the directory.
"Pull requests" step 4 already said `make lint` and `make test`, unchanged.
"Deploying" rewritten: `make bump VERSION=X.Y.Z`, the records and the
commit, `make dist` into `dist/vX.Y.Z`, the tag and the push, `make upload`.
The guide names no `requirements.txt` and no `tox` (`grep`: none).
`docutils.core.publish_doctree` of the file: no message at level 2 or above.
The layout gate's guide and link tests (`-k "guide or Links"`): 5 passed, 71
subtests passed, the movie's `test_the_guide_runs_the_movie_s_two_suites`
among them, its five spellings kept.

### 6.2 `HISTORY.rst` (task 6.2)

The `Unreleased` bullet of design.md Decision 13, verbatim, after the
movie's bullet. `tests/test_release_records.py`: 17 passed, 171 subtests
passed.

### 6.3 `docs/architecture.md` (task 6.3)

The "Repository layout" row of the Map: its code names `Makefile` beside
`.bumpversion.cfg` and `scripts/check-dist`, its specs `framework-identity`,
`release-tooling`, its ADRs 182, 183, 192.

### 6.4 ADR-192 (task 6.4)

`docs/adrs/BUILD/ADR-192-the-repository-s-steps-are-the-targets-of-one-makefile.md`,
Status Proposed: the context (the 0.8.1 release by hand, the three
spellings, the twenty files; the pilot's decisions 2 and 10; probes 1, 2, 3
and 9), four options weighed (one Makefile, chosen; another task runner;
scripts under `scripts/`; the steps left in the guide), the decision (the
targets and the package lists, the version declared once and its bump, the
archives proved and uploaded, CI on the targets), consequences, references;
amends 182 and 183, cites 187 and 188. Its index entry under BUILD after
ADR-191, **Proposed**. ADR-182's and ADR-183's status and index lines are
group 8's (task 8.1).

### 6.5 The gates (task 6.5)

`tests/test_repository_layout.py tests/test_docs_exports.py
tests/test_release_records.py tests/test_check_dist.py
tests/test_node_root_exports_nothing.py` (the last, the one module reading
`docs/adrs/`) (`<scratch>/6.5.out`): 117 passed, 730 subtests passed in
7.00 s.

## 7. Validation

### 7.1 `make sync` (task 7.1)

After 1.5's check, from the bench root (`<scratch>/7.1-sync.out`): exit 0,
4.4 s wall. uv: "Resolved 198 packages", "Checked 189 packages" (the venv
already in sync with the lock: nothing installed or removed). npm: "added 144
packages in 3s", with four `EBADENGINE` warnings (`@asamuzakjp/css-color`,
`@asamuzakjp/dom-selector`, `jsdom`, `w3c-xmlserializer` ask for Node
`^24.15.0`; the machine's is 24.11.1). `playwright install chromium`
printed nothing: Chromium build 1243 is in `~/.cache/ms-playwright`,
nothing downloaded. `git -C <bench> status --short` afterwards: this
change's files alone (the list of 7.9), nothing new.

### 7.2 `make test` (task 7.2)

No other bench's pytest ran (`pgrep -af "WTs/v0.9-joins-.*[p]ytest"`: none).
From the bench root, `PYTEST_ADDOPTS="-rs" make test`, one make process
running the suites one after another (`<scratch>/7.2-test.out`): exit 0,
21 min 29 s wall (a first start without `PYTEST_ADDOPTS`, to have the skip
reasons listed, was stopped during the core's suite and restarted; no
process of it was left). Per package of `TESTED`, in its order:

| Package | What ran | Result |
|---|---|---|
| `machinome` | the widget's bundle (0.12 s), then pytest from `packages/machinome` | 4909 passed, 9 skipped, 911.13 s |
| `machinome-mechanics` | pytest from its directory | 204 passed, 1.93 s |
| `machinome-skills` | pytest from its directory | 47 passed, 2.35 s |
| `machinome-viewer` | the widget's typecheck, its tests (65 files passed and 1 skipped, 1715 tests passed and 2 skipped, 61.47 s), its bundle, then pytest from its directory | 252 passed, 2 skipped, 257.60 s |
| `machinome-movie` | pytest from its directory, then `npm test --workspace .../movie/js -- --project pure --project stage` | 322 passed, 39.07 s; Node 31 files, 329 tests passed, 4.95 s |

No failure. The core's nine skips are the line's nine (1.3): four FreeCAD
(`MACHINOME_FREECAD_ROOT` not set), the browser photograph
(`MACHINOME_WEB_SNAPSHOT_E2E`), networkx, the jscad CLI, the two vendor
STEP files. The viewer's two: `tests/test_curta_drawing.py` "the Curta's own
builds are not at <...>/WTs/projects/Calculators/Curta-Type-I-3x/_build",
the path read relative to a worktree (design.md probe 4 counted 250 passed,
2 skipped before the line's later viewer tests).

The core's count against the line's last (1.3, 4894 passed, 9 skipped):
+15, each a test this change adds: `tests/test_check_dist.py` six;
`TheMakefileTest` seven; `ActionsDocsJobBuildsNothingTest`'s
`test_the_job_runs_the_makefile_s_docs_target`;
`VersionFilesTest.test_the_bump_neither_commits_nor_tags`. The CI tests
renamed (`test_every_job_calls_the_makefile`,
`test_the_test_job_builds_the_bundles_and_chromium_before_the_tests`)
replace one test each.

### 7.3 `make lint` (task 7.3)

From the bench root (`<scratch>/7.3-lint.out`): 18.1 s, both tools run,
make's exit 2 (the recipe's exit 1), as CI's `continue-on-error` tolerates.
flake8: 1805 lines, the count of 1.4 (`diff` of the two reports, line and
column dropped: none; a first run counted 1806, the one more an E501 in this
change's own docstring of `tests/test_release_records.py`, rewrapped). black:
563 files would be reformatted, 198 left unchanged, 1 failing to parse
(the deliberate fixture): 1.4's 562 and `tests/test_check_dist.py`, the new
module, written in the repository's single-quoted style as the 562 are. The
movie's modules were in 1.4's counts already.

### 7.4 `make docs` (task 7.4)

From the bench root (`<scratch>/7.4-docs-1.out`, `-2.out`). The first run:
`uv venv --python 3.12 .docs-venv` (CPython 3.12.3), `uv pip install`
"Resolved 39 packages", "Installed 39 packages" (Sphinx 9.1.0, the
published `machinome-viewer` 0.8.0), Sphinx `-b html -W -E`, "build
succeeded.", exit 0, 13.2 s. The second: the venv kept, "Checked 3
packages", "build succeeded.", exit 0, 9.1 s. 89 HTML files under
`packages/machinome/docs/_build/html`. `git status --short` lists neither
`.docs-venv/` nor the build.

### 7.5 `make check` (task 7.5)

No other bench's pytest ran. From the bench root (`<scratch>/7.5-check.out`):
exit 0, 7 min 15 s wall, both runs "Every distribution built, checked,
installed and smoked; nothing uploaded.", each over the sixteen members.

| Run | Archives (`<name>: N entries` lines) | `twine check` PASSED | Core sdist | Core wheel |
|---|---|---|---|---|
| the tree | 32 | 32 | 1146 entries | 114 entries |
| the clean copy of the tracked files (`/tmp/machinome-check-If30sU`) | 32 | 32 | 1083 entries | 114 entries |

The tree's core sdist holds 63 entries more than the copy's: the checkout's
ignored build directories, which 7.4's `make docs` and 7.2's suite had just
written, carried by the core's `MANIFEST.in` (design.md probe 9; the
archives were not kept, so the entries were not listed). That is the case
`make dist` builds from a copy of the commit for. Afterwards `ls -d
/tmp/machinome-check-*`: none (`TMPDIR` unset).

### 7.6 `make dist` on the bench (task 7.6)

```
make dist: the tree differs from its commit; commit or remove:
 M .bumpversion.cfg
 M .github/workflows/python-app.yml
 M .gitignore
 M CONTRIBUTING.rst
 M HISTORY.rst
D  packages/machinome/Makefile
 M packages/machinome/docs/adrs/README.md
 M packages/machinome/docs/architecture.md
 M packages/machinome/openspec/changes/release-tooling/tasks.md
 M packages/machinome/tests/test_docs_exports.py
 M packages/machinome/tests/test_release_records.py
 M packages/machinome/tests/test_repository_layout.py
 M scripts/check-dist
?? Makefile
?? packages/machinome/docs/adrs/BUILD/ADR-192-the-repository-s-steps-are-the-targets-of-one-makefile.md
?? packages/machinome/openspec/changes/release-tooling/evidence.md
?? packages/machinome/tests/test_check_dist.py
make: *** [Makefile:145: dist] Error 1
exit 2
```

Nothing built: no `<bench>/dist`, no `/tmp/machinome-dist-*`.

### 7.7 The bump on a copy (task 7.7)

`<scratch>/bump/`: the bench's tracked and new files (`git ls-files -z
--cached --others --exclude-standard | tar ...`) made a Git repository of one
commit (650db5a; the 34 tracked files the ignore rules match, the
framework's archived performance logs, stayed out of it, untracked and
ignored, and touch nothing the bump reads). `make sync` there
(`<scratch>/7.7-sync.out`): a new `.venv` ("Installed 189 packages"), "added
144 packages", exit 0, `git status --porcelain` empty.

On that copy with `README.md` changed: `make bump VERSION=0.9.0` refused,
"make bump: the tracked files have changes; commit them first: M
README.md", make's exit 2, nothing written; the change reverted.

Then `make bump VERSION=0.9.0` (`<scratch>/7.7-bump.out`): exit 0, 1.9 s.
The recipe ran bump2version (`--no-commit --no-tag --new-version 0.9.0
patch`), `npm install --package-lock-only` at the root ("up to date in
398ms") and in a temporary copy of the movie's `js` ("up to date in
286ms"), and `uv lock` (15 lines "Updated <member> v0.8.1 -> v0.9.0", every
member but the mechanics helpers), then `git diff --stat`: "25 files
changed, 79 insertions(+), 79 deletions(-)":

- design.md probe 3's twenty: `.bumpversion.cfg`, the fourteen manifests
  numbered with the set at probe 3 (the core's, the two engines', the nine
  node packages', the skills' and the viewer's, versions and pins), the
  core's `machinome/__init__.py`, `docs/conf.py` (`release`,
  `viewer_version`), `machinome/vet/universe.toml`, the viewer's
  `__init__.py` and its widget's `package.json`;
- the movie's tables: `packages/machinome-movie/pyproject.toml` (its version
  and its pins, 6 lines) and its `js/package.json`;
- the locks: the root's `package-lock.json` (4 lines, the widget's and the
  movie's entries), the movie's own `js/package-lock.json` (its two root
  entries), and `uv.lock` (30 lines).

`git log --oneline`: the one commit 650db5a; `git tag`: nothing; `make
version`: 0.9.0. The cfg's `[bumpversion]` section still holds
`current_version` alone. What still says 0.8.1 in a tracked `.toml`,
`.json`, `.py` or `.cfg` outside the archived changes: `context7.json` (2)
the core's identity test (1) and the viewer's documentation test (4), the
release cycle's records as probe 3 found them, and this change's
`tests/test_check_dist.py` (20), whose archive names are fixtures. Nothing was written in the bench.

### 7.8 The originating check, a dry release rehearsal (task 7.8)

`<scratch>/rehearsal/`: the bench's tracked and new files copied as in 7.7
and made a Git repository of one commit, cb24ea9, holding 5345 files (the
bench's tracked set with this change's files; the 34 tracked files the
ignore rules match added with `git add -f`, as a clone has them). No other
bench's pytest ran. Then, from the copy's root, `PYTEST_ADDOPTS="-rs" sh -c
'make sync && make test PKG=machinome && make docs && make dist'`
(`<scratch>/7.8-rehearsal.out`), 10 min 2 s:

- `make sync`: "Resolved 198 packages", "Checked 189 packages" (the copy's
  venv of a first sync, "Installed 189 packages", `<scratch>/7.8-sync.out`),
  "added 144 packages", Chromium cached.
- `make test PKG=machinome`: the bundle, then 4909 passed, 9 skipped (the
  nine of 7.2) in 583.70 s.
- `make docs`: a new `.docs-venv` ("Installed 39 packages"), "build
  succeeded.".
- `make dist`: **refused**, exit 2:

  ```
  make dist: the tree differs from its commit; commit or remove:
  ?? packages/machinome/_build.lock
  ```

  The core's suite, run from `packages/machinome`, leaves the empty file
  `packages/machinome/_build.lock`: the lock `project_build_lock()`
  (`machinome/core/builder.py`) takes beside the default build directory
  `_build` of the process's directory. No `.gitignore` of the repository
  names it (the framework's ignores `tests/_build*.lock`, `tests/_build/`,
  `tests/_build_*/` and `docs/_build/`); on the bench it is ignored only by
  the primary checkout's own `.git/info/exclude` (`_build*`), which a clone
  does not carry (`git -C <bench> check-ignore -v
  packages/machinome/_build.lock`: `.../machinome/.git/info/exclude:7:_build*`).
  The guard did what Decision 7 asks of it, naming the file; the chain the
  design's Decision 15 names does not reach `make dist` on a fresh clone
  after the suite. Not fixed here: see the report.

The rehearsal continued past it by hand: the stray lock removed from the
copy (`git status --porcelain` then empty, the ignored `docs/_build/html`,
`tests/_build_meta/` and the tests' locks still there), then `make dist`
(`<scratch>/7.8-dist.out`): "$ scripts/check-dist --out dist/v0.8.1, in a
copy of the commit cb24ea9", "32 archives kept in .../rehearsal/dist/v0.8.1",
"Every distribution built, checked, installed and smoked; nothing
uploaded.", exit 0, 3 min 28 s. The folder (`<scratch>/7.8-archives.txt`),
32 archives flat: the sdist and the wheel of `machinome` 0.8.1, the two
engines, the nine node packages, `machinome_movie`, `machinome_skills` and
`machinome_viewer` at 0.8.1, and `machinome_mechanics` 0.1.0.

- `twine check --strict dist/v0.8.1/*` (the copy's venv,
  `<scratch>/7.8-twine.out`): 32 PASSED, exit 0.
- `tar tzf` of each sdist and `unzip -l` of each wheel, entries under a
  `_build` directory: 0, the manual's build and the suite's
  `tests/_build_meta/` being in the checkout. The core's sdist: 1084 entries
  (7.5's clean copy built 1083 from the bench's tracked files alone, before
  this change's three new files were added to the index; the tree's, with
  the ignored builds, 1146).
- `make dist` again: check-dist's refusal, "<...>/rehearsal/dist/v0.8.1
  exists and is not an empty folder; the archives of a release are kept in a
  new one", make's exit 2 (`<scratch>/7.8-after.out`).
- `make -n upload`: prints the refusal's test and `<copy>/.venv/bin/python -m
  twine upload dist/v0.8.1/*`, runs nothing. `make upload` was never run.
- `make clean`: `rm -rf .docs-venv packages/machinome/docs/_build
  packages/*/build packages/machinome-viewer/machinome/viewer/web/widget/dist`,
  exit 0; the docs venv, the manual's build and the widget's bundle gone, no
  `packages/*/build` left; `.venv/`, `node_modules/` and `dist/v0.8.1/`
  still there; `git status --porcelain` empty. No `/tmp/machinome-dist-*`
  left.

#### The ignore of the builder's lock: the orchestrator's decision of 12 October 2026

Reviewing the checkpoint, the orchestrator decided on 12 October 2026 that
`packages/machinome/.gitignore` ignores the lock: `/_build.lock` beside its
`tests/_build*.lock` line, with one comment line saying that the builder's
lock lands beside the package directory when the suite runs the command
from there, and that a clone ignores it as the primary checkout's local
exclude does (the guard of `make dist` otherwise refuses after `make
test`). Which test leaves the lock was not identified.

Proved on the rehearsal copy without building again: the bench's
`packages/machinome/.gitignore` copied there and committed (e03a75a on
cb24ea9), then `touch packages/machinome/_build.lock`: `git status
--porcelain` empty; `git check-ignore -v packages/machinome/_build.lock`:
`packages/machinome/.gitignore:124:/_build.lock`; the guard's own command,
`test -z "$(git status --porcelain)"`, exit 0; `make -n dist`
(`<scratch>/8.0-dist-n.out`): exit 0, the recipe printed (the two guards,
the copy by `git archive HEAD`, `scripts/check-dist --out
<copy>/dist/v0.8.1`), nothing run.

### 7.9 Git (task 7.9)

The three new files added to the index (`git add`), nothing committed:

```
$ git -C <bench> status --short
 M .bumpversion.cfg
 M .github/workflows/python-app.yml
 M .gitignore
 M CONTRIBUTING.rst
 M HISTORY.rst
A  Makefile
D  packages/machinome/Makefile
A  packages/machinome/docs/adrs/BUILD/ADR-192-the-repository-s-steps-are-the-targets-of-one-makefile.md
 M packages/machinome/docs/adrs/README.md
 M packages/machinome/docs/architecture.md
 M packages/machinome/openspec/changes/release-tooling/tasks.md
A  packages/machinome/tests/test_check_dist.py
 M packages/machinome/tests/test_docs_exports.py
 M packages/machinome/tests/test_release_records.py
 M packages/machinome/tests/test_repository_layout.py
 M scripts/check-dist
?? packages/machinome/openspec/changes/release-tooling/evidence.md
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
```

The count of 1.1. After the checkpoint, the orchestrator's `.gitignore`
fix (7.8) adds ` M packages/machinome/.gitignore`, and group 8 the archive
(8.2). Ignored and untracked after the runs: `.docs-venv/`, the
manual's build, the members' `.pytest_cache/` (the targets run pytest with
its cache, where the cycles ran `-p no:cacheprovider`), the suite's builds
and locks, `packages/machinome/_build.lock` (by the primary checkout's
exclude at the checkpoint, by the framework's `.gitignore` since 7.8's fix).

### 7.10 OpenSpec (task 7.10)

`env -C <bench>/packages/machinome openspec validate release-tooling
--strict`: "Change 'release-tooling' is valid".

### 7.11 The checkpoint (task 7.11)

Stopped before any commit, for the orchestrator's review. What departed
from design.md and tasks.md:

- The rehearsal's chain stopped at `make dist`, refused on
  `packages/machinome/_build.lock`, which the core's suite leaves and no
  `.gitignore` of the repository named (7.8); finished by hand after removing
  the file. Left to the orchestrator at the checkpoint, who decided the
  ignore line (7.8, its decision of 12 October 2026).
- The movie's CI test `test_the_test_job_runs_the_movie_s_node_projects_without_a_browser`,
  landed after the design was written, keeps its name and reads the
  Makefile's movie rule (2.2); the test job's two movie steps went with the
  others (5.1).
- `scripts/check-dist`'s duplicate-name refusal names the archives built
  twice rather than every name (3.2).
- `test_the_script_parses` was green at once, the brace being on the line
  (3.1); the `SyntaxError` red was shown on 40087800's script in scratch.
- `make test` was run with `PYTEST_ADDOPTS="-rs"` to list the skips; its
  first start was stopped and restarted (7.2).
- `make lint`'s black count is 1.4's plus one, this change's new test module
  (7.3).

## 8. Records closing

The orchestrator reviewed the checkpoint on 12 October 2026, decided the
`.gitignore` fix (7.8), and ran its own validation on the bench (`make test
PKG=machinome`, `make docs`, `make check`), which ended by 17:34 UTC with no
red reported; this group's writes and test runs came after it.

### 8.1 ADR-192 accepted (task 8.1)

ADR-192's status Accepted, its change link the archive
(`openspec/changes/archive/2026-10-12-release-tooling/`); its index entry in
`docs/adrs/README.md` **Accepted**. ADR-182's status line gains "the
Makefile of the repository's steps at the root, amended 2026-10-12 by
ADR-192" and its index line "amended by 192"; ADR-183's "the version
declared once and moved by `make bump`, amended 2026-10-12 by ADR-192" and
"amended by 192". `docs/architecture.md` checked against it: the Map's
"Repository layout" row (6.3) names the `Makefile`, `release-tooling` and
192; its opening paragraph names the repository and ADR-182 only, and says
nothing ADR-192 changes.

### 8.2 The deltas against the baseline, and the archive (task 8.2)

Before the archive, each MODIFIED requirement of the deltas compared with
the baseline at the bench's head by requirement name (`<scratch>/8.2-*.diff`):
the differences are this change's edits alone (framework-identity 32 diff
lines, framework-contributor-guidance 70, user-documentation 25), every other
line and every scenario title equal; the baseline had not moved since the
planning commit.

```
$ env -C <bench>/packages/machinome openspec archive release-tooling -y
Proposal warnings in proposal.md (non-blocking):
  ⚠ Why section should not exceed 1000 characters
  ⚠ Consider splitting changes with more than 10 deltas
Task status: 39/41 tasks
Warning: 2 incomplete task(s) found. Continuing due to --yes flag.
...
Applying changes to openspec/specs/framework-contributor-guidance/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/framework-identity/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/release-tooling/spec.md:
  + 8 added
Applying changes to openspec/specs/user-documentation/spec.md:
  ~ 1 modified
Totals: + 8, ~ 3, - 0, → 0
Specs updated successfully.
Change 'release-tooling' archived as '2026-10-12-release-tooling'.
```

The two incomplete tasks were 8.3 and 8.4, done below. The new spec holds
eight requirements (design.md Decision 14 said seven; the delta, as ratified,
has eight: the Makefile, the version, the workspace and its tools, `make
test`, `check-dist --out`, `dist` and `upload`, `clean`, CI). Its Purpose,
"TBD" from the archive, written. After the archive each synced MODIFIED
requirement equals its delta (compared by name: equal, three of three).

```
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 49 passed, 0 failed (49 items)
```

### 8.3 The road's record (task 8.3)

`workflow/ongoing/release-0.9.md` at the repository root: Progress entry 2,
`release-tooling`, written as entry 1 is: the branch, the planning commit,
ADR-192, what the change does, the `.gitignore` fix, and the counts of 7.2,
7.5 and 7.8.

### 8.4 Closing (task 8.4)

The record-reading tests on the closed tree,
`tests/test_repository_layout.py tests/test_release_records.py
tests/test_docs_exports.py tests/test_check_dist.py
tests/test_node_root_exports_nothing.py` (`<scratch>/8.4-records.out`): 117
passed, 730 subtests passed in 10.35 s. `git check-ignore -v
packages/machinome/_build.lock`: `packages/machinome/.gitignore:124:/_build.lock`.
`git ls-files -ci --exclude-standard | wc -l`: 34. `make -s version`:
0.8.1.

The implementation commit and the integration into the line are the
orchestrator's; the planning commit is not amended; nothing is pushed,
tagged or uploaded, and `make upload` was never run.
