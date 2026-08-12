# shop-browser-workspace Specification

## Purpose

Provide the maker with a structured per-project workspace for live shop
context, artifact inspection, and user-facing-agent conversation.

## Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop SHALL present the maker with one full-height browser workspace for each
open project, at a browser location that identifies that project. The browser
document title and visible workspace title bar SHALL identify the product as
`SolidNode Studio` and SHALL identify which project the workspace shows. On a
desktop browser, the workspace SHALL provide a title bar and status bar
surrounding an activity rail, an area-specific left context panel, a flexible
central Model, Code, or Agents area, and a right conversation area. The activity
rail SHALL show interactive Model first, Code second, and Agents third; it SHALL
omit Files and show Sheets as a hoverable non-interactive deferred area. The status
bar SHALL remain visible and need not contain status content until that
information is available.

The workspace SHALL offer the maker a way to close the project it shows, and
SHALL return the maker to the hub when that project is no longer open.

#### Scenario: A maker opens a project workspace
- **WHEN** the maker opens a project from the hub
- **THEN** the browser and visible title bar identify `SolidNode Studio` and that project, and the page shows Model, Code, Agents, the area-specific context, central work area, and conversation within the desktop workspace shell

#### Scenario: A maker views the desktop workspace
- **WHEN** the maker opens a project workspace in a desktop browser window
- **THEN** the Model, Code, or Agents area is the flexible central viewport and the conversation is a distinct right-side column

#### Scenario: A maker selects Code
- **WHEN** the maker selects the second activity-rail item
- **THEN** the left panel shows the project-root navigator and the center shows the Monaco editor without moving the conversation

#### Scenario: A maker selects Agents
- **WHEN** the maker selects the third activity-rail item
- **THEN** the left panel shows the session roster and the center shows the selected agent inspector without moving the conversation

#### Scenario: A maker hovers the deferred activity area
- **WHEN** the maker hovers Sheets in the activity rail
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

### Requirement: The workspace menu preserves live shop context
The Model context panel SHALL show the current functional model's supported
assembly navigator when that model is mounted, alongside every
profile-declared agent's profile-provided display label and live state using
the run data of the project that workspace shows. The assembly navigator SHALL
not require or invent model data outside the viewer's published assembly, and
the panel SHALL NOT require or invent separate profile display labels, build
metadata, or per-agent assignment detail. It SHALL NOT show an agent belonging
to another open project.

#### Scenario: The default profile is visible
- **WHEN** the maker opens the workspace of a project declaring `builder`
- **THEN** the Model panel shows the mounted model's assembly navigator and
  Builder's live state

#### Scenario: Fordesmac is visible
- **WHEN** the maker opens the workspace of a project declaring `fordesmac`
- **THEN** the Model panel shows the mounted model's assembly navigator and
  Foreman, Designer, Machinist, and Librarian

#### Scenario: An agent changes work state
- **WHEN** a declared agent's state changes while its project's workspace is open
- **THEN** that agent's state updates without a page reload

#### Scenario: Two project workspaces are open at once
- **WHEN** the maker views two open projects in two browser locations
- **THEN** each Model panel shows only its own project's assembly and agents
  and their states

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
- **WHEN** the maker opens a project whose first model build did not produce a complete model
- **THEN** the Model area states why no model is available and the Code and conversation areas remain usable

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

### Requirement: Workspace-area changes preserve Agents context
Changing among Model, Code, and Agents SHALL preserve the mounted conversation
and its draft and scroll, every Monaco file model and buffer state, the mounted
functional viewer's camera and timeline state, and the Agents selection, filter,
expanded records, and unapplied runtime draft. A workspace-area change SHALL NOT
create another live-state connection or reload project conversation.

#### Scenario: The maker returns to Agents
- **WHEN** the maker selects an agent, expands a tool result, works in Model, and returns to Agents
- **THEN** the same agent, filter, expanded result, and unapplied runtime draft remain present

### Requirement: Browser participant presentation comes from the active profile
The browser SHALL render the human label, user-facing agent label, roster
labels, conversation attribution, and accessibility text supplied in run state.
It MUST NOT hard-code `Maker`,
`Foreman`, or another profile participant as the meaning of an internal author
ID.

#### Scenario: A profile changes the human label
- **WHEN** a valid profile declares a human label other than `Maker`
- **THEN** the transcript and relevant accessibility text use that configured label while API identity remains `user`

### Requirement: The workspace explains recoverable role failures
While any manifested role is failed, the browser SHALL show a live, accessible notice in the conversation area that identifies the role by its profile-provided label, displays the backend-provided reason, and tells the maker that they can message the configured user-facing agent after backend access is restored to resume the shop. The notice SHALL be derived from current run state rather than inserted as participant-authored conversation and SHALL disappear when the role recovers.

#### Scenario: Claude reports a Machinist session limit
- **WHEN** the Machinist role reports that its provider session limit has been reached
- **THEN** the open workspace displays a Machinist failure notice with that reason while keeping the shop and composer available

#### Scenario: A failed Foreman is retriggered
- **WHEN** the maker sends a new message after Foreman's backend access is restored and the new turn is accepted
- **THEN** the failure notice clears without a page reload and the conversation remains available

#### Scenario: The page reconnects during a role failure
- **WHEN** a page connects or reconnects while any role is failed
- **THEN** it displays the same current failure notice from the snapshot
