## ADDED Requirements

### Requirement: Contact-referenced belt pulley angle

`belt_pulley_angle(belt_position, pitch_radius, contact_angle,
contact_station=0.0, sense=1)` SHALL return
`contact_angle - sense * rolling_angle(belt_position - contact_station,
pitch_radius)` and SHALL be exported from the flat package and belts module.

Belt position and contact station SHALL be arc lengths in the same oriented
path coordinate, using the length unit of the pitch radius. Contact angle and
output SHALL be degrees in the caller's XY plane, from +X counterclockwise
about +Z. Sense +1 SHALL mean clockwise belt traversal about the pulley and
-1 counterclockwise, consistent with belt path geometry. At belt position
equal to contact station, the returned angle SHALL equal contact angle: the
pulley's reference tooth is at that contact direction. Callers SHALL retain
their own tooth-reference and mounting offsets.

The result SHALL remain signed and unwrapped, including multiple turns.
Numeric and supported deferred operands SHALL share one arithmetic definition.
Physical pitch radius SHALL be positive; negative radius SHALL retain ordinary
arithmetic and zero numeric radius SHALL propagate ZeroDivisionError. No
tooth fitting, route inference, tolerance clamp or phase normalization SHALL
be performed.

#### Scenario: Clockwise motion from a nonzero station

- **WHEN** belt position is 10+pi, pitch radius is 2, contact angle is 90 and station is 10
- **THEN** the angle is 0 degrees within floating tolerance
- **AND** position 10 returns 90 and position 10+4*pi returns -270, unwrapped

#### Scenario: Reverse-bend pulley follows the other sense

- **WHEN** the same inputs use sense -1, as Metamaquina2's Y pulley does
- **THEN** position 10+pi returns 180 and position 10+4*pi returns 450 degrees

#### Scenario: Changing the path origin changes no pulley pose

- **WHEN** the same offset is added to belt position and contact station
- **THEN** the returned pulley angle is unchanged within floating tolerance

#### Scenario: Deferred belt position retains contact phase

- **WHEN** supported deferred belt position or contact inputs are evaluated
  at representative numeric samples in Prusa3-vanilla and Metamaquina2
- **THEN** their pulley angle agrees with the same numeric law and preserves
  the caller's contact phase, station and mounting signs
