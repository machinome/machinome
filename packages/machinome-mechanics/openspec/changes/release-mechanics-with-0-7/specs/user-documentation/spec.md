## MODIFIED Requirements

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
