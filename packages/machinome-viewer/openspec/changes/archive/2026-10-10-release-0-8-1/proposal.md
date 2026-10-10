## Why

machinome-viewer 0.8.0 is on PyPI (uploaded 6 October 2026; the index's
sha256 digests equal the files built at `v0.8.0`, `29f1ed9`). The framework
releases **Machinome 0.8.1** on 10 October 2026 (framework change
`release-0-8-1`), and its `viewer` and `web-snapshot` extras now require
`machinome-viewer>=0.8.1`: the two packages are numbered together (change
`release-the-viewer-as-0-7`), and the framework holds its extras' floor to
the viewer its manual declares. The pilot asked on 10 October 2026 for
both packages released as 0.8.1, ready for upload, with both repositories
tagged. Since `v0.8.0` the viewer's `main` has changed no shipped code: a
stray root `openscad.py`, outside the package, was removed, and one widget
test counts a step's records from a cleared ring after a restore.

## What Changes

- The package, the widget and the bundle banner become version 0.8.1. The
  declared API stays 29 and the document versions 1 to 13; no runtime
  behaviour changes.
- The changelog gains `0.8.1 — 10 October 2026`, saying the viewer is the
  published 0.8.0 renumbered with Machinome 0.8.1, as 0.7.1's section said
  of 0.7.0.
- The manual's home, installation and compatibility pages, the `describe`
  example, the README and `context7.json` state 0.8.1, released with
  Machinome 0.8.1 on 10 October 2026; API 28 and API 29 stay named as the
  0.8.0 release that added them.
- `workflow/release-0.8.md` records the renumbering and what remains the
  pilot's.
- **Modified requirements:** the manual names version 0.8.1; the 0.8.0
  release requirement keeps its section as released; a new requirement
  states the 0.8.1 release; the distribution's version requirement moves
  from 0.8.0 to 0.8.1.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: "Makers have a viewer manual" names version 0.8.1;
  "The manual states the 0.8.0 release" keeps 0.8.0's section, home-page
  date aside, as released below later releases; a new requirement, "The
  manual states the 0.8.1 release".
- `viewer-distribution`: "Installed viewer support includes retained time
  drives" requires version 0.8.1, released with Machinome 0.8.1.

## Impact

`pyproject.toml`, `machinome_viewer/__init__.py`,
`machinome_viewer/widget/package.json` and `package-lock.json`, and the
bundle built from them; `CHANGELOG.md`, `README.md`, `context7.json`,
`docs/index.rst`, `docs/installation.rst`, `docs/compatibility.rst`,
`docs/reference/cli.rst`; `tests/test_documentation.py`;
`workflow/release-0.8.md`.

Standalone change on viewer `main` base `ff9ac52`, branch and worktree
`release-0-8-1` at `WTs/release-0-8-1`, integration by fast-forward into
`main`, then `scripts/check-dist` in the primary checkout and the
annotated `v0.8.1` tag, at the pilot's request. The push and the upload
remain the pilot's; this package uploads before the framework.
