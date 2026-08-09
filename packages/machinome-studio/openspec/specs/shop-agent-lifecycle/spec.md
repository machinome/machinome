# shop-agent-lifecycle Specification

## Purpose

Define how the shop manifests its standing role team and reflects each role's
acknowledged assignment state in the shop-floor roster.

## Requirements
### Requirement: An open shop manifests the working team
Each newly opened project SHALL manifest exactly the complete standing agent set
declared by its selected validated profile. The shop SHALL create each agent
session through the selected backend in declaration order and SHALL use the
profile's stable agent IDs and display labels. Each open project SHALL have its
own roster, and an agent SHALL appear in the roster of its own project only.

#### Scenario: The default working team starts
- **WHEN** a project declaring `builder` is opened
- **THEN** that project's roster shows one waiting Builder

#### Scenario: The Fordesmac working team starts
- **WHEN** a project declaring `fordesmac` is opened
- **THEN** that project's roster shows waiting Foreman, Designer, Machinist, and Librarian agents

#### Scenario: Either team starts through another backend
- **WHEN** either initial profile opens through Codex, Claude, or OpenCode
- **THEN** the roster contains the same profile-declared agent IDs and labels

#### Scenario: An undeclared role is addressed
- **WHEN** a participant addresses an agent ID absent from the active profile
- **THEN** the broker rejects it as an unknown active agent

#### Scenario: Two projects with the same profile are open
- **WHEN** two projects declaring the same profile are open at once
- **THEN** each has its own roster of that profile's agents, and work on one project's roster leaves the other's unchanged

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
In a delegated profile, the shop floor SHALL show an assignable specialist as
active only after that agent acknowledges its current assigned work. Assigning
work without acknowledgement, including queuing later work behind an active
assignment, MUST NOT change its displayed state. A backend turn alone MUST NOT
complete or replace delegated assignment state.

#### Scenario: Delegated work is assigned but not acknowledged
- **WHEN** a declared assigner assigns work to a waiting specialist
- **THEN** the specialist remains shown as waiting

#### Scenario: A specialist acknowledges assigned work
- **WHEN** a waiting specialist acknowledges its assigned work
- **THEN** the menu changes that specialist to active without a page reload

#### Scenario: Later work is queued for an active specialist
- **WHEN** a declared assigner assigns later work to an active specialist
- **THEN** the menu continues to show the specialist as active on its current assignment

### Requirement: The shop floor returns completed agents to waiting
In a delegated profile, the shop floor SHALL show an active specialist as
waiting after it reports completion of its matching acknowledged work. Backend
turn completion without matching assignment completion MUST NOT clear the
active assignment.

#### Scenario: An active specialist completes work
- **WHEN** an active specialist reports completion of its acknowledged work
- **THEN** the menu changes that specialist to waiting without a page reload

#### Scenario: An active specialist does not report completion
- **WHEN** an active specialist's backend turn ends without a matching completion report
- **THEN** the menu continues to show that specialist as active

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

### Requirement: Direct-agent activity follows its backend turn
In a direct profile, the user-facing agent SHALL become active when the backend
starts processing user direction and SHALL return to waiting when that same
turn completes. The broker SHALL NOT allocate, require, or accept an assignment
ID for direct work, and SHALL NOT accept self-assignment, acknowledgement,
report, or assignment-completion lifecycle operations from a direct agent.

#### Scenario: Builder starts direct work
- **WHEN** an idle Builder backend session starts processing Maker direction
- **THEN** the roster changes Builder from waiting to active

#### Scenario: Builder completes direct work
- **WHEN** Builder's active backend turn completes
- **THEN** the roster returns Builder to waiting without a completion command

#### Scenario: Builder receives a correction
- **WHEN** Maker direction steers Builder's active turn
- **THEN** Builder remains active under the original delivery until that turn completes

#### Scenario: Builder direction has no assignment identity
- **WHEN** the broker delivers Maker direction to Builder in direct mode
- **THEN** neither that delivery nor its backend turn carries a broker assignment identifier

#### Scenario: Builder attempts delegated lifecycle
- **WHEN** Builder submits an assignment-ID, acknowledgement, report, or assignment-completion operation
- **THEN** the broker rejects it without changing Builder's turn-derived state

### Requirement: The roster distinguishes role availability from work state
The broker SHALL record an optional backend failure reason for each manifested agent independently of its waiting or active work state. A role failure SHALL NOT complete, discard, or replace a delegated assignment. Recovery SHALL clear only the failure reason, leaving the broker-owned work lifecycle otherwise unchanged.

#### Scenario: An active specialist session fails
- **WHEN** a specialist with an acknowledged assignment reports `role_failed`
- **THEN** the roster identifies that specialist as failed with the backend reason while retaining its active assignment state

#### Scenario: A failed specialist recovers
- **WHEN** a later delivery to the failed specialist is accepted
- **THEN** the roster clears the failure and continues to show the specialist's unchanged assignment state

#### Scenario: A direct-agent turn fails
- **WHEN** the direct profile's active agent reports `role_failed`
- **THEN** its failed turn identity is cleared, its failure reason is shown, and a later maker direction can start a new turn
