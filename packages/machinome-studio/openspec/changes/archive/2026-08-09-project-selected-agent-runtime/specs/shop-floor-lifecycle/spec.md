## MODIFIED Requirements

### Requirement: A maker can open the shop with the Claude backend
The shop runtime SHALL support both initial profiles through Claude using the
same broker, profile prompts, profile skills, topology, and lifecycle outcomes
as the other backends. Claude SHALL be reached by an active project selecting a
`claude:<model>` runtime for an agent rather than by a launcher option.

#### Scenario: Builder opens with Claude
- **WHEN** the user opens with `--profile builder` for a project that selects a Claude runtime for Builder
- **THEN** the runtime opens one Builder Claude session with the Builder profile contract

#### Scenario: Fordesmac opens with Claude
- **WHEN** the user opens with `--profile fordesmac` for a project that selects a Claude runtime for all four agents
- **THEN** the runtime opens four project-sandboxed Claude sessions carrying the Fordesmac contracts

#### Scenario: Fordesmac opens across two backends
- **WHEN** the user opens with `--profile fordesmac` for a project that selects Claude for Designer and Codex for the other three agents
- **THEN** the runtime opens one project-sandboxed Claude session for Designer and three Codex sessions, all on the same broker with the same lifecycle outcomes
