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

## Amendment — 2026-10-07: A Witness Is Interior in Its Neighbourhood

OpenAstroMount's scenario test was refused at its Target pose for the polar
frame's F206 bearing housing and the right ascension body's UC206 insert,
two valid vendor STEP solids that meet on two concentric spheres of radius
31.000 mm: a contact of zero volume at every right ascension angle, for
which OCCT's empty common is right. The witness lay 0.0999563 mm from the
housing's nearest face and 0.135651 mm from the insert's, against face
tolerances of 10⁻⁷ mm, so the first amendment's test accepted it; yet it lay
31.135651 mm from the spheres' centre, outside the insert. The insert's
zero-tolerance classifier answered IN at that one point and OUT at its
neighbours 10⁻⁴ mm away, a ball of radius 0.01 mm there had no common with
the insert, and 40,000 samples found no point inside both. The face
tolerance test filters a classifier that rounds a point on a face; it does
not filter one that is wrong away from every face.

A candidate's smallest distance to the faces of a solid, its margin, bounds
a ball that no face of that solid enters, so every point of the ball has the
candidate's true state. A candidate resolved in both solids therefore
counts as a witness only when its six neighbours along ±x, ±y and ±z, at
half the smaller of its two margins, are also classified IN at zero
tolerance by the same two solids' classifiers. A candidate whose neighbours
are not all IN is skipped and the finite search continues, as an unresolved
candidate already is; a neighbour classified UNKNOWN refuses verification.
This narrows once more only which points can overturn an empty Boolean. It
adds no tolerance, mesh verdict, volume or second Boolean, leaves the
stencil and its budget unchanged, and certifies no unwitnessed empty.
The Curta positioning-ball/frame ±0.2 mm pairs are still refused at the same
witnesses, whose six neighbours are IN both solids, and so are the two
hand-measured witnesses of 23 September. Voron-2's thread-seat refusals,
whose independent 0.01 mm balls are inside both operands, were not re-run.
See [the archived neighbourhood evidence](../../../openspec/changes/archive/2026-10-07-a-witness-is-interior-in-its-neighbourhood/evidence.md).

## Amendment — 2026-10-09: No Classifier Verdict on an Inside-Out Operand

OCCT's solid classifier decides inside from the face orientations, so a
solid published with its faces pointing inward, whose signed volume is
negative, reads every point as inside it. Thor keeps two such parts as
published, because that is the orientation whose Booleans are right, and
13 of its 22 refused pairs were this guard finding "a point inside both"
at the first candidate inside the other part, with neighbours agreeing.
After an empty common, the engine now tests each operand's solids by signed
volume before any classifier is built; an inside-out operand is refused as
`BrepCommonVerificationError` naming that operand and its signed volume,
with no shared point claimed. The containment guard of ADR-092 declines for
such an operand without loading a classifier, so the Boolean decides the
pair as before. The common, the fusion and the volume of an inside-out
operand are computed exactly as before; nothing repairs or reorients it.
See [the archived change](../../../openspec/changes/archive/2026-10-09-an-inside-out-operand-is-refused-by-name/proposal.md).

## Amendment — 2026-10-09: A Point's Side Is Read From Its Nearest Boundary Before a Slower Classifier

Wall clock 02's weight shell and the screw it carries touch, and their
empty common is right. The search ran to the end of its stencil, 1,872
points, asking the shell's classifier first at each and the screw's for
the points inside the shell: 2,547 classifications and 324 s, with no
candidate. The shell is a valid 32-face solid whose classifier answers in
0.6 ms at its centre and in 190–300 ms at every stencil point near the
screw; the screw's, 5 faces, answers in under 0.1 ms. On a touching pair
no stencil point is inside both, so the search's cost is whatever the
slower classifier costs to say so.

The search now asks first the classifiers of the operand whose solids
have fewer faces, the first operand on a tie. For a point inside it, and
before any classifier of the other operand is asked, the point's side of
each solid of both operands is read from that solid's nearest boundary
point. That point is found face by face. Each face has a lower bound on
its distance from the point: the larger of the point's distance to the
face's box (`face_bounds`'s box, the surface's own extent plus its
tolerance) and, for a face lying in a plane or a cylinder, the point's
distance to that surface less the face's largest native tolerance, since
the face's edges and vertices may stand that far off it. The faces are
visited in ascending bound, each by one extrema from the point to that
face alone, never to the solid, against which the extrema classifies the
point at a classifier's cost; the visit stops at the first bound not below
the nearest distance found, since no face left can come closer. The
nearest face's extrema gives the distance `d`, the nearest point `q` and
its support, and the support gives the side: with `q` inside a face, the
face's outward normal, taken from the face as the solid holds it so the
solid's and the shell's orientations compose; with `q` inside an edge that
two faces meet, or a seam's face meets twice, the sum of the two outward
normals; within a face's native tolerance there the point is on the
boundary. A vertex, any other edge, a sign near a tangent direction or a
failed measurement leaves the side undecided. A solid the point reads
outside, or on the boundary of, holds no candidate there, and a point no
solid of an operand can hold is skipped without the other operand's
classifiers. Everything else is classified, measured and corroborated as
before.

The reading is sound for the reason the 2026-10-07 amendment gives: the
open ball of radius `d` about the point `p` meets no face, so all of it
has `p`'s state. With `q` inside a face the ball is tangent to the face at
`q`, and `p` lies on the side of the face its offset `p − q` points to,
along the normal. With `q` inside an edge, `p − q` lies in the
cone both faces leave free: spanned by the two outward normals at a convex
edge, which is outside, and by their opposites at a concave edge, which is
inside; at a tangent edge or a seam the normals agree. In each case the
sign of `(p − q)·(n1 + n2)` is the side. A point within a face's tolerance
is one the margin test already rejects, so reading it on the boundary
excludes nothing that could count. A bound never passes over the face that
holds the true nearest point, so the face-by-face search reads what one
extrema against the whole boundary would read.

A side reading never makes a point count: a witness is still a point
classified inside a solid of each operand at zero tolerance, resolved
beyond every face tolerance, whose six neighbours are classified inside
both. The order changes which classifier is asked at a point outside one
operand, and so where an UNKNOWN can refuse; the side reading spares only
classifications whose answer could not make a witness. Its one new way to
miss a false empty is an extrema that misplaces the nearest boundary
point at a genuine witness, the instrument the margin already trusts.

On the captured shell and screw the search asks the screw's classifier at
each of the 1,872 points and the shell's at none, in 0.5 s in either
order. Measured cold on both projects' suites against the 9 October
records, each class of empty common costs less witness time. On wall clock
02: at zero distance 582.9 s to 421.9 s, under a micrometre 47.2 s to
2.4 s, at positive distance 317.8 s to 301.8 s, all commons 948.0 s to
726.1 s. On the combination safe lock: 16.9 s to 13.7 s, 23.7 s to
20.3 s, 89.6 s to 89.1 s, with no pair group grown by half a second. The
clock's three pathological groups settle: the weight shell and its screw
297.8 s to 0.48 s, the collet and the beat screw 43.7 s to 1.38 s, the
shell and its nut 41.2 s to 0.22 s. Overlapping boxes, a 0.4 mm slab, a
pin 0.2 mm over its hole and a key 0.1 mm into its slot are refused at the
same point with the side readings as with every side undecided, and
Voron-2's twelve thread-seat refusals, six pairs in both orders, are made
at the points they were made at before. The stencil, its budget and its
order, the section, the errors and their messages are unchanged; the
shallow-dent blind spot is untouched.

The instrument has a known cost. Where the contact is a flat gear side,
a plane bounded by about two hundred edges, that face is genuinely the
nearest at most stencil points, so no lower bound can pass over it, and
one extrema to it costs 4.1–4.4 ms against 0.9 ms for a healthy
classifier of the same part. On the clock the arbor and the hour holder
grow from 119.0 s to 266.8 s and the cannon pinion and the hour holder
from 57.2 s to 134.5 s, about 2.3× each in process; a project whose
touching pairs are mostly such contacts, with healthy classifiers, would
see its witness time grow by up to that factor. Classifying the point's
projection in the plane's parameter space, the one cheaper route
measured, costs about what the healthy classifier costs and still needs
the extrema where the projection falls off the face; a cheaper reading of
a planar face is left to a finding that needs it. Nor is a slow
classifier on the operand with fewer faces helped: on OpenAstroMount's
bearing seat the insert (84 faces) classifies a point in 18–26 ms against
the housing's (110 faces) 4–6 ms, and is now asked at every stencil point,
so with the housing given first the witness grows from 34.6 s to 54.1 s;
the empty common is returned as before. Two searches were measured on the
way and not kept: one extrema against all of a solid's shells, at 8.4 ms
a reading on a 218-face gear part, which grew the clock's zero-distance
empties to 810.3 s; and the faces' boxes alone, which hold every stencil
point near a gear placed off the axes, since a tilted disc's box is a
slab.

The Curta positioning-ball/frame ±0.2 mm pairs were not re-run; by the
ball argument their witnesses read inside or undecided in both solids, so
their classifiers are asked as before, and their re-run under this
amendment is owed.
See [the archived change](../../../openspec/changes/archive/2026-10-09-witness-on-a-touching-pair/).
