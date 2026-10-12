# ADR-066: The viewer host contract adopts Machinome

**Status:** Accepted
**Date:** 2026-09-18
**Change:** `rename-viewer-to-machinome`

## Context

The viewer was founded but not published as solid-node-viewer. Renaming only
its Python distribution would leave the framework lookup, subprocess command,
browser global, bundle filename, npm identity, DOM attributes, CSS properties,
and diagnostics exposing the colliding solid-node identity.

Committed documents produced by released solid-node 0.6 must remain viewable,
even though new Machinome 0.7 documents need the new family identity.

## Decision

The distribution and repository are `machinome-viewer`, the import package is
`machinome_viewer`, the executable/module process is `machinome-viewer` /
`python -m machinome_viewer`, and framework discovery uses the
`machinome.viewer` entry-point group. The browser host contract uses
`MachinomeViewer`, `machinome-viewer.js`, `@machinome/viewer`, and Machinome
DOM/CSS prefixes. Viewer API 20 identifies that coordinated host-contract
break.

The loader accepts both the current `machinome-export` document family and the
legacy `solid-node-export` family. This compatibility is reader-only: current
fixtures and producers use `machinome-export`. Document schema versions remain
unchanged because the serialized shape did not change.

## Alternatives considered

- Preserve old browser names as aliases. Rejected because the unreleased
  package can establish one host contract before publication and aliases would
  make the collision permanent.
- Refuse legacy document families. Rejected because committed 0.6 artifacts
  are durable inputs rather than package APIs that can be migrated in place.
- Increment every schema version. Rejected because host identity and document
  family recognition, not document structure, are changing.

## Consequences

- Framework, Studio, and direct browser hosts must adopt API 20 and all renamed
  host surfaces together.
- Existing 0.6 documents continue to render; unrelated format families fail
  loudly before partial rendering.
- Historical changelog entries and earlier ADRs retain the old identifiers
  they actually specified.
- The rename does not publish the viewer; its release remains pending an
  explicit maintainer action.
