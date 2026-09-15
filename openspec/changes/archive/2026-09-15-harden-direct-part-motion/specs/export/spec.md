## ADDED Requirements

### Requirement: A selected placement is complete and ordered

Publication of a selected joint placement SHALL refuse a missing, truncated,
duplicated or reordered operation block even when its surviving operations
are contiguous and carry the correct joint slot. An unchanged complete block
SHALL remain publishable after normal rebind and checkpoint restoration.
This validation SHALL NOT add serialized fields or alter legacy documents.

#### Scenario: One centring translation is missing
- **WHEN** one operation of an off-centre revolute placement is missing
- **THEN** span publication refuses the control and names its incomplete
  placement instead of publishing the contiguous surviving operations

#### Scenario: The pivot block is reordered
- **WHEN** the pivot's complete operations remain contiguous but change order
- **THEN** span publication refuses the control rather than describing a
  different motion as the selected joint

#### Scenario: A normal rebound block is unchanged
- **WHEN** the run advances, restores a snapshot and republishes a complete
  selected joint placement
- **THEN** the span still identifies the correct complete block and the
  program and document shape remain unchanged
