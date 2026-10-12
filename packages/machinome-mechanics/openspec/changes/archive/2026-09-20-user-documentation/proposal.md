## Why

The maintainer cannot publish a useful manual for machinome-mechanics: `docs/`
contains only internal extraction and release records. V8, Kossel, clocks and
screw-driven projects already use its twelve helpers, but users must read source
and behavioral specs to learn their conventions.

## What Changes

- Build a Sphinx user manual matching the framework's Read the Docs theme.
- Explain mechanics helpers for the Machinome framework, installation, numeric
  and symbolic use, motion laws, and all twelve public functions with examples,
  parameters, returns, frames, units, branch choices and domain limits.
- Move the three internal records from `docs/` to `workflow/`, preserving history.
- Supply Read the Docs configuration, reproducible local build instructions,
  package documentation links, and checks for examples and reference coverage.
- Serve the completed manual for pilot review before spec sync or archive.

## Capabilities

### New Capabilities

- `user-documentation`: Discoverable, complete user documentation for mechanics.

### Modified Capabilities

None. Formula and distribution behavior are preserved.

## Impact

Documentation, documentation dependencies, metadata, source-distribution inputs
and documentation checks in this repository. The framework links are owned by
the separate `mechanics-documentation-links` change. No runtime API changes.
The pilot pre-ratified proposal and implementation on 2026-09-20; sync and
archive require review approval. No publication or push is included.
