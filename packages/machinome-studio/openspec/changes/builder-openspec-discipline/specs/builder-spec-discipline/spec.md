## ADDED Requirements

### Requirement: Builder plans a design change before building it

Builder SHALL carry every design change through two commits in the project
repository. The first SHALL contain only the change's planning record: what is
being built, the interfaces it establishes or alters, and the work it implies.
The second SHALL contain the built parts, their tests, the specs synced from
the change, and the archived change.

Builder SHALL NOT begin machining a design change before its planning commit
exists, and SHALL NOT leave a change's planning record uncommitted while
building against it.

A change that alters no interface between parts — a build repair, a knob value,
a snapshot, repository hygiene — is not a design change and SHALL NOT require a
planning commit.

#### Scenario: A design change establishes an interface

- **WHEN** the Maker asks for work that establishes or alters how two parts
  meet
- **THEN** Builder commits the plan for that change before creating or wiring
  any part it describes

#### Scenario: The work alters no interface

- **WHEN** the Maker asks for a fix, a knob adjustment, or other work that
  changes no interface between parts
- **THEN** Builder does the work directly, with no change record

#### Scenario: Committing is not gated on an open change

- **WHEN** Builder commits while no change is open
- **THEN** the commit proceeds, because the discipline is Builder's own conduct
  and not a precondition the floor enforces

### Requirement: A project owns its spec record

A project's spec record SHALL live inside that project's own repository.
Builder SHALL establish it through a single floor operation that creates the
record, seeds the project's house rules for writing mechanical specs, and
commits the result. That operation SHALL be repeatable: against a project whose
record already exists it SHALL report that and change nothing, and it SHALL NOT
overwrite house rules the project already carries.

Builder SHALL NOT write a project's spec record into any repository other than
the active project.

#### Scenario: A project has no spec record yet

- **WHEN** Builder establishes the spec record in a project that has none
- **THEN** the record is created inside that project, seeded with its house
  rules, and committed

#### Scenario: A project already has a spec record

- **WHEN** Builder establishes the spec record in a project that already has
  one
- **THEN** the operation reports the record already exists, and neither the
  record nor its house rules change

### Requirement: An interface between parts is the unit of specification

A capability in a project's spec record SHALL name an interface between parts,
not a part. Its requirements SHALL state what that interface guarantees —
clearance, fit, engagement, travel, load path, orientation — in terms a
manufactured part can be measured against. Each scenario SHALL describe one
condition and its expected geometric outcome, so that it corresponds to one fit
or assembly test.

Builder SHALL write each scenario's test under the profile's existing
disassembled-leaf-first workflow, so the test's first red state is the existing
leaf's wrong relationship.

#### Scenario: A change joins two parts

- **WHEN** Builder specifies work that joins a lid to a body
- **THEN** the capability names the lid-body interface and its requirements
  state the guarantees that interface holds, rather than describing the lid

#### Scenario: A scenario becomes a test

- **WHEN** Builder implements a change whose specs carry scenarios
- **THEN** each scenario has a corresponding fit or assembly test, red before
  the parts satisfy it

### Requirement: A committed plan is not rewritten

Once a change's planning commit exists, Builder SHALL NOT rewrite it to reflect
a later decision. A change of intent SHALL open a follow-up change that states
the new interface in terms of the old one. A correction that preserves meaning
— a typo, or a value the surrounding text already fixes — MAY be made in the
implementing commit.

Builder SHALL keep at most one change open at a time, and SHALL close or
abandon the open change before opening another.

Before the planning commit exists, Builder SHALL revise the plan freely as the
Maker's intent settles.

#### Scenario: The Maker changes direction after the plan is committed

- **WHEN** the Maker asks for a different interface than the committed plan
  describes
- **THEN** Builder opens a follow-up change stating the new interface, and the
  committed plan stays as it was

#### Scenario: The Maker changes direction before the plan is committed

- **WHEN** the Maker revises what they want while the plan is still uncommitted
- **THEN** Builder rewrites the plan in place, with no follow-up change

#### Scenario: A second change is requested while one is open

- **WHEN** the Maker asks for unrelated design work while a change is open
- **THEN** Builder finishes or abandons the open change before opening the new
  one

### Requirement: A change closes with an honest record

Builder SHALL close a change only when the work its record claims is done. When
work listed in a change stops being relevant, Builder SHALL remove or amend
that entry in the change's own working record and say so, rather than closing
the change over it.

#### Scenario: Listed work is no longer relevant

- **WHEN** Builder reaches the end of a change with listed work that the design
  no longer needs
- **THEN** Builder amends the change's working record to drop that work, tells
  the Maker, and then closes the change

### Requirement: The spec discipline is Builder's, not the Maker's

The Maker SHALL NOT be required to approve, ratify, or acknowledge a change's
planning record for Builder to proceed. Builder SHALL describe its plan and its
progress in the Maker's own terms, and SHALL NOT require the Maker to read,
write, or name a spec artifact in order to get work done.

#### Scenario: The Maker asks for a part

- **WHEN** the Maker describes what they want built
- **THEN** Builder plans, records, and builds it without asking the Maker to
  approve a specification

#### Scenario: The Maker asks what was decided

- **WHEN** the Maker asks why a part is the way it is
- **THEN** Builder answers from the project's spec record
