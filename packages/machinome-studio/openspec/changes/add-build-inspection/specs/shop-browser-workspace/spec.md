## MODIFIED Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop SHALL present the maker with one full-height browser workspace for each open project, at a browser location that identifies that project. The browser document title and visible workspace title bar SHALL identify the product as `SolidNode Studio` and SHALL identify which project the workspace shows. On a desktop browser, the workspace SHALL provide a title bar and status bar surrounding an activity rail, an area-specific left context panel, a flexible central Model, Code, Agents, or Build area, and a right conversation area. The activity rail SHALL show interactive Model first, Code second, Agents third, and Build fourth; it SHALL omit Files and the deferred Sheets area. The status bar SHALL remain visible and need not contain status content until that information is available.

The workspace SHALL offer the maker a way to close the project it shows, and SHALL return the maker to the hub when that project is no longer open.

#### Scenario: A maker opens a project workspace
- **WHEN** the maker opens a project from the hub
- **THEN** the browser and visible title bar identify `SolidNode Studio` and that project, and the page shows Model, Code, Agents, Build, the area-specific context, central work area, and conversation within the desktop workspace shell

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

### Requirement: Workspace-area changes preserve live context
Changing among Model, Code, Agents, and Build SHALL preserve the mounted conversation and its draft and scroll, every Monaco file model and buffer state, the mounted functional viewer's camera and timeline state, the Agents selection, filter, expanded records, and unapplied runtime draft, and the Build piece selection and camera. A workspace-area change SHALL NOT create another live-state connection or reload project conversation.

#### Scenario: The maker changes area while composing direction
- **WHEN** the maker types an unsent chat message and switches among Model, Code, Agents, and Build
- **THEN** the same composer draft and conversation scroll remain present

#### Scenario: The maker returns to the model
- **WHEN** the maker changes the model camera, works in another area, and returns to Model
- **THEN** the existing viewer shows the same camera and timeline state

#### Scenario: The maker returns to Agents
- **WHEN** the maker selects an agent, expands a tool result, works in another area, and returns to Agents
- **THEN** the same agent, filter, expanded result, and unapplied runtime draft remain present

#### Scenario: The maker returns to Build
- **WHEN** the maker selects and orbits a piece, works in another area, and returns to Build
- **THEN** Build retains the selected piece and its camera without reloading project conversation
