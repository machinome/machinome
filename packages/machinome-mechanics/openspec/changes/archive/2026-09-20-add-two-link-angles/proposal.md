## Why

Spiderbot's `_solve` repeats planar shoulder-bearing and two triangle-angle
calculations; AlbertPro's `stance_angles` solves the same two-link reach with
an interior knee angle and compensating hip bearing. BiPed and ZeroBug also
repeat this law in their own leg frames. A common solver can replace the
geometry while leaving those projects' guards and actuator conventions intact.

## What Changes

- Add `two_link_angles(x, y, first_length, second_length, side=1)` returning
  absolute shoulder and relative elbow angles in degrees, numeric or deferred.
- Document the plane, branch, domain and project frame mappings; test forward
  closure, both branches, reach limits and evaluated deferred expressions.
- Use Sol agents to migrate and empirically validate at least two real
  consumers, preserving project-specific behavior and recording exclusions.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: a planar two-link inverse-kinematics formula with explicit branch.

## Impact

Independent mechanics package linkages module, flat exports, tests, user manual
and distribution smoke. Project migrations have independent commits and
evidence. No framework change, dependency addition, publication or general
robotics solver is included. Pilot waived per-cycle ratification; empirical
validation gates local integration.
