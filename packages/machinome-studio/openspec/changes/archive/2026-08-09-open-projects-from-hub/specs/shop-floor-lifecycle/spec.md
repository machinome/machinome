## RENAMED Requirements

- FROM: `### Requirement: The shop validates the model before it becomes open`
- TO: `### Requirement: The shop reports the model state of an opened project`

- FROM: `### Requirement: A maker can open the shop with the Claude backend`
- TO: `### Requirement: A maker can open a project with the Claude backend`

## MODIFIED Requirements

### Requirement: The orchestrator opens the shop floor
The system SHALL allow the user to start the shop without naming a project, a
profile, or any other project choice, and SHALL then open a shop floor for any
project the user chooses while it runs. Starting the shop SHALL prepare no
project, build no model, and start no agent.

Opening a project SHALL resolve and validate that project's profile and its
selected backend settings before project creation, validation, or build. It
SHALL then prepare the corresponding project repository, attempt the initial
model build, and start persistent sessions for exactly the profile's standing
agents through the selected backend. Each session SHALL use the verified project
root as its workspace boundary.

A project SHALL be reported as open only after profile validation, project
preparation, and all declared agents are complete. The shop's default port SHALL
be 9000 and an explicit port SHALL remain supported.

#### Scenario: The user starts the shop
- **WHEN** the user starts the shop without any project option
- **THEN** the shop reports its browser location on port 9000 with no project prepared, no model built, and no agent running

#### Scenario: The user starts the shop on a configured port
- **WHEN** the user starts the shop with an explicit non-default port
- **THEN** the shop reports the matching browser location on that port

#### Scenario: The user opens a project declaring Fordesmac
- **WHEN** the user opens a project whose declared profile is `fordesmac`
- **THEN** the shop validates that profile and opens Foreman, Designer, Machinist, and Librarian sessions for that project

#### Scenario: Profile and backend are selected independently
- **WHEN** a project declares either initial profile with Codex, Claude, or OpenCode runtimes
- **THEN** that backend opens exactly the agents declared by that profile

#### Scenario: Profile validation fails
- **WHEN** the profile a project declares is invalid or incomplete for its selected backend
- **THEN** the shop starts no preparation, build, or agent process for that project, reports the profile error, and remains available with every other project unaffected

#### Scenario: Project preparation fails
- **WHEN** a validly configured project cannot be created or validated
- **THEN** the shop opens no agent session for it, reports why it did not open, and leaves that project not open

#### Scenario: Opening fails after preparation
- **WHEN** any declared agent session cannot start after the project is ready
- **THEN** the shop ends everything started for that attempt, reports that the project could not be opened, and leaves no partial session

#### Scenario: Profile sessions are sandboxed to the project
- **WHEN** a valid profile opens after preparing a chosen project
- **THEN** every declared agent session uses that exact verified repository as its workspace boundary

#### Scenario: Failure to open one project leaves others alone
- **WHEN** opening one project fails for any reason while other projects are open
- **THEN** those projects stay open with their agents, conversations, and models unaffected

### Requirement: The orchestrator closes the shop floor
The user SHALL be able to close an open project. The shop SHALL end every agent
session that project's profile declared through its selected backend before
reporting it closed. Close SHALL be bounded, active work SHALL NOT prevent it,
and no owned agent process may remain afterward. Closing a project SHALL NOT
stop the shop or disturb any other open project.

Stopping the shop SHALL close every open project on the same terms before the
shop exits.

#### Scenario: The user closes a project
- **WHEN** the user closes an open project
- **THEN** the shop ends every session of that project's profile, reports it closed, and keeps running

#### Scenario: The user closes while work is active
- **WHEN** a project is closed while direct or delegated work is active
- **THEN** the shop ends the active work without leaving an agent session or broker process for that project

#### Scenario: One agent will not stop
- **WHEN** an owned agent process does not exit when asked
- **THEN** the backend forces it to stop, releases all others of that project, and close completes

#### Scenario: Ending active work reports an error
- **WHEN** interrupting one profile agent reports an error during close
- **THEN** the shop still releases that project's remaining sessions and reports it closed

#### Scenario: The shop stops with projects open
- **WHEN** the shop is stopped while several projects are open
- **THEN** every open project is closed on these terms and no owned agent process survives

### Requirement: The shop reports the model state of an opened project
When a project is opened, the system SHALL build that project's default `root`
functional model and SHALL make the outcome of that build observable in the
project's workspace. A build that cannot produce a complete model SHALL NOT
prevent the project from opening: the maker SHALL be told why the model is not
available, in the workspace, where the project's sources can be corrected.

A model build SHALL NOT gate the availability of the shop, the hub, or any other
project.

#### Scenario: The initial model build succeeds
- **WHEN** a project with a buildable default `root` model is opened
- **THEN** the project's workspace presents the complete model for inspection

#### Scenario: The initial model build fails
- **WHEN** a project's default `root` model does not produce a complete viewer snapshot
- **THEN** the project still opens with its agents present and its workspace states why the model could not be built

#### Scenario: A project that could not build is corrected
- **WHEN** the sources of an opened project whose initial build failed are corrected
- **THEN** the workspace presents the completed model without the project being reopened

### Requirement: The browser shows the shop lifecycle without a reload
The shop SHALL serve a browser page that displays `Shop is open` while its live
connection to the service is established, and `Shop is closed` when that
connection is lost. The page SHALL NOT maintain a second connection for
lifecycle status. If the service restarts at the same local browser location,
the already-open page SHALL reconnect and display `Shop is open` again without a
page reload.

Because a project's session does not survive the service, a page displaying a
project whose session no longer exists after reconnection SHALL be returned to
the hub rather than left displaying a session that has ended. A page displaying
a project whose session is intact SHALL display that session's actual state —
not merely the open indicator — without a page reload.

#### Scenario: The browser opens while the shop is running
- **WHEN** a maker opens the shop's browser location while the service is running
- **THEN** the page displays `Shop is open`

#### Scenario: The service stops while the browser page remains open
- **WHEN** the shop service shuts down while its browser page remains open
- **THEN** the page displays `Shop is closed` without a page reload

#### Scenario: The service restarts while a project page remains open
- **WHEN** the shop service restarts at the same browser location while a page displaying a project remains open
- **THEN** the page reconnects, displays `Shop is open`, and is returned to the hub, which lists that project as not open

#### Scenario: The connection returns while the session is intact
- **WHEN** a page displaying a project loses and regains its live connection while that project's session continues
- **THEN** the page displays that session's agents, work states, and conversation without a page reload

#### Scenario: The reconnected page observes new work
- **WHEN** a page has reconnected to an intact session and that session manifests an agent or records a conversation entry
- **THEN** the page displays that change without a page reload

### Requirement: A maker can open a project with the Claude backend
The shop SHALL support both initial profiles through Claude using the same
broker, profile prompts, profile skills, topology, and lifecycle outcomes as the
other backends. Claude SHALL be reached by a project selecting a `claude:<model>`
runtime for an agent.

#### Scenario: Builder opens with Claude
- **WHEN** a project declaring `builder` selects a Claude runtime for Builder and is opened
- **THEN** the shop opens one Builder Claude session with the Builder profile contract

#### Scenario: Fordesmac opens with Claude
- **WHEN** a project declaring `fordesmac` selects a Claude runtime for all four agents and is opened
- **THEN** the shop opens four project-sandboxed Claude sessions carrying the Fordesmac contracts

#### Scenario: Fordesmac opens across two backends
- **WHEN** a project declaring `fordesmac` selects Claude for Designer and Codex for the other three agents and is opened
- **THEN** the shop opens one project-sandboxed Claude session for Designer and three Codex sessions, all on that project's broker with the same lifecycle outcomes
