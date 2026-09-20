## ADDED Requirements

### Requirement: Pulley pitch radius

`pulley_pitch_radius(teeth, pitch)` SHALL return `teeth * pitch / (2*pi)`,
the radius whose circumference contains the given number of linear tooth
pitches. It SHALL be exported from `machinome_mechanics` and its `belts`
module. Its output SHALL use the length unit of pitch and SHALL not include
tooth-tip or pitch-line surface offsets. Numeric and symbolic arguments SHALL
share one arithmetic definition, without count rounding or domain clamping.
Zero, negative and fractional inputs SHALL retain ordinary arithmetic behavior.

#### Scenario: GT2 and AT3 pulleys preserve their pitch circles

- **WHEN** Thor's 117-tooth GT2 pulley and Actuator's 10-tooth AT3 pinion
  request radii at pitches 2 mm and 3 mm respectively
- **THEN** their circumferences are 234 mm and 30 mm within floating tolerance

#### Scenario: Symbolic pitch remains deferred

- **WHEN** pitch or tooth count is a supported raw symbolic expression
- **THEN** the deferred radius evaluates to the same result as numeric inputs

#### Scenario: Surface offsets stay outside the helper

- **WHEN** a printer subtracts its existing pitch-line allowance from the radius
- **THEN** its surface radius is preserved with no allowance added by the helper
