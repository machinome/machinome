## Context

The three printer repositories already use rolling_angle but still assemble
the same contact-referenced pulley phase locally. Prusa subtracts a pulley
station from a clamp anchor; Kossel's pulley contact is at station zero;
Metamaquina2 Y uses a nonzero global station and counterclockwise contact.

## Goals / Non-Goals

**Goals:** Carry the common no-slip phase relationship, consistent with belt
tangent/path senses, without wrapping away revolutions or erasing tooth phase.

**Non-Goals:** Contact finding, radius fitting, tooth/groove offsets, drive
coupling objects, routing, dynamic slip, machine-axis transforms or fixing
unrelated project bugs. No new result class or general declared-token face.

## Decisions

- `belt_pulley_angle(belt_position, pitch_radius, contact_angle,
  contact_station=0.0, sense=1)` returns `contact_angle - sense *
  rolling_angle(belt_position - contact_station, pitch_radius)`.
- Belt position and contact station share an oriented arc-length coordinate.
  At equality the returned angle is the supplied contact angle, measured from
  +X counterclockwise about +Z. Sense +1 means clockwise belt traversal, -1
  counterclockwise, exactly as the path/tangent helpers. The contact angle is
  required because all real callers have a measured reference; station defaults
  to zero because Kossel and Metamaquina2 X depart the first circle there.
- A scalar law, not a circle object/machine adapter, keeps caller-owned belt
  dictionaries, clamp offsets and measured frames outside the package. Metamaquina
  Y supplies its global clamp station plus local anchor; callers retain their
  existing phase normalization and own tooth reference.
- Reuse rolling_angle instead of a second radians/degrees conversion. Physical
  radius is positive, but signed radius keeps arithmetic and zero radius its
  existing division error. Supported deferred operands use the same formula.
- Kossel's motion law must remain an invertible Affine; migrate its constant
  offset where appropriate without replacing the coupling or numeric policy.

## Risks / Trade-offs

- Station-origin confusion → nonzero-station and coordinate-shift invariance
  tests plus actual Prusa and Meta Y comparisons.
- CW/CCW confused with machine mounting handedness → test both senses and leave
  the existing outer frame signs in the project.
- Large unwrapped Kossel angles → scale-aware floating tolerance, preserve its
  documented anchor-axis bug rather than hide it with angular modulo.
- Historical Meta browser-expression workaround → preserve its chosen numeric
  phase and evaluate real deferred expressions, not just Python numeric poses.

## Migration Plan

Commit plan, observe missing API red, implement/test/document. Sol agents own
separate project branches and evidence. Review pre/post laws, CAD and images;
resolve issues, sync/archive then locally integrate and verify before next helper.
Skip blocked work unarchived. No push/publication. No open design questions.
