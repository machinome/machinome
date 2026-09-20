## ADDED Requirements

### Requirement: Rolling travel from rotation

`rolling_travel(angle, radius)` SHALL return `angle * radius * pi / 180`,
the signed tangent travel for degree rotation at a pitch/contact radius.
It SHALL be exported from `machinome_mechanics` and its `rolling` module.
Zero angle SHALL give zero travel, with no wrapping or clamping. Positive
travel SHALL follow the positively rotating surface tangent; callers SHALL
supply their own mounting signs and rest offsets. Length units SHALL be those
of radius. Ordinary numeric and symbolic arithmetic SHALL share one definition.
Zero and negative radii SHALL retain arithmetic behavior rather than be clamped.

#### Scenario: A revolution pays out the circumference

- **WHEN** angle is 360 degrees and radius is 9 mm
- **THEN** travel is `18*pi` mm, and -720 degrees gives `-36*pi` mm

#### Scenario: The existing projects retain their travel

- **WHEN** Dragon R1's rack and Thor's belt drives replace their local conversion
- **THEN** their original signed travel is preserved at negative, zero and
  positive angles, including symbolic motion

#### Scenario: Zero radius has no travel

- **WHEN** any finite angle is evaluated at zero radius
- **THEN** the returned travel is zero
