## MODIFIED Requirements

### Requirement: Codex opens the FastAPI shop floor
The system SHALL allow a maker to ask Codex to open shop-floor for a required
workspace project name. Before starting the local service or any agent, the
Codex shop runtime SHALL prepare the corresponding `projects/<name>` repository
and complete its initial functional-model build. It SHALL then run the local
shop-floor service, start persistent sessions for the foreman, designer, and
machinist in that verified project root, and keep control of those sessions for
the life of the open shop. Each role session SHALL use the verified project root
as its `workspace-write` sandbox boundary and SHALL use the configured Codex
approval behavior rather than an application-forced unrestricted execution
policy. Codex SHALL tell the maker its stable local browser location only after
the initial model is ready, the service is available, and all three agents are
running. The default browser location SHALL use port 9000, and Codex SHALL be
able to use an explicitly configured port instead.

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

#### Scenario: Role sessions are sandboxed to the project
- **WHEN** Codex opens the shop after preparing `projects/<name>`
- **THEN** each Foreman, Designer, and Machinist session uses that verified repository as its workspace-write sandbox boundary and retains the configured Codex approval behavior
