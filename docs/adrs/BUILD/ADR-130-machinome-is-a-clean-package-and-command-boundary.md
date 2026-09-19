# ADR-130: Machinome is a clean package and command boundary

**Status:** Accepted
**Date:** 2026-09-18
**Change:** `rename-framework-to-machinome`

## Context

The solid-node name collides with Tim Berners-Lee's Solid project and its
node-client ecosystem. Renaming only prose or the Git repository would leave
Python imports, the command, project declarations, environment variables,
viewer lookup, and exported documents split across two identities.

The published 0.6.0 release remains solid-node. The next release is 0.7.0 and
can establish a deliberate compatibility boundary.

## Decision

Version 0.7 is the first Machinome release. Its distribution and import package
are `machinome`, its command is `machinome`, project declarations use
`[tool.machinome]`, runtime settings use `MACHINOME_*`, and its repository is
`machinome/machinome-framework`. It does not ship `solid_node` or a `solid`
command alias. Former project tables and environment prefixes are detected and
reported with their replacements.

New documents identify their family as `machinome-export`. Document schema
version numbers do not change merely for the product rename. Machinome Viewer
accepts the legacy `solid-node-export` family so committed 0.6 artifacts remain
readable. The viewer process/entry-point boundary becomes `machinome-viewer`
and `machinome.viewer`. Optional installation is exposed as
`machinome[viewer]`, `machinome[mechanics]`, and the future
`machinome[studio]`; the Studio extra is not installable from an index until
that experimental package is published.

## Alternatives considered

- Keep compatibility import and command aliases indefinitely. Rejected because
  it leaves the collision installed and makes both identities part of the
  supported 0.7 API.
- Rename only the distribution or repository. Rejected because project source
  and operational contracts would still present solid-node as the framework.
- Increment every document schema version. Rejected because the document shape
  is unchanged; family recognition, including legacy-family reading, is the
  relevant compatibility decision.

## Consequences

- Projects must update imports, command invocations, manifest tables, and
  environment names together when adopting 0.7.
- Mistaken old configuration fails with an actionable message rather than
  selecting defaults silently.
- Existing committed 0.6 documents remain viewable, while new producers never
  emit the colliding family name.
- Historical release notes, ADRs, and archived changes retain solid-node as the
  identity that was true at the time.
