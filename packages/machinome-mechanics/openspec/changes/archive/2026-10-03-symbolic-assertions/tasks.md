## 1. Red first

- [x] 1.1 Run the suite against the framework bench before the change and record the nine failures at `tests/test_motion.py:46` and `tests/test_mechanisms.py:349` (eight subtests).

## 2. Assertions

- [x] 2.1 In `tests/test_motion.py`, assert `symbolic(result) is not None` through `machinome.expression_graph.symbolic` and drop the `OpenSCADConstant` import.
- [x] 2.2 In `tests/test_mechanisms.py`, assert `symbolic(part)` is not `None` for every part of every law under a symbolic driver and drop the `OpenSCADConstant` import.
- [x] 2.3 Add an `## Unreleased` section at the top of `CHANGELOG.md` with one bullet for the change.
- [x] 2.4 Let `test_the_manual_states_the_release` take the newest changelog section that is not `Unreleased` as the current release (found while applying: the added section failed it).

## 3. Evidence and record

- [x] 3.1 Run the whole suite against the bench (expected `201 passed`) and record before/after counts in `evidence.md`.
- [x] 3.2 Sync the `mechanisms` baseline spec, validate strictly, and archive the change.
