## ADDED Requirements

### Requirement: The product exposes one canonical identity
The system SHALL identify the customer-facing product as `SolidNode Studio` and
SHALL use `solid-node-studio` wherever package, plugin, repository, service,
agent, or temporary-resource syntax requires a machine-readable identifier.

#### Scenario: A customer views product identity
- **WHEN** a customer opens the browser workspace or reads current product
  metadata and documentation
- **THEN** the product name is presented as `SolidNode Studio`

#### Scenario: An integration addresses the product
- **WHEN** an integration reads package or plugin metadata or receives a
  product-derived runtime identifier
- **THEN** the identifier is `solid-node-studio` or is prefixed by
  `solid-node-studio-`

### Requirement: Mechanical shop vocabulary remains distinct from the product name
The system SHALL retain shop-floor, shop-root, shop-worktree, and related shop
terms when they describe the mechanical workflow rather than the product
identity.

#### Scenario: Current guidance describes a workflow concept
- **WHEN** current product guidance refers to the floor, repository lane, role
  workflow, or worktree by its shop-domain name
- **THEN** that domain term remains accurate without presenting `shop` as the
  product's customer-facing name
