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

## The day: 31 October 2026

The pilot named the day 31 October 2026: `<d Month YYYY>` 31 October 2026,
`<YYYY-MM-DD>` 2026-10-31, `<dd/Mon/YYYY>` 31/Oct/2026. Groups 6 to 8 were
applied that day by a fresh applier on the same bench, its venv synced from
the lock and `npm ci` and Chromium installed that day by the orchestrator.
Tools as above. `<scratch>` for these groups is
`/tmp/claude-1000/-home-asa-devel-machinome/56fde1bb-f65d-45ec-9043-bd2ec042abb7/scratchpad/C13-day/logs/`;
the records were placed by `<scratch>/../work/day.py`, which reads every
text of Decision 7 from design.md by its line (`block()`) and edits each
file with exact-match asserts.

## 6. The date and the bump

### 6.1 The base

The orchestrator named the head: the bench at 78276414, equal to `main`.
Nine commits landed on it after the preparation's 1e9c5024 (the studio's
third-party notices and credits, chapter 10 photographing through the web
viewer, the identity's artwork licence and `TRADEMARKS.md`, the coverage
target, and the CI corrections `pin-setup-uv`, `browser-snapshot-path` and
`creation-test-identity` with their `HISTORY.rst` bullets).

```
$ git -C <bench> log --oneline -3          (<scratch>/base.log)
78276414 Record the npm publish race that failed CI's OpenSpec CLI install
da1ac5de The studio's session-opening fixture carries a git identity for the scaffold commit
306bd75e CI's browser snapshot job names the test where it is: tests/test_web_viewer_capture.py
$ git -C <bench> status --porcelain | wc -l
0
$ env -C <bench> make -s version
0.8.1
```

### 6.2 The bump

`env -C <bench> make bump VERSION=0.9.0` (`<scratch>/bump.log`): exit 0,
3.0 s; "29 files changed, 97 insertions(+), 97 deletions(-)"
(`<scratch>/bump-diffstat.txt`), the files of probe 3: `.bumpversion.cfg`,
the eighteen manifests, the core's `machinome/__init__.py`, `docs/conf.py`
(`release` and `viewer_version`), `machinome/vet/universe.toml`, the
viewer's `__init__.py` and widget `package.json`, the movie's
`js/package.json` and its own lock, the studio frontend's `package.json`,
the root's `package-lock.json` (its three member entries) and `uv.lock`
(36 lines). The mechanics manifest is among them (`version = "0.9.0"`,
`machinome~=0.9.0`). npm printed the `EBADENGINE` warnings of probe 3 for
Node 24.11.1 and wrote the locks. `make -s version`: 0.9.0; `git log -1`:
78276414, no new commit; `git tag`: the 23 tags of before, none new.

`env -C <bench> uv sync --python 3.12` (`<scratch>/uv-sync.log`): exit 0,
"Installed 18 packages", each member `0.8.1 -> 0.9.0`.
`importlib.metadata.version` read 0.8.1 for `machinome` and
`machinome-mechanics` before it and 0.9.0 for both (and for
`machinome-viewer`) after it (probe 12).

### 6.3 The day's red

| Test | Result |
|---|---|
| core `tests/test_release_records.py` (`<scratch>/red-6.3-records.log`) | 8 failed, 17 passed, 194 subtests passed |
| viewer `tests/test_documentation.py` | 2 failed, 10 passed |
| movie `tests/test_repository.py` | 17 passed |
| studio `tests/test_documentation.py` | 23 passed, 232 subtests passed |
| mechanics `tests/test_documentation.py` | 6 passed |

The failures, each a record not yet dated:

- `test_context7_states_the_release`: `'Machinome 0.9.0 (released 2026-10-10)'`
  not found in `context7.json`'s rules, which open "Machinome 0.8.1
  (released 2026-10-10)";
- `test_each_product_records_the_release`, four subtests: the viewer's
  newest section `'0.8.1 — 10 October 2026' != '0.9.0 — 10 October 2026'`,
  the mechanics helpers' `'0.1.0 — 23 September 2026'`, the movie and the
  studio "records no release";
- `test_the_changelog_first_release_section_is_the_released_version`:
  `'Machinome 0.8.1' != 'Machinome 0.9.0'`;
- `test_the_history_top_entry_is_the_released_version`: `'0.8.1' != '0.9.0'`;
- `test_the_release_note_has_the_dated_section`: `docs/releases/release-0.9.rst`
  absent;
- the viewer's `test_the_manual_states_the_release` (the changelog's first
  release section starts `0.8.1 — 10 October 2026`) and
  `test_describe_example_matches_package_versions` (`'0.8.1' == '0.9.0'`,
  the `describe` example of `reference/viewer/cli.rst`).

The undated date in these messages is `release_date`, still 10 October
2026 until 7.1. The movie's, the studio's and the mechanics helpers'
documentation tests pass undated, as in the rehearsal (5.2): they accept
either state of their changelog, and the release-records test carries
their products' red.

## 7. The records

Placed by `day.py` with the texts of Decision 7, verbatim, the date
substituted:

- 7.1 `docs/conf.py`: `version = '0.9'`, `release_date = '31 October 2026'`;
  `viewer_api` `'29'` and `document_versions` `'1 to 13'` unchanged.
- 7.2 `HISTORY.rst` (the root's; `packages/machinome/HISTORY.rst` is its
  symlink): `Machinome 0.9.0 (2026-10-31)` over 28 dashes, then the opening
  paragraph, then the bullets as they were.
- 7.3 The manual's changelog: `Machinome 0.9.0` over 15 dashes, `Released
  on 31/Oct/2026`, the opening and the moves, then the 15 bullets as they
  were; the toctree gains `../releases/release-0.9` above
  `../releases/release-0.8`.
- 7.4 `docs/releases/release-0.9.rst`, new, verbatim.
- 7.5 The status page: the first paragraph; in "What |version| is", the
  second paragraph's first sentence (the paragraph rewrapped at 76
  columns, its other words unchanged) and the release note's link
  `</releases/release-0.9>`; "Packages"' first paragraph; the studio
  paragraph; "Direction". The running-documents paragraph is unchanged.
- 7.6 `context7.json`: the first rule's opening and "The matching viewer is
  0.9.0, API 29,".
- 7.7 The four products' changelogs: `## Unreleased` become `## 0.9.0 — 31
  October 2026` with its paragraph, the entries under it as written; the
  studio's preamble.
- 7.8 `docs/reference/viewer/cli.rst`: `"version": "0.9.0"`. The viewer's
  `openspec/specs/user-documentation/spec.md`: the requirement "The manual
  states the 0.8.1 release" is "The manual states the 0.9.0 release",
  machinome-viewer 0.9.0 released with Machinome 0.9.0 on 31 October 2026,
  its changelog's newest release section `0.9.0 — 31 October 2026`, API 29
  and document versions 1 through 13 unchanged; its scenarios "A maker
  checks the 0.9.0 release they installed" and "A reader compares 0.9.0
  with 0.8.1". `viewer-distribution/spec.md`: the version paragraph and the
  scenario "The release pair is legible" say 0.9.0, released with
  Machinome 0.9.0.

### 7.9 The re-read

`HISTORY.rst`'s 0.9.0 entry holds 20 bullets: the 16 of the line, the
mechanics bullet of the preparation, then the three landed after the
planning commit (`pin-setup-uv`, `browser-snapshot-path`,
`creation-test-identity`), kept in their place after it. The manual's
changelog holds its 15, the mechanics bullet last; nothing landed there
after the preparation. The studio's `CHANGELOG.md` gained entries after the
preparation (the third-party notices and credits); they stay under its 0.9.0
heading as written. The opening's "ADR-182 to ADR-196 are new" holds: the
ADRs of the line are 182 to 196, none later.

`git -C <bench> grep -n "0\.8\.1"` (`<scratch>/grep-081-all.txt`, 961
lines), the change's own directory, archives, `workflow/` and the ADRs set
aside, finds:

- the 0.8.1 records: `HISTORY.rst`'s 0.8.1 entry, the manual changelog's
  0.8.1 section, the upgrading page's 0.8.1 part, the release note's 0.8.1
  section, the viewer's `CHANGELOG.md` 0.8.1 section, `context7.json`'s
  "It follows 0.8.1 (2026-10-10)", the viewer's spec "unchanged from 0.8.1"
  and its scenario "compares 0.9.0 with 0.8.1";
- the framework's baseline `openspec/specs/user-documentation/spec.md`
  requirement "The 0.8.1 release is recorded", which this change's delta
  replaces at the archive (10.1), and the `release-tooling` spec's
  scenarios (`make bump VERSION=0.9.0` on a checkout at 0.8.1,
  `dist/v0.8.1` as an example);
- the tests' fixtures: `test_check_dist.py` (archive names under
  `v0.8.1`), `test_docs_structure.py` and
  `test_viewer_documentation_links.py` (the heading of the 0.8.1 part).

Nothing else.

## 8. Green and checked

### 8.1 The tests, the suite, the manual

| Test | Result |
|---|---|
| core `test_release_records.py` (`<scratch>/green-8.1-records.log`) | 21 passed, 199 subtests passed |
| core `test_release_records.py`, `test_docs_structure.py`, `test_viewer_documentation_links.py`, `test_machinome_identity.py`, `test_profile_documentation.py` | 81 passed, 6714 subtests passed |
| viewer `tests/test_documentation.py` | 12 passed |
| movie `tests/test_repository.py` | 17 passed |
| studio `tests/test_documentation.py` | 23 passed, 232 subtests passed |
| mechanics `tests/test_documentation.py` | 6 passed |

**`make test`** from the bench root (`<scratch>/make-test.log`): exit 0,
22 min 59 s.

| Package | Count |
|---|---|
| core (under coverage, 93 %) | 5049 passed, 9 skipped in 15 min 7 s |
| mechanics helpers | 204 passed |
| skills | 47 passed |
| viewer widget (typecheck, vitest, build) | 1715 passed, 2 skipped (65 files passed, 1 skipped) |
| viewer Python | 252 passed, 2 skipped |
| movie Python | 322 passed |
| movie Node `pure` and `stage` | 329 passed (31 files) |
| studio frontend (`tsc -b`, build) and Python | 490 passed, 24 skipped |

The core's 5049 are the preparation's 5047 and the two tests the commits
after it added to `test_repository_layout.py` (the uv action's pin and the
browser snapshot step); the studio's 490 the preparation's 485 and the five tests
of `test_third_party_notices.py` added after it.
The bench's npm installation is whole this time (`npm ci` that day), so the
movie's Node tests and the studio's frontend ran on the bench.

**`make docs`** (`<scratch>/make-docs.log`): "build succeeded.", exit 0,
8.8 s, no warning. Read in the built HTML under
`packages/machinome/docs/_build/html`:

- `project/status.html`: "Machinome 0.9.0 was released on 31 October 2026.
  It is the first release of the Machinome set from one repository: the
  framework and every package beside it are numbered 0.9.0, licensed
  GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice";
  "What 0.9 is"; "each CAD kernel and node type is a package of the set";
  "Packages": "All are numbered and released with the framework."; the
  matching viewer 0.9.0, API 29, document versions 1 to 13; "It runs on
  Linux only. Browser-delivery experiments are not a released capability.";
  "Direction": "are packages of one repository, released together"; the
  release note's link to `release-0.9.html`.
- `project/changelog.html`: "Machinome 0.9.0", "Released on 31/Oct/2026",
  "One repository, one release.", the six moves, then "The engines are
  packages of their own."; the toctree lists release-0.9, 0.8 and 0.7.
- `releases/release-0.9.html`: "Machinome 0.9: one repository, one
  release", "Released on 31 October 2026.", its sections from "One
  repository" to "Upgrading".
- `project/upgrading.html`: "Upgrading from Machinome 0.8 to 0.9", "Machinome
  0.9 brings the packages that grew beside the framework into its
  repository and its release", the moves from "Install the extra of every
  node type you use."

**`make lint`** (`<scratch>/make-lint.log`): exit 2, as at the base (CI's
`continue-on-error`): black "595 files would be reformatted, 198 files would
be left unchanged, 1 file would fail to reformat."; flake8 2538 findings,
the preparation's count.

### 8.2 `make check`

`env -C <bench> make check` (`<scratch>/make-check.log`): exit 0, 7 min
33 s; two passes, the tree and the clean copy of its tracked files
(`git ls-files`), each "Every distribution built, checked, installed and
smoked; nothing uploaded."; 72 `twine check` PASSED (36 archives a pass);
the smoke line of each of the eighteen distributions reads 0.9.0 in both
passes, `machinome-mechanics 0.9.0 module .../machinome/mechanics/__init__.py
numeric and symbolic` among them; no line of the output says 0.8.1. The
core's sdist: 1237 entries from the tree (its ignored files after `make
test`, which `MANIFEST.in`'s `recursive-include tests *` takes) and 1180
from the clean copy.

The clean copy holds tracked files only, so it lacks the one new file of
the day, `docs/releases/release-0.9.rst`, which `MANIFEST.in` puts in the
core's sdist. `scripts/check-dist` was therefore run once more on a scratch
copy of the tracked files and that one new file (`git ls-files --cached
--others --exclude-standard`, outside the bench,
`<scratch>/check-dist-with-new-file.log`): exit 0, 3 min 33 s, 36 PASSED,
every smoke line 0.9.0, none 0.8.1, the core's sdist 1181 entries (the
clean copy's and the release note). The copy was removed. After the commit
`make dist` builds from the commit, which holds it.

### 8.3 The tree

`git -C <bench> status --short` (`<scratch>/status.txt`, before this
file and `tasks.md` were written): 41 entries, the bump's 29 and the 12
files of group 7 that the bump does not touch (`HISTORY.rst`,
`context7.json`, the manual's `project/changelog.rst` and
`project/status.rst`, `releases/release-0.9.rst` new, `reference/viewer/cli.rst`,
the four products' `CHANGELOG.md`, the viewer's two specs); `docs/conf.py`
is in both. With `evidence.md` and `tasks.md`, 43, nothing else.

`tasks.md` 6.1 to 8.3 ticked. No commit, tag, push or upload was made.

### Departures from the design, for the orchestrator's review

- The head is 78276414, not the preparation's commit: nine commits landed
  after it (6.1); their bullets and entries stay in their place (7.9).
- The movie's, the studio's and the mechanics helpers' documentation tests
  are green before the records, not red (6.3); the release-records test
  carries their red, as the rehearsal showed.
- The viewer's spec requirement drops the 0.8.1 clause "the published 0.8.0
  renumbered, with no change to the widget, the server or the capture",
  which 0.9.0 does not satisfy, and says "unchanged from 0.8.1" of the API
  and document versions; Decision 7 gives the requirement's content, not
  its words.
- The status page's second paragraph of "What |version| is" is rewrapped
  around the new sentence.
- Not changed: the movie's `CHANGELOG.md` preamble still says "entries
  accumulate under `Unreleased` until the set is released", which Decision
  7 leaves as it is; after the release it has no `Unreleased` section.

## 9. Integration and the archives (the orchestrator)

### 9.1 The fast-forward

The orchestrator reviewed the pause of 8.3 on 31 October 2026: the tree
against Decision 6 (the bump's 29 files, the records of Decision 7,
`evidence.md`, `tasks.md`, the untracked release note), every text block
of Decision 7 found verbatim and dated in its record by a script over
`design.md`, the smaller edits read in `git diff`, the viewer's spec
wording kept, the logs' ends read (`make test` exit 0, `make check` exit
0, `make docs` "build succeeded"), and its own rerun on the bench:
`test_release_records.py`, `test_docs_structure.py`,
`test_viewer_documentation_links.py`, `test_machinome_identity.py` and
`test_repository_layout.py` together 137 passed, 7193 subtests; the
viewer's documentation test 12, the movie's repository test 17, the
studio's documentation test 23 (232 subtests), the mechanics package's 6;
`openspec validate release-0-9-0 --strict` valid; the locks' diffs
version lines alone. Commit "Release 0.9.0", 5ce19b40, 43 files, 602
insertions, 180 deletions.

```
$ git -C /home/asa/devel/machinome/machinome merge --ff-only v0.9-release
$ git -C /home/asa/devel/machinome/machinome log --oneline -1 main
5ce19b40 Release 0.9.0
```

### 9.2 `make dist` in the primary checkout

In `/home/asa/devel/machinome/machinome` at `main`: `make sync` earlier the
same day (`uv sync`, `npm ci` adding 231 packages, Chromium), then after the
fast-forward `uv sync --python 3.12` (the installed metadata of `machinome`
and `machinome-mechanics` reading 0.9.0), `git status --porcelain` empty,
`make -s version` 0.9.0.

```
$ make dist
$ scripts/check-dist --out dist/v0.9.0, in a copy of the commit 5ce19b40
...
36 archives kept in /home/asa/devel/machinome/machinome/dist/v0.9.0
Every distribution built, checked, installed and smoked; nothing uploaded.
$ ls dist/v0.9.0 | wc -l
36
$ make -n upload
test -n "$(ls -A dist/v0.9.0 2>/dev/null)" || { ...; exit 1; }
/home/asa/devel/machinome/machinome/.venv/bin/python -m twine upload dist/v0.9.0/*
```

Exit 0; the sdist and the wheel of each of the eighteen packages; `twine
check --strict` PASSED 36 times; every smoke line 0.9.0. The core's wheel
`machinome-0.9.0-py3-none-any.whl` sha256 `94b4b81137eba92c…`, its sdist
`machinome-0.9.0.tar.gz` sha256 `460b85a96bb55216…`. `make upload` was not
run. The log: `<scratch>/C13-day/logs/make-dist-primary.log`, `<scratch>`
being `/tmp/claude-1000/-home-asa-devel-machinome/56fde1bb-f65d-45ec-9043-bd2ec042abb7/scratchpad/`.

## 10. The archive

On 31 October 2026, after 9.2:

- 10.1: `openspec archive release-0-9-0 --yes` from `<bench>/packages/machinome`
  refused at first: "framework-identity MODIFIED failed for header '###
  Requirement: Extras select independent Machinome products' - current spec
  contains scenario(s) not present in the modified block: 'A reader asks for
  the studio extra before publication'. Refresh the change spec before
  archiving to avoid dropping scenarios. Aborted. No files were changed."
  The CLI (1.6.0) refuses a MODIFIED block that drops a scenario of the
  baseline, and Decision 11 drops four on purpose. The orchestrator
  applied every MODIFIED block of the three deltas to its baseline by a
  script that replaces the requirement's block wholesale, as the CLI does,
  printing each block's dropped and added scenarios, each one Decision 11
  names: `framework-identity`, "Extras select independent Machinome
  products", dropped "A reader asks for the studio extra before
  publication", added "The mechanics extra pins the framework's release"
  and "The status page records the studio as released"; "The framework is
  the package directory `packages/machinome` of a monorepo", dropped "The
  mechanics helpers carry their own version", added "The mechanics helpers
  are numbered with the set"; `mechanics-distribution`, "Framework
  independence from mechanics helpers", none; `user-documentation`, "The
  0.8.1 release is recorded", dropped "A maker installs the viewer extra"
  (0.9.0 moves the pins) and "Work lands after the release" (it is the
  0.9.0 requirement's), the other three none. Then the CLI, finding each
  MODIFIED block equal to its baseline: "Applying changes to
  openspec/specs/framework-identity/spec.md: ~ 2 modified;
  mechanics-distribution: ~ 1 modified; user-documentation: + 1 added, ~ 4
  modified. Totals: + 1, ~ 7, - 0, → 0. Specs updated successfully. Change
  'release-0-9-0' archived as '2026-10-31-release-0-9-0'." The archive
  holds this file; the change directory is gone. `openspec validate
  --specs --strict` and `openspec validate --all --strict`: 51 passed, 0
  failed each. The three baselines' diff: 129 insertions, 71 deletions.
  ADR disposition: ADR-187 amended in the preparation (3.6), nothing new.
- 10.2: the progress entry, entry 6 under "Progress" of
  `workflow/ongoing/release-0.9.md` at the repository root; the day note
  `workflow/ongoing/release-0.9.0-day.md` stays in `ongoing/` until the
  pilot's steps are done.
- 10.3: one commit on the bench touching `packages/machinome/openspec/` and
  `workflow/` alone; `main` fast-forwarded to it. The tag stays the
  pilot's, on "Release 0.9.0" (5ce19b40), the commit `dist/v0.9.0` was
  built from.
