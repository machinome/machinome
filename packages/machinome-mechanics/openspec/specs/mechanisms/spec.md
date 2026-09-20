# Mechanisms Specification

## Purpose

The mechanism laws this package carries once so a project's own
`kinematics.py` stops rewriting them: the external spur-gear mesh, the
lead screw, the planar slider-crank, linear delta kinematics, and the
circle geometry a linkage asks for. Records their frames, zeros and sign
conventions, the two faces they inherit from `machinome.math` and the
declared face they refuse, and the identities each law is held to.
Preserves the formula contract originally introduced by machinome ADR-076
(mechanism laws as compositions over expression math), over its ADR-022
(cross-runtime degree-trig parity) and ADR-062 (typed parameters and the
exponent algebra). Package ownership follows the accepted extraction recorded
in `workflow/extraction.md`; these ADR numbers refer to the framework's history.

Code: `machinome_mechanics/`.

## Requirements

### Requirement: Mechanism laws as compositions over expression math

The system SHALL provide the package `machinome_mechanics`, whose every
function is a composition of `machinome.math` functions and ordinary
arithmetic, so that one formula computes on plain numbers and builds the
viewer's deferred expression when any argument is symbolic animation time or
a driver. No function in the package SHALL emit an OpenSCAD builtin that
`machinome.math` does not already emit, so the cross-runtime parity corpus
of the `kinematics` capability covers the package without extension.

The package SHALL re-export every public function under a flat name unique
across its families, so `from machinome_mechanics import meshed_angle`
works, and SHALL keep each family in its own module with the family's
conventions stated once in that module.

Every angle SHALL be in degrees, positive by the right-hand rule about the
stated axis, matching `machinome.math` and the node transform API. Every
function's docstring SHALL state its frame, its zero and its sign, and SHALL
map that convention onto the originating project it was lifted from.

The package SHALL NOT provide a declared (class-body) face: its laws carry
degree literals such as `180` and `360` that the dimension algebra cannot
type as angles, so a declared token reaching a law raises the algebra's own
dimension error at class definition rather than yielding a formula. A class
body that needs a mechanism law over declared parameters evaluates it on
`.value` operands, which is the algebra's stated escape hatch.

#### Scenario: A law rides through a symbolic driver

- **WHEN** `piston_height` is called with a symbolic driver expression as
  the crank angle and numbers for the crank radius and rod length
- **THEN** it returns a symbolic expression composed only of `cos`, `sin`,
  `sqrt` calls and arithmetic, and nothing raises

#### Scenario: Numeric and symbolic faces agree

- **WHEN** each exported law is evaluated once on numbers and once on a
  symbolic expression that is then evaluated at the same numbers
- **THEN** the two results are equal within floating-point tolerance for
  every law and every sampled input

#### Scenario: The declared face is refused

- **WHEN** a class body computes `meshed_angle(theta, 12, 24)` over a
  declared `Angle` parameter `theta`
- **THEN** class definition raises a dimension error, and the same
  computation over `theta.value` succeeds

### Requirement: The external spur-gear mesh law

`meshed_angle(driver_angle, driver_teeth, driven_teeth, line_of_centres=0.0,
driver_gap=0.0, driven_tooth=0.0)` SHALL return the angle of the driven gear
of an external spur pair, and `driving_angle(driven_angle, driver_teeth,
driven_teeth, line_of_centres=0.0, driver_gap=0.0, driven_tooth=0.0)` SHALL
return the driver angle for a driven gear already placed, both in the common
frame in which both gears' angles and the line of centres are measured.

`line_of_centres` SHALL be the direction from the driver's centre to the
driven's. `driver_gap` SHALL be the direction, in the driver's own frame at
angle zero, of the centre of one of its gaps; `driven_tooth` SHALL be the
direction, in the driven's own frame at angle zero, of the tip of one of its
teeth. Both references default to zero and are values a caller reads from
its gear library's convention; the law SHALL NOT read any gear object.

The law SHALL be `driven = line + 180 - driven_tooth - (driver_teeth /
driven_teeth) * (driver_gap + driver_angle - line)`, and `driving_angle`
SHALL be its exact inverse.

#### Scenario: The pair is meshed at the reference pose

- **WHEN** the driver stands so that its referenced gap centre points along
  the line of centres, that is `driver_angle = line - driver_gap`
- **THEN** `meshed_angle` returns `line + 180 - driven_tooth`, the pose in
  which the driven's referenced tooth tip points back along the line of
  centres into that gap

#### Scenario: The driven counter-rotates by the tooth ratio

- **WHEN** the driver angle advances by one degree
- **THEN** `meshed_angle` decreases by `driver_teeth / driven_teeth` degrees;
  for 60 teeth driving 8, by 7.5 degrees

#### Scenario: The cq_gears convention is two values

- **WHEN** `meshed_angle(0, 12, 24, 0, 180 / 12, 0)` is evaluated, the
  driver's tooth centred on its +X at zero so its gap centre sits at
  `180 / 12`, and the driven likewise so its tooth tip sits at zero
- **THEN** the result is `172.5`, the value gearbox's `conjugate_angle(0,
  12, 24)` returns, and `meshed_angle(30, 12, 24, 45, 15, 0)` is `225`,
  matching `conjugate_angle(30, 12, 24, alpha=45)`

#### Scenario: The inverse round-trips

- **WHEN** `driving_angle(meshed_angle(10, 60, 8, 30, 3, 22.5), 60, 8, 30,
  3, 22.5)` is evaluated
- **THEN** the result is `10` within floating-point tolerance, and
  `meshed_angle(10, 60, 8, 30, 3, 22.5)` itself is `315`

### Requirement: The lead screw

`screw_travel(angle, lead)` SHALL return `lead * angle / 360` and
`screw_angle(travel, lead)` SHALL return `360 * travel / lead`, where `lead`
is the axial advance per turn (pitch times starts, never bare pitch).

The convention SHALL be a right-hand thread turned positively by the
right-hand rule about its axis, which advances the screw along that axis
relative to its nut by the returned travel. A left-hand thread, or the nut's
own motion relative to a screw held axially, is the caller's negation; the
functions SHALL take no handedness argument.

#### Scenario: One turn is one lead

- **WHEN** `screw_travel(360, 2.0)` and `screw_angle(1.0, 2.0)` are evaluated
- **THEN** the results are `2.0` and `180`, and the two functions are exact
  inverses for a nonzero lead

#### Scenario: A left-hand screw is the caller's sign

- **WHEN** the openflexure column, whose screw lowers the column as its
  motor turns positively, is expressed
- **THEN** its travel is `-screw_travel(angle, lead)`, and the framework
  function itself carries no sign choice

### Requirement: The planar slider-crank

The crank functions SHALL work in the crank's own plane: the crank axis is
normal to the plane, the cylinder axis is the plane's second coordinate,
called *along*, and the first coordinate is *across*. The crank angle SHALL
be measured from the along axis, positive by the right-hand rule about the
crank axis, with zero at top dead centre.

- `crank_pin(angle, crank_radius)` SHALL return the pin's `(across, along)`
  position: `(-crank_radius * sin(angle), crank_radius * cos(angle))`.
- `crank_rod_angle(angle, crank_radius, rod_length)` SHALL return the
  connecting rod's tilt from the cylinder axis, in the same rotational sense,
  such that a rod authored along the cylinder axis and turned by it carries
  its small end onto the axis: `-asin((crank_radius / rod_length) *
  sin(angle))`.
- `piston_height(angle, crank_radius, rod_length)` SHALL return the small
  end's along coordinate: `crank_radius * cos(angle) + sqrt(rod_length^2 -
  (crank_radius * sin(angle))^2)`.

A caller whose crank axis is not the plane normal maps these with its own
frame rotation; v8-engine's crank about +X with the pin at +Z at zero is
this plane with `across = y` and `along = z`.

#### Scenario: Top, quarter and bottom dead centre

- **WHEN** the three functions are evaluated for a crank radius of 15 and a
  rod length of 60 at angles 0, 90 and 180
- **THEN** `crank_pin` returns `(0, 15)`, `(-15, 0)` and `(0, -15)`,
  `crank_rod_angle` returns `0`, `-asin(0.25)` (about `-14.4775`) and `0`,
  and `piston_height` returns `75`, `sqrt(3375)` (about `58.0948`) and `45`,
  all within floating-point tolerance

#### Scenario: The small end stays on the cylinder axis

- **WHEN** for any sampled crank angle the rod, authored along the cylinder
  axis from the pin, is turned by `crank_rod_angle` and added to `crank_pin`
- **THEN** the small end's across coordinate is zero within tolerance and
  its along coordinate equals `piston_height`

### Requirement: Linear delta kinematics

For a linear delta whose towers stand on a circle about Z and whose
carriages ride vertically:

- `delta_carriage(x, y, rod, radius, tower, plane=0.0)` SHALL return the
  height of the carriage joint on the tower at azimuth `tower` for an
  effector at `(x, y)` whose joint plane is at height `plane`: `plane +
  sqrt(rod^2 - dx^2 - dy^2)` where `(dx, dy) = (x - radius * cos(tower),
  y - radius * sin(tower))` is the horizontal vector from the carriage joint
  to the effector joint, and `radius` is the length of that vector when the
  effector is at the origin.
- `delta_rod(x, y, rod, radius, tower)` SHALL return `(tilt, azimuth)`: the
  rod's lean from vertical, `asin(sqrt(dx^2 + dy^2) / rod)`, and the
  direction of that lean about Z, `atan2(dy, dx)`.

The two rotations SHALL pose a rod authored along Z with either of its
joints at the origin: rotate by `-tilt` about Y, then by `azimuth` about Z,
then translate to that joint. The docstring SHALL record why two rotations
about constant axes are returned rather than one about a computed axis: a
rotation axis in this framework cannot carry a driver symbol.

#### Scenario: A rod at the origin, at the tower's foot

- **WHEN** `delta_carriage(0, 0, 215, 100, 0)` and `delta_rod(0, 0, 215,
  100, 0)` are evaluated
- **THEN** the carriage is at `sqrt(215^2 - 100^2)` (about `190.3287`), the
  tilt is `asin(100 / 215)` (about `27.7177`) and the azimuth is `180`

#### Scenario: Moving toward and beside the tower

- **WHEN** the effector moves to `(10, 0)` and then to `(0, 10)`
- **THEN** the carriage rises to about `195.2562` with tilt about `24.7465`
  and azimuth `180`, then sits at about `190.0658` with tilt about `27.8680`
  and azimuth about `174.2894`

#### Scenario: The posed rod meets both joints

- **WHEN** a unit vector along -Z is rotated by `-tilt` about Y, then by
  `azimuth` about Z, and scaled by `rod`
- **THEN** it equals `(dx, dy, -(carriage - plane))`, the vector from the
  carriage joint to the effector joint, within tolerance

### Requirement: Linkage geometry

- `circle_intersection(centre_a, radius_a, centre_b, radius_b, side=1)`
  SHALL return the 2-tuple at distance `radius_a` from `centre_a` and
  `radius_b` from `centre_b` on the side named: `side = 1` the intersection
  to the left of the direction from `centre_a` to `centre_b` (counter-
  clockwise), `side = -1` to the right.
- `triangle_angle(opposite, adjacent_a, adjacent_b)` SHALL return, in
  degrees, the angle of a triangle opposite the side `opposite` between the
  two adjacent sides: `acos((a^2 + b^2 - opposite^2) / (2 a b))`.
- `link_rise(link, offset)` SHALL return `sqrt(link^2 - offset^2)`, the
  height of a rigid link of length `link` whose ends are `offset` apart
  horizontally.

None SHALL guard against an unreachable configuration numerically: a sqrt
or acos of an out-of-range value raises as `machinome.math` raises, and
symbolically evaluates to NaN as OpenSCAD and the viewer do. That is the
originating projects' behaviour and the honest one.

#### Scenario: Two circles cross on the side asked for

- **WHEN** `circle_intersection((0, 0), 5, (8, 0), 5, side)` is evaluated
  for both sides
- **THEN** it returns `(4, 3)` for `side = 1` and `(4, -3)` for `side = -1`,
  and `circle_intersection((1, 1), 5, (1, 9), 5, 1)` returns `(-2, 5)`

#### Scenario: The grasshopper's nib is a circle intersection

- **WHEN** `circle_intersection((0, 0), 45, (30, 40), 20, 1)` is evaluated
- **THEN** it equals wall_clock_53's `nib_position((30, 40), 20, 1, 45)`,
  about `(10.3625, 43.7906)`

#### Scenario: A right triangle

- **WHEN** `triangle_angle(5, 3, 4)`, `triangle_angle(3, 4, 5)` and
  `link_rise(5, 3)` are evaluated
- **THEN** the results are `90`, about `36.8699`, and `4`

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

### Requirement: Closed directed belt path measurements

`belt_path_metrics(centres, radii, senses=None)` SHALL measure the ordered closed
pitch path in the caller's XY plane, joining each circle to the next and the
last to the first with the branch of `belt_tangent_points`. Coordinates and
nonnegative radii SHALL share one length unit. Senses SHALL be literal +1 for
clockwise or -1 for counterclockwise traversal, defaulting to all +1. Sequence
lengths SHALL match and contain at least two circles, otherwise raising
`ValueError`. Geometric domain errors SHALL propagate without clamping.

The result SHALL be a dict containing tuple fields `spans`, `wrap_angles`,
`arc_lengths`, `stations` and scalar `length`. `spans[i]` SHALL be the outgoing
`(start_xy, unit_direction_xy, length)` from circle i. Wrap angles in degrees
and arc lengths SHALL be indexed by circle, with wrap in [0,360) and coincident
tangent directions giving zero, not a full turn. Arc length SHALL be radius
times wrap times pi/180. A zero radius SHALL still have a defined tangent
direction and zero arc length; limiting zero-length spans SHALL retain direction.

The arc-length origin SHALL be departure from circle 0. The 2N stations SHALL
be the starts of span 0, arc about circle 1, span 1, and so on through the arc
about circle 0. `length` SHALL be the sum of all spans and arcs. Supported raw
deferred coordinates/radii SHALL use the same formula without numeric coercion;
topology and senses remain caller-authored data. No project marker, pitch fit,
mounting transform or full-turn policy SHALL be inferred.

#### Scenario: Equal two-pulley route

- **WHEN** centers are (0,0) and (10,0), both radii 2, senses omitted
- **THEN** spans start at (0,2) and (10,-2), point along +X and -X, and each
  measure 10; wraps are (180,180), arcs are (2*pi,2*pi), stations are
  (0,10,10+2*pi,20+2*pi), and total length is 20+4*pi

#### Scenario: An idler bends the belt backwards

- **WHEN** a three-circle route includes a counterclockwise idler
- **THEN** its spans use the corresponding inner tangents and each wrap follows
  its own sense; stations alternate span i and arc i+1 without rotating the
  circle-indexed wrap and arc result fields

#### Scenario: Degenerate directions and deferred geometry

- **WHEN** a valid route has a zero-radius circle, a limiting zero-length span,
  or supported deferred coordinates evaluated at valid sampled poses
- **THEN** no normalization by a span length or radius is required, zero-radius
  arcs are zero, and evaluated symbolic results match numeric measurements

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
