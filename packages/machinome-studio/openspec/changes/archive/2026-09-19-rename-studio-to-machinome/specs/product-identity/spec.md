## MODIFIED Requirements

### Requirement: The product exposes one canonical identity
The system SHALL identify the customer-facing product as `Machinome Studio` and
SHALL use `machinome-studio` wherever package, plugin, repository, service,
agent, project-configuration, or temporary-resource syntax requires a
machine-readable identifier. Current material SHALL describe *machinome* as the
source code of one machine and, collectively, the body of source code for
machines, and SHALL identify the Machinome organization as the home for machine
source repositories, resources, and the framework.

Historical records that described LibreSolid Studio or solid-node when those
were their names SHALL retain that wording. Current indexes and synthesis SHALL
make the transition legible without rewriting those records.

#### Scenario: A customer views product identity
- **WHEN** a customer opens the browser workspace or reads current product
  metadata and documentation
- **THEN** the product name is presented as `Machinome Studio`

#### Scenario: An integration addresses the product
- **WHEN** an integration reads package metadata, project configuration, or a
  product-derived runtime identifier
- **THEN** the identifier is `machinome-studio` or is prefixed by
  `machinome-studio-`

#### Scenario: A reader follows the rename history
- **WHEN** a reader opens a past ADR, archived change, or release record that
  predates the rename
- **THEN** the record retains the name used at that time and current guidance
  explains that Machinome Studio is its continuation

### Requirement: Mechanical shop vocabulary remains distinct from the product name
The system SHALL retain shop-floor, shop-root, shop-worktree, and related shop
terms when they describe the mechanical workflow rather than the product
identity.

#### Scenario: Current guidance describes a workflow concept
- **WHEN** current product guidance refers to the floor, repository lane, role
  workflow, or worktree by its shop-domain name
- **THEN** that domain term remains accurate without presenting `shop` as the
  product's customer-facing name
