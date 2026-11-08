# ADR-197: A state color is presentation on the existing body

**Status:** Accepted
**Date:** 2026-11-08
**Change:** [color-model-lamps](../../../openspec/changes/archive/2026-11-08-color-model-lamps/)
**Related:** ADR-034 (common node document), ADR-080 (shared expressions),
ADR-128 (clocked publication); viewer ADR-076/079 (material presentation).

## Context

Enigma I's 26 existing lamp glasses need the circuit observation to select
between the source-backed dark and lit colors. Numeric Python branching
selected those colors but ordinary symbolic publication refused its truth
request. Static color, independent markings and host highlights do not carry
that same-body state selection through the ordinary model document.

The coordinated cycle received advance completion authority and agent review;
this does not claim human review of finished artifact text or publication.
Its authored rigid fixtures confirmed numeric/symbolic parity, standard
export in all three execution modes, relation-fed list-held glass color
properties, native state restoration, shared predicates and unchanged mesh,
model path, piece identity and volume across color-only updates.

## Considered options

1. Select two validated fixed colors on the existing `color` attribute.
2. Introduce an appearance declaration/mutator family with retained state.
3. Publish arbitrary expression-valued RGB channels.
4. Add a separate lit body or host-driven highlight.

## Decision

Choose option 1. `machinome.color.color_when(condition, *, on, off)` returns
the selected hex for finite numeric zero/nonzero, or a private immutable
condition graph and two palettes for a supported symbolic scalar. It does
not read a port object, defer an author callback or add an appearance bank.
An authored color property can consume an explicitly referenced settled
signal during ordinary presentation, preserving the existing solver order.

The common serializer publishes exactly `{when, on, off}` and includes
`when` in the existing document-wide scalar binding pass. Any symbolic
choice selects document 14 ahead of the earlier mode/version ladder; the
existing `program` or `clocked` payload still determines execution kind,
with neither denoting posed content. Legacy documents retain their bytes
and versions. The paired reader advertises API 30 and versions 1–14; an
older reader refuses 14 before rendering.

Color remains presentation rather than a construction parameter or physical
law. Symbolic OpenSCAD presentation uses existing scalar arithmetic per RGB
channel. Numeric reset/restore/replay computes the same color from standing
state. Publication's existing restoration boundary now includes its initial
symbolic traversal, whose failure previously escaped that boundary; its
numeric replay suffices to restore colors without new object snapshots.

## Consequences

- Same bodies, geometry and physical assertions serve dark and lit states.
- Two explicit palettes make clearing deterministic; no last-lit history
  survives release, reset or restore.
- The wire adds no scalar operation, electrical behavior, emission or
  optical-brightness claim.
- Choice-bearing posed/clocked/running documents require a capable reader;
  format number alone no longer denotes running execution at version 14.
- Interpolated RGB, textures and a general material platform remain outside
  the evidenced requirement. Source capability is recorded as unreleased.
