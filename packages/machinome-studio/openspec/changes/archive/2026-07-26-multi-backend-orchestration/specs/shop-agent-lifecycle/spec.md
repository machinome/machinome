## MODIFIED Requirements

### Requirement: An open shop manifests the working team
Each newly opened shop SHALL manifest exactly one `foreman`, one `designer`,
and one `machinist` as its initial working team. The orchestrator SHALL create
each role session through the selected agent backend. The design role MUST use
`designer`, not `drawing-office`, as its role identifier and displayed name.

#### Scenario: The working team starts
- **WHEN** the runtime successfully opens a shop
- **THEN** the agent roster shows Foreman, Designer, and Machinist as waiting agents

#### Scenario: The working team starts with the Hermes backend
- **WHEN** the runtime opens a shop with `--backend hermes`
- **THEN** the agent roster shows Foreman, Designer, and Machinist as waiting agents

#### Scenario: The retired design role is addressed
- **WHEN** a participant attempts to address `drawing-office` as an agent role
- **THEN** the shop rejects it as an unknown active role

### Requirement: The shop floor shows manifested agents
For each active shop run, the shop floor SHALL show every agent that the
orchestrator has manifested for that run.  Each shown agent SHALL identify its
role and whether it is waiting or active.

#### Scenario: An agent is manifested
- **WHEN** the orchestrator manifests an agent for an active shop run
- **THEN** the agent appears in that run's shop-floor menu as waiting

#### Scenario: The roster is viewed after agents were manifested
- **WHEN** the pilot opens or reconnects to the shop floor for an active run
- **THEN** the menu shows the current waiting or active state of every
  manifested agent without requiring a new lifecycle event

#### Scenario: An agent stops
- **WHEN** the orchestrator reports that a manifested agent has stopped
- **THEN** the menu removes that agent without a page reload

### Requirement: The shop floor shows acknowledged work as active
The shop floor SHALL show a manifested agent as active only after that agent
acknowledges its current assigned work. Assigning work without an
acknowledgment, including queuing later work behind an active assignment, MUST
NOT change the agent's displayed state.

#### Scenario: Work is assigned but not acknowledged
- **WHEN** the foreman assigns work to a waiting manifested agent
- **THEN** the agent remains shown as waiting

#### Scenario: An agent acknowledges assigned work
- **WHEN** a waiting manifested agent acknowledges its assigned work
- **THEN** the menu changes that agent to active without a page reload

#### Scenario: Later work is queued for an active agent
- **WHEN** the foreman assigns later work to an active manifested agent
- **THEN** the menu continues to show the agent as active on its current assignment

### Requirement: The shop floor returns completed agents to waiting
The shop floor SHALL show an active manifested agent as waiting after it
reports completion of its acknowledged work.

#### Scenario: An active agent completes work
- **WHEN** an active manifested agent reports completion of its acknowledged
  work
- **THEN** the menu changes that agent to waiting without a page reload

#### Scenario: An active agent does not report completion
- **WHEN** an active manifested agent has not reported completion
- **THEN** the menu continues to show that agent as active

### Requirement: Lifecycle reports are attributable to manifested agents
The shop floor MUST apply an acknowledgment or completion report only when it
is attributable to a manifested agent and its relevant assignment in the
active shop run.

#### Scenario: A report names an unknown agent
- **WHEN** a lifecycle report names an agent that is not manifested for the
  active shop run
- **THEN** the agent roster is unchanged

#### Scenario: A completion report does not match active work
- **WHEN** a manifested agent reports completion for work it has not
  acknowledged as active
- **THEN** the agent roster is unchanged
