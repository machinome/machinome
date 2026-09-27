## MODIFIED Requirements

### Requirement: Mechanical contract mate references identify their existing generated joint

A Bound read SHALL accept a moving mate declared on the body stating the Bound or reached through declared children. For Bound reads and constrain targets, the mate reference SHALL identify its existing child joint's scalar coordinate, including nested paths. A fresh-freedom mate selects its generated joint;
a reused-joint mate selects the original referenced joint by its original
child name, and SHALL preserve that joint's Bound scope. This SHALL preserve the mate's existing public coordinate, relation/wiring behavior and sole binding route. The system SHALL refuse a rigid mate by name because it owns no coordinate. Scope, inherited-path compatibility, repeated/list-held path, unused read and simulation banking checks SHALL remain effective. Self-read and duplicate-read checks SHALL compare the resolved physical coordinate: a mate reference and a reference to its generated child joint SHALL NOT evade those checks by having different written names.

#### Scenario: A Bound reads a nested moving mate

- **WHEN** a Bound names a moving mate reached through nested assembly children
- **THEN** its read identifies the existing generated child joint, within the declaring subtree, without creating a new coordinate

#### Scenario: Alias names cannot hide a self read

- **WHEN** a Bound constraining a moving mate reads that same mate or its generated child joint under another reachable spelling
- **THEN** declaration or resolved compilation refuses the self read and identifies the offending reference

#### Scenario: Alias names cannot duplicate a read

- **WHEN** one Bound lists a moving mate and its generated child joint as separate reads
- **THEN** the system refuses the duplicate physical coordinate rather than providing it twice to the expression

#### Scenario: Invalid inherited mate references do not disappear

- **WHEN** a subclass replaces a referenced child so that a Bound read or constraint no longer reaches a compatible moving mate and generated joint
- **THEN** the invalid inherited reference is refused by name instead of becoming inert or silently selecting another coordinate

#### Scenario: Rigid mate reads are refused

- **WHEN** a Bound names a rigid mate in reads
- **THEN** it is refused by name because the mate owns no coordinate

## ADDED Requirements

### Requirement: Reused-joint mechanical contracts preserve original scope

A Bound read, constrain target or explicit control reference naming an existing-joint mate SHALL resolve to its original joint. Added constraints SHALL retain their own declaring assembly scope and intersect with the original joint range. Attaching an existing joint SHALL not change the declarer of its original Bounds, shift its original argument frame or grant new binding permission. Self and duplicate Bound reads through handle/child aliases SHALL be refused canonically.

#### Scenario: A handle constrains the original range

- **WHEN** an assembly adds a constraint through an own or nested reused-joint mate handle
- **THEN** the contribution is installed on the original joint, preserves its range and original read scope, and uses the contributor's assembly scope

#### Scenario: Alias reads cannot evade Bound checks

- **WHEN** a Bound reads its target through a handle alias or reads one joint twice through handle/child spellings
- **THEN** the ordinary self-read or duplicate-read refusal applies to the original endpoint

#### Scenario: Inherited effective paths stay checked

- **WHEN** an inherited existing-joint attachment or mechanical reference no longer reaches its required compatible moving child and scalar joint
- **THEN** it is refused by name rather than becoming inert or selecting a different coordinate
