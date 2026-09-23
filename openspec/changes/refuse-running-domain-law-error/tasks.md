## 1. Red-first public running tests

- [ ] 1.1 Add a minimal public `Sim` test with valid rest `feed=0`, law `sqrt(0.1-feed)`, and immediate `to=0.2`; prove the current raw domain `ValueError` leaves the failed command active, then assert the intended named `UnsupportedLaw`, atomic bank/tick/record/pose, and free input.
- [ ] 1.2 Add red-first finite-input overflow (`feed*feed` at `1e308`) and a two-tick domain failure whose first committed tick and admitted travel remain; keep a finite square-root boundary and an unrelated non-law `ValueError`/refusal unchanged.

## 2. Focused evaluator correction

- [ ] 2.1 Audit compiled running-law numeric evaluation entry points; convert only their already-evaluated domain failures and non-finite results to named `UnsupportedLaw`, preserving order and not catching unrelated integration, Bound or pose errors.
- [ ] 2.2 Verify the existing `Run.integrate` typed-refusal path retires only commands moved in the failing tick and publishes no part of that tick, without undoing earlier successful ticks.

## 3. Validation and cycle completion

- [ ] 3.1 Run focused running tests, the relevant simulation suite, and a public `Sim` reproduction; inspect the diff for changed arithmetic, extra evaluation points, export fields or unrelated exception handling.
- [ ] 3.2 After evidence review, sync the delta spec, archive the change, complete the implementation commit, and coordinate framework integration and paired viewer parity validation. Do not modify the viewer repository or push.
