## MODIFIED Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop SHALL present the maker with one full-height browser workspace for each
open project, at a browser location that identifies that project. The browser
document title and visible workspace title bar SHALL identify the product as
`SolidNode Studio` and SHALL identify which project the workspace shows. On a
desktop browser, the workspace SHALL provide a title bar and status bar
surrounding an activity rail, an agent context panel, a central artifact area,
and a right conversation area. The activity rail SHALL show Model as selected
and SHALL show Files, Agents, Sheets, and Code as hoverable, non-interactive
deferred areas. The status bar SHALL be visible and need not contain status
content until that information is available.

The workspace SHALL offer the maker a way to close the project it shows, and
SHALL return the maker to the hub when that project is no longer open.

#### Scenario: A maker opens a project workspace
- **WHEN** the maker opens a project from the hub
- **THEN** the browser and visible title bar identify `SolidNode Studio` and that project, and the page shows the activity rail, agent context panel, artifact area, and conversation area within the desktop workspace shell

#### Scenario: A maker views the desktop workspace
- **WHEN** the maker opens a project workspace in a desktop browser window
- **THEN** the artifact area is the flexible central viewport and the conversation is a distinct right-side column

#### Scenario: A maker hovers a deferred activity area
- **WHEN** the maker hovers Files, Agents, Sheets, or Code in the activity rail
- **THEN** the item shows its hover treatment and does not navigate, select a panel, or change the model viewport

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
The agent context panel SHALL show every profile-declared agent's
profile-provided display label and live state using the run data of the project
that workspace shows. It SHALL NOT require or invent a separate profile display
label, model assembly data, build metadata, or per-agent assignment detail, and
SHALL NOT show an agent belonging to another open project.

#### Scenario: The default profile is visible
- **WHEN** the maker opens the workspace of a project declaring `builder`
- **THEN** the agent panel shows Builder's live state

#### Scenario: Fordesmac is visible
- **WHEN** the maker opens the workspace of a project declaring `fordesmac`
- **THEN** the agent panel shows Foreman, Designer, Machinist, and Librarian

#### Scenario: An agent changes work state
- **WHEN** a declared agent's state changes while its project's workspace is open
- **THEN** that agent's state updates without a page reload

#### Scenario: Two project workspaces are open at once
- **WHEN** the maker views two open projects in two browser locations
- **THEN** each agent panel shows only its own project's agents and their states

### Requirement: Deferred workspace areas are truthful
The central artifact area SHALL present the current interactive functional-model
viewer when a complete model exists for the project that workspace shows. The
conversation area SHALL show that project's conversation and allow direction to
its one user-facing agent without role-specific composer wording or a direct
control for another agent. The workspace SHALL NOT render agent activity
transcript rows or status-bar content until those capabilities are supported by
available data and behaviour.

When no complete model exists for that project — including when the project's
first build did not produce one — the artifact area SHALL state why rather than
present an empty or misleading viewport.

#### Scenario: The workspace has a built functional model
- **WHEN** the shop has successfully built the project's functional model
- **THEN** the central artifact area presents the completed `_build` model as an interactive viewer

#### Scenario: The selected profile conversation is available
- **WHEN** a project declaring either initial profile is opened
- **THEN** the right conversation area attributes the human and user-facing agent with profile-provided labels and accepts direction for that agent

#### Scenario: A model rebuild fails
- **WHEN** the project watcher reports a failed model rebuild after a completed model has been displayed
- **THEN** the central artifact area keeps the last completed model inspectable and displays the rebuild error beside it

#### Scenario: A project opened without a buildable model
- **WHEN** the maker opens a project whose first model build did not produce a complete model
- **THEN** the central artifact area states why no model is available and the conversation area remains usable
