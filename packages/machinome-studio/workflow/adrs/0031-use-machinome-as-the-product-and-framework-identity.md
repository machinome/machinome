# ADR-0031: Use Machinome as the product and framework identity

**Status:** Accepted
**Date:** 2026-09-18
**Decider:** Luis Fagundes
**Change:** `rename-studio-to-machinome`

## Context

The name LibreSolid Studio and the framework name solid-node overlap with Tim
Berners-Lee's Solid project and its node-client ecosystem. That collision makes
repository, package, and documentation references ambiguous. The framework,
viewer, mechanics package, and studio also exposed different old-name variants
across Python, browser, CLI, project configuration, and workspace paths.

Machinome names both the source code of a machine and, collectively, the body
of source code for machines. The Machinome organization is the home for those
repositories and resources.

## Decision

The product is Machinome Studio (`machinome-studio`). It coordinates the
Machinome framework (`machinome`, in repository `machinome-framework`),
Machinome Viewer (`machinome-viewer`), and Machinome Mechanics
(`machinome-mechanics`). Project runtime configuration is
`[tool.machinome-studio]`; the former `[tool.libresolid-studio]` table is
rejected with a migration message rather than ignored.

Current package, service, tool, browser, profile, skill, temporary-resource,
workspace, and documentation identities use Machinome. Historical ADRs,
archived OpenSpec changes, and past release evidence retain the names that were
true when they were written. The studio remains experimental and unpublished.

## Alternatives considered

- Keep LibreSolid Studio while renaming only the framework. Rejected because
  it leaves one ecosystem with two organization identities and does not remove
  the repository ambiguity.
- Use the two `machinode-*` spellings from the initiating message. Rejected as
  typographical variants: the term definition and canonical organization URL
  consistently establish `machinome`.
- Rewrite all historical records. Rejected because it would make old evidence
  and release history describe identities that did not exist at the time.

## Consequences

- Current surfaces and local workspace paths have one searchable identity.
- Existing project configuration fails loudly with an exact migration target.
- Hosts must update framework commands, viewer asset/API contracts, profile
  skill names, and repository paths together.
- Historical records intentionally contain former names; reference audits must
  classify them rather than demanding a context-free zero count.
- The rename does not publish, push, or claim portability the studio has not
  yet demonstrated.
