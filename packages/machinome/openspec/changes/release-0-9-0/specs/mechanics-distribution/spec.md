## MODIFIED Requirements

### Requirement: Framework independence from mechanics helpers

The default machinome installation SHALL NOT depend on machinome-mechanics.
The framework SHALL NOT import, bundle, or re-export its helpers. Its math and
motion APIs SHALL remain usable without that package installed.
Installing machinome with the mechanics extra SHALL install the
machinome-mechanics distribution, which lives in the repository at
`packages/machinome-mechanics/` and ships the package `machinome.mechanics`,
a portion of the `machinome` package that the core admits through its path
extension and never imports. The extra SHALL require the distribution with
the compatible-release pin `~=<version>`, the version being the
framework's own: the distribution is numbered with the set since Machinome
0.9.0. No module of the former name
`machinome_mechanics` SHALL be provided, and no alias of it.

#### Scenario: Motion without mechanics

- **WHEN** a project uses framework math and motion with mechanics unavailable
- **THEN** those APIs remain usable without trying to import mechanics

#### Scenario: The old helper import is removed

- **WHEN** a project imports machinome.mechanisms from the refactored framework
- **THEN** the import fails because the helpers are no longer a framework API

#### Scenario: Opt into the helper package

- **WHEN** a user installs machinome with the mechanics extra
- **THEN** machinome-mechanics is selected as an additional dependency
- **AND** helpers are imported from machinome.mechanics

#### Scenario: The core never reaches the helpers' address

- **WHEN** the framework's math, motion and assembly modules are imported
  under a guard that refuses `machinome.mechanics` and every name beneath it
- **THEN** they import and work, and the same guard refuses an explicit
  `import machinome.mechanics`, so the check watches the dotted address

#### Scenario: The former module name is gone

- **WHEN** a project on a synced workspace imports `machinome_mechanics`
- **THEN** the import fails, and the helpers resolve from
  `machinome.mechanics` in `packages/machinome-mechanics/`
