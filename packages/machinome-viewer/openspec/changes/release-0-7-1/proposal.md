## Why

Machinome 0.7.1 releases on 27 September 2026, and the viewer is numbered
with the framework it serves (decision of 21 September 2026, change
`release-the-viewer-as-0-7`): the pilot decided on 27 September that the
viewer releases as **0.7.1** beside it. The source that 0.7.1 renumbers
is the source 0.7.0 was published from: the wheel on PyPI was built from
`1e67c83`, the current `main`, so nothing in the widget, the server or
the capture changes; viewer API 27 and document versions 1 to 13 stay.
Every record still says 0.7.0, and a reader who installs 0.7.1 would be
told the package they installed does not exist.

## What Changes

- The package, the widget and the bundle banner become version 0.7.1.
  The API version stays 27 and the document versions 1 to 13; no
  runtime behaviour changes.
- The manual's home, installation and compatibility pages, the README,
  the `describe` example and `context7.json` state 0.7.1, released with
  Machinome 0.7.1 on 27 September 2026.
- The changelog gains a `0.7.1` section above `0.7.0` that says what a
  reader needs: it is the published 0.7.0 renumbered, the framework's
  frames and mates compile to what the document already carries, and a
  0.7.0 viewer reads a 0.7.1 export. The 0.7.0 section is unchanged.
- The release record `workflow/release-0.7.md` gains a dated 0.7.1 note;
  the documentation test pins 0.7.1 and its date.
- **Modified requirements:** the distribution spec requires the shipped
  version to be 0.7.1, released with Machinome 0.7.1; the manual spec's
  version scenario names 0.7.1.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-distribution`: "Installed viewer support includes retained time
  drives" requires version 0.7.1, released with Machinome 0.7.1, reported
  consistently by package, widget and bundle.
- `user-documentation`: "Makers have a viewer manual" names version 0.7.1,
  released with Machinome 0.7.1, on the home, installation and
  compatibility pages.

## Impact

`pyproject.toml`, `machinome_viewer/__init__.py`,
`machinome_viewer/widget/package.json` and `package-lock.json`, and the
rebuilt bundle; `docs/index.rst`, `docs/installation.rst`,
`docs/compatibility.rst`, `docs/reference/cli.rst`; `README.md`,
`CHANGELOG.md`, `context7.json`, `workflow/release-0.7.md`,
`tests/test_documentation.py`. The framework manual's viewer version
substitution changes in the framework repository, separately. Publishing
to PyPI, tagging and pushing remain the pilot's actions.

Standalone cycle on viewer `main` base `1e67c83`, branch and worktree
`release-0-7-1` at `machinome-viewer/WTs/release-0-7-1`, integration
target viewer `main`.
