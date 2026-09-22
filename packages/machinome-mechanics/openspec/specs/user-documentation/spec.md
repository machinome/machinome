# User documentation Specification

## Purpose

Help users install and apply the mechanics helpers through a complete, searchable
manual with tested examples and explicit coordinate conventions.
## Requirements
### Requirement: A user can understand and start using mechanics

The manual SHALL identify machinome-mechanics as mechanics helpers for the
Machinome framework, state the released version it documents and the
framework release it matches, explain installation from the package index
through the framework's `mechanics` extra with the source build kept as the
contributor's path, explain its separate import package, and provide
numeric, symbolic and motion-law examples in the framework's public
spellings. Every link into the framework manual SHALL target a page that
manual currently has. Its pages SHALL describe the machines that motivated
a convention by kind, not by the name of a consumer project, and SHALL
contain no development workflow records or decision records.

#### Scenario: First use

- **WHEN** a new user opens the manual
- **THEN** they can learn its purpose, install the released package with
  one command and run a complete example without reading internal specs or
  workflow records

#### Scenario: A user reads which version they have

- **WHEN** a user reads the home or installation page, the README or the
  changelog
- **THEN** each names version 0.1.0, released with Machinome 0.7.0, and
  none describes the package as unreleased or pending publication

#### Scenario: A user follows a link into the framework manual

- **WHEN** a user follows any link from the manual into the Machinome manual
- **THEN** it opens an existing page of the Machinome 0.7 manual

#### Scenario: Use in a machine

- **WHEN** an author connects a helper to a Machinome motion law
- **THEN** a worked example explains resolved parameters and deferred symbolic
  inputs, including the limit on dimensional class-body formulas, using the
  framework's own spellings

#### Scenario: A convention is explained without a project credit

- **WHEN** a reference page explains which mounting sign, station or branch
  a kind of machine supplies
- **THEN** it names the kind of machine and the choice, and no consumer
  project by name

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

