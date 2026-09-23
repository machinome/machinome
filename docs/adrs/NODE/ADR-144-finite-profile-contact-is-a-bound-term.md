# ADR-144: Finite profile contact is a term in an existing Bound

**Status:** Accepted

**Date:** 2026-09-23

**Change:** [convex-profile-contact-predicate](../../../openspec/changes/archive/2026-09-23-convex-profile-contact-predicate/)

**Depends on:** ADR-108, ADR-109, ADR-113, ADR-124, ADR-138 and ADR-141.
Preserves their running Bound, path sampling and Follow meanings.

## Context

The Curta Type I reverser trial already selects absolute axial stopping planes
with numeric running Bounds. Its missing angular input is a 0/1 contact flag
between the pinion and drum's finite planar covers. Expanding every convex
polygon pair into scalar expression nodes would require 633,552 pairs for
one pinion/nine-tooth drum combination; the bounded 256-pair diagnostic
already constructed 49,833 graph nodes. A browser cannot import CAD, and a
new contact solver would change proven Bound admission semantics without an
originating need.

## Decision

`ConvexProfile` owns an ordered sequence of independently supplied finite
convex CCW loops. Exact binary-coordinate validation rejects malformed,
crossing or concave loops without repairing them. The pointwise
`profile_overlap` rotates and translates two such values in XY and returns
positive `1.0` on inclusive AABB/SAT contact, otherwise positive `0.0`.
Invalid transformed geometry refuses. No tolerance or continuous-path claim
is attached to this authored data.

Only a **symbolic running Bound** may contain the compact profile operation.
Its result remains a numeric term in the Bound's existing absolute coordinate
limit; the 64-sample/bisection stop search, held-own rule and attribution do
not change. A plain numeric call remains available for independent probes
and numeric bind-time evaluation. Unsupported symbolic pose, law and clocked
paths refuse the new operation by name.

The running program owns and deduplicates the complete immutable profile
data. Version 13 publishes it once as `program.profiles` and leaves small
`profileOverlap(index,index,angle,tx,ty,angle,tx,ty)` calls in the existing
bound-expression field. Full profile content participates in program identity
so stale snapshots refuse. A program without the operation retains its prior
document version, bytes and identity; an older viewer refuses version 13.
The separate viewer must implement the same finite validation and ordered
pointwise arithmetic before portability is claimed.

One integration attempt may reuse only successful complete placed profiles
and pair decisions under exact finite builtin IEEE-bit keys and immutable
profile-object identity. Private 256-placement/1,024-pair LRU scopes end on
every normal or exceptional attempt; uncertain inputs and errors bypass or
publish nothing. This changes repeated work only, not a Bound sample or
contact answer.

## Alternatives and consequences

Direct symbolic SAT made the scalar graph impractically large. A new span or
constraint kind would alter the meaning of a Bound that already serves the
Curta trial. A CAD/native callback in the viewer would breach its separate
runtime boundary. An epsilon or mesh-volume fallback would change strict
contact. The chosen finite pointwise predicate leaves sampling gaps and
geometry-cover proof to the project; it does **not** certify installed-part
contact or admit the current Curta production law. Caching consumes bounded
per-attempt entries but not a fixed universal byte budget because authored
profile size is not truncated; the archived change records the measured
Curta cost and memory tradeoff.
