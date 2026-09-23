## 1. Red-first contract

- [ ] 1.1 Add focused repeat-fold and tick-lifetime tests; confirm the call-count test fails on the unchanged implementation.
- [ ] 1.2 Add signed-zero, distinct-root, custom/non-finite, failed-fold, eviction, failure-reset, restore, and two-run controls.

## 2. Narrow implementation

- [ ] 2.1 Implement the private finite-bit key, 256-entry successful-fold cache, and tick-scoped lifetime.
- [ ] 2.2 Run focused tests and relevant existing simulation regressions.

## 3. Production proof and completion

- [ ] 3.1 Compare unchanged frozen Curta ordered Bound sample bits and the full bank against the same-command baseline.
- [ ] 3.2 Measure repeated paired process CPU time and run the full framework test suite.
- [ ] 3.3 Sync the accepted simulation spec, archive this change with evidence, and commit the completed cycle; integrate only from the verified current main head.
