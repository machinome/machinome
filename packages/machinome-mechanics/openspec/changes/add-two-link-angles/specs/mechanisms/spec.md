## ADDED Requirements

### Requirement: Planar two-link joint angles

`two_link_angles(x, y, first_length, second_length, side=1)` SHALL return a
tuple `(shoulder, elbow)` in degrees for a fixed pivot at (0,0) and target
(x,y). Shoulder SHALL be the first link's absolute bearing from +X toward +Y
about +Z; elbow SHALL be the second link's relative rotation, so its absolute
bearing is shoulder+elbow. Coordinates and positive link lengths SHALL share
one length unit. Caller-supplied side +1 SHALL select the knee left of the
pivot-to-target direction, -1 the knee right of it.

For d=sqrt(x*x+y*y), shoulder SHALL be
`atan2(y,x) + side*triangle_angle(second_length,first_length,d)` and elbow
SHALL be `side*(triangle_angle(d,first_length,second_length)-180)`.
The helper SHALL be exported flat and from linkages, with one arithmetic
definition for numeric and supported deferred operands. Side SHALL remain
caller-authored ±1; arbitrary side values SHALL not be normalized or validated.
Zero target distance or zero divisor lengths SHALL propagate numeric division
errors; unreachable configurations SHALL propagate numeric math domain errors.
No tolerance clamp, branch tracking, servo offset or project reach guard SHALL
be inferred. The mathematical domain SHALL require positive lengths, d>0 and
abs(first_length-second_length)<=d<=first_length+second_length.

#### Scenario: Two branches reach the same target

- **WHEN** target is (3,4) and the first and second links have length 5
- **THEN** side +1 returns approximately (113.130102354,-120) degrees and
  side -1 approximately (-6.869897646,120)
- **AND** forward rotation of both links reaches (3,4) for both branches

#### Scenario: Joint rotation is relative

- **WHEN** the returned angles are used for an articulated leg
- **THEN** the second link endpoint is first_length*(cos(shoulder),sin(shoulder))
  plus second_length*(cos(shoulder+elbow),sin(shoulder+elbow))
- **AND** Spiderbot retains its measured tibia offset and AlbertPro its guard

#### Scenario: Straight and unreachable reaches

- **WHEN** target is (8,0), with first length 5 and second length 3
- **THEN** both branches give shoulder and elbow zero
- **AND** targets (9,0) or (1,0) raise numeric ValueError, while (0,0) raises
  ZeroDivisionError rather than inventing a folded bearing

#### Scenario: Deferred geometry agrees with numeric closure

- **WHEN** supported deferred coordinates or lengths are evaluated at valid
  representative samples with either side
- **THEN** the evaluated angles agree with numeric results and close the same
  two-link geometry, including the projects' driven poses
