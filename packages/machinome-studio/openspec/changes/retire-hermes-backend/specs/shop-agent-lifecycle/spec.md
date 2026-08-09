## MODIFIED Requirements

### Requirement: An open shop manifests the working team
Each newly opened shop SHALL manifest exactly the complete standing agent set
declared by its selected validated profile. The orchestrator SHALL create each
agent session through the selected backend in declaration order and SHALL use
the profile's stable agent IDs and display labels.

#### Scenario: The default working team starts
- **WHEN** the runtime opens a shop without `--profile`
- **THEN** the roster shows one waiting Builder

#### Scenario: The Fordesmac working team starts
- **WHEN** the runtime opens with `--profile fordesmac`
- **THEN** the roster shows waiting Foreman, Designer, Machinist, and Librarian agents

#### Scenario: Either team starts through another backend
- **WHEN** either initial profile opens through Codex, Claude, or OpenCode
- **THEN** the roster contains the same profile-declared agent IDs and labels

#### Scenario: An undeclared role is addressed
- **WHEN** a participant addresses an agent ID absent from the active profile
- **THEN** the broker rejects it as an unknown active agent
