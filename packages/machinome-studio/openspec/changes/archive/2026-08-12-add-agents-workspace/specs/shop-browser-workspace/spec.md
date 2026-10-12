## MODIFIED Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop SHALL present the maker with one full-height browser workspace for each
open project, at a browser location that identifies that project. The browser
document title and visible workspace title bar SHALL identify the product as
`SolidNode Studio` and SHALL identify which project the workspace shows. On a
desktop browser, the workspace SHALL provide a title bar and status bar
surrounding an activity rail, an area-specific left context panel, a flexible
central Model, Code, or Agents area, and a right conversation area. The activity
rail SHALL show interactive Model first, Code second, and Agents third; it SHALL
omit Files and show Sheets as a hoverable non-interactive deferred area. The
status bar SHALL remain visible and need not contain status content until that
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

## ADDED Requirements

### Requirement: Workspace-area changes preserve Agents context
Changing among Model, Code, and Agents SHALL preserve the mounted conversation
and its draft and scroll, every Monaco file model and buffer state, the mounted
functional viewer's camera and timeline state, and the Agents selection, filter,
expanded records, and unapplied runtime draft. A workspace-area change SHALL NOT
create another live-state connection or reload project conversation.

#### Scenario: The maker returns to Agents
- **WHEN** the maker selects an agent, expands a tool result, works in Model, and returns to Agents
- **THEN** the same agent, filter, expanded result, and unapplied runtime draft remain present
