# Planar two-link joint angles validation

## Package

Planning commit `ed004da97e8276469a1acc07753becacfda742b7`.
Tested uncommitted machinome_mechanics/linkages.py SHA-256:
`a9003c57561043e553cc2f6884e0221236b1fab94c422e354913aac2f08f53e9`.
Commands run from this worktree with `PYTHONPATH="$PWD"` and workspace Python.

- Red: `python -m pytest tests/test_two_link_angles.py -q` failed collection
  because `two_link_angles` did not exist, before implementation.
- Focused green: 19 passed. Full `python -m pytest -q`: 128 passed,
  24 subtests passed.
- Independent forward-kinematics tests cover four equal/unequal link pairs,
  seven bearings, four interior reaches and both branches, with explicit knee
  cross-product signs. Inner/outer tangent limits and invalid domains are
  tested. Real Solid2 expressions simultaneously defer x, y and both lengths
  for five samples on both sides, comparing numeric angles and forward closure.
- `python -m sphinx -q -b doctest -W --keep-going docs
  /tmp/mechanics-two-link-doctest`: 123 examples passed.
- `python -m sphinx -q -b html -n -W --keep-going docs
  /tmp/mechanics-two-link-html`: passed.
- `python scripts/check-dist`: wheel/sdist strict metadata and installed
  numeric/symbolic smoke passed outside checkout; nothing uploaded.
- `git diff --check` and `openspec validate --all --strict`: passed.

Dependencies observed clean at package checks: framework
`8d2bd71171be81f13ba5dd492851ed8b3a9ababb`, viewer
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f`.

Independent Sol review reran all 19 tests and found no substantive issue.
Its additional 528 near-tangent/quadrant samples found no wrong knee side;
maximum link-circle error 4.27e-14 length units. Endpoint error grew to
2.55e-8 near deliberately ill-conditioned tangency for the 80/121 pair.
This is the documented acos conditioning, not a reason to invent a clamp.

## Consumer preflight

Spiderbot and AlbertPro have direct mappings. ZeroBug retains atan(span/down)
by passing (distance,0) and maps the relative elbow to `-elbow-90`; the Sol
audit caught the sign before implementation. Its legacy coxa atan quotient,
negative-elevation convention and absent firmware reach guard remain unchanged.

YouCanBuildBiPed is not migrated in this cycle. Its equal-link solver defines
the arbitrary origin answer (90,-90), including through deferred evaluation;
the general nonzero-distance solver divides by zero there. Numeric-only origin
handling would not preserve the deferred behavior, and adding conditional pose
logic solely to force this consumer is unnecessary. Its original source remains
at main `8941bda36cf975eebc486ae31c2df750a6126d18`.

## Consumer validation

Consumer reviews follow. No archive or integration claim yet.

### AlbertPro

- Original main `2b79b82ac1748f3d50e8a8a85329bb556e1c2e9e`;
  migration `692c77a9fa317534d100ccde55cde280ac05b275`.
- stance_angles delegates (height,0,THIGH,SHIN) after the unchanged numeric
  guard, tolerance and exception message. Joint limits, clamps, frame mappings
  and foot_position are untouched.
- Parent reviewed the source, complete docs/mechanics-two-link-angles.md and
  independent scripts/check-two-link-angles, and reran it successfully. The
  old atan2 compensation and new triangle solution agree within 1e-10 degrees
  at 201 dense heights plus bounds/accepted tolerance neighborhoods. Rejection
  outside the guard and foot closure pass; actual deferred height evaluation
  matches six representative samples.
- Root faceted 35/35 and exact 35/35, build passed. Sol and parent inspected
  _build/two-link-angles-driven.png at height75/travel0.6. Visible joints and
  links are coherent; the chassis obscures much of the far pair. Image wording
  was narrowed after parent review: all-leg evidence comes from the suites,
  not an occluded overview. RL training and ESP32 firmware were not rerun.
- Dependency heads stayed clean/stable at 8d2bd71/4355da1. No helper issue.

### ZeroBug

- Original main `8135aa03b40f84eb5761e66236b77f020506e564`;
  migration `cdcb2960ef5ab55e66320ea76c1df3310046cdef`.
- The two inverse-cosine triangles are replaced by helper(distance,0,F,T).
  Project elevation/yaw quotients, coordinate transforms and servo mappings
  remain unchanged; returned tibia is -elbow-90, not elbow+90.
- Parent reviewed source, complete docs/two-link-angles.md and asserting
  scripts/check-two-link-angles, and reran it. Independent old/new numeric
  maximum difference 1.422e-14 degrees covers all six default legs, three
  six-leg control states, near-inner/outer valid reaches and negative-down
  behavior. Unreachable and both quotient-singular cases preserve exception
  types. Actual world_to_body/solve_leg Solid2 expressions evaluated by
  OpenSCAD at five samples differ <=4.005e-5 degrees, limited by echo precision
  (the probe acceptance bound is 1e-3 degrees).
- Faceted/exact leg each 6/6; faceted/exact root each 10/10; source-layout
  pytest 3/3; build passes. Sol and parent inspected the fresh driven
  _build/two-link-angles-driven.png: tilted body and visible articulated leg
  stacks remain coherent, gripper attached. This is rigid kinematics evidence,
  not balance, ground reaction, loading or gait-stability certification.
- Framework/viewer clean and stable at 8d2bd71/4355da1. Initial exploratory
  world-space input omitted world_to_body and hit a domain error; the durable
  probe uses the real frame conversion. No helper or baseline failure found.

### Spiderbot review finding

The first saved probe reproduced the helper adapter in a local test function
instead of calling Chassis._solve. It proved the planar formula with project
lengths but not the real adapter path. Parent requested actual-solver numeric
and deferred comparisons before accepting integration. This is resolved in
the final migration below; no production adjustment was needed.

### Spiderbot

- Original main `b3031f9ba7edb3c16f2da9512868932af403008b`;
  final migration `8630bf93d375ef5d9d22597d44b4f8787b6d6118`.
- _solve supplies span/drop and measured lengths, then retains its tibia bend,
  coxa yaw, body transforms, target mapping and front-right wave additions.
- Parent reviewed final source, complete docs/two-link-angles-verification.md
  and docs/probes/two_link_angles.py, and reran it. In addition to five primitive
  numeric/deferred samples and explicit invalid reach, the final probe compares
  actual Chassis._solve with the reconstructed old solver for three poses times
  six stations (1e-10 degrees). Its real native Solid2 animation clock flows
  through actual _solve and matches five independently recomputed numeric
  samples (1e-9 degrees). Numeric-only set_state is not bypassed.
- Established root faceted suite 34/34, build of the explicitly named Spiderbot
  node passed. An earlier bare-module build was ambiguous because it contains
  two node classes; this was not a geometry failure. Exact solids were not
  certified by this faceted gate.
- Sol and parent inspected fresh _build/two-link-angles-driven-web.png at
  height110/reach180/stride40/gait_phase0.25/roll10. Visible assembled leg chains
  share the expected branch in a coherent tilted pose; exact ground contact and
  linkage closure come from the contracts, not an overview alone. Stable clean
  dependency heads 8d2bd71/4355da1. No helper issue.

## Completion

Three real consumer migrations are empirically validated; the BiPed exclusion
and the probe-review correction remain explicit. Main-spec synchronization and
strict validation precede archival and the implementation commit. Local merges
and post-merge checks are recorded in the next campaign ledger update. Nothing
was pushed or published.
