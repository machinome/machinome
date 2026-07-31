# shop-agent-messaging Specification

## Purpose

Provide ordered role-addressed direction, assignments, reports, and portable
backend delivery with tool-boundary handling and event-driven standby.

## Requirements

### Requirement: Running agents receive ordered direction at work boundaries
Each profile-declared standing agent SHALL have an ordered inbox for direction
addressed to its stable agent ID. Direction received while the agent is using a
tool SHALL remain queued and SHALL be presented after that tool call completes
and before the agent's next task action. The orchestrator SHALL deliver a new
idle-agent envelope through `AgentBackend.deliver_start()` and later direction
for its active delivery through `AgentBackend.deliver_steer()`.

#### Scenario: Direction arrives during a tool call
- **WHEN** an agent is using a tool and new direction is addressed to that agent
- **THEN** the direction remains queued until the tool call completes and is presented before the agent's next task action

#### Scenario: Several directions arrive while work proceeds
- **WHEN** multiple directions are addressed to a running agent before it checks its inbox
- **THEN** the agent receives every direction once in recorded order

### Requirement: Standby is event driven and consumes no agent tokens
When a manifested agent has no work or direction ready, the system SHALL keep
that agent idle with no active model turn. While no addressed event is
available, the system MUST NOT poll on the agent's behalf, resume its model,
issue another agent tool call, or consume agent tokens. An addressed envelope
SHALL cause the idle agent to resume once; shop shutdown SHALL end the idle
session without first resuming its model.

#### Scenario: A standby agent receives no event
- **WHEN** a manifested agent remains waiting with no addressed event for any duration
- **THEN** it remains idle without an active model turn, periodic requests, model resumptions, agent tool calls, or token consumption

#### Scenario: An addressed event wakes a standby agent
- **WHEN** direction or available work is addressed to a standby agent
- **THEN** the system resumes that agent once and presents the addressed event

#### Scenario: Shop shutdown wakes a standby agent
- **WHEN** the shop closes while an agent is idle in standby
- **THEN** the system ends that session without resuming the agent model

### Requirement: Receiving direction does not predetermine the agent's response
Delivering direction to an agent MUST NOT by itself cancel, replace, complete,
or otherwise change delegated assignment state. In a direct profile, later
user direction SHALL steer or start the user-facing agent according to its
backend-turn state without creating an assignment. Every receiving agent SHALL
interpret direction in its current context and act according to its prompt and
declared authority.

#### Scenario: New direction arrives during delegated work
- **WHEN** an active specialist receives direction while carrying out an assignment
- **THEN** its assignment remains active until the specialist decides and reports what the direction requires

#### Scenario: New direction arrives during direct work
- **WHEN** Builder receives user direction while its direct turn is active
- **THEN** the direction is steered into that turn without creating, replacing, or completing an assignment

### Requirement: Assignments wait behind active work
Each assignable agent in a delegated profile SHALL have at most one
acknowledged active assignment. An assignment sent across a declared edge to an
active agent SHALL remain queued and MUST NOT be presented as active work until
the agent completes its current assignment and acknowledges the queued one.

#### Scenario: A later assignment is queued
- **WHEN** a declared assigner sends later work to an agent with an active assignment
- **THEN** the later assignment remains queued and the current assignment remains active

#### Scenario: An agent completes work with an assignment queued
- **WHEN** an agent completes its active assignment while a later assignment is queued
- **THEN** the completed assignment ends and the later assignment becomes available for acknowledgement

### Requirement: Declared reporters report through the broker to their parent
An agent with `reports_to` SHALL send progress, findings, and completion reports
through the broker to that declared parent. Reports and shop events SHALL
remain ordered and available while the parent manages work. The orchestrator
SHALL translate backend output from the profile's user-facing agent, and no
other agent, into user-conversation entries.

#### Scenario: A specialist reports while its parent is working
- **WHEN** a specialist reports progress or completion while its reporting parent is using a tool
- **THEN** the report remains queued and is presented after that tool call and before the parent's next task action

#### Scenario: The configured reporting parent resumes after several events
- **WHEN** several reports or lifecycle events occur before that parent next checks the floor
- **THEN** the reporting parent receives the unseen events once in recorded order

#### Scenario: The user-facing agent emits output
- **WHEN** Builder in `builder` or Foreman in `fordesmac` emits non-empty backend output
- **THEN** the orchestrator records it in the user conversation under that configured agent identity

### Requirement: The broker enforces the active profile's communication graph
The broker SHALL accept agent senders and recipients only when both are declared
by the active profile. It SHALL accept an assignment only across a declared
`assigns` edge and a report only from an agent to its declared `reports_to`
parent. Prompt text MUST NOT expand those permissions.

#### Scenario: Foreman assigns a declared specialist
- **WHEN** Fordesmac Foreman assigns Designer, Machinist, or Librarian
- **THEN** the broker records and routes the assignment

#### Scenario: A specialist attempts to assign work
- **WHEN** a Fordesmac specialist submits an assignment without a declared assignment edge
- **THEN** the broker rejects it

#### Scenario: A report bypasses its parent
- **WHEN** a specialist addresses a report to an agent other than its declared reporting parent
- **THEN** the broker rejects it

#### Scenario: Builder attempts assignment lifecycle
- **WHEN** Builder submits an assignment, report, acknowledgement, or completion operation in the direct profile
- **THEN** the broker rejects the operation as unavailable in that topology
