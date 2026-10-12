# Evidence: release-0-8-0

Base `cb39942` (viewer `main`, 5 October 2026), worktree
`machinome-viewer/WTs/release-0-8-0`, planning commit `61cc0a7`, with
`machinome_viewer/widget/node_modules` linked to the primary checkout
(build and tests only; no `npm ci`, no `npm install`, no
`scripts/check-dist` here). Python ran from the workspace venv with
`PYTHONPATH` on this worktree; `machinome_viewer.__file__` resolved to
`WTs/release-0-8-0/machinome_viewer/__init__.py`.

Ratification: the orchestrator ratified the plan on 5 October 2026 under
the pilot's decision of that day, adding the `viewer-distribution` delta
(as 0.7.1 had) and all six licensing sentences. This is advance
authorization and agent review, not a human review of the finished text.

## Red first

On the unmodified tree, with only `tests/test_documentation.py` and
`tests/test_licence.py` changed:

```
FAILED tests/test_documentation.py::test_docs_contains_no_development_records
FAILED tests/test_documentation.py::test_the_manual_states_the_release - Asse...
FAILED tests/test_documentation.py::test_film_annotations_are_documented_as_part_of_the_0_8_0_release
FAILED tests/test_documentation.py::test_on_demand_clocked_capture_is_documented
SUBFAILED(file='README.md') tests/test_licence.py::LicenceTest::test_reader_facing_pages_name_only_the_viewers_grant
SUBFAILED(file='CHANGELOG.md') tests/test_licence.py::LicenceTest::test_reader_facing_pages_name_only_the_viewers_grant
SUBFAILED(file='context7.json') tests/test_licence.py::LicenceTest::test_reader_facing_pages_name_only_the_viewers_grant
SUBFAILED(file='docs/index.rst') tests/test_licence.py::LicenceTest::test_reader_facing_pages_name_only_the_viewers_grant
SUBFAILED(file='docs/sharing.rst') tests/test_licence.py::LicenceTest::test_reader_facing_pages_name_only_the_viewers_grant
9 failed, 16 passed, 1 skipped, 435 subtests passed in 0.25s
```

The reasons, in order: `workflow/release-0.8.md` absent
(`test_documentation.py:29`); the first release section read
`0.7.1 — 27 September 2026 Released with` (`:50`); the compatibility page
had no `The 0.8.0 release declares:` (`:156`); no `## 0.8.0` section to
split on (`IndexError`, `:208`). The licence test found, on the first
four pages, one SPDX-shaped identifier that is not the viewer's grant,
and on `docs/sharing.rst` a licence named by the word before "license"
(the values are left out of this record: the viewer names no licence but
its own).

## Green

- Version 0.8.0 in `pyproject.toml`, `machinome_viewer/__init__.py`,
  `package.json` and both `version` fields of `package-lock.json`; no
  other `0.7.1` version statement remains outside the records.
- `npm run build --prefix machinome_viewer/widget`: `dist/machinome-viewer.js
  892.9kb`, `Done in 132ms`. The banner reads
  `machinome-viewer 0.8.0 - viewer API 29`.
- `test_documentation`, `test_licence`, `test_version`, `test_bundle`,
  `test_cli`: `45 passed, 1 warning, 440 subtests passed in 0.83s`.
- Python suite (`PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p
  no:cacheprovider tests`, workspace venv, Chromium present, nothing else
  running): `245 passed, 57 warnings, 462 subtests passed in 345.58s
  (0:05:45)`, nothing skipped.
- Widget suite (`npm test`): `Test Files 62 passed | 1 skipped (63)`,
  `Tests 1677 passed | 2 skipped (1679)`. The timing test
  `src/run/cost.test.ts > runs the acceptance machine far faster than
  real time`, which failed under load in the 0.7.1 run, passed; no
  failure. `npm run typecheck`: `tsc --noEmit` clean.
- Manual: `python -m sphinx -b html -n -W --keep-going docs
  docs/_build/html` from the workspace venv (Sphinx 9.1.0,
  sphinx-rtd-theme 3.1.0, the pins of `docs/requirements.txt`):
  `build succeeded.`, exit 0.
- `python scripts/check-docs-browser.py`: 14 pages at 1440 and 390 px,
  213 local links, mobile menu, search and the interactive example
  passed, both reference examples ran (pascaline `completed`, calculator
  360 admitted and restored), `browser_errors: []`.

## Pages read

The built home page at 1440 px (screenshot `_build/docs-review/
1440-index.html.png`): the note reads "This manual describes Machinome
Viewer 0.8.0, released on 5 October 2026 together with Machinome 0.8.0
and numbered with it. It declares viewer API 29 and reads document
versions 1, 2, …, 13", and "One viewer, several homes" names
AGPL-3.0-or-later and the framework as licensed separately. Also read in
the built HTML: installation ("Version 0.8.0 releases with Machinome
0.8.0"), compatibility ("The 0.8.0 release declares", viewer API 29,
"API 28 and API 29, the 0.8.0 release"), mount (`apiVersion` "29 in the
0.8.0 release"), the `describe` example (29, 0.8.0) and sharing (the
framework licensed separately, its licence not the bundle's).

## Spec sync

Both deltas applied to `openspec/specs/user-documentation/spec.md` and
`openspec/specs/viewer-distribution/spec.md` by archiving a copy of
`openspec/` outside the worktree with the OpenSpec CLI and taking its two
spec files ("+ 1 added, ~ 3 modified, → 1 renamed"). `openspec validate
--specs --strict`: 16 passed. Archive this change with the spec update
skipped.

## Facts recorded

The framework's `main` (`ee26e81`, its `release-0-8-0`) states Machinome
0.8.0, 5 October 2026, viewer 0.8.0, viewer API 29 and document versions
1 to 13: the dates agree. The changelog's `Unreleased` section had named
only `on-demand-clocked`; the API 28 changes and the asset-order
correction had written no bullet, so the 0.8.0 section was written from
their archived changes and checked against the reference pages.

## Left to the pilot

After the archive, integration into `main` by fast-forward and
`scripts/check-dist` from the primary checkout follow. The pilot's: the
`v0.8.0` tag, the push, the PyPI upload, the Read the Docs build and the
Context7 refresh.
