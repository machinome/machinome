# shop-agent-messaging Specification

## Purpose

Provide ordered role-addressed direction, assignments, reports, and portable
backend delivery with tool-boundary handling and event-driven standby.

## Requirements

### Requirement: Running agents receive ordered direction at work boundaries
Each manifested shop agent SHALL have an ordered inbox for direction addressed
to that role. Direction received while the agent is using a tool SHALL remain
queued and SHALL be presented to the agent after that tool call completes and
before the agent starts its next task action. The orchestrator SHALL deliver
each envelope to the selected backend through `AgentBackend.deliver()`.

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
or otherwise change that agent's active assignment. The receiving agent SHALL
interpret the direction in its current context and act according to its
content and role authority.

#### Scenario: New direction arrives during active work
- **WHEN** an active agent receives direction while carrying out an assignment
- **THEN** its assignment remains active until the agent decides and reports what the direction requires

### Requirement: Assignments wait behind active work
Each manifested agent SHALL have at most one acknowledged active assignment.
An assignment addressed to an active agent SHALL remain queued and MUST NOT be
presented as active work until the agent completes its current assignment and
acknowledges the queued assignment.

#### Scenario: A later assignment is queued
- **WHEN** the foreman assigns later work to an agent that already has an active assignment
- **THEN** the later assignment remains queued and the current assignment remains active

#### Scenario: An agent completes work with an assignment queued
- **WHEN** an agent completes its active assignment while a later assignment is queued
- **THEN** the completed assignment ends and the later assignment becomes available for the agent to acknowledge

### Requirement: Specialists report through the broker to the foreman
The designer and machinist SHALL send progress, findings, and completion
reports through the shop broker to the foreman. Reports and shop events SHALL
remain ordered and available to the foreman while it manages the floor. The
orchestrator SHALL translate backend `role_message` events into broker
conversation entries for foreman-to-maker communication.

#### Scenario: A specialist reports while the foreman is working
- **WHEN** a specialist reports progress or completion while the foreman is using a tool
- **THEN** the report remains queued and is presented to the foreman after that tool call completes and before its next task action

#### Scenario: The foreman resumes observation after several events
- **WHEN** several report or lifecycle events occur before the foreman next checks the floor
- **THEN** the foreman receives the unseen events once in recorded order
