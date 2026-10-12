## ADDED Requirements

### Requirement: Rotation from rolling travel

`rolling_angle(travel, radius)` SHALL return `travel / radius * 180 / pi`,
the unwrapped signed rotation in degrees from tangent travel at a constant
pitch/contact radius. It SHALL be exported from `machinome_mechanics` and its
`rolling` module. Travel and radius SHALL use the same length unit. Positive
travel SHALL follow the positively rotating surface tangent; callers supply
their mounting signs and reference phases. Numeric and symbolic arguments
SHALL share one arithmetic definition without wrapping or clamping.

Negative radius SHALL preserve arithmetic sign. Zero radius SHALL remain
undefined: ordinary Python numeric division SHALL raise ZeroDivisionError,
and symbolic division SHALL retain the expression runtime's singular behavior.

#### Scenario: A circumference is a revolution

- **WHEN** travel is `18*pi` mm and radius is 9 mm
- **THEN** the angle is 360 degrees, and travel `-36*pi` gives -720 degrees

#### Scenario: Rolling conversions are inverses

- **WHEN** a finite angle is converted by rolling_travel at a nonzero radius
  and that distance is passed to rolling_angle at the same radius
- **THEN** the original unwrapped angle is recovered within floating tolerance

#### Scenario: Existing belt wheels retain their motion

- **WHEN** Prusa3-vanilla and Kossel replace distance-to-angle conversions
- **THEN** pulley phases, idler angles, signs and numeric/symbolic motion are
  preserved at representative negative, zero and positive travel

#### Scenario: A wheel cannot roll at zero radius

- **WHEN** rolling_angle is called with ordinary Python numbers at zero radius
- **THEN** it raises ZeroDivisionError rather than returning a clamped angle
