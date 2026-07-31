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
The full-height workspace menu SHALL show current lifecycle status, run
identity, stable active profile ID, and every profile-declared agent's display
label and live state using broker run data. It SHALL NOT require or invent a
separate profile display label.

#### Scenario: The default profile is visible
- **WHEN** the user opens a default-profile workspace
- **THEN** the menu identifies profile `builder` and shows Builder's live state

#### Scenario: Fordesmac is visible
- **WHEN** the user opens a Fordesmac workspace
- **THEN** the menu identifies profile `fordesmac` and shows Foreman, Designer, Machinist, and Librarian

#### Scenario: An agent changes work state
- **WHEN** a declared agent's state changes while the workspace is open
- **THEN** that agent's state updates without a page reload

### Requirement: Deferred workspace areas are truthful
The artifact area SHALL present the current interactive functional-model viewer
when a complete model exists. The conversation area SHALL show the active
profile conversation and allow direction to its one user-facing agent without
role-specific composer wording or a direct control for another agent.

#### Scenario: The workspace has a built functional model
- **WHEN** the shop floor has successfully built the project's functional model
- **THEN** the artifact area presents the completed `_build` model as an interactive viewer

#### Scenario: The selected profile conversation is available
- **WHEN** either initial profile opens
- **THEN** the conversation area attributes the human and user-facing agent with profile-provided labels and accepts direction for that agent

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
- **WHEN** another broker event arrives after the event log has reached its configured bound
- **THEN** the oldest displayed event is removed and the newest timestamped
  event is shown first

#### Scenario: The maker reconnects to an open shop
- **WHEN** the maker loads or reconnects to the workspace after broker events have occurred
- **THEN** the menu restores the broker's current bounded event history in
  newest-first order with a timestamp on every event

### Requirement: Browser participant presentation comes from the active profile
The browser SHALL render the human label, user-facing agent label, roster
labels, conversation attribution, event-log participant summaries, and
accessibility text supplied in run state. It MUST NOT hard-code `Maker`,
`Foreman`, or another profile participant as the meaning of an internal author
ID.

#### Scenario: A profile changes the human label
- **WHEN** a valid profile declares a human label other than `Maker`
- **THEN** the transcript and relevant accessibility text use that configured label while API identity remains `user`
