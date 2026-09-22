## 1. Red-first behavioral and cost evidence

- [ ] 1.1 Add focused running-constraint tests that fail before caching: identical finite standing bits reuse, moving first-sample recomputation, changed standing input and moving-name shape fallback, one-entry-per-constraint bound.
- [ ] 1.2 Add error/lifecycle tests for signed zeros, NaN/infinity/missing inputs, first-error order with competing standing and moving faults, failed-bind atomicity, quiet/untraced behavior, restore/reset and new run; prove the relevant tests red or baseline parity before implementation.

## 2. Bound-specific standing bind reuse

- [ ] 2.1 Implement a private successful-bind snapshot with exact finite standing input bits and stable graph/moving shape; use one Run-owned entry per compiled constraint and preserve the complete bind on any miss or uncertainty.
- [ ] 2.2 Reconstruct a fresh `_PathValue` on a hit and evaluate the moving cone at `t=0` in original order; publish only after success and leave later `at` calls, samples and fallback replay unchanged.
- [ ] 2.3 Clear the bounded run cache on successful restore/reset and verify all focused framework tests, error ordering and visit/evaluation counts.

## 3. Real Curta, framework, and architecture gates

- [ ] 3.1 On frozen project commit `7586002`, compare default-cadence first 48 ticks and full 360-degree turn CPU, exact 213-bank and ordered constraint samples; compare active stop, withdrawal and replay with the pre-change framework.
- [ ] 3.2 Repeat numerical and operational parity on the current production Curta checkpoint with its program identity pinned, and run relevant framework regression suites plus strict OpenSpec validation.
- [ ] 3.3 If evidence confirms the design, record the narrow amendment to ADR-124 and the framework architecture synthesis, synchronize the simulation spec, archive the change, and complete the two-commit cycle.
