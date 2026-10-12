# Evidence — write-the-studio-manual

Filled in as the increments land; the reviewer reads it instead of
re-running the cycle. A command without its output, a red step recorded only
as "failed", is not evidence.

## 0. Baseline

Worktree: `machinome-studio/WTs/write-the-manual`, branch `write-the-manual`,
starting head `c912033` ("Relicense Machinome Studio as AGPL-3.0-or-later"; the
history was rewritten by the pilot while the cycle opened, and the branch was
rebased with it: `git merge-base main write-the-manual` is main's head).

Studio suite in the primary checkout before the change (workspace venv,
Python 3.12.3):

```
$ python -m unittest discover -s tests
Ran 341 tests in 151.164s
OK (skipped=1)
```

Sibling manuals built for link verification (both exit 0):

```
$ python -m sphinx -b html -q docs docs/_build/html      # in machinome/
$ python -m sphinx -b html -q docs docs/_build/html      # in machinome-viewer/
```

## 1. Red

`tests/test_documentation.py` against the tree before the manual existed
(planning commit `9cbbd00`):

```
$ python -m unittest tests.test_documentation
Ran 19 tests in 0.022s

FAILED (failures=8, errors=16)
```

Every test of the module failed or errored: the pages, `docs/conf.py`,
`docs/requirements.txt`, `.readthedocs.yaml`, `workflow/`, `CHANGELOG.md`
absent; `docs/shop-history.md` present; the `floor` docstring
("Local shop-floor FastAPI application.") naming neither the product nor
its launcher; the README saying "not published to any package index". The
25 FAIL/ERROR lines are in the raw log kept beside this record during the
cycle (`docs-test-red.log`), and the first two failures were:

```
EEEEEEFFFFFFEFEFEEEEEEEE
======================================================================
ERROR: test_no_caveat_outside_the_status_page (tests.test_documentation.CaveatTest.test_no_caveat_outside_the_status_page)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/asa/devel/machinome/machinome-studio/WTs/write-the-manual/tests/test_documentation.py", line 236, in test_no_caveat_outside_the_status_page
    for relative, text in reader_facing():
                          ^^^^^^^^^^^^^^^
  File "/home/asa/devel/machinome/machinome-studio/WTs/write-the-manual/tests/test_documentation.py", line 96, in reader_facing
    documents.append(("CHANGELOG.md", (ROOT / "CHANGELOG.md").read_text()))
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/pathlib.py", line 1029, in read_text
```

## 2. Green

Strict build, twice (before and after the reader-pass fixes below), both
warning-free:

```
$ python -m sphinx -b html -n -W --keep-going docs docs/_build/html
build succeeded.
The HTML pages are in docs/_build/html.
```

The documentation test, after one fix to the test itself (the navigation
regex lacked `re.M`, so `^` never matched a toctree line and nine subtests
failed against a correct index):

```
$ python -m unittest tests.test_documentation tests.test_license_headers tests.test_product_identity tests.test_machinome_identity
Ran 29 tests in 0.389s
OK
```

Sibling-manual link targets, opened in the siblings' built HTML
(`machinome/docs/_build/html`, `machinome-viewer/docs/_build/html`, both
built at the start of the cycle):

- `index.html` and `start/install.html` of the framework manual;
- `index.html` and `using-the-viewer.html` of the viewer manual.

Those four are the allowlist in `tests/test_documentation.py`.

Derived facts rendered from the source: the index note says
"Machinome Studio 0.1.0" and "Machinome 0.7.0" and "API 20 or later"; the
configuration reference says "one of sonnet, opus, fable" and "low,
medium, high"; the workspace page says "250 × 210 × 220 mm". Each is a
substitution in the page source; the test compares the values with
`pyproject.toml`, `floor/preparation.py` and `floor/build_package.py`.

The whole studio suite in the worktree, first attempt:

```
$ python -m unittest discover -s tests
Ran 360 tests in 435.231s
FAILED (failures=40, errors=2)
```

Every one of the 42 was the same environmental cause and none touched the
manual: `RuntimeError: Directory '.../WTs/write-the-manual/floor/static/assets'
does not exist`. The worktree had no generated frontend, which
`floor/app.py` mounts at start, so every `test_floor_api` server refused
connections and two `test_model_watcher` artifact-route tests could not
create the app. The remedy is the build the README documents, run in the
worktree (fresh `node_modules`, no symlink):

```
$ npm --prefix floor/frontend install --no-audit --no-fund
$ npm --prefix floor/frontend run build
frontend build exit 0
```

Second attempt, after the build:

```
$ python -m unittest discover -s tests
Ran 360 tests in 158.469s
OK (skipped=1)
```

360 tests against the primary's 341 before the change: the 19 of
`tests/test_documentation.py`. The one skip is the same Playwright-gated
skip the baseline had. The `RuntimeError: Event loop is closed` lines at
the end of both logs are interpreter-shutdown ResourceWarnings that the
baseline run prints too.

## 3. Read as the reader

Every built page was read once as text extracted from its HTML. Two
defects found and fixed:

- `project/status`: the version substitution sat inside `**...**`, where
  Sphinx does not expand it, and rendered literally as `|release|`. The
  sentence is now plain, and the build (which passed with `-W` either way)
  is not the check that catches this; reading is.
- `reference/project-configuration`: "separated by ``:``:" rendered as a
  double colon. Now "joined by ``:``." before the two forms.

Everything else read as intended: the note on the index, the two
definition lists of the command and configuration references, the two
profile tables, the code blocks, and the cross-page links by title.

## 4. Out of scope, found while applying

- `floor/mcp_server.py`'s module docstring said "The workspace venv also
  carries the machinome CLI"; a docstring is documentation, and the
  workspace is not the package's business. Reworded to "the environment
  the studio runs in" in this change, since the new test scans module
  docstrings.
- The framework's `reference/manuals.rst` lists the viewer and mechanics
  manuals and not the studio's. That is a framework change for when the
  studio's manual is hosted; recorded in `workflow/documentation.md`.
- The studio's `README.md` used to carry a long summary of runtime rules
  (backend policy, OpenCode's compatibility exception, the retired
  backends). Those now live on the manual's pages and the README points
  there; nothing was lost, the architecture overview and the specs remain
  the record of the rules themselves.
- `AGENTS.md` of the studio gained the manual, the changelog and
  `workflow/` among its entry points, `docs/_build/` among the paths never
  staged, and a paragraph saying what the manual is and which skill governs
  it; part of this change, since the contract's entry points would
  otherwise not name what a reader is sent to.
- The workspace's `skills/write-the-manual/SKILL.md` did not know the
  studio's manual. A one-commit companion on a workspace branch
  (`write-the-manual-studio`, worktree `WTs/write-the-manual-studio`)
  adds its row, its shape and how its release facts are derived; the
  pilot integrates it.
- No screenshots. The pilot's catalogue names projects the manual may not
  name, so a neutral catalogue would have to be made to photograph; left as
  an open question in the design.
