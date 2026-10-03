## MODIFIED Requirements

### Requirement: A maker can open a project with the Claude backend
The shop SHALL support both initial profiles through Claude using the same
broker, profile prompts, profile skills, topology, and lifecycle outcomes as the
other backends. Claude SHALL be reached by a project selecting a `claude:<model>`
runtime for an agent, and SHALL be the backend an agent opens on when the
project selects no runtime for it.

#### Scenario: Builder opens with Claude
- **WHEN** a project declaring `openspec` selects a Claude runtime for Builder and is opened
- **THEN** the shop opens one Builder Claude session with the `openspec` profile's Builder contract

#### Scenario: Fordesmac opens with Claude
- **WHEN** a project declaring `fordesmac` selects a Claude runtime for all four agents and is opened
- **THEN** the shop opens four project-sandboxed Claude sessions carrying the Fordesmac contracts

#### Scenario: Fordesmac opens across two backends
- **WHEN** a project declaring `fordesmac` selects OpenCode for Designer and names no runtime for the other three agents and is opened
- **THEN** the shop opens one project-sandboxed OpenCode session for Designer and three Claude sessions, all on that project's broker with the same lifecycle outcomes
