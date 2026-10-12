## Why

Machinome 0.7.0 releases on 21 September 2026 with its independent browser
viewer beside it, and the pilot decided the viewer releases as **0.7.0**,
the same number as the framework it serves. Every viewer record still says
"0.2.0 — unreleased": the manual's home page, the installation page, the
compatibility page, the README, the changelog, the release-preparation
record and a ratified requirement of the distribution spec. A reader of the
published manual would be told the package they installed does not exist.

The manual also links framework pages that the framework's 0.7 manual
revamp renamed, and its running reference carries release-note prose and a
project code-name that mean nothing to a host developer.

## What Changes

- The package, widget and bundle banner become version 0.7.0. The API
  version stays 23 and the document versions stay 1 to 10; no runtime
  behaviour changes.
- The manual states the released version it documents instead of an
  unreleased-source caveat, and installs the package from the index with
  the framework's `viewer` extra, keeping the source build as the
  contributor's path.
- Cross-manual links follow the framework manual's 0.7 structure.
- The running reference folds its release-note paragraphs into the place a
  host developer looks for stops and time drives, without project names.
- The changelog gains a `0.7.0` release section written for users; the
  development log it replaces moves to `workflow/archive/`, unchanged.
- The release-preparation record becomes `workflow/release-0.7.md`.
- **Modified requirement:** the distribution spec no longer requires 0.2.0
  to be identified as unreleased; it requires the shipped version to be
  0.7.0, released with Machinome 0.7.0.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-distribution`: "Installed viewer support includes retained time
  drives" stops pinning the package to an unreleased 0.2.0 and requires
  version 0.7.0 reported consistently by package, widget and bundle.
- `user-documentation`: "Makers have a viewer manual" states the released
  version and its matching framework release rather than distinguishing
  unreleased source capabilities from published ones.

## Impact

`pyproject.toml`, `machinome_viewer/__init__.py`,
`machinome_viewer/widget/package.json` and the rebuilt bundle;
`docs/index.rst`, `docs/installation.rst`, `docs/compatibility.rst`,
`docs/sharing.rst`, `docs/reference/cli.rst`, `docs/reference/running.rst`;
`README.md`, `CHANGELOG.md`, `workflow/release-0.7.md`,
`workflow/README.md`, `workflow/documentation.md`,
`tests/test_documentation.py`. The framework manual's viewer version
substitution changes in the framework repository, separately. Publishing
to PyPI, tagging and pushing remain the pilot's actions.
