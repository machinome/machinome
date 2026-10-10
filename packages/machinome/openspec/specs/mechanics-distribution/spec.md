# Mechanics Distribution Specification

## Purpose

Keep the framework usable independently of the separate mechanical helper package.

## Requirements

### Requirement: Framework independence from mechanics helpers

The default machinome installation SHALL NOT depend on machinome-mechanics.
The framework SHALL NOT import, bundle, or re-export its helpers. Its math and
motion APIs SHALL remain usable without that package installed.
Installing machinome with the mechanics extra SHALL install the separate
machinome-mechanics distribution.

#### Scenario: Motion without mechanics

- **WHEN** a project uses framework math and motion with mechanics unavailable
- **THEN** those APIs remain usable without trying to import mechanics

#### Scenario: The old helper import is removed

- **WHEN** a project imports machinome.mechanisms from the refactored framework
- **THEN** the import fails because the helpers are no longer a framework API

#### Scenario: Opt into the helper package

- **WHEN** a user installs machinome with the mechanics extra
- **THEN** machinome-mechanics is selected as an additional dependency
- **AND** helpers remain imported from machinome_mechanics
