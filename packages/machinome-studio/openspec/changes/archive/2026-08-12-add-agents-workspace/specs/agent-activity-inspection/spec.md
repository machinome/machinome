## ADDED Requirements

### Requirement: The shop normalizes agent activity for inspection
Each backend SHALL translate observable role messages, tool calls and results,
file changes with available unified diffs, and role errors into portable agent
activity records without exposing backend-native session or event identifiers.
Each record SHALL identify its role, category, state, time, display name and
summary, and MAY include bounded detail, path, diff, and native token usage when
available. A running operation and its later result SHALL share one stable
activity identity and SHALL be presented as one updated operation.

#### Scenario: A tool completes
- **WHEN** a backend reports a tool start and later its result for one agent
- **THEN** the session activity contains one tool record that changes from running to its completed or failed result

#### Scenario: An agent edits a file
- **WHEN** a backend reports a file edit with a unified diff
- **THEN** the activity record identifies the project path and preserves the bounded unified diff for inspection

#### Scenario: A backend has no token usage
- **WHEN** an activity frame carries no reliable token accounting
- **THEN** the record omits token usage rather than inventing or estimating it

### Requirement: Agent activity remains bounded and session-scoped
The shop SHALL stream every accepted activity update to browsers of that session
through the existing project live-state connection and SHALL retain a bounded
recent activity history in the session snapshot. Activity from another project
SHALL NOT appear, and ending the ephemeral session SHALL discard its activity.

#### Scenario: A browser opens after tools ran
- **WHEN** a maker opens or reloads an active project after recent agent tools completed
- **THEN** the first session snapshot contains that project's retained recent activity

#### Scenario: Activity exceeds the retained bound
- **WHEN** a session produces more activity than its configured history bound
- **THEN** connected browsers receive the live records and a later snapshot contains the newest bounded history without growing indefinitely

#### Scenario: Two projects have active agents
- **WHEN** agents in two open projects publish activity
- **THEN** each project workspace receives only its own activity

### Requirement: The maker can inspect and filter one agent's activity
The Agents workspace SHALL let the maker select a manifested agent and inspect
that agent's retained and live activity in publication order. The maker SHALL be
able to filter all activity, tools, files, messages, or errors; expand tool
details; inspect unified diffs; and open a diff's project path in the Code area.
The feed SHALL update without a page reload or an additional live connection.

#### Scenario: The maker selects an agent
- **WHEN** the maker selects Designer in the Agents roster
- **THEN** the central header and feed show Designer's current runtime, state, and activity only

#### Scenario: The maker filters files
- **WHEN** the maker chooses the files filter
- **THEN** the feed shows that agent's file activity and hides its other activity without changing retained data

#### Scenario: The maker opens a changed file
- **WHEN** the maker activates Open in Code on an available activity path
- **THEN** the workspace selects Code and opens that project file through the existing source workspace
