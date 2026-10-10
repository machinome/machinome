## 1. Red-first path and Curta evidence

- [x] 1.1 Add focused tests that fail on the planning base for same-instance exact successful-bind reuse, retained later `at` behavior, unchanged unreferenced inputs and bounded one-entry storage.
- [x] 1.2 Pin fallback/error tests for changed finite bits, signed zero, NaN/infinity, missing/custom inputs and mappings, competing eager errors, failed-bind recovery, `bind_from` invalidation and fresh path/reset/replay lifecycle; demonstrate red or baseline parity before implementation.

## 2. Path-local implementation

- [x] 2.1 Add exact finite graph-referenced input identity and one last-successful-bind entry to `_PathValue`, with successful publication only after its existing eager walk.
- [x] 2.2 Return the proven result without changing path standing state on a hit, invalidate on successful `bind_from`, and retain the original walk and errors on any miss or uncertainty.
- [x] 2.3 Run focused evaluator, running Bound, path-order and error-order regressions; confirm no new public declaration, document field, timestep, tolerance or sample count.

## 3. Originating project and completion

- [x] 3.1 Measure frozen Curta first48 default-dt baseline/candidate CPU and compare all ordered Bound sample bytes and 213 bank; compare a full turn and active stop/restore/replay without changing project source.
- [x] 3.2 Repeat relevant exact parity and speed checks on a pinned current-production Curta program, run the complete top-level framework suite and strict OpenSpec validation, and obtain independent source review.
- [x] 3.3 If gates confirm the design, update the simulation baseline spec and architectural record as applicable, archive this OpenSpec change, make the implementation commit, and integrate locally only after verifying current main and preserving unrelated state.
