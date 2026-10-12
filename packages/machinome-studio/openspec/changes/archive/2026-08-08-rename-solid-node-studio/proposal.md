## Why

The project has been renamed to solid-node-studio, but the repository still
exposes its former identity throughout package metadata,
plugin manifests, runtime integration identifiers, documentation, and user
interface. The active product must present one coherent identity: SolidNode
Studio to people and `solid-node-studio` where a machine-readable name is
required.

## What Changes

- **BREAKING**: Rename the Python distribution and plugin identifier to
  `solid-node-studio`.
- Replace active runtime service, agent, temporary-resource, and integration
  identifiers derived from the former product name.
- Present the customer-facing product name as “SolidNode Studio” in the browser,
  documentation, prompts, and descriptive metadata.
- Update workspace examples and repository-development guidance to use the
  renamed `solid-node-studio/` checkout.
- Preserve “shop floor” and similar mechanical-workflow language where it names
  a domain concept rather than the product.
- Preserve immutable historical evidence when rewriting it would misrepresent
  commands or content captured at the time; describe the rename explicitly
  where historical records remain discoverable.

## Capabilities

### New Capabilities

- `product-identity`: Defines the canonical customer-facing and machine-readable
  identities exposed by the product.

### Modified Capabilities

- `shop-browser-workspace`: The browser workspace presents the canonical
  customer-facing product name.

## Impact

This affects package and plugin metadata, backend integration identifiers,
browser copy, repository documentation and skills, workspace-path examples,
tests, and baseline OpenSpec documentation. Existing installations or tooling
that address the old distribution or plugin identifier must migrate to
`solid-node-studio`.
