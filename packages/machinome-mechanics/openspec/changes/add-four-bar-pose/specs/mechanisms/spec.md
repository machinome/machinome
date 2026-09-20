## ADDED Requirements

### Requirement: Driven planar four-bar pose

`four_bar_pose(angle, crank_pivot, rocker_pivot, crank_length, coupler_length,
rocker_length, side=1)` SHALL return a dict with exactly `crank_end`,
`rocker_end`, `rocker_angle` and `coupler_angle`. Let A and D be the supplied
fixed crank and rocker pivots. The moving crank end B SHALL be
A+crank_length*(cos(angle),sin(angle)). The moving rocker end C SHALL have
distance rocker_length from D and coupler_length from B. Lengths SHALL be
positive in the same unit as the pivot coordinates. Angles SHALL be degrees
from +X toward +Y about +Z in the caller's plane.

For v=B-D and d=|v|, rocker_angle SHALL be
`atan2(v.y,v.x) + side*triangle_angle(coupler_length,rocker_length,d)` and C
SHALL be D+rocker_length*(cos(rocker_angle),sin(rocker_angle)). Coupler_angle
SHALL be atan2(C.y-B.y,C.x-B.x). Crank_end and rocker_end SHALL be XY tuples.
Literal side+1 SHALL select C left of D→B and -1 right; arbitrary side values
SHALL not be validated or normalized. Rocker_angle SHALL retain the constructed
unnormalized sum; coupler_angle SHALL retain atan2's principal representation.
No continuous angle unwrapping or branch tracking SHALL be inferred.

The helper SHALL be exported flat and from linkages, using one arithmetic
definition for numeric and supported deferred values. Numeric coincident D/B
or zero divisor length SHALL propagate division errors; impossible closure
SHALL propagate math domain errors. No tolerance clamp or project-specific
frame, source-part offset, ride inversion or reach policy SHALL be added.

#### Scenario: A selected four-bar closes

- **WHEN** angle is 90, A=(0,0), D=(4,0), crank=3, coupler=4, rocker=3, side=-1
- **THEN** B is approximately (0,3), C is (4,3), rocker_angle is 90 and
  coupler_angle is 0 degrees, within floating tolerance
- **AND** side+1 instead returns C approximately (1.12,-0.84) on the other branch

#### Scenario: The source rocker bearing is not normalized

- **WHEN** the constructed center bearing plus closure exceeds 180 degrees
- **THEN** rocker_angle retains that sum rather than subtracting 360
- **AND** Dragon R1 can preserve its existing source-minus-target part rotation

#### Scenario: Two real projects retain their closures

- **WHEN** Dragon R1 maps ride to the absolute crank bearing and Strandbeest
  selects the W and U closure branches
- **THEN** their existing pivot positions and source-part poses are preserved
  within empirical floating tolerances at the tested motion and scale samples

#### Scenario: Deferred pose obeys the same geometry

- **WHEN** supported deferred angle, pivot or length operands are evaluated
  at reachable sampled configurations on either side
- **THEN** the returned points and angles agree with numeric evaluation and
  the three moving-link lengths remain satisfied

#### Scenario: Invalid closure is not invented

- **WHEN** the closure circles are disjoint or strictly nested
- **THEN** numeric evaluation raises ValueError
- **AND** coincident closure centers raise ZeroDivisionError
