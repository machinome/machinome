## ADDED Requirements

### Requirement: Active agents receive retained maker file-change notices
After an accepted maker save, the shop SHALL snapshot every profile agent whose
broker work state is active and queue for each one a trusted informational
`user_file_changed` notice naming the relative path and installed revision.
The notice SHALL NOT be conversation, user direction, an assignment, or a work
state transition. The shop SHALL inject it into that agent's current delivery
only when the backend accepts a steer-only operation; otherwise it SHALL retain
the notice for that recipient's next ordinary broker delivery. A notice alone
MUST NOT start or resume an agent turn.

#### Scenario: An active agent is using a tool when the maker saves
- **WHEN** the maker saves a file while an agent's active delivery is inside a tool call
- **THEN** the agent receives the notice after that tool call and before its next task action without changing its work state

#### Scenario: The active turn completes during notice delivery
- **WHEN** an agent was active at save time but its delivery completes before the notice can be steered into it
- **THEN** the shop retains the notice and includes it in that agent's next ordinary broker delivery without starting a turn for the notice

#### Scenario: An active delegated agent has no running turn
- **WHEN** a delegated agent owns active broker work but has no current backend delivery when the maker saves
- **THEN** the notice waits for that agent's next ordinary broker delivery and consumes no agent tokens while waiting

#### Scenario: No agent is active
- **WHEN** the maker saves while every manifested agent's broker work state is waiting
- **THEN** the shop queues no agent file-change notice and wakes no agent

#### Scenario: The maker saves the same file several times before delivery
- **WHEN** several accepted saves of one path occur before a recipient receives its pending notice
- **THEN** that recipient receives the latest unsent revision of that path without a notice for each superseded revision
