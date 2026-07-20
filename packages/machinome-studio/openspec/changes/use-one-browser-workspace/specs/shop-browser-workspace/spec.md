## ADDED Requirements

### Requirement: The shop floor provides one browser workspace
The shop floor SHALL present the maker with one browser workspace containing a
shop menu, an artifact area, and a foreman-conversation area at the shop-floor
browser location.

#### Scenario: A maker opens the shop floor
- **WHEN** the maker opens the running shop-floor browser location
- **THEN** the page shows the shop menu, artifact area, and foreman-conversation area together

#### Scenario: A maker uses a narrow browser window
- **WHEN** the maker opens the shop floor in a narrow browser window
- **THEN** every workspace area remains reachable without horizontal page overflow

### Requirement: The workspace menu preserves live shop context
The workspace menu SHALL show the current shop lifecycle status, active run
identity, and manifested-agent state using the existing live shop-floor data.

#### Scenario: An agent changes work state
- **WHEN** a manifested agent's state changes while the maker is viewing the workspace
- **THEN** the corresponding agent state in the workspace menu updates without a page reload

### Requirement: Deferred workspace areas are truthful
Until their respective capabilities are available, the artifact area and the
foreman-conversation area SHALL show that no artifact is selected and that no
foreman conversation is available, respectively.

#### Scenario: The workspace has no artifact or conversation content
- **WHEN** the maker opens the Story 2 workspace before artifact inspection and foreman direction are implemented
- **THEN** the artifact and foreman-conversation areas show their respective empty states
