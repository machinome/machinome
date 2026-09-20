## Context

CycloidalDrive layout records a measured 20-lobe disk and 21-pin fixed ring;
both its main and visual-only assemblies repeat three -1/20 spin bindings.
Its positive reduction magnitude also controls a 7200-degree instruction and
must not become the signed coefficient. OpenCycloid repeats the same spin
coefficient for two disks, output carrier and standalone output stage, while
its pure-translation eccentric orbits remain one-to-one.

## Goals / Non-Goals

Goals: share a signed fixed-ring cycloidal angular ratio with explicit lobe
and fixed-pin counts; preserve existing frames, phases, orbits and controls.
Non-goals: positive reduction inverse API, rotating-ring trains, profiles,
output-pin layouts, tooth compatibility, backlash, contact or torque models.

## Decisions

`cycloidal_ratio(lobes, pins)` belongs in gears and the flat export. Return
`-(pins-lobes)/lobes`, not a floored positive reduction or a phased angle.
The fixed ring is stationary, the input is the eccentric carrier, and disk
attitude/output increments use the same positive axis as the input. The
relative mesh identity is lobes*(output-input) = pins*(0-input). For 20/21,
one input revolution gives -18 degrees. A rest angle is caller-owned.

Physical use assumes positive integer lobes and more fixed pins than lobes;
ordinary arithmetic is not coerced, rounded or guarded. Zero numeric lobes
raise division errors; equal counts yield zero algebraically, not a validated
physical reducer. Supported raw deferred operands use identical arithmetic.
This follows existing helper conventions, rather than inventing a parameter
validation policy absent from both consumers.

CycloidalDrive uses one project-owned signed constant at all six bindings.
Its existing positive REDUCTION_RATIO and independent expected-angle oracles
remain unchanged. OpenCycloid names the explicit source lobe count alongside
FIXED_PIN_COUNT and shares one signed constant among its four bindings. The
21 fixed pins are not its six output pins. Both projects retain mounting
phases and +1 orbit laws. No reusable mechanism classes or new dependencies
are introduced in this package.

## Risks / Trade-offs

- Ratio vs inverse magnitude or a double negation → pin -18 degrees per turn
  and compare old/new actual state over signed and multi-turn inputs.
- Confusing disk attitude and eccentric orbit → retain +1 orbit bindings and
  verify independent center/centroid evidence, not scalar equality alone.
- Inferring lobe count from the desired ratio → preserve CycloidalDrive's
  existing measured count and independently inspect OpenCycloid's source mesh.
- Source geometry limitations → retain existing overlap inventories and
  omitted-sleeve limitations; no engagement certification is implied.
- Resource use → sequential cgroup-bounded CAD at 768 MiB, no swap, 300 seconds;
  no unbounded graph expansion, duplicate heavy checks or silently raised caps.

## Migration Plan

Commit validated planning, prove missing-helper tests red, implement one
formula and docs/distribution smoke, then use Sol consumer branches. Check
existing dependency manifests (do not invent packaging for tool-only projects).
Keep independent probes and original test oracles. Review bounded CAD/build
logs and fresh images, sync/compare baseline, archive, commit and fast-forward
unchanged original branches. Keep branches, remove only clean worktrees; no
push, publication, shared installation changes or framework mutation.

## Open Questions

No API question remains. OpenCycloid's pinned stage-one STL was inspected by
a bounded read-only mesh probe: its outer radial envelope has dominant
harmonic 20 and 20 separated outer maxima about the recorded center (0,-2.5).
The consumer record will retain the probe and its internal-hole/interpolation
limitations; this is count evidence, not a new watertightness/contact claim.
