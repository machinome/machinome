## ADDED Requirements

### Requirement: The shop menu shows a rolling broker-event log
Below the manifested-agent roster, the workspace menu SHALL show a bounded
rolling log of the most recent broker events in recorded order. Each event
SHALL appear in its own compact entry with enough information to identify the
event kind and involved shop role without displaying full instruction or
report text.

#### Scenario: A broker event occurs while the workspace is open
- **WHEN** an agent is manifested, receives or changes work, reports, or stops
- **THEN** a compact event entry appears below the agent roster without a page reload

#### Scenario: The rolling limit is reached
- **WHEN** another broker event arrives after the event log has reached its configured bound
- **THEN** the oldest displayed event is removed and the newest event is shown

#### Scenario: The maker reconnects to an open shop
- **WHEN** the maker loads or reconnects to the workspace after broker events have occurred
- **THEN** the menu restores the broker's current bounded event history in recorded order
