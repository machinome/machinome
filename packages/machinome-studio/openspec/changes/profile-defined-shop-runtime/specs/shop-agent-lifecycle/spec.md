## MODIFIED Requirements

> **Synchronization intent:** each MODIFIED requirement in this file replaces
> its complete baseline requirement block, including its scenario set.

### Requirement: An open shop manifests the working team
Each newly opened shop SHALL manifest exactly the complete standing agent set
declared by its selected validated profile. The orchestrator SHALL create each
agent session through the selected backend in declaration order and SHALL use
the profile's stable agent IDs and display labels.

#### Scenario: The default working team starts
- **WHEN** the runtime opens a shop without `--profile`
- **THEN** the roster shows one waiting Builder

#### Scenario: The Fordesmac working team starts
- **WHEN** the runtime opens with `--profile fordesmac`
- **THEN** the roster shows waiting Foreman, Designer, Machinist, and Librarian agents

#### Scenario: Either team starts through another backend
- **WHEN** either initial profile opens through Codex, Claude, or Hermes
- **THEN** the roster contains the same profile-declared agent IDs and labels

#### Scenario: An undeclared role is addressed
- **WHEN** a participant addresses an agent ID absent from the active profile
- **THEN** the broker rejects it as an unknown active agent

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

## ADDED Requirements

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
