## MODIFIED Requirements

### Requirement: The product exposes one canonical identity
The system SHALL identify the customer-facing product as `LibreSolid Studio` and
SHALL use `libresolid-studio` wherever package, plugin, repository, service,
agent, or temporary-resource syntax requires a machine-readable identifier.

#### Scenario: A customer views product identity
- **WHEN** a customer opens the browser workspace or reads current product
  metadata and documentation
- **THEN** the product name is presented as `LibreSolid Studio`

#### Scenario: An integration addresses the product
- **WHEN** an integration reads package or plugin metadata or receives a
  product-derived runtime identifier
- **THEN** the identifier is `libresolid-studio` or is prefixed by
  `libresolid-studio-`
