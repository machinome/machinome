## ADDED Requirements

### Requirement: A user can understand and start using mechanics

The manual SHALL identify machinome-mechanics as mechanics helpers for the
Machinome framework, explain optional installation and its separate import
package, and provide numeric, symbolic and motion-law examples. It SHALL state
the documented version's publication status honestly.

#### Scenario: First use

- **WHEN** a new user opens the manual
- **THEN** they can learn its purpose, install the available source version and
  run a complete example without reading internal specs or workflow records

#### Scenario: Use in a machine

- **WHEN** an author connects a helper to a Machinome motion law
- **THEN** a worked example explains resolved parameters and deferred symbolic
  inputs, including the limit on dimensional class-body formulas

### Requirement: Every public helper is documented for its caller

The manual SHALL document all public helpers with their import path, signature,
parameter meanings, return value, units, frame, zero and sign where applicable,
branch selection, domain limitations and executable examples. A reference index
SHALL let a user choose a helper by mechanical purpose.

#### Scenario: Choose and apply a formula

- **WHEN** a user looks up any exported helper
- **THEN** its reference explains how to call it and interpret its result in a
  machine's coordinate system, with an example that agrees with the implementation

### Requirement: User documentation is readable and independently hosted

The manual SHALL provide searchable navigation and readable desktop and mobile
pages consistent with the framework documentation. The repository SHALL support
building the manual on Read the Docs and locally without requiring unpublished
runtime packages just to render its pages. `docs/` SHALL contain user
documentation; internal extraction, validation and release preparation records
SHALL live in `workflow/`.

#### Scenario: Build and read the manual

- **WHEN** a maintainer builds the documentation using its declared dependencies
- **THEN** a navigable HTML manual is produced with no broken internal references
- **AND** its user pages do not require workflow records as API instructions
