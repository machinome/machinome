## Context

The viewer already has `ExpressionPath`/`PathValue`: a search-local bound snapshot and an exact moving-node cone used by running jump levels. `Run.searchedConstraint` does not use it. Its determined-motion branch builds the same constraint scope at every prescribed subdivision and bisection sample, then calls the full generic DAG evaluator. The pinned OperatingCurta post-cap profile measured 34.328 s of 53.846 s under this search during only 48 crank ticks; 28.827 s lay under generic expression evaluation. The expanded result-bank bound has many standing reads and few moving ones. The corresponding framework search-local path proved a 134-sample active-stop parity trace and a measured gain, but that is evidence to test here, not authority to port its code.

## Goals / Non-Goals

**Goals:** Evaluate a traced constraint's bound once at the first sampled point and thereafter only along its actual moving cone, while preserving bitwise sample values, the exact search schedule, outcome and full bank. Prove the speedup on the fixed committed export.

**Non-Goals:** Change constraints, subdivision/bisection counts, admission, eager piecewise evaluation, generic expression semantics, the untraced replay branch, or public API. No assumption that all future bounds fit the path evaluator.

## Decisions

- Create one `ExpressionPath` inside one determined `searchedConstraint`, initialized with the bound text and a conservative set of reads whose traced `Motion` is nonconstant or whose endpoint bits differ. A read without a traced motion is moving when its linear delta can change its sampled value. This keeps movement classification tied to the exact same physical paths already used for the search. Do not use `start === end` alone: +0 and -0 can compare equal yet have different bits at cached endpoints.
- At the first existing sample, bind the path to the exact scope already built by `level(t)`; at later samples, use `at` on that scope. Keep `Number(...)` conversion and the level subtraction in precisely the existing order. `ExpressionPath` reacquires generation-qualified binding roots and its existing `PathValue` preserves the DAG's operator order, including min/max choice and IEEE-754 values.
- If the path refuses an unsupported node shape, disable it for this search and use the existing generic `evaluateExpression` for that sample and all later samples. Do not catch other errors or reinterpret NaN; the original native error and refusal behavior must remain visible. Keep nontraced `constraintLevel`, final `constraintBound`, and all localization arithmetic untouched.
- Prove first with a viewer-owned red test that counts actual expression resolutions for a standing-heavy searched bound and checks the terminal bank, outcome, stop and replay against a generic baseline. Then trace the same pinned active Curta stop through both implementations, comparing the ordered sample scope and result IEEE-754 bytes, full 213-coordinate bank, and a reserved-core timing pair. If exact parity fails, correct the optimization or stop; never relax tolerance or sample count.

## Risks / Trade-offs

- [A motion classified standing might hide a signed-zero or interior change.] → Conservatively include nonconstant motions, compare endpoint values with `Object.is`, and compare exact sample traces, including bit patterns.
- [PathValue has a narrower syntax than generic evaluation.] → Its explicit `UnsupportedPathNode` causes a search-local fallback; all other errors propagate. Include a fallback fixture.
- [First bind walks a large graph.] → It is paid once per search instead of once per sample; measure the full segment and active stopped tick before claiming a gain.
- [Machine traces depend on ignored project artifacts.] → Keep synthetic viewer-owned tests in source control and cite pinned export hashes in evidence; do not commit the project export into viewer tests.

## Migration Plan

This is an internal viewer-only change. A previous bundle remains a rollback path; no document conversion or host API change is required. Build and smoke the installed primary bundle after viewer-main integration.

## Open Questions

Whether the current expanded Curta browser turn reaches acceptable wall time after this fix remains a measurement, not an assumption.
