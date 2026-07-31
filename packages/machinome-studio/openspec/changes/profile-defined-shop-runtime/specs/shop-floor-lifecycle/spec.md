## MODIFIED Requirements

> **Synchronization intent:** each MODIFIED requirement in this file replaces
> its complete baseline requirement block, including its scenario set.

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
- **WHEN** either initial profile is selected with Codex, Hermes, or Claude
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

### Requirement: The orchestrator closes the shop floor
The user SHALL be able to close shop-floor. The runtime SHALL end every agent
session declared by the active profile through the selected backend and stop
the service before reporting closure. Close SHALL be bounded, active work SHALL
NOT prevent it, and no owned agent process may remain afterward.

#### Scenario: The user closes either profile
- **WHEN** the user closes an open Builder or Fordesmac shop
- **THEN** the runtime ends every active profile session, stops the floor, and reports closure

#### Scenario: The user closes while work is active
- **WHEN** the shop closes while direct or delegated work is active
- **THEN** the runtime ends the active run without leaving an agent session or broker process

#### Scenario: One agent will not stop
- **WHEN** an owned agent process does not exit when asked
- **THEN** the backend forces it to stop, releases all others, and close completes

#### Scenario: Ending active work reports an error
- **WHEN** interrupting one profile agent reports an error during close
- **THEN** the runtime still releases remaining sessions and stops the floor

### Requirement: A maker can open the shop with the Claude backend
The shop runtime SHALL support both initial profiles through Claude using the
same broker, profile prompts, profile skills, topology, and lifecycle outcomes
as the other backends.

#### Scenario: Builder opens with Claude
- **WHEN** the user opens with `--profile builder --backend claude`
- **THEN** the runtime opens one Builder Claude session with the Builder profile contract

#### Scenario: Fordesmac opens with Claude
- **WHEN** the user opens with `--profile fordesmac --backend claude`
- **THEN** the runtime opens four project-sandboxed Claude sessions carrying the Fordesmac contracts
