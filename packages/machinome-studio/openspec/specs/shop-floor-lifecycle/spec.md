# shop-floor-lifecycle Specification

## Purpose

Define fail-closed preparation, opening, operation, and shutdown of the local
shop floor across supported agent backends.
## Requirements
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

### Requirement: The shop validates the model before it becomes open
When the runtime opens a named project shop floor, the system SHALL build the
project's default `root` functional model and validate its complete published
viewer snapshot before starting the floor service or agent runtime. If that
build cannot produce a complete model, the system SHALL tell the maker why the
shop was not opened and SHALL leave no listening floor or running shop agent.

#### Scenario: The initial model build succeeds
- **WHEN** the runtime opens a shop for a named project with a buildable default `root` model
- **THEN** the runtime starts the shop-floor service and provides its browser location only after the complete model is ready for inspection

#### Scenario: The initial model build fails
- **WHEN** the default `root` model does not produce a complete viewer snapshot
- **THEN** the runtime reports the build failure without starting the floor service or any shop agent

### Requirement: The browser shows the shop lifecycle without a reload
The shop-floor service SHALL serve a browser page that displays `Shop is open`
while its live connection to the service is established, and `Shop is closed`
when that connection is lost. The page SHALL NOT maintain a second connection
for lifecycle status. If the service restarts at the same local browser
location, the already-open page SHALL reconnect, display `Shop is open` again,
and display the restarted shop's actual state — not merely the open indicator —
without a page reload.

#### Scenario: The browser opens while shop-floor is running
- **WHEN** a maker opens the shop-floor browser location while the service is running
- **THEN** the page displays `Shop is open`

#### Scenario: The service stops while the browser page remains open
- **WHEN** the shop-floor service shuts down while its browser page remains open
- **THEN** the page displays `Shop is closed` without a page reload

#### Scenario: The service restarts while the browser page remains open
- **WHEN** the shop-floor service restarts at the same browser location after the page displayed `Shop is closed`
- **THEN** the page reconnects, displays `Shop is open`, and displays the agents, work states, and conversation of the restarted shop without a page reload

#### Scenario: The restarted service publishes new work
- **WHEN** a page has reconnected to a restarted shop-floor service and that service manifests an agent or records a conversation entry
- **THEN** the page displays that change without a page reload

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
