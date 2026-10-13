# Evidence: `release-0-9-0`

Cycle 10 of the road in `workflow/ongoing/release-0.9.md` at the repository
root (its decisions 2 and 10, cycle 10 and "Held for the pilot", the pilot,
12 October 2026). Worktree `machinome/WTs/v0.9-release`, branch
`v0.9-release`, planning commit 0266d3e6 on the framework's main 5ae35987
(the line `v0.9-joins` closed, `manual-extras` included). Ratified by the
orchestrator on 13 October 2026 with the recommendations of every Open
Question accepted. This file records the preparation, groups 1 to 5 of
`tasks.md`, applied on 13 October 2026; the day (groups 6 to 8) waits for
the pilot's date.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv, synced from the lock,
`.../scratchpad/C13-join/uv-sync-2.log` ending "exit 0"), Node 24.11.1, npm
11.6.2, the OpenSpec CLI 1.6.0. `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-release`, `<scratch>`
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C13-apply/`.
The core's tests ran from `<bench>/packages/machinome` on the bench venv
(`<bench>/.venv/bin/python -m pytest -q <module> -p no:cacheprovider`), a
product's from its own directory the same way, one pytest process at a
time. Logs are in `<scratch>`, never in the bench.

## 1. The base

### 1.1 The head, the tree, the version and the records

```
$ git -C <bench> log --oneline -3
0266d3e6 Propose release-0-9-0: Machinome 0.9.0, the set released as one
5ae35987 Implement manual-extras: every manual page declares the extra it needs
70be3aab Propose manual-extras: every manual page declares the extra it needs
$ git -C <bench> status --porcelain | wc -l
0
$ env -C <bench> make -s version
0.8.1
```

`HISTORY.rst`'s `Unreleased` holds 16 bullets, from "The framework is a
PACKAGE of its repository." (`monorepo-layout`) to "Every page of the
manual says what it needs." (`manual-extras`), as expected. The manual's
changelog holds 14 bullets under `Unreleased`, from "The engines are
packages of their own." to "Every page says what to install."
(`manual-extras`), as expected.

The pages that spell `|mechanics_version|` (`grep -rn mechanics_version
<bench>/packages/machinome/docs --exclude-dir=_build`):

```
docs/conf.py:48:mechanics_version = '0.1.0'
docs/conf.py:73:.. |mechanics_version| replace:: {mechanics_version}
docs/reference/api.rst:983:formulas are the package ``machinome-mechanics`` |mechanics_version|,
docs/reference/mechanics/index.rst:16:The helpers are the package ``machinome-mechanics`` |mechanics_version|,
docs/project/upgrading.rst:494:``machinome-mechanics`` |mechanics_version| package. Projects using the unreleased
docs/project/status.rst:66:|mechanics_version| is the optional helper package behind the
docs/adrs/README.md:174: (ADR-187's index line, a record)
docs/adrs/BUILD/ADR-187-...-at-their-own-version.md:77: (a record)
```

`start/install.rst` no longer spells it: `manual-extras` replaced the
installation page's hand-kept list of extras, the mechanics phrase with it,
by the `.. extras::` directive. Decision 3's "and `start/install.rst` if
`manual-extras` left the phrase" therefore has nothing to change there.

### 1.2 The line's last suite counts (not rerun here)

From the close of `manual-extras`
(`openspec/changes/archive/2026-10-13-manual-extras/evidence.md`, "The
orchestrator's run at the checkpoint", 13 October 2026): `make test
PKG=machinome` exit 0, 5046 passed, 9 skipped in 13 min 35 s; `make docs`
exit 0; `make check` exit 0, 72 PASSED (36 archives on the tree and 36 on
the clean copy). The products' suites, last run whole by this change's
proposer on the line's copy at c5eeb038 (design.md, probe 13): the
mechanics helpers 204 passed; the skills 47; the viewer's widget 1715
passed, 2 skipped, its Python 252 passed, 2 skipped; the movie 322 and its
Node `pure` and `stage` 329; the studio 485 passed, 24 skipped.

## 2. Red first

The edits of group 2 were applied by a script with exact-match asserts
(`<scratch>/apply.py`, stages `tests` and `literal_tests`), the texts of
design.md Decision 4 and the proposer's rehearsal (`C13-propose/prep.py`
and `prep2.py`) as their source. Every search string of the rehearsal
still matched the closed head but one: `start/install.rst` no longer
states the mechanics version (1.1).

### 2.1 `tests/test_release_records.py`

`OWN_VERSION` and its three branches gone; `test_a_member_of_its_own_version_is_outside_the_bump`
replaced by `test_the_mechanics_helpers_are_bumped_with_their_two_pins`;
`PRODUCTS` and `ReleaseRecordsTest.test_each_product_records_the_release`
added (with `from packaging.version import Version`); the docstring.
`python -m pytest -q tests/test_release_records.py` (`<scratch>/red-2.1.log`):
exit 1, 5 failed, 20 passed, 191 subtests passed:

- `test_every_member_is_numbered_with_the_core[machinome-mechanics]`:
  `'0.1.0' != '0.8.1'`;
- `test_every_pin_between_members_is_compatible`, two subtests:
  `'>=0.1.0' != '~=0.8.1'` (the core's extra) and `'>=0.8.0' != '~=0.8.1'`
  (the helpers' requirement);
- `test_the_version_is_bumped_from_the_root[machinome-mechanics]`: the
  manifest is not among the tables;
- `test_the_mechanics_helpers_are_bumped_with_their_two_pins`: `[] !=` the
  two tables.

`test_each_product_records_the_release` passed: at 0.8.1 it holds the
viewer alone, whose newest release section is `0.8.1 — 10 October 2026`.

### 2.2 The boundary and the helpers' identity

`tests/test_mechanics_boundary.py` expects the extra
`[f"machinome-mechanics~={project['version']}"]`; the helpers'
`tests/test_machinome_identity.py` expects
`[f"machinome~={project['version']}"]`. Red (`<scratch>/red-2.2-*.log`):
the core's module 1 failed, 3 passed (`['machinome-mechanics>=0.1.0'] !=
['machinome-mechanics~=0.8.1']`); the helpers' 1 failed, 2 passed
(`['machinome>=0.8.0'] != ['machinome~=0.1.0']`, the manifest still at
0.1.0).

### 2.3 `tests/test_docs_structure.py`

`mechanics_version` out of `test_facts_are_substitutions`,
`test_the_mechanics_version_is_the_package_s` removed,
`UpgradingPageTest.test_the_0_9_part_names_every_move` added (21 spellings).
`<scratch>/red-2.3.log`: exit 1, 14 subtests failed, 38 passed, 6466
subtests passed. The 14: `machinome[stl]`, `machinome[jscad]`, the two
former modules, `machinome.mechanics`, `machinome-mechanics`,
`machinome-studio`, `machinome studio`, ``` ``floor`` ```,
`machinome.studio`, `machinome movie`, `machinome[movie]` and the two
subsections' references. The other seven (`machinome.viewer.web`,
``` ``--renderer`` ```, ``` ``--viewer`` ```, `machinome[viewer-openscad]`,
`machinome-viewer describe`, `machinome viewer describe`,
`machinome.viewer`) are already spelled by the two subsections the seam
and the command wrote. Design.md probe 6 counted seventeen on its copy of
c5eeb038; the head counts fourteen. The failures are the moves the part
does not yet spell, as expected.

### 2.4 The tests that pinned a literal state

Rewritten as Decision 4's table says. Green at 0.8.1 (`<scratch>/green-2.4.log`):

| Test | Count |
|---|---|
| core `tests/test_machinome_identity.py` and `tests/test_viewer_documentation_links.py` | 20 passed, 5 subtests passed |
| viewer `tests/test_documentation.py` | 12 passed |
| movie `tests/test_repository.py` | 17 passed |
| studio `tests/test_documentation.py` | 23 passed, 232 subtests passed |
| mechanics `tests/test_documentation.py` | 6 passed |

The mechanics helpers' `test_documentation.py` no longer reads the
manifest, so its `import tomllib` went with that line (flake8 would
otherwise report it unused). Their red is the day's (6.3); the rehearsal
of 5.2 runs them on the dated copy.

## 3. The mechanics helpers numbered with the set

### 3.1 The manifests, the tables, the lock

Stage `mechanics` of `<scratch>/apply.py`: the helpers' manifest at
`version = "0.8.1"` with its comment, `machinome~=0.8.1` with its comment;
the core's `mechanics = ["machinome-mechanics~=0.8.1"]`, its comment
"numbered with the set"; the two tables of Decision 3 appended after the
studio's frontend table.

```
$ env -C <bench> uv lock          (<scratch>/uv-lock.log)
Resolved 201 packages in 675ms
Updated machinome-mechanics v0.1.0 -> v0.8.1
exit 0
$ env -C <bench> uv sync --python 3.12          (<scratch>/uv-sync.log)
 ~ machinome==0.8.1 (from file:///.../packages/machinome)
 - machinome-mechanics==0.1.0 (from file:///.../packages/machinome-mechanics)
 + machinome-mechanics==0.8.1 (from file:///.../packages/machinome-mechanics)
exit 0
```

`git diff --stat uv.lock`: 1 line changed (the member's `version`; uv
records no specifier for an editable workspace member).

After it (`<scratch>/after-3.1.log`): `test_release_records.py` and
`test_mechanics_boundary.py` 1 failed, 24 passed, 195 subtests passed, the
one failure `test_the_mechanics_helpers_are_bumped_with_their_two_pins` on
its second assertion, `'mechanics_version' unexpectedly found in`
`docs/conf.py`, which 3.3 removes; the helpers' identity test 3 passed.

### 3.2 `scripts/check-dist`

`MECHANICS_VERSION` and its comment gone; the mechanics row's code asserts
`distribution.version == metadata.version('machinome')`,
`machinome~={version}` among its requirements and a core requirement
starting `machinome-mechanics~={version}`. The script parses
(`ast.parse`). Its run is 5.1's `make check`.

### 3.3 `docs/conf.py` and the pages

`mechanics_version`, its comment and its substitution line gone;
`reference/api.rst` and `reference/mechanics/index.rst` state
``` ``machinome-mechanics`` |release| ```; the upgrading page's 0.7 part
states ``` ``machinome-mechanics`` 0.1.0 package ```; the status page's
sentence is "Machinome Mechanics, numbered with the framework, is the
optional helper package behind the ``mechanics`` extra." `grep -rn
mechanics_version <bench>/packages/machinome/docs --exclude-dir=_build`
then finds only the two ADR records (ADR-187's body and its index line),
which state what was decided at the join.

`<scratch>/green-3.1-3.3.log`: `test_release_records.py`,
`test_mechanics_boundary.py` and `test_docs_structure.py::ReleaseFactsTest`
28 passed, 284 subtests passed; the helpers' `test_machinome_identity.py`
and `test_documentation.py` 9 passed.

### 3.4 The records

- `HISTORY.rst`: the join bullet reads "It keeps its changelog, its specs
  and its tests in its directory"; the mechanics bullet of Decision 7 last
  under `Unreleased`, after `manual-extras`' (17 bullets).
- The manual's changelog: the mechanics bullet of Decision 7 last under
  `Unreleased`, after `manual-extras`' (15 bullets).
- The helpers' `CHANGELOG.md`: the join bullet says "is numbered with
  Machinome, requiring the matching release" where it said "requires
  Machinome 0.8 or newer", the rest of its sentence rewrapped.
- `context7.json`: "(the distribution machinome-mechanics, numbered with
  the framework)".

### 3.5 The helpers' own specs, in place

- `openspec/specs/distribution/spec.md`: the requirement declares
  `machinome~=<version>`, the version being Machinome's own; the scenario
  "The release pair is legible" names 0.1.0 released with Machinome 0.7.0
  and the package numbered with Machinome since 0.9.0. The scenario
  "Install a built distribution", which said "with Machinome 0.8 or newer
  available", says "with the Machinome release of its own version
  available": a floor no longer describes the requirement (not named by
  Decision 3; see the departures below).
- `openspec/specs/user-documentation/spec.md`, the scenario "A user reads
  which version they have": the manual and the changelog name the
  framework's version as the helpers', the changelog's 0.1.0 section states
  0.1.0 released with Machinome 0.7.0, the README names no version.

### 3.6 ADR-187

Its status line as Decision 10 gives it and the section "Amendment
(2026-10-13, change `release-0-9-0`)" at its end, verbatim, `<prep date>`
2026-10-13 (the ADRs' own date form); its index line in
`docs/adrs/README.md` gains ", amended by `release-0-9-0` (numbered with
the set from 0.9.0)" after "amended by 188".

### 3.7 `tests/test_repository_layout.py`

The docstring: the helpers keep their record in their directory,
"numbered with the set since change `release-0-9-0`" (ADR-187, amended),
in place of "at its own version".

## 4. The upgrading page and the day note

- 4.1: the 0.9 part of Decision 5, verbatim, under the title, its label
  and `.. needs:: none`, before the label of "The viewer flag".
- 4.2: the installation page's "Upgrading" paragraph of Decision 5,
  verbatim.
- 4.3: `workflow/ongoing/release-0.9.0-day.md` at the repository root,
  verbatim from Decision 9, `<prep date>` 13 October 2026.

The texts were read from design.md by the script (`block()`), not
retyped. No page was added, so no `.. needs::` declaration is new.

`<scratch>/green-4.1.log`: `test_docs_structure.py`,
`test_viewer_documentation_links.py`, `test_release_records.py`,
`test_repository_layout.py`, `test_manual_extras.py`,
`test_mechanics_boundary.py`, `test_machinome_identity.py`,
`test_kernel_extras.py` and `test_sphinx_ext.py` together: exit 0, 188
passed, 7275 subtests passed.

## 5. Checked and rehearsed

### 5.1 The bench at 0.8.1

**`make test`** from the bench root, started 01:31 on 13 October 2026
(`<scratch>/make-test.log`): exit 2 after 24 min 27 s, stopping at the
viewer's Python suite.

| Package | Count |
|---|---|
| core | 5047 passed, 9 skipped in 18 min 16 s (the close's 5046 and one net: two tests added to `test_release_records.py`, one replaced there; one added to `test_docs_structure.py`, one removed there) |
| mechanics helpers | 204 passed |
| skills | 47 passed |
| viewer widget (typecheck, vitest, build) | 1715 passed, 2 skipped (65 files passed, 1 skipped) |
| viewer Python | 1 failed, 251 passed, 2 skipped |

The one failure,
`tests/test_widget_e2e.py::FullscreenE2ETest::test_a_plain_mount_goes_full_screen_and_the_canvas_grows_to_the_viewport`
("200 not greater than 400 : the canvas did not follow the host into full
screen"), is a browser timing test this change does not touch: rerun alone
(`<scratch>/viewer-fullscreen-rerun.log`), `FullscreenE2ETest` 12 passed.
`make test PKG=machinome-viewer` then `PKG=machinome-movie`
(`<scratch>/make-test-products.log`): the viewer's widget 1715 passed, 2
skipped, its Python 252 passed, 2 skipped; the movie's Python 322 passed,
and its Node `pure` and `stage` projects 4 failed, 248 passed, 6 test files
failing to start.

**The bench's npm installation is incomplete, not the change.** The
movie's Node failures are `TS7016: Could not find a declaration file for
module 'react-dom'` and `ERR_MODULE_NOT_FOUND` for
`js/node_modules/@csstools/css-calc/index.js`: `find
<bench>/packages/machinome-movie/machinome/movie/js/node_modules -maxdepth 3
-type d -empty` lists `@vitest/spy`, `@csstools/css-calc` and
`@types/react-dom`, empty directories of the install of 12 October 2026,
23:36. `make test PKG=machinome-studio` stops in the frontend's `tsc -b`
the same way (`Cannot find module '@monaco-editor/react'`,
`<scratch>/make-test-studio.log`), and the studio's Python suite run
directly then has 21 failures, every one the absent built surface
(`static/assets does not exist`, "Connection refused" from the floor that
cannot serve it; `<scratch>/studio-pytest.log`). `npm ci` at the bench
root, which the brief allows, was refused by this session's permission
classifier, so the bench was not repaired. The same tree at the same
state, installed from its locks on the rehearsal copy (5.2), passes both
targets: `make test PKG=machinome-movie` 322 passed and Node 329 passed (31
files); `make test PKG=machinome-studio` 485 passed, 24 skipped, its
frontend's tests and build included (`<scratch>/r-products-test.log`).

**`make docs`** (`<scratch>/make-docs.log`): "build succeeded.", exit 0,
14 s, no Sphinx warning, 97 HTML pages. Read in the built HTML: the
upgrading page's 0.9 part opens with "Machinome 0.9 brings the packages";
`reference/mechanics/index.html` reads "machinome-mechanics 0.8.1,
installed by machinome[mechanics]"; the status page "Machinome Mechanics,
numbered with the framework, is the optional helper package"; the
installation page "Coming from Machinome 0.8? Read Upgrading from Machinome
0.8 to 0.9 first".

**`make check`** (`<scratch>/make-check.log`): exit 0, 8 min 36 s; "Every
distribution built, checked, installed and smoked; nothing uploaded." twice
(the tree and the clean copy of its tracked files); 72 `twine check`
PASSED; the smoke line of each of the eighteen distributions reads 0.8.1 in
both passes, `machinome-mechanics 0.8.1 module .../machinome/mechanics/__init__.py
numeric and symbolic` among them; no line of the output says 0.1.0.

**`make lint`** (`<scratch>/make-lint.log`): exit 2 as at the base (CI's
`continue-on-error`). black: "595 files would be reformatted, 198 files
would be left unchanged, 1 file would fail to reformat." on the base
(`git archive` of 0266d3e6) and on the bench. flake8, the same command on
both (`<scratch>/flake8-j1-*.txt`): 2538 findings each, the same findings
(diff of the sorted lists without line numbers empty). Two findings this
change first added, `E303` before `UpgradingPageTest` and `E501` in the
records test's docstring, were corrected before the count. The products'
tests, which `make lint` does not read: flake8 counts unchanged on the
viewer's, the movie's and the helpers' edited modules; the studio's
`test_documentation.py` gains one `E501` (93 characters, as the module's
neighbouring lines run to 97).

### 5.2 The rehearsal

`<scratch>/day/`: the bench's tracked files at this group's state and its
two new files (6166 files: `git ls-files --cached --others
--exclude-standard`, the 34 tracked files the ignore rules match added with
`git add -f`), made a Git repository of one commit, 1a774c7. Nothing in it
was written back to the bench.

- **The install.** `make sync` ends with `playwright install chromium`,
  which the brief forbids, so its two other steps were run by hand
  (`<scratch>/r-sync.log`): `uv sync --python 3.12` "Resolved 201
  packages", "Installed 192 packages", exit 0; `npm ci --no-audit
  --no-fund` "added 229 packages", exit 0; 30 s. Chromium was already in
  `~/.cache/ms-playwright` (chromium-1243 among four).
- **`make bump VERSION=0.9.0`** (`<scratch>/r-bump.log`,
  `<scratch>/r-bump-diffstat.txt`): exit 0, 2.0 s, "29 files changed, 97
  insertions(+), 97 deletions(-)", the files of probe 3; the mechanics
  manifest among them (`version = "0.9.0"`, `machinome~=0.9.0`) and the
  core's `mechanics = ["machinome-mechanics~=0.9.0"]`; `uv.lock`'s
  `machinome-mechanics` at 0.9.0. `make -s version` 0.9.0; `git log` one
  commit; `git tag` none.
- **`uv sync --python 3.12`** (`<scratch>/r-uv-sync.log`): exit 0;
  `importlib.metadata.version` reads 0.9.0 for `machinome` and
  `machinome-mechanics`.
- **The day's red** (`<scratch>/r-day-red.log`): `test_release_records.py`
  8 failed, 17 passed, 194 subtests passed: `test_context7_states_the_release`,
  `test_each_product_records_the_release` for each of the four products,
  `test_the_changelog_first_release_section_is_the_released_version`,
  `test_the_history_top_entry_is_the_released_version`,
  `test_the_release_note_has_the_dated_section`; the viewer's
  `test_documentation.py` 2 failed, 10 passed
  (`test_the_manual_states_the_release`,
  `test_describe_example_matches_package_versions`); the movie's 17, the
  studio's 23 (232 subtests) and the helpers' 6 passed. Probe 7's
  failures.
- **The records at a stand-in date**, 13 October 2026, placed by the
  proposer's `C13-propose/day.py` with its texts, each of which is a
  verbatim block of design.md (`<scratch>/cmp-texts.py`: 18 of 18).
  `<scratch>/r-day-green.log`: the core's `test_release_records.py`,
  `test_docs_structure.py`, `test_viewer_documentation_links.py`,
  `test_machinome_identity.py` and `test_profile_documentation.py` 81
  passed, 6714 subtests passed; the viewer's 12, the movie's 17, the
  studio's 23 (232 subtests), the helpers' `test_documentation.py` and
  `test_machinome_identity.py` 9 passed.
- **`make docs`** (`<scratch>/r-docs.log`): "build succeeded.", 11.6 s;
  read: "Machinome 0.9.0 was released on 13 October 2026. It is the first
  release of the Machinome set from one repository", the release note's
  "Released on 13 October 2026.", the changelog's "Released on
  13/Oct/2026 One repository, one release."
- **`make check`** (`<scratch>/r-check.log`): exit 0, 8 min 31 s; two
  passes, 72 PASSED; each of the eighteen distributions' smoke lines reads
  0.9.0 in both, the mechanics helpers' among them; no line says 0.8.1.
- **Committed** (c1bea29, 39 files), `git status --porcelain` empty, then
  **`make dist`** (`<scratch>/r-dist.log`): "$ scripts/check-dist --out
  dist/v0.9.0, in a copy of the commit c1bea29", "36 archives kept in
  .../day/dist/v0.9.0", exit 0, 4 min 7 s; 18 wheels and 18 sdists, all
  0.9.0 (`<scratch>/r-archives.txt`). `twine check --strict
  dist/v0.9.0/*`: 36 PASSED, exit 0 (`<scratch>/r-twine.log`). `make -n
  upload` prints the folder test and `.venv/bin/python -m twine upload
  dist/v0.9.0/*` and runs nothing (`<scratch>/r-upload-n.log`). `git tag`
  on the copy: none. `make upload` was not run.

The copy was removed after these records.

### 5.3 The state left for the orchestrator

`openspec validate release-0-9-0 --strict` (from
`<bench>/packages/machinome`): "Change 'release-0-9-0' is valid".
`tasks.md` groups 1 to 5 ticked. No commit, tag, push or upload was made;
the change is not archived.

### Departures from the design, for the orchestrator's review

- 2.3's red counts 14 subtests, not probe 6's 17: the closed head's two
  subsections already spell seven of the 21 moves.
- Decision 3's `start/install.rst` edit has nothing to change:
  `manual-extras` removed the phrase (1.1).
- The helpers' `distribution` spec: besides the two changes Decision 3
  names, the scenario "Install a built distribution" no longer says
  "with Machinome 0.8 or newer available", which a `~=` requirement makes
  false; it says "with the Machinome release of its own version
  available".
- The helpers' `tests/test_documentation.py` loses `import tomllib` with
  the line that used it.
- `test_repository_layout.py`'s docstring names ADR-187 "amended".
- `make sync` in the rehearsal ran without its `playwright install
  chromium` step (the brief forbids it); Chromium was cached.
- `make test` on the bench could not run the movie's Node tests or the
  studio's frontend and browser-served tests green, the bench's npm
  installation being incomplete and `npm ci` refused to this session; the
  rehearsal copy, installed from the same locks, ran both targets green at
  this state.
- Not changed, for the orchestrator's judgement: the comment above the
  mechanics row of `scripts/check-dist` still says the wheel is installed
  by path because "the index serves another wheel of the same version,
  whose import is the former one"; at 0.8.1 and 0.9.0 the index holds no
  other wheel of the version (it holds 0.1.0), so the reason no longer
  holds, though installing by path still does.
