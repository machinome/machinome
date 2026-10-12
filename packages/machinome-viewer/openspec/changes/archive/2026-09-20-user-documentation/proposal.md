## Why

The maintainer has approved the mechanics manual and asks for the same treatment
for machinome-viewer: a release-ready package currently has a long README but no
user documentation site, and `docs/` contains development records. This is
explicit release/documentation maintenance, not a new viewer capability.

## What Changes

- Publish a Sphinx manual matching the Machinome framework's Read the Docs theme,
  with maker guides, embedding examples, and the complete supported browser and
  command-line interfaces.
- Include a working, self-contained interactive example using a committed viewer
  fixture and the package's own bundle, without importing or building Machinome.
- Put release preparation and decision records under `workflow/`, preserving
  their contents and authority; reserve `docs/` for the user manual.
- Add reproducible local and Read the Docs builds, documentation metadata,
  coverage/build/browser checks, and a local review site.
- Keep 0.2.0 explicitly unreleased. Do not change runtime behavior, API versions,
  licensing, package dependencies on the framework, or publish anything.

## Capabilities

### New Capabilities

- `user-documentation`: A navigable, accurate manual for makers and embedding
  developers, including reference coverage and a reproducible documentation site.

### Modified Capabilities

None. Existing runtime and distribution requirements remain unchanged.

## Impact

Viewer documentation, README, package metadata/source manifest, documentation
dependencies, tests, and workflow record paths. Framework documentation links
belong to a separate framework-owned cycle. The pilot pre-ratified proposal and
implementation by asking to do the same as mechanics; site approval is required
before spec sync, archival, or the implementation commit. No Git integration,
push, hosting-account mutation, or publication is authorized.
