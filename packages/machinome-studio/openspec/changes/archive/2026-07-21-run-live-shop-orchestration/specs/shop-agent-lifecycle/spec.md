## ADDED Requirements

### Requirement: An open Codex shop manifests the working team
Each newly opened Codex shop SHALL manifest exactly one `foreman`, one
`designer`, and one `machinist` as its initial working team. The design role
MUST use `designer`, not `drawing-office`, as its role identifier and displayed
name.

#### Scenario: The working team starts
- **WHEN** Codex successfully opens a shop
- **THEN** the agent roster shows Foreman, Designer, and Machinist as waiting agents

#### Scenario: The retired design role is addressed
- **WHEN** a participant attempts to address `drawing-office` as an agent role
- **THEN** the shop rejects it as an unknown active role

## MODIFIED Requirements

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
