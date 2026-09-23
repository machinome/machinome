## ADDED Requirements

### Requirement: Framework exact operations preserve their reusable native inputs

The framework SHALL run native Common and Fuse operations, and the Section used to verify an empty Common, without allowing the operation to change the caller-owned input shapes' subshape tolerances or topology. The same native shape SHALL remain usable for later exact comparisons and compositions regardless of the order of earlier framework exact operations. Existing kernel Build-failure and empty-common verification refusals SHALL remain; this requirement SHALL NOT treat an invalid result as clearance, replace an exact verdict with a mesh, heal geometry, or introduce an overlap tolerance.

#### Scenario: Curta reuses one posed drum across a boundary search
- **WHEN** the Curta reverser tooth is compared against the same native drum at successive shaft angles around an observed contact boundary
- **THEN** the drum's original native subshape tolerances remain unchanged and the later common is not corrupted by the preceding comparisons

#### Scenario: An ordinary fresh-input Curta common remains valid
- **WHEN** an exact comparison uses the Curta reverser tooth and drum at the measured crank-169° fresh-input near-contact pose
- **THEN** the common remains a valid, positive native result as in the existing default kernel, without treating an invalid result as clearance

#### Scenario: Fusion and section also receive reusable operands
- **WHEN** a framework exact fusion or an empty-common verification section runs on caller-owned native shapes
- **THEN** each operation preserves those inputs for a later comparison

#### Scenario: Ordinary contact and failure retain their meaning
- **WHEN** the exact operands are disjoint, merely tangent, overlapping, or cause the native Build or independent witness verification to fail
- **THEN** the existing exact verdict or refusal is obtained without a mesh fallback, epsilon waiver, or input mutation
