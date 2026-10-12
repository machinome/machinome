## Why

The viewer is the browser surface of the renamed Machinome framework and must
not retain the conflicting solid-node product identity. Its unreleased status
makes this the point at which its repository and public package contracts can
move without breaking a published viewer release.

## What Changes

- Rename the repository and Python distribution to `machinome-viewer`, the
  Python package to `machinome_viewer`, and the console/module command to
  `machinome-viewer` / `python -m machinome_viewer`.
- **BREAKING**: rename the framework lookup entry point to `machinome.viewer`,
  the browser global to `MachinomeViewer`, the shipped bundle and embedding
  attributes/classes to Machinome names, and raise the declared viewer API
  version for the renamed host contract. No solid-node-named API alias is
  shipped.
- Keep accepting documents with the legacy `solid-node-export` format identity
  while treating `machinome-export` as the current producer identity, so
  committed 0.6 artifacts remain viewable.
- Rename repository URLs, source banners, packaging, tests, fixtures, current
  specs, documentation, changelog and commands while preserving old ADRs,
  archived changes and earlier changelog entries as historical evidence.
- Reconcile the existing one-commit `@machinome/viewer` npm name-holder as a
  retained package-registry provenance repository, not as a replacement for
  this full-history viewer repository. The viewer continues to ship through
  the Python extra unless a separate npm release is later authorized.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-distribution`: Rename the distribution, package, command, entry
  point, built artifact and repository identities while keeping the independent
  AGPL process boundary.
- `viewer-package`: Rename the public browser host contract and accept current
  and legacy export-format identities.

## Impact

Python package paths, entry points, CLI calls, frontend globals, attributes,
CSS selectors, bundle filenames, build metadata, fixtures, tests, docs and
framework integration all change. No package publication, tag, push, or npm
release is part of this change.
