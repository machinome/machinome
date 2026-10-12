## ADDED Requirements

### Requirement: Internal ring and pinion angular increments

`internal_mesh_angle(ring_angle, ring_teeth, pinion_teeth, carrier_angle=0.0)`
SHALL return `carrier_angle + (ring_teeth/pinion_teeth)*(ring_angle-carrier_angle)`.
Input/output angles SHALL be signed unwrapped degree increments from a
caller-registered pose, measured about the same positive axis in a common
nonrotating frame. The output SHALL be the pinion increment in that frame;
subtracting carrier SHALL give its increment relative to the carrier.
The helper SHALL be exported flat and from gears. Tooth registration, rest
phases, source placement and local-axis signs SHALL remain caller-owned.

Numeric and supported deferred operands SHALL share the same arithmetic.
Physical counts SHALL be positive integers with ring greater than pinion;
no count coercion, wrapping, validation or geometry certification SHALL be
performed. Zero numeric pinion count SHALL propagate ZeroDivisionError;
other arithmetic counts SHALL retain their algebraic result.

#### Scenario: A moving ring drives a fixed-center pinion in the same sense

- **WHEN** ring_angle=30, ring_teeth=60, pinion_teeth=10 and carrier defaults to zero
- **THEN** the pinion increment is 180 degrees
- **AND** Thor's separate mounting signs and tooth phases remain unchanged

#### Scenario: Fixed ring and moving carrier retain the planetary law

- **WHEN** ring_angle=0, ring_teeth=126, pinion_teeth=54 and carrier_angle=45
- **THEN** the common-frame pinion increment is -60 degrees within floating tolerance
- **AND** subtracting the carrier gives -105 degrees, preserving OpenTorque's
  child-local spin for one sun revolution

#### Scenario: Relative mesh and common-frame motion agree

- **WHEN** representative finite signed ring/carrier increments and nonzero pinion counts are used
- **THEN** pinion_teeth*(output-carrier) equals ring_teeth*(ring-carrier)
- **AND** adding the same increment to ring and carrier adds it to output
- **AND** equal ring and carrier increments give that same pinion increment

#### Scenario: Deferred values retain the same relative law

- **WHEN** supported deferred angle or tooth-count operands are evaluated at valid samples
- **THEN** output agrees with numeric evaluation and remains unwrapped across turns

#### Scenario: Count domain is not repaired

- **WHEN** numeric pinion_teeth is zero
- **THEN** ZeroDivisionError propagates
- **AND** equal nonzero ring/pinion counts return ring_angle algebraically,
  without implying a physically realizable pair
