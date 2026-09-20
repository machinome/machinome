## Context

ADR-132 gives mechanics ownership of the helper formulas and their reference.
The framework currently links only to its GitHub repository and asks readers to
read module docstrings and internal specifications. Its Sphinx site already
links to other independent package manuals.

## Goals / Non-Goals

Give framework readers a direct path to mechanics installation, conventions and
helpers. Preserve the existing runtime boundary and avoid a duplicate reference.
No framework code, publication, integration, spec sync or archive in this phase.

## Decisions

Link the intended mechanics RTD manual from guide navigation, the mechanics
section of the API reference, project-supplied motion laws and upgrading. Use
ordinary HTTPS links so rendering the framework manual does not require the
new site to be online or import mechanics. Check the local companion build's
target pages. No architectural decision changes, so no new ADR is warranted.

## Risks / Trade-offs

The mechanics site is not yet hosted → distinguish intended hosting from local
proof, and verify link targets in the companion output before pilot review.
The framework's existing full build requires generated example exports → use
existing local artifacts where available and report any environmental limits.

## Working record and approval

Standalone cycle; not sprint-scoped. Framework primary `main` is clean at
`4d747191f8a94cb72fa3a4bef23a9742b91f0acf` (recorded integration target/base).
Cycle branch `mechanics-documentation-links`; worktree
`/home/asa/devel/machinome-studio/machinome/WTs/mechanics-documentation-links`,
opened by the shop's `scripts/dev-env`. Existing unrelated worktrees are preserved.
The pilot pre-ratified proposal and implementation on 2026-09-20, explicitly
reserving site approval before sync and archive. Commit planning only, implement
without intermediate commits, serve for review. Integration needs pilot authority.
