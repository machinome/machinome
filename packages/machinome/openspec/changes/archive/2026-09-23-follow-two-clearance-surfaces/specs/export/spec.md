## ADDED Requirements

### Requirement: Follow has an explicit versioned running edge

The edge SHALL also publish nullable `lower_plan` and `upper_plan` in the existing running law-plan format so a consumer uses the producer's jump partition and branch order for each envelope.

A published running program containing Follow SHALL carry an edge with `kind: "follow"`, ordered `needs` of lower source, upper source, and retained coordinate, the retained `gives`, and `lower`/`upper` serialized expression graphs. Its program identity SHALL include the ordered ends and both expressions. Such a document SHALL declare version 12; documents without Follow SHALL preserve their prior lowest version and fields. A consumer that lacks version 12 SHALL refuse it rather than reinterpret it as an ordinary law or Play.

#### Scenario: Curta Follow publication and old-consumer refusal
- **WHEN** the radial ball trial is exported with its Follow relation and matching dynamic Bounds
- **THEN** the document declares version 12, publishes one explicit Follow edge and the two existing spans, and a version-11 consumer refuses the document by version

#### Scenario: Older running models are unchanged
- **WHEN** a running model has ordinary laws, ADR-121 switches, or Play but no Follow
- **THEN** its published edge fields, document version, and program identity remain unchanged

#### Scenario: Envelope change invalidates a snapshot
- **WHEN** either Follow envelope expression or the order of its sources changes after a snapshot was captured
- **THEN** the program identity changes and restoring that snapshot is refused
