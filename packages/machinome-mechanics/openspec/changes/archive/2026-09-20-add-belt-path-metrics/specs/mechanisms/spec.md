## ADDED Requirements

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
