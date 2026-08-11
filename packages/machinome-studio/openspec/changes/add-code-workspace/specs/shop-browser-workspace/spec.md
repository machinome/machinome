## MODIFIED Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop SHALL present the maker with one full-height browser workspace for each
open project, at a browser location that identifies that project. The browser
document title and visible workspace title bar SHALL identify the product as
`SolidNode Studio` and SHALL identify which project the workspace shows. On a
desktop browser, the workspace SHALL provide a title bar and status bar
surrounding an activity rail, an area-specific left context panel, a flexible
central Model or Code area, and a right conversation area. The activity rail
SHALL show Model first and interactive Code second; it SHALL omit Files and
show Agents and Sheets as hoverable non-interactive deferred areas. The status
bar SHALL remain visible and need not contain status content until that
information is available.

The workspace SHALL offer the maker a way to close the project it shows, and
SHALL return the maker to the hub when that project is no longer open.

#### Scenario: A maker opens a project workspace
- **WHEN** the maker opens a project from the hub
- **THEN** the browser and visible title bar identify `SolidNode Studio` and that project, and the page shows Model, Code, the area-specific context, central work area, and conversation within the desktop workspace shell

#### Scenario: A maker views the desktop workspace
- **WHEN** the maker opens a project workspace in a desktop browser window
- **THEN** the Model or Code area is the flexible central viewport and the conversation is a distinct right-side column

#### Scenario: A maker selects Code
- **WHEN** the maker selects the second activity-rail item
- **THEN** the left panel shows the project-root navigator and the center shows the Monaco editor without moving the conversation

#### Scenario: A maker hovers a deferred activity area
- **WHEN** the maker hovers Agents or Sheets in the activity rail
- **THEN** the item shows its hover treatment and does not navigate, select a panel, or change the central area

#### Scenario: A maker uses a narrow browser window
- **WHEN** the maker opens a project workspace in a narrow browser window
- **THEN** every workspace area remains reachable without horizontal page overflow

#### Scenario: A maker closes the project they are working in
- **WHEN** the maker closes the project from its own workspace
- **THEN** that project closes and the maker is returned to the hub

#### Scenario: A maker asks for a project that is not open
- **WHEN** the maker reaches the browser location of a project that has no session
- **THEN** the maker is presented with the hub rather than an empty workspace

### Requirement: Deferred workspace areas are truthful
The Model area SHALL present the current interactive functional-model viewer
when a complete model exists for the project that workspace shows. The Code
area SHALL present only source and editor behavior supported by the project's
source API. The conversation area SHALL show that project's conversation and
allow direction to its one user-facing agent without role-specific composer
wording or a direct control for another agent. The workspace SHALL NOT render
agent activity transcript rows, unsupported file mutation controls, or
status-bar content until those capabilities are supported by available data
and behaviour.

When no complete model exists for that project — including when the project's
first build did not produce one — the Model area SHALL state why rather than
present an empty or misleading viewport, while Code and conversation remain
usable.

#### Scenario: The workspace has a built functional model
- **WHEN** the shop has successfully built the project's functional model
- **THEN** the Model area presents the completed `_build` model as an interactive viewer

#### Scenario: The selected profile conversation is available
- **WHEN** a project declaring either initial profile is opened
- **THEN** the right conversation area attributes the human and user-facing agent with profile-provided labels and accepts direction for that agent in both Model and Code

#### Scenario: A model rebuild fails
- **WHEN** the project watcher reports a failed model rebuild after a completed model has been displayed
- **THEN** the Model area keeps the last completed model inspectable and displays the rebuild error beside it while Code remains usable

#### Scenario: A project opened without a buildable model
- **WHEN** the maker opens a project whose first build did not produce a complete model
- **THEN** the Model area states why no model is available and the Code and conversation areas remain usable

## ADDED Requirements

### Requirement: Workspace-area changes preserve live context
Changing between Model and Code SHALL preserve the mounted conversation and its
draft and scroll, every Monaco file model and buffer state, and the mounted
functional viewer's camera and timeline state. A workspace-area change SHALL
NOT create another live-state connection or reload project conversation.

#### Scenario: The maker changes area while composing direction
- **WHEN** the maker types an unsent chat message and switches between Model and Code
- **THEN** the same composer draft and conversation scroll remain present

#### Scenario: The maker returns to the model
- **WHEN** the maker changes the model camera, works in Code, and returns to Model
- **THEN** the existing viewer shows the same camera and timeline state
