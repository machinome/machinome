## Context

Thor computes directed circle contacts with atan2+acos; printer timing modules
construct their unit normal algebraically. Both use positive physical radii
and opposite turn markers for belt-back idlers. The public mechanics boundary
is scalar/tuple arithmetic, not a dependency on project dictionaries or Molejo.

## Goals / Non-Goals

Share tangent contact geometry in numeric and deferred evaluation. Do not own
loop topology, wrap/station metrics, guards/messages in existing wrappers,
tooth fitting or force/contact simulation. Kossel's separate anchor-axis bug
remains outside scope.

## Decisions

The signature follows circle_intersection's centre/radius ordering. Return
`(point_a, point_b)`, each an XY pair. Explicit senses are +1 clockwise and
-1 counterclockwise along travel from A to B; equal senses give an outer
tangent, opposite senses an inner tangent. This avoids adopting either
project's turn-marker dialect and allows the reverse route by swapping circles
and negating both senses. No extra independent side argument is needed.

Derive the common normal n from `dot(n, B-A)=sa*ra-sb*rb` and `dot(n,n)=1`.
Let d=B-A, q=dot(d,d), r=sa*ra-sb*rb, h=sqrt(q-r*r).
Then `n=((d.x*r-d.y*h)/q, (d.y*r+d.x*h)/q)`.
Return A+sa*ra*n and B+sb*rb*n. This construction chooses the normal to the
left of A-to-B for equal signed radii. It uses ordinary arithmetic and
machinome.math.sqrt, independently expressing textbook constraints rather than
copying licensed project code.

Physical radii are nonnegative and senses must be literal +/-1 chosen by the
caller. No rounding, clamping, radius-sign validation or symbolic branching.
Distinct centers with q>=r*r are required. Impossible contacts raise the
numeric math domain error; coincident centers remain undefined by division.
At q=r*r the contacts coincide, a zero-length limit rather than a usable span.
Symbolic invalid inputs retain the math runtime's singular behavior.

## Risks / Trade-offs

- Senses differ between consumers → explicitly adapt each existing marker.
- Floating regrouping can affect fitted tooth geometry → compare contacts,
  spans, wraps and actual contracts, not just radii.
- Printers consume normals as well as points → keep local adapters narrow;
  deriving normals must not introduce a zero-radius/zero-span regression.
  Preserve any necessary existing degenerate-case handling in project wrappers.
- Overview images hide contacts → geometric identities and existing mesh
  contracts establish modeled contact; pixels establish visible poses only.

## Migration Plan

Red-first perpendicularity, radius, known-reference, reversed-traversal,
singularity and symbolic tests; then implement/docs/distribution checks.
Sol agents migrate Thor and printer consumers on isolated project branches,
record old/new independent results and helper source identity, run affected
contracts and inspect images. Review, sync, archive and locally integrate
before the next helper. Revert a focused consumer change to restore old
arithmetic. Skip unresolved helper blockers without archiving incomplete work.
