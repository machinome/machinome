## MODIFIED Requirements

### Requirement: The orchestrator opens the shop floor
The system SHALL allow the user to open shop-floor for a required workspace
project and selected runtime profile. Before project creation, validation, or
build, it SHALL resolve and validate that profile and selected backend settings.
It SHALL then prepare the corresponding `projects/<name>` repository, complete
the initial model build, run the local service, and start persistent sessions
for exactly the profile's standing agents through the selected backend. Each
session SHALL use the verified project root as its workspace boundary.

The runtime SHALL report its stable browser location only after profile
validation, model preparation, service availability, and all declared agents
are complete. The default port SHALL be 9000 and an explicit port SHALL remain
supported.

#### Scenario: The user opens the default shop
- **WHEN** the user opens a named project without profile or port options
- **THEN** the runtime validates `builder`, prepares the project, opens one Builder session through Codex, and reports the browser location on port 9000

#### Scenario: The user opens either profile on a configured port
- **WHEN** the user opens a named project with an explicit non-default port and either valid built-in profile
- **THEN** the runtime opens that profile on the configured port and reports the matching browser location

#### Scenario: The user opens Fordesmac
- **WHEN** the user opens a named project with `--profile fordesmac`
- **THEN** the runtime validates that profile and opens Foreman, Designer, Machinist, and Librarian sessions

#### Scenario: Profile and backend are selected independently
- **WHEN** either initial profile is selected with Codex, Claude, or OpenCode
- **THEN** that backend opens exactly the agents declared by that profile

#### Scenario: Profile validation fails
- **WHEN** the selected profile is invalid or incomplete for the selected backend
- **THEN** the runtime starts no preparation, service, build, or agent process and reports the profile error

#### Scenario: Project preparation fails
- **WHEN** the validly configured project cannot be created, validated, or built
- **THEN** the runtime starts no floor service or agent session, reports why it did not open, and provides no browser location

#### Scenario: Runtime opening fails after preparation
- **WHEN** the service or any declared session cannot start after the project is ready
- **THEN** the runtime ends everything started for that attempt and reports that it could not open

#### Scenario: Profile sessions are sandboxed to the project
- **WHEN** a valid profile opens after preparing a named project
- **THEN** every declared agent session uses that exact verified repository as its workspace boundary
