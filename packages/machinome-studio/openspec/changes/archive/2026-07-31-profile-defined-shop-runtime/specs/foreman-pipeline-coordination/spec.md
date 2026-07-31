## MODIFIED Requirements

> **Synchronization intent:** each MODIFIED requirement in this file replaces
> its complete baseline requirement block, including its scenario set.

### Requirement: The foreman controls every pipeline transition
Within the `fordesmac` profile, Foreman SHALL be the sole agent that starts
Designer, Machinist, or Librarian assignments. A specialist report, completed
artifact, or prompt instruction MUST NOT directly start another specialist's
work.

#### Scenario: Maker begins project work
- **WHEN** Maker gives Foreman sufficient direction to begin a mechanical project
- **THEN** Foreman assigns Designer to prepare the first executable drawing while Machinist and Librarian remain waiting

#### Scenario: Designer reports a released drawing
- **WHEN** Designer reports an immutable drawing and its project commit
- **THEN** Foreman decides and issues the Machinist assignment for that exact drawing

#### Scenario: A specialist completes work
- **WHEN** Designer, Machinist, or Librarian reports assignment completion
- **THEN** no other specialist assignment starts until Foreman directs that transition

### Requirement: Design stays at most one increment ahead of machining
Within the `fordesmac` profile, after the first drawing is released, Foreman
SHALL run Machinist on that released increment while Designer prepares at most
one following increment. If Designer completes that ahead-work while machining
remains active, Designer SHALL wait rather than begin another increment or
alter Machinist's assignment.

#### Scenario: The first drawing enters machining
- **WHEN** Foreman starts Machinist on the first released drawing
- **THEN** Foreman concurrently assigns Designer to prepare the single next increment as a draft

#### Scenario: The designer finishes first
- **WHEN** Designer completes the next draft while Machinist remains active on the current released drawing
- **THEN** Foreman leaves Designer waiting and Machinist continues with its unchanged assignment

#### Scenario: The machinist finishes the current increment
- **WHEN** Machinist reports completion and the next draft is waiting
- **THEN** Foreman assigns Designer to reconcile that draft with machining evidence and release it before Foreman starts the next machining assignment

### Requirement: New direction enters active work through foreman judgment
Within the `fordesmac` profile, when user direction affects work already in
progress, Foreman SHALL decide which agents need the direction and which later
pipeline transitions remain valid. Delivering the direction MUST NOT
automatically cancel active work or activate a draft drawing.

#### Scenario: The maker changes direction during machining
- **WHEN** Maker gives Foreman new project direction while Machinist and Designer are active
- **THEN** Foreman communicates the relevant direction to the affected agents and retains control of any cancellation, revision, or later assignment

## ADDED Requirements

### Requirement: Fordesmac Librarian is a standing Foreman-controlled specialist
The `fordesmac` profile SHALL open Librarian as a regular persistent standing
agent with token-free standby. Foreman SHALL assign Librarian narrow external
library research and Librarian SHALL report only to Foreman. Designer and
Machinist MUST NOT assign Librarian directly.

#### Scenario: The shop opens before research is needed
- **WHEN** Fordesmac opens and no research assignment exists
- **THEN** Librarian is manifested as waiting with no active model turn or token consumption

#### Scenario: Foreman requests library research
- **WHEN** Foreman assigns Librarian a declared research task
- **THEN** Librarian follows delegated acknowledgement, report, and completion lifecycle

#### Scenario: Another specialist requests Librarian directly
- **WHEN** Designer or Machinist attempts to assign Librarian
- **THEN** the broker rejects the undeclared edge
