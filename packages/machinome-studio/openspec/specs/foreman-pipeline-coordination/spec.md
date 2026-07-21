# foreman-pipeline-coordination Specification

## Purpose

Keep design and machining concurrent under one foreman-controlled sequence,
with design held at most one increment ahead.

## Requirements

### Requirement: The foreman controls every pipeline transition
The foreman SHALL be the sole role that starts designer and machinist
assignments. A specialist report or completed design artifact MUST NOT directly
start another specialist's work.

#### Scenario: The maker begins project work
- **WHEN** the maker gives the foreman sufficient direction to begin a mechanical project
- **THEN** the foreman assigns the designer to prepare the first executable drawing while the machinist remains waiting

#### Scenario: The designer reports a released drawing
- **WHEN** the designer reports that an immutable drawing has been released and identifies its project commit
- **THEN** the foreman decides and issues the machinist assignment for that exact drawing

#### Scenario: A specialist completes work
- **WHEN** a specialist reports completion of an assignment
- **THEN** no other specialist assignment starts until the foreman directs that transition

### Requirement: Design stays at most one increment ahead of machining
After the first drawing is released, the foreman SHALL run the machinist on
that released increment while the designer prepares at most one following
increment. If the designer completes that ahead-work while machining remains
active, the designer SHALL wait rather than begin another increment or alter
the machinist's assignment.

#### Scenario: The first drawing enters machining
- **WHEN** the foreman starts the machinist on the first released drawing
- **THEN** the foreman concurrently assigns the designer to prepare the single next increment as a draft

#### Scenario: The designer finishes first
- **WHEN** the designer completes the next draft while the machinist remains active on the current released drawing
- **THEN** the foreman leaves the designer waiting and the machinist continues with its unchanged assignment

#### Scenario: The machinist finishes the current increment
- **WHEN** the machinist reports completion and the next draft is waiting
- **THEN** the foreman assigns the designer to reconcile that draft with machining evidence and release it before the foreman starts the next machining assignment

### Requirement: New direction enters active work through foreman judgment
When maker direction affects work already in progress, the foreman SHALL decide
which agents need the direction and which later pipeline transitions remain
valid. Delivering the direction MUST NOT automatically cancel active work or
activate a draft drawing.

#### Scenario: The maker changes direction during machining
- **WHEN** the maker gives the foreman new project direction while the machinist and designer are active
- **THEN** the foreman communicates the relevant direction to the affected agents and retains control of any cancellation, revision, or later assignment
