## ADDED Requirements

### Requirement: Session live state includes runtime and agent activity
The project session snapshot SHALL include each manifested role's resolved
backend, provider, model, reasoning level, tool summary, runtime-mutation
support, authoritative idle availability, current and queued assignment data,
and the session's bounded recent agent activity. Subsequent runtime, lifecycle,
catalogue-availability, and activity changes SHALL arrive through the existing
project live-state connection in publication order without polling or a second
connection.

#### Scenario: A browser connects to an idle mixed-backend session
- **WHEN** a maker opens Agents after Codex and OpenCode roles have manifested
- **THEN** the existing snapshot is sufficient to display each role's current runtime, editability, idle availability, assignments, and recent activity

#### Scenario: A runtime update succeeds
- **WHEN** an idle role applies a new model and reasoning level
- **THEN** connected workspaces receive its complete updated agent value and a runtime-change activity record without another request

#### Scenario: A tool runs while Agents is visible
- **WHEN** the selected role starts and completes a tool operation
- **THEN** the existing live-state stream adds and then updates that activity record in publication order
