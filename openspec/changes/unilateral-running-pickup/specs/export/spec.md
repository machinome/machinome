## ADDED Requirements

### Requirement: A play edge is explicit in a version 9 running document

The published program SHALL represent each play relation as one edge with `kind: "play"`, `needs` containing source then retained coordinate, `gives` containing that retained coordinate, and finite numeric `low` and `high`.  A document containing a play edge SHALL declare version 9.  A document containing none SHALL keep the same lowest version and bytes it had before this capability.

`play` SHALL be an additional edge kind under "The published edges say what
each one reads, gives and computes". The version-9 selection SHALL take
precedence over the version-5/6/7 selection for ordinary running programs;
it SHALL NOT change the version-8 clocked document contract.

#### Scenario: A play model publishes its full semantics
- **WHEN** a running model declares `Play(low=-329, high=3)`
- **THEN** its version-9 document carries a play edge naming both coordinate ids and the two offsets, and its program identity changes if either offset changes

#### Scenario: An old running model does not move version
- **WHEN** a running model contains ordinary, jumping, self-read, or block edges but no play edge
- **THEN** its document version, program entries, identity, and committed fixtures are byte-identical to the prior behavior

#### Scenario: An installed viewer cannot read version 9
- **WHEN** a snapshot or development command is asked to use a viewer reporting only document versions 1 through 8 for a play model
- **THEN** the framework refuses before staging or execution, naming required version 9 and the viewer's reported versions

### Requirement: The running corpus covers play semantics

The cross-runtime running conformance corpus SHALL contain play cases sufficient to distinguish retention, either-flank pickup, immediate reversal release, non-integer contact, command splitting, a three-edge cascade, downstream stop localization, and snapshot replay.  Corpus validation SHALL refuse a consumer or generator omitting the play edge kind or one of those behaviors.

#### Scenario: Corpus coverage is complete
- **WHEN** the running corpus is generated and validated
- **THEN** its inventory proves every required play behavior and every expected state, status, and stop agrees within the corpus's stated numeric contract
