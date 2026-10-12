## 1. Baseline and proof

- [ ] 1.1 Pin the OperatingCurta export and record first-48 default-dt CPU, bank and search-sample baseline.
- [ ] 1.2 Add red-first clean-rebind allocation and exactness tests, including presence, signed zero, NaN, scratch sample and thrown getter order.

## 2. Focused change

- [ ] 2.1 Make incremental `PathValue.bind` compare primitives and allocate dirty state only on a changed input.
- [ ] 2.2 Run focused suites, same-export sample/bank parity and CPU15 before/after; retain only if material.

## 3. Completion

- [ ] 3.1 Run proportionate broader validation, document limitations, sync spec, archive, and integrate while preserving concurrent viewer history.
