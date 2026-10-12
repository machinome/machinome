## MODIFIED Requirements

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
