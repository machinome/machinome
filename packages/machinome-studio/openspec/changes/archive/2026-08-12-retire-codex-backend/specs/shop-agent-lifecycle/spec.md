## MODIFIED Requirements

### Requirement: An open shop manifests the working team
Each newly opened project SHALL manifest exactly the complete standing agent set
declared by its selected validated profile. The shop SHALL create each agent
session through the selected backend in declaration order and SHALL use the
profile's stable agent IDs and display labels. Each open project SHALL have its
own roster, and an agent SHALL appear in the roster of its own project only.

#### Scenario: The default working team starts
- **WHEN** a project declaring `builder` is opened
- **THEN** that project's roster shows one waiting Builder

#### Scenario: The Fordesmac working team starts
- **WHEN** a project declaring `fordesmac` is opened
- **THEN** that project's roster shows waiting Foreman, Designer, Machinist, and Librarian agents

#### Scenario: Either team starts through another backend
- **WHEN** either initial profile opens through Claude or OpenCode
- **THEN** the roster contains the same profile-declared agent IDs and labels

#### Scenario: An undeclared role is addressed
- **WHEN** a participant addresses an agent ID absent from the active profile
- **THEN** the broker rejects it as an unknown active agent

#### Scenario: Two projects with the same profile are open
- **WHEN** two projects declaring the same profile are open at once
- **THEN** each has its own roster of that profile's agents, and work on one project's roster leaves the other's unchanged
