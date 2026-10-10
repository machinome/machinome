## ADDED Requirements

### Requirement: Equivalent Follow Bound prefix probes may reuse a successful propagation

When running Bounds in one stretch require the same certified Follow-containing compiled prefix subprogram at the same finite IEEE-754 search fraction and fixed stretch inputs, the run SHALL be allowed to reuse the successful prefix result. Each Bound SHALL still evaluate its own expression and its original ordered search points, one-sided Follow cut evidence, crossing bracket, bisection and admission. A different subprogram, changed stretch, failed prefix or uncertain fraction SHALL use the original prefix replay. Reuse SHALL NOT change any value, earliest error, refusal, landing, stop, bank, replay, declaration or document.

#### Scenario: Paired bounds share an identical successful prefix
- **WHEN** two dynamic Bounds of a certified Follow target query the same compiled subprogram at the same finite fraction during one stretch
- **THEN** a successful prefix may be reused, while both Bounds independently evaluate their levels and produce their original bank and stop results

#### Scenario: Different fraction, subprogram, or stretch
- **WHEN** a Bound asks at a neighboring representable cut side, has a distinct compiled edge, or runs in a later tick or restored run
- **THEN** no stale prefix result is reused and the original fraction-specific propagation and Bound result are observed

#### Scenario: Prefix or Bound evaluation fails
- **WHEN** a prefix fails before completion or a Bound expression fails after a successful prefix
- **THEN** the same first error arises in the original search order; a failed prefix does not become reusable, and a successful prefix does not skip a later Bound's own evaluation
