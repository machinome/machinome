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
- **WHEN** a project declares either initial profile with Claude or OpenCode runtimes
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

### Requirement: A maker can open a project with the Claude backend
The shop SHALL support both initial profiles through Claude using the same
broker, profile prompts, profile skills, topology, and lifecycle outcomes as the
other backends. Claude SHALL be reached by a project selecting a `claude:<model>`
runtime for an agent, and SHALL be the backend an agent opens on when the
project selects no runtime for it.

#### Scenario: Builder opens with Claude
- **WHEN** a project declaring `builder` selects a Claude runtime for Builder and is opened
- **THEN** the shop opens one Builder Claude session with the Builder profile contract

#### Scenario: Fordesmac opens with Claude
- **WHEN** a project declaring `fordesmac` selects a Claude runtime for all four agents and is opened
- **THEN** the shop opens four project-sandboxed Claude sessions carrying the Fordesmac contracts

#### Scenario: Fordesmac opens across two backends
- **WHEN** a project declaring `fordesmac` selects OpenCode for Designer and names no runtime for the other three agents and is opened
- **THEN** the shop opens one project-sandboxed OpenCode session for Designer and three Claude sessions, all on that project's broker with the same lifecycle outcomes
