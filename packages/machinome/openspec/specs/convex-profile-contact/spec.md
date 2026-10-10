# convex-profile-contact Specification

## Purpose

Define authored finite convex-profile values and their pointwise placed-contact predicate for compact running Bounds.

## Requirements

### Requirement: A contact profile consists only of authored finite convex polygons

The system SHALL accept an ordered finite sequence of independent planar polygon coordinate loops as one immutable contact profile. Each polygon SHALL have at least three distinct finite binary-float vertices, positive counterclockwise area and convex orientation; collinear consecutive edges SHALL be permitted. Exact tests on the supplied binary coordinates SHALL reject missing, zero-length-edge, repeated-vertex, self-crossing, non-convex or nonfinite polygons without repairing, welding, expanding or constructing a hull. The profile SHALL retain its supplied vertex values and polygon order and SHALL contain no CAD or mesh object. The constructor and evaluator SHALL live at the public `machinome.simulation.profile` import path.

#### Scenario: Independently supplied mesh triangle extends a profile
- **WHEN** an author combines independently supplied valid native-cover polygons and projected published-mesh triangles in one profile
- **THEN** all supplied polygons remain in the profile without a point-cloud hull or inferred connectivity

#### Scenario: A narrow concavity is not filled
- **WHEN** one supplied polygon has an exact concave turn in its binary coordinates
- **THEN** construction refuses that polygon rather than treating a rounded orientation or a convex hull as the authored shape

#### Scenario: Collinear boundary is accepted
- **WHEN** a polygon has a collinear consecutive corner but nonzero area and no concave turn
- **THEN** construction accepts and retains that corner

#### Scenario: Same-sign turns do not excuse a crossing
- **WHEN** a pentagram loop has positive area and local turns of one sign but nonadjacent edges cross, or a loop repeats a vertex or has a zero-length edge
- **THEN** construction refuses the loop by name without interpreting its crossing as a convex union

### Requirement: A placed-profile predicate decides pointwise contact

`profile_overlap(left, right, left_angle, right_angle, left_xy=(0,0), right_xy=(0,0))` SHALL rotate each supplied profile in degrees about its own origin, translate it in XY, and return positive numeric `1.0` if any convex polygon pair has no strict separating AABB or edge-normal projection axis; otherwise it SHALL return positive numeric `0.0`. A shared boundary point or projection endpoint SHALL count as contact. Angle conversion SHALL be one multiplication by binary64 `0x1.1df46a2529d39p-6` without reduction; the transform SHALL compute `(cos(theta)*x - sin(theta)*y) + tx` and `(sin(theta)*x + cos(theta)*y) + ty` in that grouped order. Each complete transformed profile SHALL have all vertices and edge axes prepared and validated before any pair AABB early return. AABB and projection min/max SHALL visit supplied vertices in order, retaining the first value on equal comparisons including signed zero. SAT axes SHALL be made from transformed edges in polygon order as `(u.y-v.y, v.x-u.x)` and projections SHALL compute `(x*nx) + (y*ny)` in that order. Evaluation SHALL reject nonfinite inputs or any nonfinite intermediate, and an axis that becomes zero after finite placement, rather than guess, even when the other profile is far away. A huge finite binary64 angle SHALL use the same unreduced calculation with no arbitrary cutoff; a non-binary64 input that cannot convert to a finite binary64 operand, or later arithmetic/geometry that becomes invalid, SHALL refuse. It SHALL use no epsilon, volume threshold or tessellation at evaluation.

#### Scenario: Strict clearance and touching differ
- **WHEN** two valid square profiles are placed with a strict positive gap, then translated to touch at one edge
- **THEN** the two pointwise results are respectively `0.0` and `1.0`, with no magnitude cutoff

#### Scenario: Rotation and translation use the stated frames
- **WHEN** the same valid profile pair is rotated about each profile's own origin and then translated by finite XY offsets
- **THEN** the predicate tests those resulting coordinates, not a rotation about the world's origin or an inferred CAD placement

#### Scenario: Invalid arithmetic fails closed
- **WHEN** a placement operand or transformed projection becomes nonfinite
- **THEN** evaluation raises a named refusal and no numeric contact answer is produced

#### Scenario: Representability failures are not clearance
- **WHEN** a huge finite translation collapses a transformed edge to zero or a numeric angle cannot be represented as finite binary64
- **THEN** evaluation refuses rather than treating the pair as separated or applying a magnitude cutoff to an otherwise representable angle

#### Scenario: A distant polygon cannot hide a collapsed edge
- **WHEN** a profile has a transformed edge that collapses under a finite placement and the other profile's AABB is strictly distant
- **THEN** placement preparation refuses before any pairwise AABB rejection can return `0.0`

#### Scenario: Signed-zero ties have one ordered interpretation
- **WHEN** placement or polygon coordinates contain positive and negative zero
- **THEN** the ordered transform and strict projection comparisons determine the result without a normalization or tolerance, and the predicate returns positive `0.0` or `1.0`

### Requirement: A symbolic profile contact is a bounded-size expression operation

When any placement operand is symbolic, `profile_overlap` SHALL produce one contact operation referencing immutable profile data and scalar placement operands; the expression graph SHALL NOT materialize a polygon-pair SAT formula or use a process-global mutable profile registry. A profile value SHALL be owned by the expression or compiled program that uses it.

#### Scenario: Curta-sized pair does not become a pairwise graph
- **WHEN** a 591-piece pinion profile and a 1,072-piece drum profile are supplied to one symbolic contact call
- **THEN** the graph contains one contact operation and its scalar operands, rather than 633,552 per-pair formula subgraphs

#### Scenario: Independent programs do not exchange profile data
- **WHEN** two runs use equal scalar contact-call operands but different profile tables
- **THEN** each evaluates against its own immutable table and no cached result from one is used by the other

### Requirement: Repeated pointwise contacts do not repeat successful preparation without bound

Within one running integration attempt, the system MAY reuse a successful complete placed
profile or pair result for the same immutable profile objects and exact finite
builtin-numeric placement bits, including signed zero. Any such reuse SHALL
have a fixed bounded entry count, end with that attempt on normal or exceptional
exit, and never carry a result into another run, reset or replay. Uncertain
keys, custom numeric conversions, nonfinite values, failed preparations and
failed contact evaluations SHALL use the ordinary evaluator without caching a
failure or suppressing its original first error. Cache eviction SHALL affect
only work, never the returned 0/1 result or the Bound's sample/stop order.

#### Scenario: Paired bounds ask the same contact question twice
- **WHEN** one tick evaluates two existing numeric Bounds with bit-identical finite profile placements
- **THEN** a later call may reuse the earlier successful pair result without changing ordered contact results, Bound samples, bank, stop or replay

#### Scenario: Failed or custom evaluation cannot poison later samples
- **WHEN** an operand has a custom conversion, cannot be represented as finite binary64, or a placed edge collapses
- **THEN** the original numeric evaluation refuses or runs its conversion in the original order, and no partial cache entry can answer a later call

### Requirement: Reused large placed profiles avoid exhaustive disjoint-pair scans

Within one integration attempt, an eligible repeated pointwise contact over large finite profiles SHALL be able to prune polygon pairs whose placed AABBs are strictly disjoint without evaluating each pair's AABB individually. The pruning SHALL be conservative: it SHALL preserve complete left-then-right placement validation, the original polygon-order visitation of remaining SAT candidates, every returned positive `0.0` or `1.0` and first refusal, and the existing success-only bounded cache lifetime. It SHALL introduce no epsilon, omitted polygon, or caller-visible eligibility limit. Calls outside the eligible repeated-work path SHALL retain the ordinary evaluator's behavior and error order.

#### Scenario: Curta-sized repeated separated covers
- **WHEN** a 591-polygon profile is repeatedly tested against a successfully placed 159-polygon profile during one running integration attempt and their placed AABBs are strictly separated
- **THEN** contact remains positive `0.0`, and the repeated calls avoid an exhaustive 591-by-159 individual pair-AABB scan

#### Scenario: A late contact retains authored order
- **WHEN** a conservative index leaves several possible polygon pairs and the first contact occurs in a later authored pair
- **THEN** the result is positive `1.0` after visiting surviving candidates in the same left-then-right order as the ordinary predicate

#### Scenario: Earlier invalid placement or projection is never hidden
- **WHEN** a later polygon has invalid finite-placement geometry, or an earlier surviving pair's SAT projection becomes nonfinite before a later contact
- **THEN** the original first refusal occurs before any numerical result, and no failed or partial index is published for reuse

#### Scenario: Direct and uncertain evaluations remain ordinary
- **WHEN** a contact is called without an integration cache or with uncertain/custom placement keys
- **THEN** its conversions, validation, result and refusal order are unchanged, and no persistent spatial index is registered

#### Scenario: Skewed calls cannot force index construction
- **WHEN** a successfully cached right placement has many polygons but the left placement has only one or two polygons
- **THEN** repeated contact retains the ordinary evaluator's result and error order without building a spatial tree merely because the polygon-pair product is large
