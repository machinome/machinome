## MODIFIED Requirements

### Requirement: The shop menu shows a rolling broker-event log
Below the manifested-agent roster, the workspace menu SHALL show a bounded
rolling log of the most recent broker events with the newest event first. Each
event SHALL appear in its own compact entry with enough information to identify
the event kind and involved shop role, a readable timestamp of when the broker
recorded it, and without displaying full instruction or report text.

#### Scenario: A broker event occurs while the workspace is open
- **WHEN** an agent is manifested, receives or changes work, reports, or stops
- **THEN** a compact timestamped event entry appears immediately below the
  agent roster without a page reload

#### Scenario: The rolling limit is reached
- **WHEN** another broker event arrives after the event log has reached its
  configured bound
- **THEN** the oldest displayed event is removed and the newest timestamped
  event is shown first

#### Scenario: The maker reconnects to an open shop
- **WHEN** the maker loads or reconnects to the workspace after broker events
  have occurred
- **THEN** the menu restores the broker's current bounded event history in
  newest-first order with a timestamp on every event
