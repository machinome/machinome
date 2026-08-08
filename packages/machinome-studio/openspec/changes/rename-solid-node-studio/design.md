## Context

The checkout directory has already moved from `solid-node-shop/` to
`solid-node-studio/`, while active repository content still uses the former
name. The old string appears in public metadata, machine identifiers, runtime
session labels, operating instructions, current specifications, and product
design material. “Shop” also remains a legitimate domain term for the floor,
worktrees, roles, and mechanical workflow, so a blind replacement would damage
the product language.

## Goals / Non-Goals

**Goals:**

- Establish “SolidNode Studio” as the only active customer-facing product name.
- Establish `solid-node-studio` as the canonical distribution, plugin, service,
  and repository identifier.
- Update active workspace examples and cross-repository contracts to the renamed
  checkout.
- Add automated checks for the public metadata and browser brand.

**Non-Goals:**

- Rename the `solid-node` framework.
- Rename domain concepts such as shop floor, shop worktree, shop root, roles, or
  the `shop-skills/` directory.
- Rewrite captured command output or immutable historical evidence whose former
  name is part of an accurate record.
- Introduce compatibility aliases for the former package or plugin identifier.

## Decisions

### Separate display and machine identities

Human-visible product labels use the exact spelling “SolidNode Studio”. Values
constrained to identifier syntax use `solid-node-studio`; compound identifiers
use that as their prefix. This keeps UI and prose polished without introducing
spaces or capitalization into protocol fields, package names, filesystem
prefixes, or plugin keys.

Alternative: use `solid-node-studio` everywhere. Rejected because the pilot
explicitly selected a different customer-facing form.

### Classify occurrences by meaning

Active references to the former product/repository are renamed. Generic “shop”
terminology remains when it describes the mechanical environment or runtime
concept. Historical artifacts remain unchanged only when their exact old text
is evidence rather than current guidance; current summaries and baseline specs
are migrated.

Alternative: global textual replacement. Rejected because it would incorrectly
rename durable domain vocabulary and could falsify captured evidence.

### Make browser branding explicit

The browser document title and visible title bar identify SolidNode Studio.
Tests assert both surfaces so package/plugin renames cannot leave the running
product branded with an incidental generic title.

Alternative: limit the rename to metadata and documentation. Rejected because
the requested customer-facing name must be observable in the tool itself.

## Risks / Trade-offs

- [External automation still addresses `solid-node-shop`] → Treat the identifier
  rename as breaking and document the new value consistently.
- [A former-name occurrence is missed in a non-obvious active file] → Search
  tracked text case-insensitively after implementation and review every residue.
- [Historical records become internally inconsistent] → Keep captured evidence
  intact and distinguish it from current operational documentation.
- [Generic shop terminology is over-renamed] → Review each occurrence by
  semantics rather than applying an unrestricted replacement.

## Migration Plan

1. Change public metadata and runtime identifiers.
2. Add visible browser branding and acceptance coverage.
3. Migrate active docs, skills, design references, and baseline specs.
4. Review all residual former-name occurrences and retain only justified
   historical evidence.
5. Validate OpenSpec artifacts, metadata parsing, and the relevant test suite.

Rollback is a revert of the rename cycle; no persistent user data is migrated.

## Open Questions

None. The pilot supplied both canonical names.
