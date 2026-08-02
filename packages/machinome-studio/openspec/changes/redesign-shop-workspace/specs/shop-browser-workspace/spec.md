## MODIFIED Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop floor SHALL present the maker with one full-height browser workspace
at the shop-floor browser location. On a desktop browser, it SHALL provide a
title bar and status bar surrounding an activity rail, an agent context panel,
a central artifact area, and a right conversation area. The activity rail SHALL
show Model as selected and SHALL show Files, Agents, Sheets, and Code as
hoverable, non-interactive deferred areas. The status bar SHALL be visible and
need not contain status content until that information is available.

#### Scenario: A maker opens the shop floor
- **WHEN** the maker opens the running shop-floor browser location
- **THEN** the page shows the activity rail, agent context panel, artifact area,
  and conversation area within the desktop workspace shell

#### Scenario: A maker views the desktop workspace
- **WHEN** the maker opens the shop floor in a desktop browser window
- **THEN** the artifact area is the flexible central viewport and the
  conversation is a distinct right-side column

#### Scenario: A maker hovers a deferred activity area
- **WHEN** the maker hovers Files, Agents, Sheets, or Code in the activity rail
- **THEN** the item shows its hover treatment and does not navigate, select a
  panel, or change the model viewport

#### Scenario: A maker uses a narrow browser window
- **WHEN** the maker opens the shop floor in a narrow browser window
- **THEN** every workspace area remains reachable without horizontal page overflow

### Requirement: The workspace menu preserves live shop context
The agent context panel SHALL show every profile-declared agent's
profile-provided display label and live state using broker run data. It SHALL
NOT require or invent a separate profile display label, model assembly data,
build metadata, or per-agent assignment detail.

#### Scenario: The default profile is visible
- **WHEN** the user opens a default-profile workspace
- **THEN** the agent panel shows Builder's live state

#### Scenario: Fordesmac is visible
- **WHEN** the user opens a Fordesmac workspace
- **THEN** the agent panel shows Foreman, Designer, Machinist, and Librarian

#### Scenario: An agent changes work state
- **WHEN** a declared agent's state changes while the workspace is open
- **THEN** that agent's state updates without a page reload

### Requirement: Deferred workspace areas are truthful
The central artifact area SHALL present the current interactive functional-model
viewer when a complete model exists. The conversation area SHALL show the
active profile conversation and allow direction to its one user-facing agent
without role-specific composer wording or a direct control for another agent.
The workspace SHALL NOT render agent activity transcript rows or status-bar
content until those capabilities are supported by available data and behaviour.

#### Scenario: The workspace has a built functional model
- **WHEN** the shop floor has successfully built the project's functional model
- **THEN** the central artifact area presents the completed `_build` model as an
  interactive viewer

#### Scenario: The selected profile conversation is available
- **WHEN** either initial profile opens
- **THEN** the right conversation area attributes the human and user-facing
  agent with profile-provided labels and accepts direction for that agent

#### Scenario: A model rebuild fails
- **WHEN** the project watcher reports a failed model rebuild after a completed
  model has been displayed
- **THEN** the central artifact area keeps the last completed model inspectable
  and displays the rebuild error beside it

## REMOVED Requirements

### Requirement: The shop menu shows a rolling broker-event log

**Reason**: The reference-design 1b slice reserves agent activity presentation
for a future capability and the current agent context panel contains only the
live roster.

**Migration**: The broker continues to retain and stream bounded events; no API
consumer changes are required. A later workspace increment can render those
events in a design-consistent activity surface.
