## 1. Red first

- [ ] 1.1 Run the suite against the framework bench before the change and record the nine failures at `tests/test_motion.py:46` and `tests/test_mechanisms.py:349` (eight subtests).

## 2. Assertions

- [ ] 2.1 In `tests/test_motion.py`, assert `symbolic(result) is not None` through `machinome.expression_graph.symbolic` and drop the `OpenSCADConstant` import.
- [ ] 2.2 In `tests/test_mechanisms.py`, assert `symbolic(part)` is not `None` for every part of every law under a symbolic driver and drop the `OpenSCADConstant` import.
- [ ] 2.3 Add an `## Unreleased` section at the top of `CHANGELOG.md` with one bullet for the change.

## 3. Evidence and record

- [ ] 3.1 Run the whole suite against the bench (expected `201 passed`) and record before/after counts in `evidence.md`.
- [ ] 3.2 Sync the `mechanisms` baseline spec, validate strictly, and archive the change.
