## Why

Machinome 0.8.0 is on PyPI (uploaded 6 October 2026, tagged `v0.8.0` at
`d22d0a1`). Since then `main` has taken the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, closed 7 October 2026) and four
cycles from wall clock 02 and the combination safe lock (8 and 9 October
2026): twenty-two corrections and speed-ups, each recorded as it landed in
the changelog's `Unreleased` section, and the `viewer` and `web-snapshot`
extras now floored at the matching viewer. On 10 October 2026 the pilot
asked for releases of the framework and the viewer as **0.8.1**, ready for
upload, with both repositories tagged. Every record still says 0.8.0.

## What Changes

- **The version is 0.8.1**, dated 10 October 2026, in the five files of
  `setup.cfg`'s bumpversion table, moved by hand (bumpversion commits and
  tags). `docs/conf.py`: `release = '0.8.1'`, `version` stays `'0.8'`,
  `release_date = '10 October 2026'`, `viewer_version = '0.8.1'`;
  `viewer_api` stays `'29'`, `document_versions` `'1 to 13'` and
  `mechanics_version` `'0.1.0'`. The extras `viewer` and `web-snapshot`
  require `machinome-viewer>=0.8.1`, as the floor test requires; the
  viewer releases 0.8.1 beside the framework in its own repository, the
  0.8.0 viewer renumbered.
- **The records describe 0.8.1 as released.** The changelog's
  `Unreleased` section becomes `Machinome 0.8.1`, `Released on
  10/Oct/2026`, with a short opening: what a maker gets, that the
  document does not move, and the four changes a project may have to
  follow, sent to the upgrading page; the bullets stay as written, grouped
  in the order a maker meets them. `HISTORY.rst` gains
  `Machinome 0.8.1 (2026-10-10)`. `docs/releases/release-0.8.rst` gains a
  dated last section, `0.8.1: ...`, as `release-0.7.rst` did for 0.7.1.
  `context7.json` states 0.8.1, its date and the matching viewer 0.8.1,
  API 29. The status page needs no edit: it states the version and date
  through substitutions.
- **The upgrading page opens with "Upgrading from Machinome 0.8.0 to
  0.8.1"**: the changes a 0.8.0 project may have to follow (a read of
  `children` before linking is refused; a one-member repeated production
  binding is named `kids-0`; `ClockedSnapshot` takes the identity as its
  third argument and a clocked restore refuses another machine's
  snapshot; an undeclared leaf source is a `ValueError`), each with what
  to change. The 0.7 to 0.8 part follows, intact.
- **Tests:** `tests/test_machinome_identity.py`'s version literal moves to
  0.8.1; `tests/test_production_documentation.py` reads the section that
  records production profiles, still 0.8.0's; the release-records test
  already derives everything else from `pyproject.toml`.
- **A clean checkout's suite is green.** `tests/test_missing_source_file.py`
  resolved a declaration against `tests/stl_project/bracket.stl`, a
  gitignored mesh that `tests/test_stl_node.py` writes and a clean checkout
  runs later, so the suite failed on a fresh clone, as CI runs it
  (`workflow/warts.md`, 9 October 2026; reproduced on a fresh clone of
  `31c8507` with a fresh environment, 1 failed, 4751 passed). The test
  writes and removes its own file beside the module, as its module already
  does for its other fixtures. As at 0.7.1, whose release committed the
  vet fixtures `.gitignore` hid, a red CI is not a released state.
- **No source, document or behaviour change.** Every capability described
  is already on `main`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: a new requirement, "The 0.8.1 release is
  recorded", fixes where the 0.8.1 facts live and that they agree, the
  release note's dated section and the upgrading page's 0.8.0 to 0.8.1
  part. "The 0.8.0 release is recorded" stops requiring 0.8.0 to be the
  changelog's first release section, the history's top entry, the status
  page's version, `context7.json`'s version and the upgrading page's first
  part, which 0.8.1 supersedes, and keeps the 0.8.0 section, its history
  entry, the release note and the 0.7 to 0.8 part as released records.

## Impact

`pyproject.toml` (version and the two viewer extras' floor), `setup.cfg`,
`machinome/__init__.py`, `machinome/vet/universe.toml`, `docs/conf.py`
(release block), `docs/project/changelog.rst` (the 0.8.1 section),
`docs/project/upgrading.rst` (a new first part), `docs/releases/release-0.8.rst`
(a dated last section), `HISTORY.rst`, `context7.json`; tests
`test_machinome_identity.py`, `test_missing_source_file.py`;
`workflow/warts.md` (the fixture entry marked fixed);
`workflow/ongoing/release-0.8.1.md` (new: the pilot's steps).

Outside the framework and not this change's: the viewer's own 0.8.1
release in its repository (change `release-0-8-1` there), which must be
uploaded before or with the framework, since `machinome[viewer]` 0.8.1
requires it. The push and the upload remain the pilot's; the annotated
`v0.8.1` tag is made at the pilot's request after integration, and the
distributions are built from the tagged commit.

Standalone cycle on framework `main` base `31c8507`, branch and worktree
`release-0-8-1` at `machinome/WTs/release-0-8-1`, integration target
framework `main`. Authorization: the pilot's request of 10 October 2026,
"prepare releases for v0.8.1 of framework and viewer. leave everything
ready for me to twine upload. tag repositories", which covers proposal,
apply, integration by fast-forward and the tag; my review stands as the
ratification gate.
