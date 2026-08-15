## MODIFIED Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop SHALL present the maker with one full-height browser workspace for each
open project, at a browser location that identifies that project. The browser
document title and visible workspace title bar SHALL identify the product as
`LibreSolid Studio` and SHALL identify which project the workspace shows. On a
desktop browser, the workspace SHALL provide a title bar and status bar
surrounding an activity rail, an area-specific left context panel, a flexible
central Model, Code, Agents, or Build area, and a right conversation area. The
activity rail SHALL show interactive Model first, Code second, Agents third,
and Build fourth; it SHALL omit Files and the deferred Sheets area. The status
bar SHALL remain visible and need not contain status content until that
information is available.

The workspace SHALL offer the maker a way to close the project it shows, and
SHALL return the maker to the hub when that project is no longer open.

#### Scenario: A maker opens a project workspace
- **WHEN** the maker opens a project from the hub
- **THEN** the browser and visible title bar identify `LibreSolid Studio` and that project, and the page shows Model, Code, Agents, Build, the area-specific context, central work area, and conversation within the desktop workspace shell

#### Scenario: A maker views the desktop workspace
- **WHEN** the maker opens a project workspace in a desktop browser window
- **THEN** the selected Model, Code, Agents, or Build area is the flexible central viewport and the conversation is a distinct right-side column

#### Scenario: A maker selects Code
- **WHEN** the maker selects the second activity-rail item
- **THEN** the left panel shows the project-root navigator and the center shows the Monaco editor without moving the conversation

#### Scenario: A maker selects Agents
- **WHEN** the maker selects the third activity-rail item
- **THEN** the left panel shows the session roster and the center shows the selected agent inspector without moving the conversation

#### Scenario: A maker selects Build
- **WHEN** the maker selects the fourth activity-rail item
- **THEN** the left panel shows the distinct-piece navigator and the center shows the selected representative piece on the fixed virtual build volume without moving the conversation

#### Scenario: A maker uses a narrow browser window
- **WHEN** the maker opens a project workspace in a narrow browser window
- **THEN** every workspace area remains reachable without horizontal page overflow

#### Scenario: A maker closes the project they are working in
- **WHEN** the maker closes the project from its own workspace
- **THEN** that project closes and the maker is returned to the hub

#### Scenario: A maker asks for a project that is not open
- **WHEN** the maker reaches the browser location of a project that has no session
- **THEN** the maker is presented with the hub rather than an empty workspace
