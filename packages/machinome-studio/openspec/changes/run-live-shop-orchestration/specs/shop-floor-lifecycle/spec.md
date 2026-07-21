## MODIFIED Requirements

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
