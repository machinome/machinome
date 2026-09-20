## Context

This independent package carries pure degree-based formulas over machinome.math.
Spiderbot's simulation/spiderbot.py `_solve` already composes atan2 and two
triangle_angle calls. AlbertPro's simulation/layout.py `stance_angles` uses
acos for the relative knee and atan2 of the rotated shin for the hip. Both
are real, clean project consumers with existing forward-closure contracts.

## Goals / Non-Goals

Goals: one shared planar reach law, explicitly selected knee branch, common
numeric/deferred arithmetic and empirical preservation of at least two projects.
Non-goals: yaw, robot coordinates, servo zeros, gait, joint limits, reach
clamping, dynamic branch tracking, or a declared-dimensional formula face.

## Decisions

Signature: `two_link_angles(x, y, first_length, second_length, side=1)`.
The fixed pivot is (0,0); target and positive link lengths use one length unit.
Return `(shoulder, elbow)` in degrees: shoulder absolute from +X toward +Y,
elbow relative to the first link, so second absolute bearing is their sum.
Let d=sqrt(x*x+y*y). Compose existing triangle_angle:

    shoulder = atan2(y,x) + side*triangle_angle(second_length,first_length,d)
    elbow = side*(triangle_angle(d,first_length,second_length)-180)

Side +1 selects a knee left of pivot-to-target, -1 right, matching the existing
circle_intersection convention. Side is caller-authored literal ±1, not
normalized or validated. The alternative of returning two absolute angles
would require most articulated consumers to subtract them again. The alternate
atan2-based shoulder compensator is equivalent for valid positive links, but
the triangle formulation is already the exact Spiderbot seam and its branch
is explicit. No singular-pose convention is invented: d=0 divides by zero,
unreachable acos arguments propagate the existing math domain behavior.

Mappings: Spiderbot passes (span,drop,FEMUR_LENGTH,TIBIA_REACH) and subtracts
its measured TIBIA_BEND from the returned elbow. AlbertPro passes
(height,0,THIGH,SHIN), after its existing UnreachableHeight guard. BiPed's
equal links and ZeroBug's firmware quadrants are additional candidates,
not required consumers: audit their origin/atan conventions before migrating.

## Risks / Trade-offs

- Equivalent acos/atan2 calculations differ near singularities → compare
  independent old formulas at dense valid samples and project range endpoints;
  require forward closure and actual evaluated deferred-expression parity.
- Project offsets can conceal a branch/sign error → preserve adapter code,
  run affected CAD contracts, build and inspect fresh driven images.
- Zero-distance BiPed pose has an old arbitrary finite answer; ZeroBug uses
  atan of a quotient → preserve in the caller or exclude that migration,
  never alter the shared geometry to manufacture coverage.

## Migration Plan

Commit planning, prove missing helper red, implement and pass package/docs/dist
checks, then use Sol agents for separate project branches and evidence. Review
their commits and issues before sync/archive and local fast-forward merges.
Do not repoint shared editable installs; use explicit worktree PYTHONPATH.
Retain clean branches for recovery. No push, publication or package release.

## Open Questions

No interface choice is outstanding. Additional candidate eligibility is an
empirical check, not a requirement to force every solver into this API.
