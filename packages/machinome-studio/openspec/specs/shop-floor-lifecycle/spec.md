# shop-floor-lifecycle Specification

## Purpose

Define fail-closed preparation, opening, operation, and shutdown of the local
shop floor across supported agent backends.
## Requirements
### Requirement: The orchestrator opens the shop floor
The system SHALL allow a maker to open shop-floor for a required workspace
project name. Before starting the local service or any agent, the shop runtime
SHALL prepare the corresponding `projects/<name>` repository and complete its
initial functional-model build. It SHALL then run the local shop-floor service,
start persistent sessions for the foreman, designer, and machinist through the
selected agent backend in that verified project root, and keep control of those
sessions for the life of the open shop. Each role session SHALL use the
verified project root as its workspace boundary. The shop runtime SHALL tell
the maker its stable local browser location only after the initial model is
ready, the service is available, and all three agents are running. The default
browser location SHALL use port 9000, and the runtime SHALL be able to use an
explicitly configured port instead.

#### Scenario: A maker opens the shop
- **WHEN** a maker opens the shop for a named project without configuring a port
- **THEN** the runtime prepares and builds that project, runs the shop-floor service and three-agent team in it, and provides its browser location on port 9000

#### Scenario: A maker opens the shop on a configured port
- **WHEN** a maker opens the shop for a named project with an explicit port
- **THEN** the runtime prepares and builds that project, runs the shop-floor service and three-agent team in it, and provides its browser location on that port

#### Scenario: A maker opens the shop with the Codex backend
- **WHEN** a maker opens the shop with `--backend codex` (or omitting the flag)
- **THEN** the runtime uses the Codex backend for all three agent sessions

#### Scenario: A maker opens the shop with the Hermes backend
- **WHEN** a maker opens the shop with `--backend hermes`
- **THEN** the runtime uses the Hermes backend for all three agent sessions

#### Scenario: Project preparation fails
- **WHEN** the named project cannot be created, validated, or built into a complete initial model
- **THEN** the runtime starts no floor service or agent session, provides no browser location, and tells the maker why the shop was not opened

#### Scenario: The runtime cannot be opened after project preparation
- **WHEN** the service or any required agent session cannot be started after the project is ready
- **THEN** the runtime ends anything started for that attempt and tells the maker that the shop could not be opened

#### Scenario: Role sessions are sandboxed to the project
- **WHEN** the runtime opens the shop after preparing `projects/<name>`
- **THEN** each Foreman, Designer, and Machinist session uses that verified repository as its workspace boundary

### Requirement: The orchestrator closes the shop floor
The system SHALL allow a maker to close shop-floor. The shop runtime SHALL end
the foreman, designer, and machinist sessions through the selected backend and
stop the shop-floor service before telling the maker that the shop is closed.

Closing SHALL complete within a bounded time. Ending a session that has active
work SHALL NOT prevent the runtime from closing, and no agent subprocess SHALL
be left running after the maker is told the shop is closed. When the selected
backend owns more than one agent subprocess, this SHALL hold for every one of
them.

#### Scenario: A maker closes the shop
- **WHEN** a maker closes the shop
- **THEN** the runtime ends all three shop-agent sessions, stops shop-floor, and reports that the shop is closed

#### Scenario: A maker closes the shop while work is active
- **WHEN** a maker closes the shop while one or more agents have active work
- **THEN** the runtime ends the active shop runtime without leaving an agent session or broker process running

#### Scenario: Closing does not hang on an agent that will not stop
- **WHEN** a maker closes the shop and the agent subprocess does not exit when asked
- **THEN** the runtime forces it to stop, completes the close, and reports that the shop is closed

#### Scenario: Ending active work does not abort the close
- **WHEN** ending an agent's active work reports an error while the shop is closing
- **THEN** the runtime still ends the remaining sessions, stops shop-floor, and reports that the shop is closed

#### Scenario: Closing releases every process of a multi-process backend
- **WHEN** a maker closes the shop running a backend that owns one subprocess per role and one of those subprocesses does not exit when asked
- **THEN** the runtime forces that subprocess to stop, still releases the others, and reports that the shop is closed

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
while its lifecycle-status stream is connected. The page SHALL maintain a
Server-Sent Events connection to the service and display `Shop is closed` when
that connection is lost. If the service restarts at the same local browser
location, the already-open page SHALL reconnect and display `Shop is open`
again without a page reload.

#### Scenario: The browser opens while shop-floor is running
- **WHEN** a maker opens the shop-floor browser location while the service is running
- **THEN** the page displays `Shop is open`

#### Scenario: The service stops while the browser page remains open
- **WHEN** the shop-floor service shuts down while its browser page remains open
- **THEN** the page displays `Shop is closed` without a page reload

#### Scenario: The service restarts while the browser page remains open
- **WHEN** the shop-floor service restarts at the same browser location after the page displayed `Shop is closed`
- **THEN** the page reconnects through Server-Sent Events and displays `Shop is open` without a page reload

### Requirement: A maker can open the shop with the Claude backend
The shop runtime SHALL support opening the shop with the Claude backend, using
the same broker, role cards, skills, and product pipeline as the other backends.

#### Scenario: A maker opens the shop with the Claude backend
- **WHEN** a maker opens the shop with `--backend claude`
- **THEN** the runtime uses the Claude backend for all three agent sessions

#### Scenario: Claude role sessions are sandboxed to the project
- **WHEN** the runtime opens the shop with the Claude backend after preparing `projects/<name>`
- **THEN** each Foreman, Designer, and Machinist session uses that verified repository as its workspace boundary

