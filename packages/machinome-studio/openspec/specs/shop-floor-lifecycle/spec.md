# shop-floor-lifecycle Specification

## Purpose
TBD - created by archiving change open-and-close-shop. Update Purpose after archive.
## Requirements
### Requirement: Codex opens the FastAPI shop floor
The system SHALL allow a maker to ask Codex to open shop-floor. The Codex shop
runtime SHALL run the local shop-floor service, start persistent sessions for
the foreman, designer, and machinist, and keep control of those sessions for
the life of the open shop. Codex SHALL tell the maker its stable local browser
location only after the service is available and all three agents are running.
The default browser location SHALL use port 9000, and Codex SHALL be able to
use an explicitly configured port instead.

#### Scenario: A maker opens the shop
- **WHEN** a maker asks Codex to open the shop without configuring a port
- **THEN** Codex runs the shop-floor service and the three-agent team and provides its browser location on port 9000

#### Scenario: A maker opens the shop on a configured port
- **WHEN** a maker asks Codex to open the shop with an explicit port
- **THEN** Codex runs the shop-floor service and the three-agent team and provides its browser location on that port

#### Scenario: The shop cannot be opened
- **WHEN** the service or any required Codex agent cannot be started
- **THEN** Codex ends anything started for that attempt and tells the maker that the shop could not be opened

### Requirement: Codex closes the shop floor
The system SHALL allow a maker to ask Codex to close shop-floor. The Codex shop
runtime SHALL end the foreman, designer, and machinist sessions and stop the
shop-floor service before telling the maker that the shop is closed.

#### Scenario: A maker closes the shop
- **WHEN** a maker asks Codex to close the shop
- **THEN** Codex ends all three shop-agent sessions, stops shop-floor, and reports that the shop is closed

#### Scenario: A maker closes the shop while work is active
- **WHEN** a maker asks Codex to close the shop while one or more agents have active work
- **THEN** Codex ends the active shop runtime without leaving an agent session or broker process running

### Requirement: The shop validates the model before it becomes open
When Codex opens a project shop floor, the system SHALL build the selected
project-local functional model before making the shop floor available at its
browser location. If that build cannot produce a model, the system SHALL tell
the maker why the shop was not opened.

#### Scenario: The initial model build succeeds
- **WHEN** Codex opens a shop for a project with a buildable selected model path
- **THEN** Codex starts the shop-floor service and provides its browser location only after the model is ready for inspection

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
