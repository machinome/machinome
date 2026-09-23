## ADDED Requirements

### Requirement: A running profile contact publishes compact immutable data behind a version gate

A running program using profile contact SHALL publish a deterministic `program.profiles` table whose entries contain exact supplied finite XY point values and polygon index loops, and scalar `profileOverlap(leftIndex,rightIndex,leftAngleDeg,leftTx,leftTy,rightAngleDeg,rightTx,rightTy)` expressions referencing literal valid profile indices. Equivalent profile content SHALL be shared within that program without changing polygon order or vertex values. The complete profile content SHALL participate in program identity and snapshot compatibility. A document carrying it SHALL declare running document version 13; a document without it SHALL omit the table and retain its previous version, program identity and bytes. An older viewer SHALL refuse version 13 by its existing compatibility gate rather than evaluate a wrong motion.

#### Scenario: Two bounds share a profile without duplicating its polygons
- **WHEN** two running Bound expressions reference the same immutable profile
- **THEN** the document carries one copy of that profile's polygon data and both scalar calls reference it

#### Scenario: Profile contents change snapshot identity
- **WHEN** two programs have the same tree and expression call operands but one vertex coordinate differs
- **THEN** their program identities differ and a snapshot of one refuses restoration into the other

#### Scenario: A model without profile contact is byte-stable
- **WHEN** an existing version-11 or version-12 running model contains no profile contact operation
- **THEN** its exported program, document version and identity remain byte-identical to the pre-change result

#### Scenario: An old viewer cannot misread profile contact
- **WHEN** a viewer that supports document versions only through 12 is asked to open a version-13 profile-contact export
- **THEN** it refuses the document before operating the model

## MODIFIED Requirements

### Requirement: Follow has an explicit versioned running edge

The edge SHALL also publish nullable `lower_plan` and `upper_plan` in the existing running law-plan format so a consumer uses the producer's jump partition and branch order for each envelope.

A published running program containing Follow SHALL carry an edge with `kind: "follow"`, ordered `needs` of lower source, upper source, and retained coordinate, the retained `gives`, and `lower`/`upper` serialized expression graphs. Its program identity SHALL include the ordered ends and both expressions. Such a document SHALL declare version 12 when it contains no profile-contact operation and version 13 when it does; documents without Follow or profile contact SHALL preserve their prior lowest version and fields. A consumer that lacks the selected version SHALL refuse it rather than reinterpret Follow as an ordinary law or Play or omit the profile-contact operation.

#### Scenario: Curta Follow publication and old-consumer refusal
- **WHEN** the radial ball trial is exported with its Follow relation and matching dynamic Bounds and no profile-contact operation
- **THEN** the document declares version 12, publishes one explicit Follow edge and the two existing spans, and a version-11 consumer refuses the document by version

#### Scenario: Follow and profile contact select the newer version
- **WHEN** one running root carries both a Follow relation and a profile-contact operation in a Bound
- **THEN** its Follow edge remains unchanged, its profile table and scalar call are published, and the document declares version 13

#### Scenario: Older running models are unchanged
- **WHEN** a running model has ordinary laws, ADR-121 switches, or Play but neither Follow nor profile contact
- **THEN** its published edge fields, document version, and program identity remain unchanged

#### Scenario: Envelope change invalidates a snapshot
- **WHEN** either Follow envelope expression or the order of its sources changes after a snapshot was captured
- **THEN** the program identity changes and restoring that snapshot is refused
