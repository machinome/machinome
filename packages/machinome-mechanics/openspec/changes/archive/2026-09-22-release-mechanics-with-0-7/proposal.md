## Why

Machinome 0.7.0 is released, with its viewer 0.7.0, and the framework
manual names Machinome Mechanics 0.1.0 as the third package of that
release set. The mechanics manual, README and changelog still describe
0.1.0 as founded, unpublished and awaiting the framework, link into
framework pages the 0.7 manual no longer has, and credit some twenty
consumer projects by name in the helper reference. A reader who installs
the release set today is told to clone two repositories instead.

## What Changes

- The manual, README and changelog state that 0.1.0 is released with
  Machinome 0.7.0 on 20 September 2026, install it from the index through
  the framework's `mechanics` extra first, and keep the source install as
  the contributor's path.
- Every cross-manual link targets a page the Machinome 0.7 manual has:
  installation, relations, values, test assertions and upgrading.
- The helper reference describes the machines that motivated a convention
  by kind (a delta printer, a hexapod leg, a cam hammer) rather than by
  project name, and the worked examples use the framework's public
  spellings rather than a modelling library's internals.
- The changelog gains a reader-facing 0.1.0 release section; the release
  record, the maintainer notes and the OpenSpec context stop saying
  "pending".
- The documentation test refuses reader-facing text that calls the package
  unreleased, links to a framework page outside the known set, or names a
  consumer project.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: the manual states the release it documents and
  the framework release it matches, installs from the index first, links
  to the framework's current pages, and names no consumer project.
- `distribution`: the first release's compatibility statement is phrased
  against the published release rather than an unpublished state.

## Impact

`docs/` (index, getting started, using with Machinome, conventions, all
nine reference pages), `README.md`, `CHANGELOG.md`, `workflow/release-0.1.md`,
`workflow/README.md`, `workflow/documentation.md`, `openspec/config.yaml`,
`tests/test_documentation.py`. No formula, signature or version number
changes. The framework's own manual has a companion correction in its
repository (helper count and the "publication pending" sentence).
