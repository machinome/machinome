## Context

The mechanics repository was extracted from the framework with two commits and
has never been pushed or published. Its formulas and tests are already
independent, but its distribution, import package and only runtime dependency
use the old solid-node name.

## Goals / Non-Goals

**Goals:**

- Make the repository, distribution and imports canonical Machinome names.
- Preserve all twelve APIs and their numerical and symbolic behavior.
- Keep the dependency one-way from mechanics to the framework.

**Non-Goals:**

- Formula changes, project migration, publication, pushing, or compatibility
  aliases for an unpublished package.

## Decisions

- Move `solid_node_mechanics/` to `machinome_mechanics/` and update imports,
  package discovery, tests and docs as one atomic source rename. Keeping the old
  import alias was rejected because there is no published caller to protect.
- Require `machinome>=0.7.0`; this is the first version that owns
  `machinome.math`. Depending on `solid-node` would make the renamed package
  straddle both product identities.
- Keep version 0.1.0 and its unpublished status. A brand rename does not create
  a prior public release.
- Retain archived extraction provenance with its historical names; current
  README, changelog, specs and metadata explain the continuation.

## Risks / Trade-offs

- **Mechanical import changes could alter expression behavior** → run the full
  numeric/symbolic, integration and distribution-install suites against the
  renamed framework.
- **Package discovery could omit renamed modules** → inspect wheel and sdist and
  execute helpers from both installed artifacts.
- **Historical extraction links can look stale** → add current rename context
  without rewriting the original evidence.

## Migration Plan

Implement red-first import and metadata tests, rename the source tree and
current records, validate installed artifacts, archive the change, fast-forward
the primary branch, remove the worktree, move the repository directory to
`machinome-mechanics/`, and set `origin` to the new GitHub URL. Do not push or
publish.

## Open Questions

None.
