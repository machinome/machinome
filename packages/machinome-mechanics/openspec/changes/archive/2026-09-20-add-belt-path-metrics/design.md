## Context

Four printer timing modules duplicate spans, arcs and stations after the tangent
extraction; Thor duplicates a subset. Printers index arcs after each span, while
Thor's wraps are indexed by circle. Existing projects use numeric route geometry
and deferred motion; the package must also preserve deferred route geometry.

## Goals / Non-Goals

**Goals:** Measure a caller-ordered closed route once, retain explicit indexing
and tangent branch conventions, remove real repeated mechanics in consumers.

**Non-Goals:** Route discovery, self-intersection detection, tension, tooth
fitting, mesh generation, project dictionaries, a new result class or framework
mutation. No dimensional declaration face or arbitrary symbolic engine support.

## Decisions

- Parallel sequences `centres`, `radii`, optional `senses` avoid coupling to a
  project's circle schema. At least two entries and matching lengths are static
  structural requirements; geometry retains tangent helper domain behavior.
- Return an ordinary dict with tuple fields `spans`, `wrap_angles`,
  `arc_lengths`, `stations`, plus scalar `length`. The first three are indexed
  by circle; stations are indexed by traversal element. This serves the actual
  printer adapters and Thor without a speculative public class.
- Share a private directed tangent primitive with `belt_tangent_points` to
  retain its unit normal even at zero radius or zero-length span; do not
  normalize a zero segment or divide by a zero radius. Span length is the
  tangent discriminant's square root; direction is `(normal_y, -normal_x)`.
- Wrap is the clockwise/counterclockwise arrival-to-departure angular difference
  reduced to [0,360) with `a - 360*floor(a/360)`. `machinome.math.wrap` is signed
  (-180,180], so it is deliberately not used. Degrees convert to arc length
  using pi/180. No numeric branching over deferred operands.
- Coincident tangent directions mean zero wrap, not a full turn. Thor's legacy
  full-turn choice, if retained during migration, is a numeric adapter policy,
  not a speculative helper flag. Printer arcs rotate circle-indexed lengths
  by one position to preserve their existing after-span indexing.

## Risks / Trade-offs

- Angular seam rounding → explicit collinear/zero-radius/limiting-span tests
  and independent legacy route comparisons; report discrepancies before merge.
- Private tangent refactor affects a settled helper → rerun all tangent tests.
- Existing CAD failures can hide regressions → compare targeted pre/post
  contracts and name known failures; inspect images as well as scalar probes.
- Kossel's known axis-projection bug remains outside this equivalent extraction.

## Migration Plan

Commit the plan, prove missing API red, implement and test. Sol consumer agents
own disjoint project branches, keep public wrappers and guards, commit evidence.
Review their reports and images; sync, archive, locally integrate only after
two or more distinct consumers pass. Skip a blocked cycle unarchived. No push.

## Open Questions

Thor adapter feasibility is being checked against its actual and degenerate
routes. It is not required to manufacture a second consumer; four printers
already use the complete measurement operation.
