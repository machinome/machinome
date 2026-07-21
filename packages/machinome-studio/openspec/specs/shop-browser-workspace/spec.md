# shop-browser-workspace Specification

## Purpose

Provide the maker with one structured shop-floor workspace for live shop
context, artifact inspection, and foreman conversation.

## Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop floor SHALL present the maker with one full-height browser workspace
containing a left shop-menu column and a right content column at the shop-floor
browser location. The content column SHALL contain the artifact area above the
conversation area, with each area receiving half of the available content
height in a desktop browser.

#### Scenario: A maker opens the shop floor
- **WHEN** the maker opens the running shop-floor browser location
- **THEN** the page shows the menu as a left column and the artifact and conversation areas as vertically stacked right-side panes

#### Scenario: A maker views the desktop workspace
- **WHEN** the maker opens the shop floor in a desktop browser window
- **THEN** the artifact and conversation areas are both visible and receive equal shares of the right-side content height

#### Scenario: A maker uses a narrow browser window
- **WHEN** the maker opens the shop floor in a narrow browser window
- **THEN** every workspace area remains reachable without horizontal page overflow

### Requirement: The workspace menu preserves live shop context
The full-height workspace menu SHALL show the current shop lifecycle status,
active run identity, and manifested-agent state using the existing live
shop-floor data.

#### Scenario: An agent changes work state
- **WHEN** a manifested agent's state changes while the maker is viewing the workspace
- **THEN** the corresponding agent state in the workspace menu updates without a page reload

### Requirement: Deferred workspace areas are truthful
Until artifact inspection is available, the artifact area SHALL show that no
artifact is selected. Once a functional model is available, it SHALL present an
interactive, correctly materialled browser viewer. The foreman-conversation
area SHALL show the active foreman conversation and a control for directing the
foreman; it SHALL not claim that a foreman conversation is unavailable.

#### Scenario: The workspace has no selected artifact
- **WHEN** the maker opens the Story 3 workspace before artifact inspection is implemented
- **THEN** the artifact area shows its empty state and the foreman-conversation area remains available for conversation

#### Scenario: The workspace has a built functional model
- **WHEN** the shop floor has successfully built the project's functional model
- **THEN** the artifact area presents the current completed `_build` model as an interactive browser viewer instead of the empty state

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
