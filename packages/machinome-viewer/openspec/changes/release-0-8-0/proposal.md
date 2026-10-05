## Why

Machinome 0.8.0 releases on 5 October 2026, and the viewer is numbered
with the framework it serves (decision of 21 September 2026, change
`release-the-viewer-as-0-7`): the pilot decided on 5 October that the
viewer releases as **0.8.0** beside it. Unlike 0.7.1, this release ships
new source: everything landed on `main` after 0.7.1 (`cb39942`), which
declares viewer API 29 and reads document versions 1 through 13. Every
record still says 0.7.1 and API 27, and the compatibility page says API
28 and 29 are "in no published release"; a reader who installs 0.8.0
would be told the package they installed does not exist and that what it
does is unpublished. The framework's own 0.8.0 record already names
viewer 0.8.0, API 29 and document versions 1 to 13, dated 5 October 2026.

Separately, the pilot decided that the viewer never states the
framework's licence: a reader learns the viewer's licence here and the
framework's from the framework's manual.

## What Changes

- The package, the widget and the bundle banner become version 0.8.0.
  The declared API stays 29 and the document versions 1 to 13, as the
  source already declares them; no runtime behaviour changes in this
  change.
- The changelog's `Unreleased` section becomes `0.8.0 — 5 October 2026`,
  released with Machinome 0.8.0 and numbered with it, telling a reader
  what 0.8.0 gives a host and a maker: a part's screen position and the
  projection of any world point, a part highlighted with the rest kept,
  dimmed or ghosted, an up direction and field of view per view call
  (API 28), fresh rigid assets drawn in a deterministic order (no API
  change), and a clocked machine captured on demand (API 29), each naming
  its archived change in one line. A 0.7 viewer reads a 0.8 export and
  this viewer reads every 0.7 export, because the document format does
  not move. No `Unreleased` section remains.
- The manual's home, installation, compatibility and mount-reference
  pages, the `describe` example, the README and `context7.json` state
  0.8.0, released with Machinome 0.8.0 on 5 October 2026, API 29; the
  compatibility page names API 28 and API 29 as the 0.8.0 release.
- Every reader-facing sentence about licensing names only the viewer's
  licence and says the framework is licensed separately: the README, the
  manual's home and sharing pages, `context7.json` and the 0.7.0
  changelog section's one sentence; also the project context of
  `openspec/config.yaml`. A test refuses any other licence identifier on
  those pages.
- A new release record `workflow/release-0.8.md` states the prepared state
  and what remains the pilot's.
- **Modified requirements:** the manual spec's version scenario names
  0.8.0; the 0.7.1 comparison stays true as a released section below
  later ones; the film-annotation requirement, which required API 28 to be
  "in no published release", becomes part of the 0.8.0 release; a new
  requirement states the 0.8.0 release facts, where they live and that
  they agree; the distribution spec's version requirement moves from
  0.7.1 to 0.8.0, as the 0.7.1 change moved it from 0.7.0.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: "Makers have a viewer manual" names version
  0.8.0, released with Machinome 0.8.0, and keeps the 0.7.1 section as
  released below later releases; "The manual states film annotations as
  current-source capability" is renamed and rewritten as part of the
  0.8.0 release; a new requirement, "The manual states the 0.8.0
  release", fixes where the 0.8.0 facts live, that they agree with the
  package's declarations, and that licensing sentences name only the
  viewer's licence.
- `viewer-distribution`: "Installed viewer support includes retained time
  drives" requires version 0.8.0, released with Machinome 0.8.0, reported
  consistently by package, widget and bundle.

## Impact

`pyproject.toml`, `machinome_viewer/__init__.py`,
`machinome_viewer/widget/package.json` and `package-lock.json`, and the
rebuilt bundle; `docs/index.rst`, `docs/installation.rst`,
`docs/compatibility.rst`, `docs/sharing.rst`, `docs/reference/cli.rst`,
`docs/reference/mount.rst`; `README.md`, `CHANGELOG.md`, `context7.json`,
`openspec/config.yaml`, `workflow/README.md`, the new
`workflow/release-0.8.md`; `tests/test_documentation.py`,
`tests/test_licence.py`. The framework's record of this viewer release is
already on the framework's `main`. Tagging, pushing, uploading to PyPI,
Read the Docs and Context7 remain the pilot's actions, and
`scripts/check-dist` runs in the primary checkout after integration.

Standalone cycle on viewer `main` base `cb39942`, branch and worktree
`release-0-8-0` at `machinome-viewer/WTs/release-0-8-0`, integration
target viewer `main`.
