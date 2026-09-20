## MODIFIED Requirements

### Requirement: The framework has one Machinome identity

The framework distribution SHALL be named `machinome`, its import package
SHALL be `machinome`, its executable SHALL be `machinome`, and its source
repository SHALL be `machinome/machinome`. Current product metadata,
documentation, diagnostics, templates and integration contracts SHALL use
those names.

#### Scenario: A user installs and imports the framework

- **WHEN** a user installs `machinome`
- **THEN** the framework is importable as `machinome`
- **AND** its command is available as `machinome`

#### Scenario: A reader follows the source link

- **WHEN** current package metadata or documentation names the source
  repository
- **THEN** it points to `github.com/machinome/machinome`

