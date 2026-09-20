## Context

Thor main c229b25322e3b899aa70349355dccd262fb8748b is clean. art1.py's
60/10 shoulder coefficient feeds four real motor/pinion bindings; all retain
their local mounting signs and source PHASES. OpenTorque master (not main)
59c51fda7f183b98682a65227b3d288e13941ad7 is clean. Its reducer.py binds
three orbits at input/8 and three child-local spins through the external
sun/planet ratio -18/54 applied to sun-minus-carrier.

The independent package remains a pure arithmetic library; no registry,
framework reverse dependency or ownership/axis change is needed.

## Goals / Non-Goals

Goals: one internal mesh relation serving moving-ring and moving-carrier cases,
with real production consumers and numeric/deferred parity.
Non-goals: generated teeth, automatic registration, inverse helper, backlash,
gear validity checks, flattening assemblies or replacing independent oracles.

## Decisions

`internal_mesh_angle(ring_angle, ring_teeth, pinion_teeth, carrier_angle=0.0)`
returns `carrier_angle + (ring_teeth/pinion_teeth)*(ring_angle-carrier_angle)`.
All angles are unwrapped degree increments from a caller-registered pose,
measured about the same positive axis in a common nonrotating frame. The
output is common-frame pinion increment; subtract carrier to obtain child-local
spin. Rest phases and placement signs stay outside. Unlike external
meshed_angle, this law does not perform tooth/gap registration.

Physical counts are positive integers with ring>pinion; arithmetic inputs are
not rounded/validated. Zero numeric pinion count divides by zero; negative,
fractional and equal counts retain algebraic behavior, not a geometry promise.
Pure ordinary arithmetic supports numeric and deferred operands without branches.

Thor computes the coefficient with helper(1,60,10), retaining all four signed
runtime bindings. OpenTorque replaces the three actual planet bindings with
orbit-to-local-spin law factories: helper(0,126,54,carrier)-carrier. Each orbit
remains driven by the sun at 1/8; each law binds its own orbit to its own child.
Keep the old kinematics.py external derivation and SUN_PLANET_MESH constant as
independent oracles. This uses the actual fixed-ring constraint, not an unused
utility migration. The law factory also avoids unsupported dimensional
class-body subtraction of literal zero from an Angle declaration.

Alternative merely changing OpenTorque's standalone absolute-angle utility
would not migrate runtime behavior and is rejected. Flattening carrier and
planet transforms would alter project ownership and is unnecessary.

## Risks / Trade-offs

- Absolute-vs-local confusion -> explicitly subtract carrier and test both frames.
- Rebinding stale state -> repeated set_state sequence and three actual laws.
- Lost mounting phases -> unchanged source transforms and signs, independent probes.
- Broad CAD cost -> serialize all CAD imports/checks in 768 MiB cgroups,
  zero swap, threads1, runtime <=300 seconds. Report failures without raising cap.
- Existing Thor overlap failures -> retain evidence, no unrelated repairs or weakened tests.

## Migration Plan

Commit planning; red-first package implementation/tests/manual/distributions;
Sol consumer migrations, focused numeric/deferred checks, bounded CAD/build and
fresh images; parent review; sync/compare, archive, implementation commit and
guarded local integration. No shared installs, pushes or publication. Focused
commits are independently revertible. Blocked helpers remain unarchived.

## Open Questions

No unresolved interface choice; empirical consumer findings gate completion.
