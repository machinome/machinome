## ADDED Requirements

### Requirement: Directed belt tangent points

`belt_tangent_points(centre_a, radius_a, centre_b, radius_b,
sense_a=1, sense_b=1)` SHALL return two XY contact points, ordered from
circle A to circle B. Positive physical radii SHALL use the caller's length
unit. Senses SHALL denote clockwise (+1) or counterclockwise (-1) traversal
about each circle in that XY plane. Equal senses SHALL select an outer tangent;
opposite senses SHALL select an inner tangent.

For d=B-A, q=dot(d,d), r=sense_a*radius_a-sense_b*radius_b and
h=sqrt(q-r*r), the shared normal SHALL be
`((d.x*r-d.y*h)/q, (d.y*r+d.x*h)/q)`; returned points SHALL be
A+sense_a*radius_a*n and B+sense_b*radius_b*n. The helper SHALL be exported
from the flat package and belts module and SHALL use the same arithmetic for
numbers and supported symbolic expressions. It SHALL not clamp impossible
configurations: numeric square-root domain and division errors SHALL propagate.
Zero-radius contact SHALL reduce to its center when centers are distinct.

#### Scenario: An outer tangent runs above equal pulleys

- **WHEN** centers are (0,0) and (10,0), radii are both 2 and senses default
- **THEN** contacts are (0,2) and (10,2)

#### Scenario: A back idler reverses the contact side

- **WHEN** centers are (0,0) and (10,0), radii are 2 and 3, senses are +1,-1
- **THEN** contacts are (1,sqrt(3)) and (8.5,-1.5*sqrt(3))
- **AND** their connecting segment is perpendicular to both contact radii

#### Scenario: The same route can be traversed backwards

- **WHEN** circles are swapped and both senses negated
- **THEN** the same two contacts are returned in reverse order within tolerance

#### Scenario: Invalid contacts are not invented

- **WHEN** an inner tangent between radii 2 and 3 is requested at separation 4
- **THEN** numeric evaluation raises ValueError
- **AND** coincident numeric centers are undefined rather than clamped

#### Scenario: Existing belt geometry is preserved

- **WHEN** Thor and Prusa3-vanilla adapt their turn markers to the helper
- **THEN** existing contact points, span lengths and wrap behavior are preserved
  at their representative routes within established floating tolerances
