## Context

The line `v0.9-joins` holds every cycle of the 0.9 road
(`workflow/ongoing/release-0.9.md` at the repository root, "The cycles, in
order", 1 to 7 and 9): the eighteen distributions of the set under
`packages/`, the command `machinome` with the films', the skills' and the
studio's commands, the seam of viewers and `machinome viewer`, the manual
with every page's extras, and the release tooling of `release-tooling`
(ADR-192): the set's version declared once as `current_version` of the
root's `.bumpversion.cfg`, `make bump VERSION=` moving every copy and lock
without committing or tagging and refusing a tree whose tracked files
changed, `make dist` building every archive of the commit into
`dist/vX.Y.Z` from a copy of it and refusing a tree that differs from it,
`make upload` alone running twine, and CI's `build` job, on a tag, checking
that the tag names `make -s version`, running `make dist` and creating the
GitHub release. This change is cycle 10, the last of the road.

The pilot's decisions of 12 October 2026 that bound it (`release-0.9.md`):
decision 2 (one bump of everything to 0.9.0 from the root's
`.bumpversion.cfg`, mechanics and the skills included, ending the mechanics
helpers' own version; one tag `v0.9.0`; the number declared once), decision
10 (the release tooling, no target chaining `dist` and `upload`), cycle 10
(the bump, the release sections dated by the pilot, the upgrading page's 0.9
section, `make dist`; the tag, the push and the upload the pilot's), and
"Held for the pilot" (the release day, the tag, the push, the upload, the
Read the Docs dashboard and the retirement of the mechanics and viewer
projects there, the original repositories on GitHub).

How 0.8.1 was released is the model (archive `2026-10-10-release-0-8-1`):
the five version files moved by hand, the changelog's `Unreleased` section
become the release's with an opening and the moves a project may follow,
`HISTORY.rst` given its entry, the release note given a section, the
upgrading page a first part, `context7.json` the release, the identity
literal moved, a release-only correction of a test that failed on a clean
checkout, and a handoff note for the pilot
(`packages/machinome/workflow/ongoing/release-0.8.1.md`, still in
`ongoing/`). 0.8.1 was tagged `v0.8.1` locally and never uploaded (probe 1);
0.9.0 follows it.

The records this change reads, at c5eeb038: `HISTORY.rst`'s `Unreleased`
holds fifteen bullets in the road's order, from `monorepo-layout` to
`viewer-command`; `manual-extras`, landing before this planning commit,
adds a sixteenth after them and one to the manual's changelog. The manual's
changelog has thirteen bullets under `Unreleased`; the upgrading page opens
with "Upgrading from Machinome 0.8 to 0.9", holding two subsections, "The
viewer flag" and "The viewer's command"; `docs/conf.py` states `release =
'0.8.1'`, `version = '0.8'`, `release_date = '10 October 2026'`,
`viewer_version = '0.8.1'`, `viewer_api = '29'`, `document_versions = '1 to
13'` and `mechanics_version = '0.1.0'`. The viewer's `CHANGELOG.md` has an
`Unreleased` section over `0.8.1 — 10 October 2026`; the movie's holds its
whole history under `Unreleased` (it was `0.0.0` in its own repository and
never numbered); the studio's holds its whole history under `Unreleased`
(0.1.0 in its own repository, never published); the mechanics helpers' has
an `Unreleased` section over `0.1.0 — 23 September 2026`; the skills keep no
changelog. The README states no version and a test pins that.

### Probes

All on scratch copies under
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C13-propose/`
(`<scratch>`), on 12 and 13 October 2026; nothing was written in the bench but
this change's directory. The copy `<scratch>/day/` is `git archive` of the
bench's c5eeb038 with the 34 tracked files the ignore rules match added with
`git add -f` (6145 files, the bench's count), made a Git repository of one
commit, 572b810. `make sync` there: "Resolved 201 packages", "Installed 192
packages", "added 229 packages", Chromium cached, exit 0, 29 s
(`<scratch>/p1-sync.out`). The scripts that applied each half are
`<scratch>/prep.py`, `<scratch>/prep2.py` and `<scratch>/day.py`, the texts
they placed `<scratch>/texts/`; they are evidence, not the implementation.

1. **The index.** `https://pypi.org/pypi/<name>/json` for the eighteen
   distributions (`<scratch>/pypi-state.txt`): `machinome` holds 0.0.1,
   0.7.0, 0.7.1 and 0.8.0; `machinome-viewer` 0.7.0, 0.7.1 and 0.8.0;
   `machinome-mechanics` 0.1.0; the fifteen others answer 404. 0.8.1 is on
   no index.
2. **The mechanics tables before the hand step.** The two tables of
   Decision 3 appended to the copy's `.bumpversion.cfg`, the manifest still
   at 0.1.0. `make bump VERSION=0.9.0` on the uncommitted change: "make bump:
   the tracked files have changes; commit them first: M .bumpversion.cfg",
   exit 2 (`<scratch>/p2a-bump-dirty.out`). Committed, then `make bump
   VERSION=0.9.0`: bump2version stops before writing anything,
   `bumpversion.exceptions.VersionNotFoundException: Did not find 'version =
   "0.8.1"' in file: 'packages/machinome-mechanics/pyproject.toml'`, exit 2,
   the tree clean after it (`<scratch>/p2b-bump-tables-first.out`).
3. **The hand step, committed, then the bump.** On the copy reset to
   572b810: the mechanics manifest at `version = "0.8.1"` with
   `machinome~=0.8.1`, the core's extra `machinome-mechanics~=0.8.1`, the
   tables, `uv lock` ("Updated machinome-mechanics v0.1.0 -> v0.8.1"), one
   commit; then `make bump VERSION=0.9.0`: exit 0, 1.2 s, "29 files changed,
   97 insertions(+), 97 deletions(-)" (`<scratch>/p3-bump.out`,
   `<scratch>/p3-diffstat.txt`): `.bumpversion.cfg`, the eighteen
   manifests, the core's `machinome/__init__.py`, `docs/conf.py` (`release`
   and `viewer_version`), `machinome/vet/universe.toml`, the viewer's
   `__init__.py` and widget `package.json`, the movie's `js/package.json`
   and its own lock, the studio frontend's `package.json`, the root's
   `package-lock.json` (its three member entries) and `uv.lock` (36 lines).
   `make -s version`: 0.9.0; `git log`: no new commit; `git tag`: none.
   Node 24.11.1 printed `EBADENGINE` warnings for four test dependencies
   (jsdom among them) that want Node `^22.22.2 || ^24.15.0 || >=26.0.0`;
   the locks were written.
4. **What still says 0.8.1 after the bump** (`git grep` of tracked files,
   the release records, archives, workflow and ADRs set aside;
   `<scratch>/p3-leftovers.txt`): `context7.json` (2 lines), the viewer's
   own specs `user-documentation` ("The manual states the 0.8.1 release")
   and `viewer-distribution` (its version paragraph), the viewer's
   `tests/test_documentation.py` (4 lines), the manual's
   `reference/viewer/cli.rst` (the `describe` example's `"version"`), the
   framework's `user-documentation` spec (the 0.8.1 requirement),
   `tests/test_machinome_identity.py` (the version literal) and
   `tests/test_viewer_documentation_links.py` (two references to the 0.8.1
   upgrading part, which stay true).
5. **The tests that would fail on the day if nothing were prepared.** The
   base's forms of six tests put back on a worktree of the dated copy of
   probe 9 (77d1002) and run there (`<scratch>/p10-unprepared.out`): each
   fails. The identity test (`'0.9.0' != '0.8.1'`);
   `test_viewer_documentation_links.py::test_no_current_page_spells_the_former_flag`
   (`current_text` raises `ValueError` on `text.index('Unreleased')`); the
   viewer's `test_the_manual_states_the_release` (its literal `0.8.1 — 10
   October 2026`); the movie's
   `test_the_changelog_has_an_unreleased_section_with_this_change`; the
   studio's `test_the_changelog_records_the_join`; the mechanics package's
   `test_the_changelog_states_the_release` (its newest release 0.9.0, not
   0.1.0). With their prepared forms all six pass on the same tree
   (probe 7).
6. **The preparation, red then green.** `prep.py` and `prep2.py` applied to
   the copy (Decisions 3 to 5). Their tests copied onto a worktree of
   572b810 and run there (`<scratch>/red/`): 20 failed, 17 passed, each
   failure a mechanics fact (the member not numbered with the core, the two
   floors not `~=`, the manifest outside the tables, the two tables absent,
   the boundary test's extra) or a move the upgrading part does not yet
   spell (seventeen subtests). On the prepared copy, the core's
   documentation and records tests 141 passed; the mechanics package's
   suite 204 passed; the viewer's `test_documentation.py` 12, the movie's
   `test_repository.py` 17, the studio's `test_documentation.py` 23 passed
   (`<scratch>/p4-prep-green.out`).
7. **The day, red then green.** The prepared copy committed, then `make
   bump VERSION=0.9.0` (29 files, as probe 3; `<scratch>/p5-bump.out`).
   Undated, the release-records test failed on context7, the four
   products' changelogs, the changelog's first release section, the
   history's top entry and the release note's page, and the viewer's test
   on its release section and its `describe` example
   (`<scratch>/p6-day-red.out`, 8 and 2 failed). With the records of
   Decision 7 placed at a stand-in date, 13 October 2026 (`day.py`), the
   core's documentation, records and tutorial tests 198 passed, 7312
   subtests, and the four products' tests as in probe 6
   (`<scratch>/p7-day-green.out`). `make docs`: "build succeeded.", no
   warning, 10.9 s (`<scratch>/p8-docs.out`); the status page and the
   release note read in the built HTML.
8. **`make check` on the dated copy** (`<scratch>/p9-check.out`): exit 0, 8 min 3 s; two passes, the tree and a clean copy of its
   tracked files, each "Every distribution built, checked, installed and
   smoked; nothing uploaded."; 72 `twine check` PASSED (36 archives a
   pass); the smoke line of each of the eighteen distributions reads 0.9.0
   in both passes, the mechanics helpers' among them, and no line of the
   output says 0.8.1; the core's sdist 1099 entries from the tree and 1092
   from the clean copy.
9. **`make dist`, `twine check`, `make -n upload` on the dated copy**,
   committed (`<scratch>/p11-dist.out`): the copy's records committed (77d1002, 39 files), `git status
   --porcelain` empty; `make dist`: "$ scripts/check-dist --out
   dist/v0.9.0, in a copy of the commit 77d1002", "36 archives kept in
   .../day/dist/v0.9.0", exit 0, 4 min 1 s; the folder holds the sdist
   and the wheel of the eighteen distributions at 0.9.0, flat
   (`<scratch>/p11-archives.txt`); `twine check --strict dist/v0.9.0/*`
   36 PASSED (`<scratch>/p11-twine.out`); no entry under a `_build`
   directory in any sdist or wheel. `make dist` again: "check-dist failed:
   .../dist/v0.9.0 exists and is not an empty folder; the archives of a
   release are kept in a new one", exit 2 (`<scratch>/p11-dist-again.out`).
   `make -n upload` prints the folder test and `.venv/bin/python -m twine
   upload dist/v0.9.0/*` and runs nothing; the glob puts
   `machinome-0.9.0-py3-none-any.whl` first. `make upload` was never run.
   `git tag` on the copy: none.
10. **Read the Docs.** `packages/machinome/.readthedocs.yaml` builds with
    Python 3.12 and Node 22, runs `npm ci` and the widget's build at the
    repository root before Sphinx, installs `packages/machinome/docs/requirements.txt`
    alone and fails on a warning; `make docs` runs the same steps (probe 7).
    Nothing of this change touches it; the dashboard's configuration path is
    the pilot's (`packages/machinome/.readthedocs.yaml`).
11. **The projects' pins.** The project repositories' manifests and
    requirement files (read only): every requirement on the set is a floor
    0.9.0 satisfies (`machinome>=0.6`, `>=0.7`, `>=0.7.1`,
    `machinome-mechanics>=0.1`, `machinome[viewer]>=0.6`) but two:
    `Robotic-Arms/Dum-E` requires `machinome[freecad]~=0.8.1`, which 0.9.0
    does not satisfy, and `Locks/designs` requires `machinome>=0.7,<0.8`,
    which 0.8 already did not. The universe sweep runs the projects on the
    bench's environment and reads no pin, so neither changes a row.
12. **The environment after the bump.** On the dated copy, before a sync,
    `importlib.metadata.version('machinome')` read 0.8.1 beside
    `machinome.__version__` 0.9.0, and the mechanics helpers' 0.1.0; the
    core's version-reading tests (`test_vet_universe.py`,
    `test_verdict_store.py`, `test_viewer_report.py`,
    `test_cli_contributed.py`, `test_machinome_identity.py`), the viewer's
    (`test_version.py`, `test_machinome_identity.py`, `test_bundle.py`) and
    the skills' suite passed all the same (94, 22 and 47). After `uv sync
    --python 3.12` the metadata read 0.9.0 for the core and the mechanics
    helpers, and the same tests passed again (`<scratch>/p12-venv.out`).
13. **Every package's tests on the dated copy**, after that sync: `make
    test` (`<scratch>/p13-make-test.out`): exit 0,
    17 min 32 s. The core 5024 passed, 9 skipped (viewer-command's 5023 and
    the one test the preparation adds net); the mechanics helpers 204
    passed; the skills 47; the viewer's widget 1715 tests passed, 2
    skipped, and its Python 252 passed, 2 skipped; the movie 322 and its
    Node `pure` and `stage` 329; the studio 485 passed, 24 skipped.
    `manual-extras` is not on this copy.

## Goals / Non-Goals

**Goals:**

- Every package of the set at 0.9.0 by one `make bump` from the root, the
  mechanics helpers included, every copy held by the release-records test.
- Every reader-facing record dated the day the pilot names: the history, the
  manual's changelog and release note, the status page, `context7.json` and
  the four products' changelogs.
- A 0.8 user finds every move of 0.9 on the upgrading page, with what to
  change.
- The archives the pilot uploads are built, checked and smoked by `make
  dist` from the commit the pilot tags, and the day is a short list the
  pilot runs.

**Non-Goals:**

- No tag, push, upload, dashboard or repository change on GitHub; no
  Context7 refresh. The pilot's.
- No change of behaviour, document version (1 to 13) or viewer API (29).
- No rewording of a bullet written as its change landed, but the one clause
  of the mechanics join bullet that the mechanics step makes false.
- The projects' pins (probe 11) and the workspace's records: their own
  repositories and the `workspace-consistency` cycle.

## Decisions

### 1. Two halves: the preparation, then the day

The planning commit carries this design with every text the day places.
After it, two kinds of work remain, and the tasks say which is which.

**Before the day**, one commit on the bench, "Prepare 0.9.0: the mechanics
helpers numbered with the set", made by an applier the orchestrator briefs,
reviewed and committed by the orchestrator: the mechanics step (Decision 3),
the tests (Decision 4), the upgrading page's 0.9 part and the installation
page's pointer to it (Decision 5), ADR-187's amendment (Decision 10), the
day note (Decision 9), and `evidence.md` begun. The suite is green at 0.8.1
after it; nothing in it needs the date. It is not integrated into `main`
alone.

**On the day**, a fresh agent briefed with the pilot's date makes one
commit, "Release 0.9.0" (Decisions 2, 6, 7). The orchestrator fast-forwards
`main` to it and runs `make dist`; the change is archived after it (Decision
6). The pilot then runs the day note's steps.

Alternative rejected: everything on the day. It is possible, but the
mechanics step must still be a commit of its own before the bump (probe 2),
so the day would carry two implementation commits and the most intricate
edits of the change, the only ones that touch code and specs, would be made
under the release's clock.

### 2. The day's commands, in order

From the bench root, on its synced venv, the tree clean at the preparation's
head (or the line's, if the orchestrator rebased it):

1. `git status --porcelain` empty; `make -s version` prints 0.8.1.
2. `make bump VERSION=0.9.0`: the 29 files of probe 3; `make -s version`
   prints 0.9.0. Then `uv sync --python 3.12` at the root, so that the
   installed metadata of the editable members read 0.9.0 (they read 0.8.1
   and the mechanics helpers 0.1.0 until it, probe 12; no test failed on
   the stale venv, but the suite then runs on what CI installs).
3. The release-records test and the products' documentation tests, red
   (probe 7's failures, each naming a record not yet dated).
4. The records of Decision 7 placed with the date.
5. The same tests green; `make test` whole (every package with tests);
   `make docs`; `make lint` compared with the base (its findings are
   CI's `continue-on-error`).
6. `make check`: every archive at 0.9.0 from the tree and from a clean
   copy of its tracked files, every smoke line reading 0.9.0.
7. `git status --short` lists only the bump's files and the records;
   `evidence.md` and `tasks.md` updated; the one commit.

`make dist` is not the applier's: it runs after the orchestrator's
fast-forward, in the checkout the pilot uploads from (Decision 6).

### 3. The mechanics helpers numbered with the set, before the day

`make bump` refuses a dirty tree, and bump2version refuses a table whose
search it cannot find (probe 2). The mechanics helpers therefore join the
set's number in a commit of their own before the bump, at the set's current
version, 0.8.1, so that the one bump of the day moves them with every
package, as decision 2 says:

- `packages/machinome-mechanics/pyproject.toml`: `version = "0.8.1"`, its
  comment saying the set's version is moved by the root's
  `.bumpversion.cfg` (change `release-0-9-0`; its own 0.1.0 until then);
  `dependencies = ["machinome~=0.8.1"]`, its comment the core of the set's
  own release.
- `packages/machinome/pyproject.toml`: `mechanics =
  ["machinome-mechanics~=0.8.1"]`, its comment "numbered with the set".
- `.bumpversion.cfg`: after the studio's tables, the two tables of a package
  with pins, as the skills' and the OpenSCAD viewer's:

  ```ini
  [bumpversion:file(version):packages/machinome-mechanics/pyproject.toml]
  search = version = "{current_version}"
  replace = version = "{new_version}"

  [bumpversion:file(pins):packages/machinome-mechanics/pyproject.toml]
  search = ~={current_version}"
  replace = ~={new_version}"
  ```
  The core's own pins table already moves its `mechanics` extra once it is
  `~=`.
- `uv lock`: "Updated machinome-mechanics v0.1.0 -> v0.8.1".
- `scripts/check-dist`: `MECHANICS_VERSION` and its comment gone; the
  mechanics row asserts the distribution's version equal to
  `metadata.version('machinome')`, `machinome~={version}` among its
  requirements and the core's requirement starting
  `machinome-mechanics~={version}`; still installed from its own wheel by
  path.
- `docs/conf.py`: `mechanics_version`, its comment and its substitution
  line gone. Every page that still states `|mechanics_version|` on the
  closed head states `|release|`, the framework's version
  (`reference/api.rst`, `reference/mechanics/index.rst`, and
  `start/install.rst` if `manual-extras` left the phrase), but the
  upgrading page's 0.7 part, a record of the 0.7 release, which states the
  literal `0.1.0`. The status page's sentence is rewritten on the day
  (Decision 7); before it, "Machinome Mechanics, numbered with the
  framework, is the optional helper package behind the ``mechanics``
  extra."
- `context7.json`: "(the distribution machinome-mechanics, at its own
  version)" becomes "(the distribution machinome-mechanics, numbered with
  the framework)".
- The records: `HISTORY.rst`'s mechanics join bullet loses "its own version"
  ("It keeps its changelog, its specs and its tests in its directory"), and
  one bullet is added last under `Unreleased`; the manual's changelog gains
  one bullet; the mechanics changelog's join bullet says "is numbered with
  Machinome, requiring the matching release" where it said "requires
  Machinome 0.8 or newer" (texts in Decision 7).
- The mechanics package's own specs, brought current in place as
  `viewer-command` did the viewer's: `distribution` ("It SHALL declare
  `machinome~=<version>`, the version being Machinome's own, as its runtime
  dependency"; its scenario "The release pair is legible" naming 0.1.0 as
  released with Machinome 0.7.0 and the package numbered with Machinome
  since 0.9.0) and `user-documentation` (its scenario "A user reads which
  version they have": the manual and the changelog name the framework's
  version, the changelog's 0.1.0 section stating 0.1.0 released with
  Machinome 0.7.0).
- ADR-187 amended (Decision 10).

Alternatives rejected. **The same commit on the day, before the bump**:
the same content, but two implementation commits on the day; kept as the
fallback if the orchestrator keeps the step on the day (Open Questions 7).
**By hand after the bump**: the mechanics manifest moved to 0.9.0 and the
tables added at 0.9.0, in the day's one commit. The end state is the same,
but the one bump would not have moved the mechanics helpers, which
contradicts decision 2's "in one bump from the root's `.bumpversion.cfg`,
mechanics ... included", and the tables would first be read by a bump at
0.10.

### 4. The tests: no literal version, and the day's expectations

Every test that pinned 0.8.1, a mechanics floor or an `Unreleased` heading
is rewritten in the preparation to read the set's version and to accept
either state of a record, so that it is green at 0.8.1 before the day and at
0.9.0 after it; the release-records test gains the one expectation the day
must meet, dormant until the set's version reaches it. Probe 5 lists what
fails on the dated tree without this; probe 6 the red before it, probe 7
the red and the green of the day.

| Test | Before the preparation | After it |
|---|---|---|
| `tests/test_release_records.py` | `OWN_VERSION`, the floor branch, `test_a_member_of_its_own_version_is_outside_the_bump` | no exception: every member numbered with the core, every pin `~=`, every manifest in the tables; `test_the_mechanics_helpers_are_bumped_with_their_two_pins` (the two tables, and no `mechanics_version` in `docs/conf.py`); `PRODUCTS` and `test_each_product_records_the_release` (below); the docstring |
| `tests/test_mechanics_boundary.py` | `["machinome-mechanics>=0.1.0"]` | `[f"machinome-mechanics~={project['version']}"]` |
| `tests/test_docs_structure.py` | `mechanics_version` among the facts; `test_the_mechanics_version_is_the_package_s` | neither; `UpgradingPageTest.test_the_0_9_part_names_every_move` (Decision 5) |
| `tests/test_machinome_identity.py` | `'0.8.1'` | `current_version` of the root's `.bumpversion.cfg` |
| `tests/test_viewer_documentation_links.py` | `current_text` finds the changelog's current section by `text.index('Unreleased')`, a `ValueError` once it is dated | the first dashed section, `Unreleased` or `Machinome <version>` |
| `tests/test_repository_layout.py` | docstring: the mechanics helpers "at its own version" | the helpers among the products numbered with the set |
| viewer `tests/test_documentation.py` | the first release section starts `0.8.1 — 10 October 2026`, names `Machinome 0.8.1`, "published 0.8.0 renumbered" and "viewer API 29"; the manifest `'0.8.1'` | it starts `<version> — <release_date>` from the manifest and `docs/conf.py`, names `Machinome <version>`, the widget's API and document versions; the manifest equals `viewer_version` |
| movie `tests/test_repository.py` | `'## Unreleased' in text` | the first section is `Unreleased` or `<version> — ` |
| studio `tests/test_documentation.py` | `sections[0].startswith("Unreleased")` | `Unreleased` or `<version> — ` |
| mechanics `tests/test_documentation.py` | the newest release is 0.1.0 and equals the manifest | the 0.1.0 section holds its date and Machinome 0.7.0; the manifest's version is the records test's |
| mechanics `tests/test_machinome_identity.py` | `['machinome>=0.8.0']` | `[f"machinome~={project['version']}"]` |

The day's expectation, in `tests/test_release_records.py`:

```python
#: The products that keep a changelog of their own, by directory, and the
#: first version of the set each is released at: the viewer is numbered with
#: the set since 0.7.0; the mechanics helpers, the films and the studio first
#: release with it at 0.9.0 (changes `join-viewer`, `join-movie`,
#: `join-studio`, `release-0-9-0`).
PRODUCTS = {'machinome-viewer': '0.7.0', 'machinome-mechanics': '0.9.0',
            'machinome-movie': '0.9.0', 'machinome-studio': '0.9.0'}
```

`ReleaseRecordsTest.test_each_product_records_the_release`: for each
product whose first version is at or below the set's, the changelog's
newest release section is `<version> — <d Month YYYY>`, the date
`release_date`'s, with at most one `Unreleased` section and only above it.
At 0.8.1 it holds the viewer alone, which records `0.8.1 — 10 October 2026`
(green); after the bump it holds all four, red until their sections are
dated (probe 7); a later patch holds every product to it. The other day
expectations already exist and derive from `current_version`: the
changelog's first release section, the history's top entry, the release
note's page (a `.0` release opens `docs/releases/release-<major>.<minor>.rst`,
whose title names the line), `context7.json`, the viewer extras' pins, the
matching viewer, and every copy and lock.

Alternative rejected: the day's expectations written before the day and
red on the bench until it. A red suite at the head the orchestrator commits
is a red line, and the dormant form is red on the day exactly where the
records are missing.

### 5. The upgrading page's 0.9 part

Under the title "Upgrading from Machinome 0.8 to 0.9", its label and its
`.. needs:: none` (from `manual-extras`), before the subsection "The viewer
flag", which stays with "The viewer's command" as the seam and the command
cycles wrote them:

```rst
Machinome 0.9 brings the packages that grew beside the framework into its
repository and its release, and moves the ones that had addresses of their
own under ``machinome``, without aliases: a former spelling fails where it
is used, naming what to write instead. These are the moves a 0.8 project
makes, and what to change for each. A project's machines, tests and exports
are otherwise unchanged: exports keep document versions 1 to 13, and a 0.8
viewer reads a 0.9 export.

#. **Install the extra of every node type you use.** A bare ``pip install
   machinome`` carries no node type: ``StlNode`` and ``JScadNode``, which
   came with the framework in 0.8, need ``machinome[stl]`` and
   ``machinome[jscad]``, and without them the import names the line that
   installs them. :doc:`/start/install` lists every extra.
#. **Import the helpers and the viewer from their addresses.**
   ``machinome_mechanics`` is ``machinome.mechanics`` and
   ``machinome_viewer`` is ``machinome.viewer.web``; names, signatures and
   formulas are unchanged, and no module of a former name is installed.
   A script that ran ``python -m machinome_viewer`` runs ``machinome
   viewer``.
#. **Install every package at the framework's release.** Each extra
   installs the package of Machinome's own release, ``mechanics`` among
   them: ``machinome-mechanics``, 0.1.0 until now, is numbered with the
   framework, so a project that pinned it drops the pin and names the
   ``mechanics`` extra. ``pip install --upgrade "machinome[...]"`` with
   your extras moves the set together.
#. **Name the viewer of a still with** ``--viewer``. ``--renderer`` is
   refused, naming ``--viewer``, and the OpenSCAD viewer is installed by
   ``machinome[viewer-openscad]``, ``[openscad]`` or ``[solid2]``; see
   :ref:`upgrade-viewer-flag`.
#. **Run the commands of** ``machinome``. ``machinome-viewer describe``,
   ``serve`` and ``capture`` are ``machinome viewer describe``, ``serve``
   and ``capture`` (:ref:`upgrade-viewer-command`), and the entry point
   ``machinome.viewer`` is gone: a host reads ``machinome viewer``.
#. **Run the studio and the films through** ``machinome`` **if you ran them
   from their repositories.** The ``machinome-studio`` command is
   ``machinome studio``, with the same options and configuration file, and
   the studio's package ``floor`` is ``machinome.studio``
   (:ref:`studio-command`); the videomaker is ``machinome movie``, installed
   by ``machinome[movie]`` and ``machinome movie setup`` (:ref:`movie-command`).
#. **Expect one rebuild after upgrading.** A node is rebuilt only for edits
   to what it names in its sources, but the first edit after the upgrade is
   judged by the earlier rule and rebuilds what it would have; the edits
   after it are spared. Nothing is to be run by hand.
```

What it leaves unspelled, and why: the films' former module
(`test_no_page_shows_the_videomaker_s_former_command_lines` allows it on one
changelog line alone), the videomaker's former command line (the same test
forbids it everywhere), `python -m floor` and the FreeCAD adapter's former
module (`STALE`, refused on the upgrading page). The changelog keeps their
records; the part names the studio's former package as ``floor`` and the
videomaker by name. The studio, the films and the FreeCAD adapter were never
published, so a 0.8 project from the index met none of them.

`UpgradingPageTest.test_the_0_9_part_names_every_move` holds the part
(between its title and "Upgrading from Machinome 0.8.0 to 0.8.1") to
spelling: `machinome[stl]`, `machinome[jscad]`, the mechanics helpers' and
the viewer's former and new modules, `machinome-mechanics`,
``` ``--renderer`` ```, ``` ``--viewer`` ```, `machinome[viewer-openscad]`,
`machinome-viewer describe`, `machinome viewer describe`,
`machinome.viewer`, `machinome-studio`, `machinome studio`,
``` ``floor`` ```, `machinome.studio`, `machinome movie`,
`machinome[movie]` and the two subsections' references. Red on the base
(probe 6: seventeen subtests), green with the part.

The installation page's "Upgrading" section, before the day:

```rst
Coming from Machinome 0.8? Read :doc:`/project/upgrading` first: 0.9
releases every package of the set together and moves the mechanics helpers
and the viewer under ``machinome``, with no aliases. Coming from 0.7, the
same page lists the moves of 0.8: the kernels in extras, every name imported
from its module and the engines' flags renamed. Coming from solid-node 0.6
or earlier, it maps the names renamed for 0.7; a 0.5 environment must be
recreated rather than upgraded in place.
```

### 6. The commit, the integration, `make dist`, the archive, the tag

- **The day's commit** is one, "Release 0.9.0", holding the bump's 29
  files and the records of Decision 7, with `evidence.md` and `tasks.md`
  updated; nothing else. The applier pauses before it; the orchestrator
  reviews and commits.
- **The integration** is the orchestrator's: `main` fast-forwarded to
  "Release 0.9.0" (the line closed and merged into `main` before; the
  preparation reaches `main` with it).
- **`make dist`** runs in the checkout the pilot uploads from, the primary
  checkout at `main` after the fast-forward, whose `dist/` already holds
  `0.7.1-2026-09-27`, `0.8.0-2026-10-06` and `0.8.1-2026-10-10`: `make sync`
  there first (it has no `.venv` or `node_modules`), `git status
  --porcelain` empty, then `make dist`: `dist/v0.9.0`, 36 archives,
  `twine check --strict` on each; `make -n upload` prints the one twine
  line. Open Questions 8 is the alternative.
- **The archive** of this change follows, in one more commit on the bench:
  `evidence.md` with `make dist`'s record, the spec deltas synced, the
  change moved to `archive/<date>-release-0-9-0/`, ADR index untouched (the
  amendment is in the preparation), and the progress entry of
  `release-0.9.md` (cycle 10). It touches `packages/machinome/openspec/`
  and the root's `workflow/` alone, neither in any archive (the core's
  `MANIFEST.in` names neither), so the archives of `dist/v0.9.0` stay those
  of the release commit. The orchestrator fast-forwards `main` again.
- **The tag** is the pilot's, on "Release 0.9.0", the commit the archives
  were built from; CI's build job rebuilds from it.

### 7. The release sections, verbatim

`<date>` stands for the pilot's day in each record's form: `<d Month YYYY>`
(`13 October 2026`), `<YYYY-MM-DD>` (`2026-10-13`), `<dd/Mon/YYYY>`
(`13/Oct/2026`). The texts were placed on the copy at 13 October 2026
(probe 7); the applier re-derives the bullet lists from the head it works
on, adding any bullet landed after this planning commit in its place.

**`docs/conf.py`** (the bump moves `release` and `viewer_version`):
`version = '0.9'`, `release_date = '<d Month YYYY>'`; `viewer_api` stays
`'29'`, `document_versions` `'1 to 13'`.

**`HISTORY.rst`.** `Unreleased` with its dashes becomes `Machinome 0.9.0
(<YYYY-MM-DD>)` with 28 dashes; under it, before the first bullet, this
paragraph; the bullets stay in the road's order, `manual-extras`' and the
mechanics bullet last:

```rst
**One repository, one release.** The joins of the 0.9 road
(``workflow/ongoing/joins-0.9.md`` and ``workflow/ongoing/release-0.9.md``
at the repository root): the framework, its two engines and nine node
types, the OpenSCAD viewer, and the products that lived in repositories of
their own, the mechanics helpers, the browser viewer, the skills, the films
and the studio, are eighteen distributions of one repository under one
licence, GPL-2.0-or-later or CERN-OHL-S-2.0-or-later at the recipient's
choice, stated once at its root. Every package carries one version, 0.9.0,
declared once in ``.bumpversion.cfg``; ``machinome`` is the one command, to
which the films, the skills and the studio add theirs; the products' pages
are part of the one manual; and one release builds, checks and smokes every
archive into ``dist/v0.9.0``, uploaded in one command. Nothing in the
published document moves: exports declare document versions 1 to 13, and
the matching viewer 0.9.0 reads them with API 29. ADR-182 to ADR-196 are
new. Each item names the archived OpenSpec change that carries its
evidence.
```

The mechanics bullet, placed last under `Unreleased` by the preparation:

```rst
* **The mechanics helpers are NUMBERED WITH THE SET.**
  ``machinome-mechanics`` leaves the number of its own it kept at its join:
  the root's ``.bumpversion.cfg`` moves its version with every package's,
  its requirement on the framework and the ``mechanics`` extra are ``~=``
  pins both ways, and the manual states its version as the framework's.
  Its 0.1.0 stays the release it was. Change ``release-0-9-0`` (ADR-187
  amended).
```

**The manual's changelog.** `Unreleased` becomes `Machinome 0.9.0` with 15
dashes, then `Released on <dd/Mon/YYYY>`, then this, then the bullets as
written, in their order:

```rst
**One repository, one release.** Every Machinome package now comes from one
repository and one release: the framework, its engines and node types, the
mechanics helpers, the browser viewer and the OpenSCAD viewer, the skills
for assistants, the films and the studio, each installed by its extra and
all numbered 0.9.0. ``machinome`` is the one command, to which ``machinome
movie``, ``machinome skills`` and ``machinome studio`` belong beside
``machinome viewer``, and every page of this manual says which extras it
needs. A project's machines, tests and exports are unchanged: exports
declare document versions 1 to 13, and the matching viewer 0.9.0 reads them
with API 29.

**What a project may have to follow**, each with what to change on
:doc:`the upgrading page <upgrading>`:

- a project of ``StlNode`` or ``JScadNode`` parts installs
  ``machinome[stl]`` or ``machinome[jscad]``;
- ``machinome_mechanics`` and ``machinome_viewer`` are ``machinome.mechanics``
  and ``machinome.viewer.web``, with no alias;
- ``machinome-mechanics`` is numbered with the framework, and every extra
  installs the package of the framework's own release;
- ``--renderer`` is refused for ``--viewer``, and the OpenSCAD viewer of
  ``machinome snapshot`` is installed by ``machinome[viewer-openscad]``,
  ``[openscad]`` or ``[solid2]``;
- the ``machinome-viewer`` command is ``machinome viewer``, and the entry
  point ``machinome.viewer`` is gone;
- the studio and the films, run from their repositories until now, are
  ``machinome studio`` and ``machinome movie``.
```

Its mechanics bullet, placed last under `Unreleased` by the preparation:

```rst
* **The mechanics helpers are numbered with the framework.**
  ``machinome-mechanics`` takes the framework's version, and ``pip install
  "machinome[mechanics]"`` installs the helpers of the framework's own
  release, as ``machinome[viewer]`` installs its viewer
  (:ref:`upgrading-0-8-to-0-9`).
```

The toctree at the end of the 0.7.0 section gains `../releases/release-0.9`
above `../releases/release-0.8`.

**`docs/releases/release-0.9.rst`**, new (exempt from `.. needs::` as every
release note):

```rst
Machinome 0.9: one repository, one release
==========================================

Released on <d Month YYYY>.

Machinome 0.9 changes where the packages come from rather than what a
machine can say. The framework and every package that grew beside it, the
mechanics helpers, the browser viewer, the skills for assistants, the films
and the studio, are developed in one repository, released together under
one version and one licence, and documented in this one manual. The machine
you describe, the documents you publish and the verdicts your tests reach
are what they were in 0.8.

One repository
--------------

Each package is a directory of the repository, named as the distribution it
builds, and each installs as an extra of the framework: the node types and
the two engines as in 0.8, and ``machinome[mechanics]``,
``machinome[viewer]``, ``machinome[viewer-openscad]``,
``machinome[skills]``, ``machinome[movie]`` and ``machinome[studio]``. Each
is imported from its address under ``machinome``: ``machinome.mechanics``,
``machinome.viewer.web``, ``machinome.movie``, ``machinome.studio``. A bare
``pip install machinome`` is still the core alone, and now carries no node
type at all: a project of STL or JSCAD parts names its extra, as every other
node type's project does.

One version and one licence
---------------------------

Every package is numbered 0.9.0, and an extra installs the package of the
framework's own release, so ``pip install --upgrade "machinome[...]"`` moves
the set together. Every package is licensed |framework_licence|, at the
recipient's choice.

One command
-----------

``machinome`` learns its commands from the packages installed beside it.
``machinome viewer`` describes, serves and photographs through the browser
viewer; ``machinome movie`` makes a narrated film of a machine; ``machinome
skills`` installs the machinome skills where your assistants read them; and
``machinome studio`` opens the studio's project hub. ``machinome -h`` lists
every command an installed package adds, after the framework's own.

Viewers chosen by name
----------------------

A still, a development session and an export each use the viewer you name:
``--viewer web`` for the browser viewer, ``--viewer openscad`` for OpenSCAD,
or ``viewer = "web"`` under ``[tool.machinome]`` for the whole project. The
browser viewer serves and captures inside the command's own process, so a
rebuild reaches the open page without a reconnect.

Fewer rebuilds
--------------

A node is rebuilt only for edits to what it names in its sources: editing a
definition no node names restamps the parts instead of rebuilding them, so a
tuning edit to one part of a large machine no longer re-derives the rest.

One manual
----------

The pages of the browser viewer, the mechanics helpers, the films, the
skills and the studio are part of this manual, and every page says at its
top which extras it needs.

Upgrading
---------

0.9 moves and renames without aliases. :doc:`/project/upgrading` lists every
move a 0.8 project makes and what to change for each: the node types' extras,
the helpers' and the viewer's addresses, the viewer flag and the commands.
Exports keep document versions 1 to 13, read by the matching viewer 0.9.0
with API 29, so a 0.8 viewer reads a 0.9 export.

See :doc:`/project/changelog` for the complete list of what 0.9 brings.
```

**The status page.** The first paragraph:

```rst
Machinome |release| was released on |release_date|. It is the first release
of the Machinome set from one repository: the framework and every package
beside it are numbered |release|, licensed |framework_licence|, at the
recipient's choice, and released together from the `machinome GitHub
organisation <https://github.com/machinome>`_. It continues Machinome 0.8
and 0.7, the published continuation of solid-node 0.6.0 under the Machinome
name; the distribution, import package, command and configuration table are
all ``machinome``. The :doc:`upgrading page <upgrading>` lists every move
from 0.8 and every breaking change from 0.7, and maps the 0.6 names to the
new.
```

In "What |version| is", the second paragraph's first sentence: "A plain
installation is the core alone: each CAD kernel and node type is a package
of the set, installed by an extra named for the module that needs it
(:doc:`/start/install`), and every name is imported from the one module
that defines it."; the third paragraph's release note link is
`</releases/release-0.9>`. "Packages", its first paragraph:

```rst
Machinome is licensed |framework_licence|, at the recipient's choice, as
every package of the set. The browser viewer is the package
``machinome-viewer``, installed through the ``viewer`` extra; the framework
builds and tests without it, and interactive development requires it. The
mechanics helpers ``machinome-mechanics``, the skills ``machinome-skills``
and the films ``machinome-movie`` are optional packages behind the
``mechanics``, ``skills`` and ``movie`` extras. All are numbered and
released with the framework.
```

Its paragraph on running documents stays as it is (it holds "profile
contact" and "schema 13", which `test_profile_documentation.py` reads). Its
studio paragraph:

```rst
Machinome Studio is the package ``machinome-studio`` of the set, installed
by the ``studio`` extra (:doc:`/reference/studio/index`). It is
experimental: its roles, prompts and disciplines are exercised and revised
on real projects. It runs on Linux only. Browser-delivery experiments are
not a released capability.
```

"Direction":

```rst
The node types, the engines and the products that grew beside the framework
are packages of one repository, released together. Further work follows
findings from real machines: performance on larger assemblies, inspection,
and mechanical contracts. These are directions, not promised release
features.
```

**`context7.json`.** The first rule's opening, "Machinome 0.8.1 (released
2026-10-10) corrects 0.8.0 (2026-10-05), which continues 0.7.1
(2026-09-27);", becomes "Machinome 0.9.0 (released <YYYY-MM-DD>) is the
first release of the Machinome set from one repository: the framework and
every package beside it under packages/, numbered 0.9.0 under one licence,
with machinome as the one command. It follows 0.8.1 (2026-10-10), which
corrects 0.8.0 (2026-10-05), which continues 0.7.1 (2026-09-27);", the rest
unchanged; "The matching viewer is 0.8.1, API 29," becomes "The matching
viewer is 0.9.0, API 29,".

**The products' changelogs.** In each, `## Unreleased` and its blank line
become the heading and paragraph below; the entries under it stay as
written.

The viewer:

```markdown
## 0.9.0 — <d Month YYYY>

Released with Machinome 0.9.0 and numbered with it, the first release of
the viewer from the Machinome repository. It still declares viewer API 29
and reads document versions 1 through 13; what changed is where it lives,
how Machinome reaches it and the command that runs it.
```

The mechanics helpers:

```markdown
## 0.9.0 — <d Month YYYY>

Released with Machinome 0.9.0 and numbered with it: the helpers follow
0.1.0 with the set's version, and `pip install 'machinome[mechanics]'`
installs the helpers of the framework's own release. Names, signatures and
formulas are those of 0.1.0.
```

The films:

```markdown
## 0.9.0 — <d Month YYYY>

The first release of Machinome Movie, released with Machinome 0.9.0 and
numbered with it. Until it joined the Machinome repository it was the
videomaker, kept in a repository of its own from 19 September 2026 and
never published or numbered; the entries below record its whole history.
```

The studio, whose preamble, "All notable changes to Machinome Studio. The
first section describes the current source; when a release is cut it
becomes that release's section and a new `Unreleased` section opens above
it.", becomes "All notable changes to Machinome Studio, numbered with
Machinome. Work after a release is recorded as it lands, in one
`Unreleased` section above that release's section.", since no empty
`Unreleased` section is opened:

```markdown
## 0.9.0 — <d Month YYYY>

The first release of Machinome Studio, released with Machinome 0.9.0 and
numbered with it. It was developed in a repository of its own, where it
stood at 0.1.0 and was never published.
```

**The viewer's `describe` example** (`docs/reference/viewer/cli.rst`):
`"version": "0.9.0"`, which the viewer's
`test_describe_example_matches_package_versions` holds to the package.

**The viewer's own specs**, in place: `user-documentation`'s "The manual
states the 0.8.1 release" becomes "The manual states the 0.9.0 release",
machinome-viewer 0.9.0 released with Machinome 0.9.0 on the day, its
changelog's newest section `0.9.0 — <d Month YYYY>`, API 29 and document
versions 1 to 13 unchanged; `viewer-distribution`'s version paragraph says
0.9.0, released with Machinome 0.9.0. Its `0.8.1` scenarios become 0.9.0's.

### 8. What the release-records test holds on the day

Every copy of the version at 0.9.0, read from `current_version`: the
eighteen manifests and their pins (`~=0.9.0` both ways), the core's
`__init__.py`, `universe.toml` and `docs/conf.py`'s `release`; the viewer's
`__init__.py`, widget `package.json` and root lock entry; the movie's
`js/package.json`, its own lock's two root entries and the root lock's
entry; the studio frontend's `package.json` and root lock entry;
`viewer_version` equal to `release`, the `viewer` and `web-snapshot` extras
`~=` it; the `[bumpversion]` section holding `current_version` alone; every
manifest in the tables, the mechanics helpers' in two after the studio's.
Dated: the changelog's first release section `Machinome 0.9.0` with
`Released on <dd/Mon/YYYY>` and no `unreleased` in it; the history's top
entry `Machinome 0.9.0 (<YYYY-MM-DD>)`, nothing `Unreleased` above it;
`docs/releases/release-0.9.rst`, titled `Machinome 0.9...`, holding the
date; `context7.json`'s `Machinome 0.9.0 (released <YYYY-MM-DD>)` and `The
matching viewer is 0.9.0, API 29`; the status page free of "unreleased",
"current source" and "since |release|"; the four products' newest sections
dated. `uv.lock` is not read by the test; `uv sync --locked` in CI is its
check, and probe 3 shows `make bump` writes it.

### 9. The pilot's day note

`workflow/ongoing/release-0.9.0-day.md` at the repository root, beside
`release-0.9.md`, whose campaign it closes: a set's release spans the
packages, and the root's `workflow/` holds what spans them
(`workflow/README.md`). 0.8.1's note stays in the framework's
`workflow/ongoing/`, where its single-package release put it. Written by the
preparation, so the pilot reads it before naming the day; the day's commit
leaves it as is and the archive commit leaves it in `ongoing/` until the
pilot's steps are done. Its text, with `<prep date>` the preparation's day:

```markdown
# Machinome 0.9.0: the release day

Status: working record, written <prep date> by the OpenSpec change
`release-0-9-0` (bench `v0.9-release`). Not ratified; the change's archive
is the authority for what was released. Every step under "The pilot's
steps" is the pilot's: no agent tags, pushes or uploads.

## Where the release stands

The bench `v0.9-release` holds the set at 0.8.1, with the mechanics helpers
numbered with it, the release's tests and the upgrading page's 0.9 part, in
the commit "Prepare 0.9.0: the mechanics helpers numbered with the set",
which reaches `main` with the release. When the pilot names
the day, the orchestrator briefs a fresh agent with the date; it bumps the
set with `make bump VERSION=0.9.0`, dates the records, runs the tests,
`make docs` and `make check`, and leaves one commit, "Release 0.9.0". The
orchestrator reviews it, fast-forwards `main` to it and runs `make dist` in
the primary checkout, which keeps the archives in `dist/v0.9.0` beside the
earlier releases' folders; then it archives the change and records the
progress. Nothing is tagged, pushed or uploaded by then.

## The pilot's steps

1. **Read the folder.** `ls dist/v0.9.0` in the primary checkout: 36
   archives, the sdist and the wheel of each of the eighteen packages at
   0.9.0, each checked with `twine check --strict` by `make dist`.
2. **Tag the release commit**, the commit "Release 0.9.0" the archives were
   built from: `git tag -a v0.9.0 <commit> -m "Machinome 0.9.0"`.
3. **Push `main` and the tag**: `git push origin main v0.9.0`. GitHub
   Actions runs the tests on the tag, checks that the tag names the set's
   version, builds the archives again with `make dist` and creates the
   GitHub release `0.9.0` with them attached. The other local tags
   (`v0.8.1`, `viewer-v0.7.0` to `viewer-v0.8.1`, `mechanics-v0.1.0`) are a
   separate choice.
4. **Upload**: `make upload` in the primary checkout uploads
   `dist/v0.9.0/*` with twine, in one go. Fifteen of the eighteen projects
   are new on PyPI (`machinome-movie`, `machinome-skills`,
   `machinome-studio`, `machinome-engine-brep`, `machinome-engine-mesh`,
   the nine `machinome-node-*` and `machinome-viewer-openscad`), so the
   token must be one that may create projects, not one scoped to
   `machinome`. The packages pin each other `~=0.9.0` both ways, so no
   order helps: `machinome[viewer]` and every other extra resolves once all
   are up. If the upload stops part way, `twine upload --skip-existing
   dist/v0.9.0/*` completes it.
5. **Read the Docs.** The project `machinome` reads its configuration at
   `packages/machinome/.readthedocs.yaml` (Admin, Settings, the path of the
   configuration file); build `latest` and activate `v0.9.0`. The build
   installs `docs/requirements.txt` and builds the viewer's bundle with Node
   22, as the file says. The projects `machinome-mechanics` and
   `machinome-viewer` there: retire, or point at the manual's sections.
6. **Context7**: refresh from `context7.json`.
7. **The original repositories on GitHub** (the mechanics helpers', the
   viewer's, the videomaker's, the skills', the studio's and the FreeCAD
   adapter's): a note pointing to `machinome/machinome`, archive, or leave.
8. **0.8.1**, if wanted: its archives are in `dist/0.8.1-2026-10-10/`,
   never uploaded. Uploading them is independent of 0.9.0; PyPI shows the
   highest version as the latest whatever the order.
```

### 10. The ADR: ADR-187 amended, nothing new

A release records a decision the pilot made; it decides no architecture.
The one architectural fact that moves is ADR-187's "It carries its own
version", which decision 2 ends, so ADR-187 is amended in the preparation.
Its status line becomes:

```markdown
**Status:** Accepted; a second product keeping its record in its directory, numbered with the set, amended 2026-10-12 by [ADR-188](ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md); its own version ended, the helpers numbered with the set from 0.9.0, amended <prep date> by change `release-0-9-0` (note below)
```

and a section is added at its end:

```markdown
## Amendment (<prep date>, change `release-0-9-0`)

On 12 October 2026, after the join, the pilot decided how Machinome 0.9.0 is
released (`workflow/ongoing/release-0.9.md` at the repository root, decision
2): every package is bumped to 0.9.0 in one bump from the root's
`.bumpversion.cfg`, the mechanics helpers included, which ends their own
version. "It carries its own version" no longer holds, and Option 2, the
set's version, is the outcome from 0.9.0. The manifest states the set's
version and two tables of `.bumpversion.cfg` move it, its version and its pin
on the core; the package requires `machinome~=<version>` and the core's
`mechanics` extra `machinome-mechanics~=<version>`; the manual states no
version of its own for the helpers (`mechanics_version` is gone, its pages
say `|release|`); `tests/test_release_records.py` holds them as every
member. `scripts/check-dist` still installs their wheel by path, and finds
its version and its pin the framework's. The consequence "the extra's floor
admits the published 0.1.0 of the former import" ends: a `~=` pin admits no
0.1.0. Their 0.1.0 stays the release it was. Everything else stands.
```

Its index line in `docs/adrs/README.md` gains ", amended by
`release-0-9-0` (numbered with the set from 0.9.0)" after "amended by 188".
ADR-182, ADR-183 and ADR-192 are not edited: their amendments by ADR-187
name the exception, and ADR-187's amendment ends it.

### 11. The spec deltas

- `user-documentation`: ADDED "The 0.9.0 release is recorded"; MODIFIED
  "The 0.8.1 release is recorded" (kept as a released record below the
  later release; the scenario on work landing after it moves to 0.9.0's;
  the viewer-extra scenario dropped, since 0.9.0 moves the pins), "The
  0.8.0 release is recorded" (the mechanics version leaves the release
  facts), "The mechanics helpers are documented in the manual" (their
  version through `|release|`), "The studio is documented in the manual"
  (no "no index serves it" once the release that includes the studio is
  recorded).
- `framework-identity`: MODIFIED "Extras select independent Machinome
  products" (the `mechanics` extra `~=`; the studio's publication clause
  ends at its release; the scenario "A reader asks for the studio extra
  before publication" replaced by "The status page records the studio as
  released", and "The mechanics extra pins the framework's release"
  added) and "The framework is the package directory `packages/machinome`
  of a monorepo" (one version without the mechanics exception; "The
  mechanics helpers carry their own version" replaced by "The mechanics
  helpers are numbered with the set"; the smoke scenario's version and
  pins).
- `mechanics-distribution`: MODIFIED "Framework independence from mechanics
  helpers" (the extra `~=` the framework's version).
- `release-tooling`: unchanged.

### 12. Validation

Before the day: the red of probe 6 and its green on the bench; `make test`
whole (the core, the mechanics helpers, the skills, the viewer, the films,
the studio); `make docs`; `make check` (36 archives from the tree and 36
from the clean copy, the mechanics row reading the framework's version).
No universe sweep: no import a project makes moves, and the sweep reads no
pin (probe 11).

On the day: the red and green of probe 7 on the bench; `make test` whole;
`make docs` (the manual at 0.9.0, the status page, the changelog, the
release note and the upgrading page read in the built HTML); `make check`;
after the fast-forward, `make dist` and `make -n upload` in the primary
checkout. No universe sweep: the bump moves no import, and the projects'
pins are not read by it (probe 11); the orchestrator may run it on the
closed line before the planning commit, as the close does.

## Risks / Trade-offs

- [The fifteen new project names on PyPI] → the upload creates them; a
  token scoped to one project cannot. The day note says so; `twine upload
  --skip-existing` completes a partial upload.
- [`~=` both ways] → no wheel of the set resolves its extras until all are
  on the index. One `make upload` puts them up in one run; nothing depends
  on the order.
- [The mechanics helpers at 0.8.1 on the bench between the preparation and
  the day] → a number the helpers never released, as the films, the skills
  and the studio carry it; nothing is built from it for upload, and `main`
  receives it only together with "Release 0.9.0".
- [A cycle lands between the preparation and the day] → the applier
  re-derives the bullet lists from the head (Decision 7) and the day's red
  names any record left behind.
- [Node 24.11.1 on this machine is below the engines four test
  dependencies ask] → `npm install --package-lock-only` warns and writes the
  locks (probe 3); CI and Read the Docs use Node 22.
- [`Robotic-Arms/Dum-E` pins `machinome[freecad]~=0.8.1`] → a fresh install
  of that project from its manifest refuses 0.9.0. Its repository's move,
  after the release, not this change's.

## Migration Plan

The pilot names the day. The orchestrator briefs a fresh applier with the
date; it runs Decision 2 and stops before its commit; the orchestrator
reviews, commits "Release 0.9.0", fast-forwards `main`, runs `make sync`
and `make dist` in the primary checkout, then has the archive commit made
and fast-forwards again. The pilot runs the day note. Rollback before the
tag: `main` reset to the preparation by the pilot, `dist/v0.9.0` removed;
after the upload, a release on PyPI cannot be replaced, only followed by
0.9.1.

## Open Questions

1. **The ADR.** Recommendation: ADR-187's amendment alone (Decision 10); a
   release decides no architecture, and the one decision that moves is
   ADR-187's.
2. **The history section's order.** The road's order, as the bullets were
   written, or grouped by package. Recommendation: the road's order with
   the opening paragraph (Decision 7); it is the order the decisions and
   ADRs were taken in, and each bullet names its change.
3. **The films' and the studio's first numbered sections.** Whether to
   name their former numbering. Recommendation: one sentence each, as
   drafted: the studio "stood at 0.1.0 and was never published", the
   videomaker was "never published or numbered", so a reader of the
   former repositories is not misled and no unpublished version is
   presented as a release.
4. **The upload order.** Recommendation: none; `~=` both ways means every
   wheel at once, and `make upload` uploads the folder in one run. The
   0.8.1 note's "upload the viewer first" does not carry over.
5. **Where the pilot's day note lives.** Recommendation: the root's
   `workflow/ongoing/release-0.9.0-day.md` (Decision 9).
6. **The day's applier.** Recommendation: a fresh agent, briefed by the
   orchestrator with the date and this design, as the brief says.
7. **The mechanics step before the day or on it.** The brief placed it on
   the day; probe 2 shows it must be a commit before the bump either way.
   Recommendation: before the day, in the preparation commit (Decision 3),
   so the day keeps one implementation commit; else the same content as
   the first of two commits on the day.
8. **Where `make dist` runs.** Recommendation: the primary checkout after
   the fast-forward, where `make upload` then runs and the earlier
   releases' folders are (Decision 6); it writes only ignored paths
   (`.venv`, `node_modules`, `dist/v0.9.0`). The alternative, the bench,
   leaves the archives in a worktree that is removed at cleanup.
9. **The projects' pins.** The brief expected none; probe 11 found
   `Robotic-Arms/Dum-E`'s `machinome[freecad]~=0.8.1`, which refuses 0.9.0
   on a fresh install, and `Locks/designs`' `<0.8`. Recommendation: a
   project move after the release (Dum-E to `~=0.9.0` or a floor), in its
   repository, held for the pilot; the sweep is unaffected.
