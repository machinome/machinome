# ADR-142: A Shared-Interior Witness Refuses an Empty Exact Common

**Status:** Accepted
**Date:** 2026-09-23
**Extends:** [ADR-073: The Comparison Kernel Is a Property of the Test Run](./ADR-073-the-comparison-kernel-is-a-property-of-the-test-run.md)
**Related to:** [ADR-092: Face Boxes Decide an Enclosed Pair Without a Boolean](./ADR-092-face-boxes-decide-an-enclosed-pair-without-a-boolean.md)

## Context

Curta Type I's unchanged positioning sphere, placed at its outer radial
position and shifted axially by either 0.2 mm, shares strictly positive
native interior with its frame. OCCT's common nevertheless returns a valid
empty shape. The project measured exact section edges and points classified
strictly inside both operands at zero tolerance, with positive distance to
both boundaries. A faceted common corroborates this but is not authority for
an exact verdict. See the
[archived change evidence](../../../openspec/changes/archive/2026-09-23-refuse-false-empty-exact-common/evidence.md)
for source hashes and coordinates.

## Decision

After an exact common reports no solids, use a bounded native section-edge
stencil and independently classify candidate points against each solid at
zero tolerance. A point strictly inside both operands contradicts the empty
Boolean; raise `ExactCommonInconsistency` and do not manufacture a volume.
If the section fails or a classifier reports an indeterminate state, raise
`ExactCommonVerificationError`. A normal classifier rejection is an OUT
result, not a failed classification. A completed finite search finding no
witness leaves the Boolean verdict unchanged; it is not a universal
certificate of emptiness.

The direct `machinome.exact.intersect_shapes` helper and the exact test
assertions share this rule. Correctly nonempty native commons, disjoint
solids, and zero-volume boundary contacts keep their existing treatment.
No mesh verdict or overlap tolerance is introduced. A refusal is not cached
as a successful clearance verdict.

## Alternatives

- Reparameterizing the sphere did not repair the Boolean consistently; a
  new coincident sphere instead yielded the entire sphere as common.
- Treating the positive faceted volume as an exact overlap would exchange
  one untrustworthy verdict for another and invent an exact volume.
- Accepting every empty common silently would retain the demonstrated false
  clearance. The finite witness guard is deliberately narrower than a
  general Boolean repair or proof of emptiness.

## Consequences

Exact comparisons near complex contacts can pay an additional section and
classification cost after an empty common. A witnessed inconsistency now
fails closed, so a project can repair geometry or record the kernel limit
without accidentally passing a clearance assertion. An unwitnessed OCCT
empty remains an OCCT empty, and tests must not claim that this guard finds
every Boolean defect.

## Amendment — 2026-09-23: Resolve the Interior Beyond Native Face Tolerance

The first implementation exposed a false witness on Curta Type I's nominal
planar carry-slider/guide contact. Both zero-tolerance classifiers returned
IN at a section-stencil point, yet that point was only 2.66 × 10⁻¹⁵ and
7.11 × 10⁻¹⁵ mm from the opposed planar faces, each with native tolerance
10⁻⁷ mm. A 10⁻⁷ mm probe to either side was OUT of one solid. This is
boundary roundoff, not a reliable shared-interior point.

The contradiction test therefore also requires the point's distance from
every face of each classified solid to exceed that face's own OCCT tolerance.
Unresolved candidates are skipped; failed or invalid native distance and
tolerance measurements refuse verification. This narrows only which points
can overturn an empty Boolean. It does not turn positive native volume into
clearance, introduce an overlap epsilon, or certify every unwitnessed empty.
The original Curta positioning-ball/frame ±0.2 mm witnesses remain far
beyond native face tolerance and still refuse their false-empty commons.
See [the archived correction evidence](../../../openspec/changes/archive/2026-09-23-require-resolved-exact-witness/evidence.md).
