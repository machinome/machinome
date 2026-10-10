# ADR-154: A Mate May Reference an Existing Child Joint

**Status:** Accepted
**Date:** 2026-09-27
**Ratified:** The pilot explicitly ratified the existing-child-joint reference design before its proposal and implementation.
**Amends:** ADR-147 — a moving mate need not install a fresh joint or own an assembly coordinate
**Extends:** ADR-153 — referenced-joint handles resolve to the original physical endpoint in every reference context
**Preserves:** ADR-088, ADR-093, ADR-097, ADR-098, ADR-105, ADR-121 — joint ownership, order, declarer scope, site arguments, binding and retained laws
**OpenSpec change:** [mate-existing-child-joint](../../../openspec/changes/archive/2026-09-27-mate-existing-child-joint/)

## Context

Curta-Type-I-3x's seventeen register dials already have named site joints,
guarded defaults, retained clearing laws and published `child.turn` identities.
Fresh-freedom mates would install a second joint under the mate's name and
require rewriting those contracts. The project needs frames to state where
the existing dials attach, not another degree of freedom or a string-based
joint-name override.

## Decision

`ones_mount = ones.axle.on(ones_seat, ones.turn)` attaches the same direct
moving child and references its explicit scalar Revolute or Prismatic.
The frames supply the existing mate rest placement. The original class or
site joint is neither specialized, replaced, renamed nor reordered; its
geometric frame, argument vocabulary, factory timing/receiver, Bound scope,
unit, original wiring and guarded default remain unchanged.

The named mate is a reference handle, not an assembly-owned coordinate.
Instance reads return the original child's BoundPort and writes invoke its
original binder. Relations, derived formulas, wiring sources, Bounds,
additive constraints and explicit controls resolve to the same child endpoint.
The handle introduces no bank entry, wiring edge, document address or format.
Fresh-freedom mates retain their assembly-port semantics; rigid mates remain
non-coordinate attachments.

Canonical identity detects mixed handle/child self laws, duplicate writers,
grouped aliases and Bound aliases. Written ownership is checked before
resolution. Derived formulas retain separate written reused-reference
provenance through scaling, flattening and cancellation: canonical term
merging cannot erase a foreign declaration, even when child declarations are
shared exactly. Ordinary formulas retain their original direct dictionary
merge and do not traverse alias-comparison keys.

The freedom must be an explicit joint path of the same direct moving child.
Bare declarations, strings, nodes, deeper/foreign paths, ports, derived
coordinates, Orbit, Free, components and broadcasts are refused. Existing
frame, fixed-end, loop, render-placement and inheritance restrictions remain.
This does not broaden replacement of a mated child under inheritance.

## Consequences and evidence

One original joint remains authoritative. No duplicated coordinate bank or
new runtime solver is required. Class/site factory-scope traps, noncommuting
poses, separate instances, aliases, running retained self laws, clocked
state-driven readout, replay, explicit controls and foreign provenance are
executable tests. A seventeen-dial fixture compares independent ordinary
placement, complete poses, original ids and retained histories.

Root-owned real Curta adoption and Studio API follow-through are recorded in
the change evidence. Caller geometry remains a separate gate: the discovered
adapter/base artifact-name/source-time collision also reproduces on unchanged
framework main and is not repaired or silently included in this decision.
