## 1. Prove existing cost and semantics

- [ ] 1.1 Pin current Curta project source hashes, compiled program identity and a bounded before-state/CPU measurement.
- [ ] 1.2 Add red tests for repeated node-keyed evaluation and numeric min/max face dispatch, plus exact floating, first-error precedence and malformed-arity parity in both evaluators.

## 2. Implement and verify

- [ ] 2.1 Compile a GraphValue-local postorder/child-slot plan and evaluate fresh values from it; preserve public invalid-arity errors in GraphValue and _PathValue, and make focused tests green.
- [ ] 2.2 Recheck the same Curta graph and exact 213-entry bank, measure bounded CPU, and run expression, source-timing, carry, stop and exact-geometry regressions.
- [ ] 2.3 Sync baseline spec, archive change, strict-validate, commit the completed two-commit cycle and integrate on verified current framework main.
