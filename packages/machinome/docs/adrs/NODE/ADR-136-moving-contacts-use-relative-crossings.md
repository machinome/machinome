# ADR-136: Moving contacts use relative crossings

**Status:** Accepted

**Date:** 2026-09-21

**Amends:** ADR-121's branch-departure and local landing implementation.

**Preserves:** ADR-124 point-evaluation arithmetic, ADR-108 absolute commits,
ADR-113/135 constraint observation and transactional refusals.

**Change:** [mixed-threshold-landing](../../../openspec/changes/archive/2026-09-21-mixed-threshold-landing/)

## Context

Operating Curta's actual carry lever fails an ordinary input-9/360° request
when a crank restraint observes it. Its engagement threshold overtakes the
lever, but the landing walk searches in the lever's own travel direction.
Correcting that direction exposes a second error: two parts following one
another give a rounded relative-level sample of +2.22e−16, falsely turning
on a reset whose opposing motion then looks like an impossible sliding mode.
Both faults have independent public-Sim reproductions and a real exported
Curta reproduction. Neither establishes a print defect.

The pilot approved correcting both executors, without changing geometry,
carry laws, tolerances, public declarations or genuine error refusals.

## Decision

A running self-read level that reads another moving source uses its local
relative crossing to orient the landing. With sources fixed at the located
crossing, search either side using the existing ulp stride and doubling
budget until the incoming/non-incoming branch bracket is demonstrated.
Supply that near-to-far orientation to the existing ordinal bisection. Its
body, absolute bank commit and invariant refusal are unchanged. A stationary
threshold keeps its previous evaluation path; a source-only crossing does
not reposition an unmoving driven coordinate.

Before treating a mixed contact's rounded sample as departure or crossing,
allow a conservative algebraic certificate of constant relative level.
Interpret finite binary input constants as exact rationals, represent affine
expressions by constant and slope, and compose the skeleton increment into
the level's own-coordinate reading. Only an exactly zero slope certifies
following contact. A nonzero slope, including the smallest subnormal, is
never suppressed on grounds of magnitude.

Supported operations are affine arithmetic and continuous `abs`, `min` and
`max` selections. A selection must be valid on its whole checked interval.
An exact selection crossing can partition the interval into affine pieces;
every piece must certify zero. Unsupported curves, moving divisors, unknown
expressions and exhausted proof work return to the existing executor. The
1024-piece proof-work ceiling limits proof effort, not admitted motion.

This is a certificate used in branch decisions, not an alternate evaluator.
Every bank increment still uses the existing floating-point expression
evaluation. No persistent state, epsilon, public flag or document field is
added. Clocked arithmetic and shared landing code are untouched. Python and
the independent browser executor each implement the certificate locally;
the unchanged producer/consumer package boundary remains in force.

## Alternatives and consequences

The part's own direction is insufficient when its threshold overtakes it.
Accepting an unlanded value after an invariant failure would hide a real
error. An epsilon would erase genuine small departures. Splitting requests,
adding clearance or rewriting Curta's carry law would conceal the executor
failure. Replacing bank arithmetic with exact arithmetic would change far
more than the demonstrated branch-decision defect.

The certificate costs additional work on mixed contact levels; it is not a
general contact solver and promises no proof for curved following motion.
Existing bounded-search limitations remain. Five producer scenarios pin
both directions, a restraint observer, following contact and a stationary
follower, including real replay and subsequent motion. Every previous corpus
scenario remains unchanged. Curta's carry-law reduction and its actual
browser carry pass without modifying source geometry or carry laws.
The archive's evidence records full regressions and complete-machine gates
separately from this decision; it does not certify Operating Curta's entire
unfinished mechanical roadmap or adopt its provisional T07 fit.
