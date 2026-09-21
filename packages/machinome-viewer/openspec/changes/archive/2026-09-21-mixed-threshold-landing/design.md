## Context

Viewer base `e82b5214e4460e606cb86608f042e7a6fcefa49d`, isolated branch/worktree
`mixed-threshold-landing` / `WTs/mixed-threshold-landing`. Framework paired
cycle is based on `e63700e`, amended planning commit `5673d1f`. Curta's actual
export reproduces the original direction error in the browser worker. The
pilot approved both executor corrections, the precision extension and local
integration after validation on 2026-09-21.

## Goals / Non-Goals

Goals: correct relative crossing and following-contact decisions, unchanged
bank arithmetic and nearest-float landings, genuine atomic refusals, producer
parity and actual Curta worker acceptance. Non-goals: print changes, new APIs,
document versions, tolerances, contact dynamics, release or publication.

## Decisions

1. Match the producer's branch-verified local orientation for mixed moving
   thresholds. Keep stationary thresholds on their existing path.
2. Match the conservative constant-relative-level certificate using exact
   rationals over binary input numbers, implemented with local BigInt arithmetic.
   Compose the skeleton's increment into the level; certify only affine
   operations and min/max/abs branches valid across the entire interval.
   Unknowns, curves and crossed kinks fall back to the existing executor.
   Prove zero exactly; do not treat a small nonzero slope as zero. Keep bank
   evaluation and clocked arithmetic unchanged.
3. Consume producer-generated exported fixtures byte for byte, without a
   framework import or dependency. Add negative controls for false certificates,
   genuine sliding modes and transactional refusal, and run existing corpus,
   widget, Python and distribution checks as appropriate.
4. Build a new bundle and run the full real Curta request through its worker
   in an isolated browser, with snapshot/replay and inspected pixels. No use
   of the pilot's live Studio session. Record the tested content pair.

## Risks / Trade-offs

- Exact proof costs more than sampling → use it only for mixed contact levels;
  retain existing fast paths and measure actual Curta behavior.
- Wrong certificate could suppress real motion → any unproved case falls back;
  require infinitesimal departures, kink and curved-expression negative tests.
- Cross-runtime numeric drift → identical binary-to-rational interpretation,
  copied producer fixture and real-machine acceptance.

## Migration Plan

Commit this ratified planning state, implement red-first, validate both runtimes
and Curta, record ADR disposition, synchronize and archive, then make one
implementation commit. Fast-forward main only if it remains clean at the base;
otherwise return the divergence to the pilot. No package/API version bump.
