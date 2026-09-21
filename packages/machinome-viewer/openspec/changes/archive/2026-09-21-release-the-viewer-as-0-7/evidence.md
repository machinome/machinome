# Evidence: release-the-viewer-as-0-7

Date: 2026-09-21. Worktree `WTs/release-0-7`, branch `release-0-7`, base
viewer main `a1ae12d`. Planning commit `f1a86e5`.

## Red first

`tests/test_documentation.py` gained the release expectations before any
other edit. Run against the base: two failures, `workflow/release-0.2.md`
still present and the word "unreleased" in `docs/index.rst`. After the change:
7 passed. One adjustment during application: the changelog check joins
whitespace before looking for "Machinome 0.7.0", because the sentence wraps.

## What changed

- Version 0.7.0 in `pyproject.toml`, `machinome_viewer/__init__.py` and the
  widget's `package.json`; bundle rebuilt with `npm run build` only through
  the linked `node_modules`; banner reads `machinome-viewer 0.7.0 - viewer
  API 23`. API 23 and document versions 1–10 unchanged.
- Manual: home note, installation (index install first, source build as the
  contributor's path), compatibility, sharing links, CLI example version,
  running reference (release paragraphs folded into "Stops and time drives",
  project name removed, fixture named by shape). Cross-manual links now name
  the framework manual's 0.7 pages `start/install`, `tutorial/10-share`,
  `reference/cli`, `project/upgrading`; all four exist in the framework's
  built manual at main `e6a42c8`.
- `CHANGELOG.md`: a 0.7.0 release section for readers; the 0.2.0 and 0.1.0
  development sections moved verbatim, with a heading note, to
  `workflow/archive/changelog-before-0.7.md`.
- `workflow/release-0.7.md` replaces `release-0.2.md`; README, `workflow/
  README.md` and `workflow/documentation.md` follow.
- Baseline specs: the two modified requirements synced.

## Review of the manual as a developer's document

Fourteen pages read end to end. They are written for makers and hosts:
what to install, how to inspect and operate each kind of machine, how to
share and embed, and a complete public reference with units, errors and
restrictions stated per member. No page names an ADR, an OpenSpec change,
the Studio or a workflow record; `docs/` holds no decision records. The only
project names were one code-name in the running reference and one fixture
credited by project; both are now described by what they are. The
troubleshooting page answers the questions a host actually hits. Nothing was
found that reads as internal.

## Validation

- `python -m pytest tests/test_documentation.py`: 7 passed.
- Strict Sphinx build (`-n -W --keep-going`): clean.
- `scripts/check-docs-browser.py`: 14 pages at 1440 and 390 px, 203 local
  links, mobile menu, search and interactive example passed, running and
  clocked reference snippets executed, no browser errors.
- Widget: typecheck clean; 1413 tests in 50 files passed.
- Python suite: 186 passed, 20 subtests, 4 min 32 s.
- `git diff --check` clean.

## Not done here

Uploading to PyPI, tagging, pushing and the Read the Docs project import
remain the pilot's actions. The framework's `viewer` extra stays unpinned, as
every extra there is. Two other viewer changes remain open and untouched:
`scripted-camera` (4/5 tasks) and `slide-and-turn-parts` (0/9 tasks, whose
code is on main).
