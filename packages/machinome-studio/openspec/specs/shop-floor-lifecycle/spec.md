# shop-floor-lifecycle Specification

## Purpose
TBD - created by archiving change open-and-close-shop. Update Purpose after archive.
## Requirements
### Requirement: Codex opens the FastAPI shop floor
The system SHALL allow a maker to ask Codex to open shop-floor. Codex SHALL
run the local shop-floor service and tell the maker its stable local browser
location. The default browser location SHALL use port 9000, and Codex SHALL be
able to use an explicitly configured port instead.

#### Scenario: A maker opens the shop
- **WHEN** a maker asks Codex to open the shop without configuring a port
- **THEN** Codex runs the shop-floor service and provides its browser location
  on port 9000

#### Scenario: A maker opens the shop on a configured port
- **WHEN** a maker asks Codex to open the shop with an explicit port
- **THEN** Codex runs the shop-floor service and provides its browser location
  on that port

#### Scenario: The shop cannot be opened
- **WHEN** a maker asks Codex to open the shop and shop-floor cannot run
- **THEN** Codex tells the maker that the shop could not be opened

### Requirement: Codex closes the shop floor
The system SHALL allow a maker to ask Codex to close shop-floor. Codex SHALL
stop the shop-floor service and tell the maker that the shop is closed.

#### Scenario: A maker closes the shop
- **WHEN** a maker asks Codex to close the shop
- **THEN** Codex stops shop-floor and reports that the shop is closed

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
