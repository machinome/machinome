## Context

Leonardo at 87b76494fe9509b82b72468e9448a2949c908d42 has a 240-degree
half-cosine rise and separate 80-degree follower/45-degree profile returns.
Deepseek Leonardo-hydraulic-sawmill at 6ae7aa8429a60a11ce86f45794fa2d93688af55d
has a symmetric 180/180 feed law, FEED_THROW*(1-cos(angle)), whose full stroke
is twice FEED_THROW. Both preflights verified clean independent repositories.
The package extraction boundary stays unchanged: pure arithmetic functions,
machinome.math degree/deferred operations, no framework dependency reversal.

## Goals / Non-Goals

Goals: a single periodic displacement envelope, with full signed lift and
explicit degree timing, used by both existing projects without changing motion.
Non-goals: arbitrary dwell schedules, a cam shape generator, velocity/force,
spring contact, arbitrary dimensional declarations, or a new simulation model.

## Decisions

`harmonic_cam_lift(angle, lift, rise_span=180, return_span=180)` is exported
flat and from cams. Defaults serve the current symmetric sawmill; Leonardo
explicitly passes 240 and its local return span. Lift means peak displacement
from the base, in caller units (mm or follower rotation degrees), not half stroke.
Signed lift retains mounting direction. No axis is inferred.

Use phase=angle-360*floor(angle/360), u=clamp01(phase/rise_span),
v=clamp01((phase-rise_span)/return_span), and
lift*(cos(180*v)-cos(180*u))/2. This is an independent textbook composition
over existing expression primitives, not a transfer of project-licensed source.
It has no symbolic branching or integer coercion. Floor wrapping replaces the
hammer's atan2 wrapping with the same periodic envelope at finite tested seams.
Physical domain requires positive spans with sum <=360. Spans are not validated
or silently repaired: zero numeric denominators raise; out-of-domain spans
retain algebraic behavior without a physical-envelope guarantee. Clamping u/v
defines dwell intervals, not tolerance or input validation.

Alternative direct cosine is the symmetric special case but cannot represent
Leonardo's asymmetric return/base dwell. Adding top dwell, phase or period
parameters has no current need; phase shifts remain angle subtraction by callers.

## Risks / Trade-offs

- Half-stroke confusion -> named full-lift documentation and independent 180° oracle.
- Lost release clearance -> keep 45/80 return distinction and unchanged contact tests.
- Periodic seams and floating rounding -> signed/unwrapped seam and deferred samples.
- Expanded downstream expressions -> inspect changed boundaries; no unbounded stringify.
- CAD memory -> one heavy process tree at a time, 768 MiB, zero swap, <=300 seconds;
  report bounded failures without increasing limits. CAD imports also use the slot.

## Migration Plan

Plan commit, missing-helper red, package tests/manual/distributions; then Sol
project adapters, independent actual numeric/deferred checks, affected bounded
CAD, build and fresh pixels. Parent review precedes sync/archive/implementation
commit and guarded local fast-forwards. Revert focused commits if needed; no
shared editable install changes, pushes, publication or unrelated source fixes.

## Open Questions

No unresolved interface choice. Consumer findings can narrow validation or
block this helper, with durable evidence and no incomplete archive.
