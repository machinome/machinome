## ADDED Requirements

### Requirement: State-selected node colors carry an explicit format gate

A live document containing a symbolic color choice SHALL publish that node's `color` as exactly `{when: <scalar expression>, on: '#RRGGBB', off: '#RRGGBB'}` and declare document version 14. `when` SHALL be a string in the existing scalar expression grammar and SHALL use the existing shared-binding machinery, with the same qualified scope as placement. This content gate SHALL dominate the earlier posed, clocked and running version ladders for choice-bearing documents; execution kind SHALL still be identified by its existing `clocked` or `program` payload, with the absence of both identifying a posed document and both together forbidden. No new scalar operation, appearance bank or electrical behavior SHALL be published.

Ordinary build, export and snapshot producers SHALL use the common color serialization. A numeric snapshot containing only a selected static hex SHALL retain that legacy color form, since it contains no deferred choice. Documents without a symbolic choice SHALL retain their existing color representation, version and bytes. A consumer unable to honor version 14 SHALL refuse it before rendering, rather than silently displaying a static color.

#### Scenario: A live observed glass publishes its choice

- **WHEN** the glass's state-dependent color is built or exported through the standard producer
- **THEN** its existing node and model reference carry one conditional color and the document declares version 14

#### Scenario: Version 14 preserves all three execution modes

- **WHEN** posed, clocked and running roots each carry a symbolic color choice
- **THEN** each declares version 14 and retains exactly its own execution payload semantics; the posed document is not mistaken for a missing running program

#### Scenario: Static color publication remains compatible

- **WHEN** a document carries only hex/None colors, including the numeric result of a constant `color_when` call
- **THEN** its version and serialized bytes remain those of the existing producer

#### Scenario: Shared state predicates remain shared

- **WHEN** multiple lamps and placements reuse one predicate graph
- **THEN** normal publication preserves its sharing through bindings rather than duplicating its ancestry per lamp

#### Scenario: An older reader does not silently miss the lamp state

- **WHEN** a version-14 color document is opened by a reader supporting only versions 1–13
- **THEN** it refuses the version before rendering a misleading static lamp
