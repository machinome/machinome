## ADDED Requirements

### Requirement: Current documentation presents Machinome and its lineage

Every current entry page, installation guide, tutorial, API reference, status
page, contributor guide and source link SHALL use Machinome distribution,
import, command, configuration and repository names. The 0.7 changelog and
release note SHALL explain why solid-node was renamed, define *machinome*, and
provide a tested migration from solid-node 0.6.0. Historical release notes and
decision records SHALL retain their original terminology.

#### Scenario: A new user follows the quickstart

- **WHEN** the user follows current installation and first-project guidance
- **THEN** every command and import uses `machinome` and every optional product
  uses its Machinome name

#### Scenario: An existing user migrates

- **WHEN** a solid-node 0.6 user opens the 0.7 migration section
- **THEN** it maps distributions, imports, executable, environment variables,
  project configuration, viewer and mechanics names and states which aliases
  are not provided
