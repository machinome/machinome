## MODIFIED Requirements

### Requirement: Codex opens the FastAPI shop floor
The system SHALL allow a maker to ask Codex to open shop-floor for a required
workspace project name. Before starting the local service or any agent, the
Codex shop runtime SHALL prepare the corresponding `projects/<name>` repository
and complete its initial functional-model build. It SHALL then run the local
shop-floor service, start persistent sessions for the foreman, designer, and
machinist in that verified project root, and keep control of those sessions for
the life of the open shop. Codex SHALL tell the maker its stable local browser
location only after the initial model is ready, the service is available, and
all three agents are running. The default browser location SHALL use port 9000,
and Codex SHALL be able to use an explicitly configured port instead.

#### Scenario: A maker opens the shop
- **WHEN** a maker asks Codex to open the shop for a named project without configuring a port
- **THEN** Codex prepares and builds that project, runs the shop-floor service and three-agent team in it, and provides its browser location on port 9000

#### Scenario: A maker opens the shop on a configured port
- **WHEN** a maker asks Codex to open the shop for a named project with an explicit port
- **THEN** Codex prepares and builds that project, runs the shop-floor service and three-agent team in it, and provides its browser location on that port

#### Scenario: Project preparation fails
- **WHEN** the named project cannot be created, validated, or built into a complete initial model
- **THEN** Codex starts no floor service or agent session, provides no browser location, and tells the maker why the shop was not opened

#### Scenario: The runtime cannot be opened after project preparation
- **WHEN** the service or any required Codex agent cannot be started after the project is ready
- **THEN** Codex ends anything started for that attempt and tells the maker that the shop could not be opened

### Requirement: The shop validates the model before it becomes open
When Codex opens a named project shop floor, the system SHALL build the
project's default `root` functional model and validate its complete published
viewer snapshot before starting the floor service or agent runtime. If that
build cannot produce a complete model, the system SHALL tell the maker why the
shop was not opened and SHALL leave no listening floor or running shop agent.

#### Scenario: The initial model build succeeds
- **WHEN** Codex opens a shop for a named project with a buildable default `root` model
- **THEN** Codex starts the shop-floor service and provides its browser location only after the complete model is ready for inspection

#### Scenario: The initial model build fails
- **WHEN** the default `root` model does not produce a complete viewer snapshot
- **THEN** Codex reports the build failure without starting the floor service or any shop agent
