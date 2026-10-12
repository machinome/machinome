## ADDED Requirements

### Requirement: Session live state includes runtime and agent activity
The project session snapshot SHALL include each manifested role's resolved
backend, provider, model, reasoning level, tool summary, authoritative idle
availability, current and queued assignment data, and the
session's bounded recent agent activity. A role-scoped catalogue request SHALL
report mutation support and choices when the maker focuses that role.
Subsequent runtime, lifecycle, and activity changes SHALL arrive through the
existing project live-state connection in publication order without polling or
a second connection.

#### Scenario: A browser connects to an idle mixed-backend session
- **WHEN** a maker opens Agents after Codex and OpenCode roles have manifested
- **THEN** the existing snapshot displays each role's current runtime, idle availability, assignments, and recent activity, and the focused role's catalogue request supplies its editability and choices

#### Scenario: A runtime update succeeds
- **WHEN** an idle role applies a new model and reasoning level
- **THEN** connected workspaces receive its complete updated agent value and a runtime-change activity record without another request

#### Scenario: A tool runs while Agents is visible
- **WHEN** the selected role starts and completes a tool operation
- **THEN** the existing live-state stream adds and then updates that activity record in publication order
