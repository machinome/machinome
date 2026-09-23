## ADDED Requirements

### Requirement: Preserved inherited controls follow a compatible replaced child

When a running node subclass explicitly preserves a control from an ancestor's `controls` table under the same name, and replaces the control's first named child at the same path with a subclass-compatible child, the system SHALL validate and resolve that control against the effective child tree. The part and any explicit selected coordinate SHALL resolve on that effective tree, and the existing control ownership, selected-joint ancestry, run-banked-coordinate, domain, driver, and input-reachability checks SHALL remain in force. The control SHALL publish the effective part and coordinate without changing the document schema or the run program.

This inheritance allowance SHALL NOT turn a subclass `controls` mapping into an automatic merge. A newly authored control or one borrowed from an unrelated class SHALL NOT gain permission from a matching child name alone.

#### Scenario: A Curta carriage replacement preserves its inherited controls
- **WHEN** a running Curta subclass replaces `carriage` with a compatible specialized carriage and declares `controls = {**OperatingCurta.controls, 'deploy loop': Turn(...)}`
- **THEN** class definition succeeds, the inherited controls resolve to the effective carriage and their selected effective joints, and the additional control is enumerated and compiled alongside them

#### Scenario: A subclass-only table replaces inherited controls
- **WHEN** a subclass declares a `controls` mapping containing only a new control, or declares `controls = {}`
- **THEN** its effective control table contains only those explicit entries, or no entries respectively

#### Scenario: A foreign same-name reference remains refused
- **WHEN** a subclass writes a new control referring to another class's child declaration that happens to have the same local name as its own child
- **THEN** class definition refuses the foreign part or coordinate, naming the control and declaring class

#### Scenario: An incompatible or missing effective path remains refused
- **WHEN** a preserved inherited control names a child that is replaced incompatibly, or its part or selected joint does not exist on the effective tree
- **THEN** class definition or compilation refuses that control; it does not publish an ancestor declaration or infer a different gesture

#### Scenario: Existing gesture checks still apply after rebinding
- **WHEN** a preserved inherited control's effective selected joint poses a different branch, has the wrong domain, is not run-banked, or is not reached by its declared input
- **THEN** the corresponding existing control compilation refusal still applies
