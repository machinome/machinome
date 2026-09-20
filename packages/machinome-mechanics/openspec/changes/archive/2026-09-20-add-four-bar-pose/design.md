## Context

Dragon R1 `simulation/suspension.py:_four_bar_geometry` calculates the lower
endpoint, closes the upper arm against the upright, then uses two absolute
bearings to rotate source parts. Strandbeest `strandbeest/kinematics.py:leg_points`
closes O-C-W-H and O-C-U-H loops before constructing its remaining triangles.
Both were re-inspected this cycle; each has numeric, geometry and motion gates.

## Goals / Non-Goals

Goals: share driven crank endpoint, selected closure and output bearings;
retain degree/deferred parity and source frame conventions in both projects.
Non-goals: ride inversion, gait, mounting offsets, 3D pivots, dynamic branch
tracking, Grashof classification, toleranced fitting or reach clamping.

## Decisions

Signature: `four_bar_pose(angle, crank_pivot, rocker_pivot, crank_length,
coupler_length, rocker_length, side=1)`. Fixed points are A=crank_pivot and
D=rocker_pivot. Moving B=A+crank_length*(cos(angle),sin(angle)). Let v=B-D,
d=|v|. Rocker bearing is atan2(v.y,v.x) plus
side*triangle_angle(coupler_length,rocker_length,d). Then
C=D+rocker_length*(cos(rocker_bearing),sin(rocker_bearing)); coupler bearing
is atan2(C.y-B.y,C.x-B.x).

Return an ordinary dict with exactly `crank_end` (B), `rocker_end` (C),
`rocker_angle` and `coupler_angle`. No redundant copy of input angle, pivots or
lengths. All angles are absolute in the caller plane (+X toward +Y, +Z normal).
Side+1 is left of D→B, -1 right, matching existing circle_intersection.

The point-only alternative would make Dragon repeat bearing mechanics. The
circle-intersection-plus-atan2 alternative normalizes the rocker bearing and
can change source rotations by 360 degrees. Preserve the constructed rocker
angle instead; coupler angle retains atan2's principal representation. Neither
is a continuous-unwrapping promise. Triangle arithmetic uses existing math;
no CAD geometry, registry, object dependencies or external source code is copied.

Dragon keeps ride→lower_angle, then passes source_lower_heading-lower_angle
(positive +Y rotation is clockwise in its XZ projection), measured lengths,
lower/upper inner pivots and closure_branch. Source rocker/upright bearings
minus helper output bearings give existing part rotations. Y offsets, reflected
Z adapters, -ride mappings and SuspensionPose remain local.

Strand uses (angle,O,H,15s,50s,41.5s,+1) for W and
(angle,O,H,15s,61.9s,39.3s,-1) for U. It retains its scale guard, other three
intersection calls and guarded local intersection function. Its branch mutation
must target the new W call, not silently lose coverage.

## Risks / Trade-offs

- Angle normalization and rotation signs → assert all old/new Dragon pose fields
  through dense normal/handed sweeps and actual deferred ride evaluation.
- Different trig algebra changes tiny point rounding → compare independently
  reconstructed legacy Strand points over complete turns and tested scales;
  run closure, mutation and affected whole-machine gates with honest tolerances.
- Tangent/invalid geometry has conditioning/domain limits → test both branches
  and failure paths; propagate errors, no fabricated pose.
- Existing physical limits → preserve Dragon's mechanism ±4 mm and installed
  car ±2 mm claims; Strand walking stays prescribed, not stability certification.

## Migration Plan

Planning commit, red-first implementation and package/docs/distribution gates,
then Sol-owned project branches with durable independent probes, CAD, builds
and fresh inspected images. Use explicit worktree PYTHONPATH, not shared
install changes. Review before sync/archive and local fast-forward integration;
retain branches. No push or publication.

Consumers with package metadata declare machinome-mechanics when introducing
their first import. Strand's isolated mutation subprocess retains the caller's
explicit source overlay, ensuring its failing branch contract exercises this
cycle's implementation rather than the previously installed helper set.

## Open Questions

No interface question remains; both independent preflights confirmed the seam.
