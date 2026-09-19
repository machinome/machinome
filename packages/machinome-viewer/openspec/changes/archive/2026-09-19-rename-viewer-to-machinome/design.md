## Context

The viewer was extracted from the framework into an independent AGPL package
and repository, but neither its 0.1.0 foundation nor its current 0.2.0 line has
been published. Its Python, process and browser surfaces all carry solid-node
names. A separate one-commit `@machinome/viewer` npm name-holder also exists;
it is not the full viewer repository and the actual viewer currently ships as
assets inside a Python distribution.

## Goals / Non-Goals

**Goals:**

- Rename Python, command, entry-point, bundle and public browser identities.
- Preserve the AGPL/process boundary and all functional viewer behavior.
- Keep committed solid-node 0.6 exports readable.
- Preserve the full viewer history and the separate name-holder provenance.

**Non-Goals:**

- Publishing to PyPI or npm, pushing, tagging, or merging unrelated Git
  histories.
- Maintaining browser or Python aliases for the unpublished viewer name.
- Changing numerical document versions for a product-name change.

## Decisions

### Rename every public layer together

`solid_node_viewer/` moves to `machinome_viewer/`; the distribution, command,
module invocation and entry point move with it. The bundle becomes
`machinome-viewer.js`, the global becomes `MachinomeViewer`, and the published
DOM/CSS contract uses a consistent `machinome-` prefix. Partial renames were
rejected because they would leave host code and diagnostics carrying the
conflicting brand.

### The browser API version rises, document versions do not

Hosts must change global, attribute, selector and asset names, so the viewer
API version rises by one. Node-document versions describe mechanical-document
capabilities and do not rise. The loader accepts both `machinome-export` and
legacy `solid-node-export`; new fixtures and outputs use the former.

### No compatibility alias is shipped

The viewer has no published release to protect. Shipping both globals,
commands, entry points, file names and selectors would create permanent duplicate
contracts. Compatibility is limited to reading already committed framework
documents, which are durable artifacts rather than unpublished viewer APIs.

### The npm holder remains separate provenance

The `@machinome/viewer` holder repository moves under `name-holders/` and is
retained. This repository becomes `machinome-viewer` with its full history and
continues to package the bundle through Python. A future npm package is a
separate release decision.

### History remains historically named

Current specs, README, metadata, code, tests, fixtures, changelog heading and
unreleased entry move to Machinome. Relocated ADR bodies, archived changes and
past historical statements retain their old names. A new ADR records the
public host-contract rename and the legacy-format decision; the architecture
index and synthesis identify the transition.

## Risks / Trade-offs

- **String replacement can damage three.js/CSS behavior** → add red contract
  tests for globals, attributes, selectors, theme properties and bundle names,
  then run typecheck, unit, browser and Python suites.
- **Framework and viewer can disagree on entry point or command** → run paired
  installed-distribution tests from one isolated environment.
- **Renaming fixtures could lose old-artifact coverage** → retain dedicated
  immutable legacy fixtures and add current-format equivalents.
- **Packaging can omit renamed files** → build wheel/sdist, inspect contents,
  install each, and run describe/serve/capture smoke tests as available.

## Migration Plan

Implement red-first public-name and legacy-format tests; rename Python and
frontend trees and current records; rebuild the bundle; run all frontend,
Python, packaging and paired framework tests; accept the rename ADR; sync and
archive; fast-forward the clean primary branch; remove the worktree; move the
holder and full repository directories; set the new remote without pushing.

## Open Questions

None.
