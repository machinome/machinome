## ADDED Requirements

### Requirement: Fixed-ring cycloidal angular ratio

`cycloidal_ratio(lobes, pins)` SHALL return `-(pins-lobes)/lobes`, the signed
disk/output angle increment per eccentric-input angle increment for a fixed
ring. Pins SHALL mean fixed ring pins, not output-transfer pins. Input and
output increments SHALL use the same positive axis and angular unit; degree
increments SHALL remain degrees when multiplied by this dimensionless ratio.
The function SHALL be exported flat and from the gears module.

Physical use SHALL assume positive integer lobes and pins greater than lobes.
Numeric and supported deferred operands SHALL share one arithmetic definition
without integer coercion, floor division, wrapping, clamping or validation.
Zero numeric lobes SHALL propagate ZeroDivisionError; other arithmetic inputs,
including equal counts, SHALL retain arithmetic results without implying
physical geometry certification. Reference phases, eccentric center orbit,
mounting transforms and positive reduction magnitudes SHALL remain caller-owned.

#### Scenario: One input revolution reverses a twenty-lobe disk

- **WHEN** lobes=20 and fixed pins=21
- **THEN** the ratio is -0.05 and 360 degrees of input gives -18 degrees of
  disk/output increment, while 7200 gives -360 without wrapping

#### Scenario: The fixed-ring relative mesh identity holds

- **WHEN** a finite input increment is multiplied by the ratio at nonzero lobes
- **THEN** lobes*(output-input) equals pins*(0-input) within floating tolerance
- **AND** scaling both counts by the same positive factor leaves the ratio unchanged

#### Scenario: Consumer eccentric motion is not reduced

- **WHEN** CycloidalDrive and OpenCycloid replace their signed spin coefficients
- **THEN** their disk/output increments retain the old -1/20 law
- **AND** eccentric center orbits remain one-to-one with input and existing
  rest placements and controls remain unchanged

#### Scenario: Deferred arithmetic remains deferred

- **WHEN** supported deferred counts or an input angle are evaluated at
  representative finite samples with nonzero lobes
- **THEN** the resulting ratio and multiplied angle agree with numeric evaluation

#### Scenario: No positive reduction or valid geometry is invented

- **WHEN** zero numeric lobes are supplied
- **THEN** evaluation raises ZeroDivisionError
- **AND** equal nonzero counts return zero algebraically, without a geometry claim
